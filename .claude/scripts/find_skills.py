import os
import sys
import re

def find_skills(query_terms):
    """
    Simple keyword-based skill search.
    In a more advanced version, this would use embeddings/semantic search.
    """
    skills_dir = ".claude/skills"
    if not os.path.exists(skills_dir):
        print("No skills directory found.")
        return

    matches = []
    
    # 1. Scan all skills
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if not os.path.isdir(skill_path):
            continue
            
        md_file = os.path.join(skill_path, "SKILL.md")
        if not os.path.exists(md_file):
            continue
            
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Calculate score based on term matches
            score = 0
            content_lower = content.lower()
            name_lower = skill_name.lower()
            
            for term in query_terms:
                term = term.lower()
                if term in name_lower:
                    score += 10  # Name match is strong
                if term in content_lower:
                    score += 1   # Content match is weak
            
            if score > 0:
                # Extract description from frontmatter if possible
                desc = "No description"
                desc_match = re.search(r'description:\s*"(.*?)"', content)
                if desc_match:
                    desc = desc_match.group(1)
                
                matches.append({
                    "name": skill_name,
                    "score": score,
                    "desc": desc,
                    "path": md_file
                })
        except Exception as e:
            continue

    # 2. Sort and Display
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    if not matches:
        print(f"No skills found matching: {' '.join(query_terms)}")
        print("\nTip: Try broader terms like 'test', 'git', 'plan'")
        return

    print(f"🔍 Found {len(matches)} relevant skills:\n")
    for m in matches[:5]:  # Top 5
        print(f"🎯 {m['name']} (Score: {m['score']})")
        print(f"   📖 {m['desc']}")
        print(f"   📂 {m['path']}")
        print("")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: /find-skills <keywords>")
        sys.exit(1)
    
    find_skills(sys.argv[1:])
