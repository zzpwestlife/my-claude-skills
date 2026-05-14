#!/usr/bin/env python3
import os
import sys
import json
import argparse
import datetime
import re
from pathlib import Path

# Configuration
SKILLS_ROOT = Path(os.environ.get('CLAUDE_PLUGIN_ROOT', Path.home() / ".claude/skills")).resolve()
# If we are running inside the skill directory itself, adjust root
if SKILLS_ROOT.name == "scripts":
    SKILLS_ROOT = SKILLS_ROOT.parent.parent

SKILL_TEMPLATE = """---
name: {name}
description: {description}
version: "1.0.0"
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - AskUserQuestion
---

# {name}

{description}

## Usage
To use this skill, simply invoke the tools defined below or ask Claude to help you with the relevant task.

## 🧠 Learned Experience
This section contains knowledge distilled from previous interactions.
<!-- EVOLUTION_START -->
<!-- EVOLUTION_END -->

## Tools
"""

def get_skill_dir(name):
    return SKILLS_ROOT / name

def get_skill_file(name):
    return get_skill_dir(name) / "SKILL.md"

def get_evolution_file(name):
    return get_skill_dir(name) / "evolution.json"

def ensure_skill_exists(name):
    path = get_skill_dir(name)
    if not path.exists():
        print(f"Error: Skill '{name}' does not exist at {path}")
        sys.exit(1)

def forge_skill(name, description, tools_def=None):
    """Create a new skill structure."""
    skill_dir = get_skill_dir(name)
    if skill_dir.exists():
        print(f"Warning: Skill '{name}' already exists. Skipping creation.")
        return

    print(f"Forging new skill: {name}...")
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "scripts").mkdir(exist_ok=True)
    
    # Create initial evolution.json
    evolution_data = {
        "name": name,
        "created_at": datetime.datetime.now().isoformat(),
        "preferences": [],
        "fixes": [],
        "prompts": []
    }
    with open(get_evolution_file(name), 'w') as f:
        json.dump(evolution_data, f, indent=2)
    
    # Create SKILL.md
    content = SKILL_TEMPLATE.format(name=name, description=description)
    if tools_def:
        content += "\n" + tools_def
    
    with open(get_skill_file(name), 'w') as f:
        f.write(content)
        
    print(f"Skill '{name}' created successfully at {skill_dir}")

def refine_skill(name, exp_type, content):
    """Add experience to evolution.json and stitch."""
    ensure_skill_exists(name)
    
    evo_file = get_evolution_file(name)
    if not evo_file.exists():
        # Create if missing
        evolution_data = {
            "name": name,
            "created_at": datetime.datetime.now().isoformat(),
            "preferences": [],
            "fixes": [],
            "prompts": []
        }
    else:
        with open(evo_file, 'r') as f:
            evolution_data = json.load(f)
            
    # Normalize type
    valid_types = {"preference": "preferences", "fix": "fixes", "prompt": "prompts"}
    target_key = valid_types.get(exp_type.lower())
    
    if not target_key:
        print(f"Error: Invalid experience type '{exp_type}'. Must be one of: preference, fix, prompt")
        sys.exit(1)
        
    # Add content if not exists
    if content not in evolution_data.get(target_key, []):
        if target_key not in evolution_data:
            evolution_data[target_key] = []
        evolution_data[target_key].append(content)
        print(f"Added new {exp_type}: {content}")
        
        with open(evo_file, 'w') as f:
            json.dump(evolution_data, f, indent=2)
            
        stitch_skill(name)
    else:
        print("Experience already exists. Skipping.")

def stitch_skill(name):
    """Inject evolution data into SKILL.md."""
    ensure_skill_exists(name)
    
    evo_file = get_evolution_file(name)
    skill_file = get_skill_file(name)
    
    if not evo_file.exists():
        print("No evolution data found.")
        return

    with open(evo_file, 'r') as f:
        data = json.load(f)
        
    # Generate Markdown Section
    md_lines = []
    
    if data.get("preferences"):
        md_lines.append("### 💡 Preferences")
        for item in data["preferences"]:
            md_lines.append(f"- {item}")
        md_lines.append("")
        
    if data.get("fixes"):
        md_lines.append("### 🔧 Troubleshooting & Fixes")
        for item in data["fixes"]:
            md_lines.append(f"- {item}")
        md_lines.append("")
        
    if data.get("prompts"):
        md_lines.append("### 📝 Prompt Optimization")
        for item in data["prompts"]:
            md_lines.append(f"- {item}")
        md_lines.append("")
        
    if not md_lines:
        md_lines.append("_No learned experience yet._")
        
    injection_content = "\n".join(md_lines)
    
    # Read SKILL.md
    with open(skill_file, 'r') as f:
        content = f.read()
        
    # Regex Replace
    pattern = r"(<!-- EVOLUTION_START -->)(.*?)(<!-- EVOLUTION_END -->)"
    replacement = f"\\1\n{injection_content}\n\\3"
    
    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    
    if count == 0:
        print("Warning: Could not find <!-- EVOLUTION_START --> tags in SKILL.md. Appending to end.")
        new_content = content + "\n\n## 🧠 Learned Experience\n<!-- EVOLUTION_START -->\n" + injection_content + "\n<!-- EVOLUTION_END -->"
    
    with open(skill_file, 'w') as f:
        f.write(new_content)
        
    print(f"Stitched skill '{name}' successfully.")

def main():
    parser = argparse.ArgumentParser(description="Skill Architect Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Forge Command
    forge_parser = subparsers.add_parser("forge", help="Create a new skill")
    forge_parser.add_argument("name", help="Skill name")
    forge_parser.add_argument("--desc", help="Description", default="A new skill")
    
    # Refine Command
    refine_parser = subparsers.add_parser("refine", help="Add experience to a skill")
    refine_parser.add_argument("name", help="Skill name")
    refine_parser.add_argument("type", help="Type: preference, fix, prompt")
    refine_parser.add_argument("content", help="Content of the experience")
    
    # Stitch Command
    stitch_parser = subparsers.add_parser("stitch", help="Manually stitch skill")
    stitch_parser.add_argument("name", help="Skill name")

    args = parser.parse_args()
    
    if args.command == "forge":
        forge_skill(args.name, args.desc)
    elif args.command == "refine":
        refine_skill(args.name, args.type, args.content)
    elif args.command == "stitch":
        stitch_skill(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
