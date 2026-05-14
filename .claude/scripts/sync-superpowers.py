#!/usr/bin/env python3
import os
import json
import subprocess
import shutil
import sys
from datetime import datetime

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLAUDE_DIR = os.path.join(PROJECT_ROOT, ".claude")
LOCK_FILE = os.path.join(CLAUDE_DIR, "superpowers.lock.json")
TEMP_DIR = os.path.join(CLAUDE_DIR, "tmp", "superpowers-sync")

def load_lock_file():
    if not os.path.exists(LOCK_FILE):
        print(f"Error: Lock file not found at {LOCK_FILE}")
        sys.exit(1)
    with open(LOCK_FILE, 'r') as f:
        return json.load(f)

def save_lock_file(data):
    with open(LOCK_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Updated lock file: {LOCK_FILE}")

def run_command(cmd, cwd=None):
    try:
        result = subprocess.check_output(cmd, shell=True, cwd=cwd, stderr=subprocess.STDOUT)
        return result.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(e.output.decode('utf-8'))
        sys.exit(1)

def run_command_output(cmd, cwd=None):
    try:
        result = subprocess.check_output(cmd, shell=True, cwd=cwd, stderr=subprocess.STDOUT)
        return 0, result.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output.decode('utf-8')

def main():
    print("🚀 Superpowers Sync Tool")
    
    lock_data = load_lock_file()
    repo_url = lock_data["repository"]
    current_commit = lock_data["last_synced_commit"]
    customized_files = set(lock_data.get("customized_files", []))
    
    print(f"Current version: {current_commit[:7]}")
    
    # 1. Clone Upstream
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    print(f"Cloning {repo_url}...")
    run_command(f"git clone {repo_url} {TEMP_DIR}")
    
    upstream_commit = run_command("git rev-parse HEAD", cwd=TEMP_DIR)
    print(f"Upstream version: {upstream_commit[:7]}")
    
    if upstream_commit == current_commit:
        print("✅ Already up to date.")
        sys.exit(0)
        
    print("\n📦 Starting Update Process...")
    
    # 2. Iterate and Update
    # Map upstream paths to local paths
    # Upstream structure: skills/, commands/, hooks/session-start
    # Local structure: .claude/skills/, .claude/commands/, .claude/hooks/superpowers-session-start
    
    updated_count = 0
    conflict_count = 0
    
    # Sync Skills
    upstream_skills_dir = os.path.join(TEMP_DIR, "skills")
    for skill_name in os.listdir(upstream_skills_dir):
        skill_path = os.path.join("skills", skill_name, "SKILL.md")
        local_skill_path = os.path.join(CLAUDE_DIR, "skills", skill_name, "SKILL.md")
        upstream_skill_file = os.path.join(upstream_skills_dir, skill_name, "SKILL.md")
        
        if not os.path.exists(upstream_skill_file):
            continue
            
        if skill_path in customized_files:
            # 3-way merge
            upstream_rel_path = f"skills/{skill_name}/SKILL.md"
            base_tmp_file = os.path.join(TEMP_DIR, f"base_{skill_name}_SKILL.md")
            
            # Extract base file content
            code, out = run_command_output(f"git show {current_commit}:{upstream_rel_path}", cwd=TEMP_DIR)
            if code == 0:
                with open(base_tmp_file, 'w') as f:
                    f.write(out)
            else:
                with open(base_tmp_file, 'w') as f:
                    f.write("")
                    
            # git merge-file <current> <base> <other>
            merge_code, _ = run_command_output(f"git merge-file {local_skill_path} {base_tmp_file} {upstream_skill_file}")
            
            if merge_code == 0:
                print(f"✅ [AUTO-MERGED] {skill_path} - Clean merge.")
                updated_count += 1
            else:
                print(f"⚠️  [CONFLICT] {skill_path} - Conflicts found, please resolve markers (<<<<<<<).")
                conflict_count += 1
        else:
            # Safe to overwrite if not customized
            # But let's check if local exists first
            if os.path.exists(local_skill_path):
                shutil.copy2(upstream_skill_file, local_skill_path)
                print(f"✅ [UPDATED] {skill_path}")
                updated_count += 1
            else:
                # New skill
                os.makedirs(os.path.dirname(local_skill_path), exist_ok=True)
                shutil.copy2(upstream_skill_file, local_skill_path)
                print(f"✨ [NEW] {skill_path}")
                updated_count += 1

    # Sync Commands
    upstream_commands_dir = os.path.join(TEMP_DIR, "commands")
    if os.path.exists(upstream_commands_dir):
        for cmd_file in os.listdir(upstream_commands_dir):
            if not cmd_file.endswith(".md"): continue
            
            local_cmd_path = os.path.join(CLAUDE_DIR, "commands", cmd_file)
            upstream_cmd_path = os.path.join(upstream_commands_dir, cmd_file)
            
            shutil.copy2(upstream_cmd_path, local_cmd_path)
            print(f"✅ [UPDATED] commands/{cmd_file}")
            updated_count += 1

    # 3. Update Lock File
    lock_data["last_synced_commit"] = upstream_commit
    lock_data["last_synced_date"] = datetime.now().strftime("%Y-%m-%d")
    save_lock_file(lock_data)
    
    print("\n" + "="*40)
    print(f"Summary: {updated_count} files updated, {conflict_count} files have conflicts.")
    
    if conflict_count > 0:
        print("👉 Please manually resolve the conflict markers (<<<<<<<) in the affected files.")
        print(f"   Upstream source is currently in: {TEMP_DIR}")
        print("   After resolving, commit manually.")
    else:
        shutil.rmtree(TEMP_DIR)
        print("🤖 All files merged cleanly! Please review and commit manually.")
        
if __name__ == "__main__":
    main()
