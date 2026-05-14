import sys
import os
import glob
from pathlib import Path

def get_latest_transcript():
    """Try to find the latest transcript in common locations."""
    # Common locations for Claude Code transcripts
    locations = [
        # Check standard user history first
        os.path.expanduser("~/.claude/history.jsonl"),
        # Check standard backups (finding newest)
    ]
    
    # Try to find newest backup history
    backup_pattern = os.path.expanduser("~/.claude_backup_*/history.jsonl")
    backups = glob.glob(backup_pattern)
    if backups:
        locations.extend(sorted(backups, reverse=True))

    locations.append(os.path.join(os.getcwd(), ".claude/tmp/session_summary.md"))
    
    for loc in locations:
        if os.path.exists(loc):
            return loc
            
    # Check for transcripts in project directories if structure is known
    # (Simplified for now)
    return None

def main():
    # 1. Get arguments or auto-detect
    log_file = None
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        print("No log file specified. Attempting to auto-detect latest session log...")
        log_file = get_latest_transcript()
        
    # 2. List existing skills
    skills_dir = ".claude/skills"
    skills = []
    if os.path.exists(skills_dir):
        skills = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
    
    print(f"Current Skills ({len(skills)}):")
    for s in skills:
        print(f"- {s}")
    
    if not log_file:
        print("\n❌ Could not auto-detect a log file.")
        print("Please provide a path explicitly: /audit-skills <path/to/log>")
        sys.exit(1)
        
    # 3. Read log file
    print(f"\nAnalyzing log file: {log_file}")
    
    if os.path.exists(log_file):
        print("\n--- Log Content Preview (Last 3000 chars) ---")
        try:
            # Read the END of the file as it's more relevant for recent context
            file_size = os.path.getsize(log_file)
            read_size = 3000
            
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                if file_size > read_size:
                    f.seek(file_size - read_size)
                    content = f.read()
                    # Skip partial line at start if we seeked
                    first_newline = content.find('\n')
                    if first_newline != -1:
                        content = content[first_newline+1:]
                else:
                    content = f.read()
                
                print(content)
        except Exception as e:
            print(f"Error reading log file: {e}")
    else:
        print(f"\nError: Log file '{log_file}' not found.")

if __name__ == "__main__":
    main()
