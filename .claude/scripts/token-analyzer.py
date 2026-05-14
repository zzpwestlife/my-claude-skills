import os
import glob

def estimate_tokens(text):
    # Simple estimation: 1 token approx 4 characters
    return len(text) // 4

def analyze_directory(directory):
    files = glob.glob(os.path.join(directory, "**/*"), recursive=True)
    active_report = []
    reference_report = []
    active_tokens = 0
    reference_tokens = 0
    
    for file_path in files:
        if not os.path.isfile(file_path) or not file_path.endswith(('.md', '.py', '.sh', '.json')):
            continue
            
        # Classify as Reference (Inactive) or Active
        is_reference = (
            "archive" in file_path or 
            "tmp" in file_path or 
            "docs/references" in file_path or
            "_full.md" in file_path or
            "lib/" in file_path or
            "docs/whitepapers" in file_path or
            "docs/mental_model" in file_path
        )
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            tokens = estimate_tokens(content)
            lines = content.count('\n') + 1
            
            entry = {
                'path': file_path,
                'lines': lines,
                'tokens': tokens
            }
            
            if is_reference:
                reference_tokens += tokens
                reference_report.append(entry)
            else:
                active_tokens += tokens
                active_report.append(entry)
    
    # Sort by tokens descending
    active_report.sort(key=lambda x: x['tokens'], reverse=True)
    return active_report, active_tokens, reference_report, reference_tokens

if __name__ == "__main__":
    claude_dir = ".claude"
    active_rep, active_total, ref_rep, ref_total = analyze_directory(claude_dir)
    
    print(f"Token Analysis for {claude_dir}")
    print("=" * 80)
    print(f"ACTIVE CONTEXT (Loaded by Agent) - Total: {active_total}")
    print("-" * 80)
    print(f"{'Path':<60} | {'Lines':<5} | {'Tokens':<6}")
    print("-" * 80)
    for entry in active_rep[:15]: # Top 15 Active
        print(f"{entry['path']:<60} | {entry['lines']:<5} | {entry['tokens']:<6}")
        
    print("\n" + "=" * 80)
    print(f"REFERENCE CONTEXT (On-Demand Only) - Total: {ref_total}")
    print("-" * 80)
    for entry in sorted(ref_rep, key=lambda x: x['tokens'], reverse=True)[:10]:
        print(f"{entry['path']:<60} | {entry['lines']:<5} | {entry['tokens']:<6}")
        
    print("=" * 80)
    print(f"GRAND TOTAL: {active_total + ref_total}")
    print(f"OPTIMIZATION SAVINGS (Active vs Total): {round((1 - active_total/(active_total+ref_total))*100, 1)}%")
