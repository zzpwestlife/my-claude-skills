#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


REQUIRED_FILES = [
    "SKILL.md",
    "references/artifacts.md",
    "references/dataset-format.md",
    "references/distribution.md",
    "references/runbook.md",
    "references/safety-rules.md",
    "references/mutation-layers.md",
    "references/evaluation-layers.md",
    "references/eval-noise.md",
    "scripts/check_skill_package.py",
    "scripts/setup_workspace.py",
    "scripts/validate_dataset.py",
    "assets/example/target_skill/SKILL.md",
    "assets/example/dataset/gt.jsonl",
    "assets/example/dataset/dev.jsonl",
    "assets/example/dataset/holdout.jsonl",
    "assets/example/dataset/regression.jsonl",
]

BANNED_NAMES = {".DS_Store", "__pycache__", ".pytest_cache", ".git"}
BANNED_SKILL_TEXT = ["this repository", "skill" + "_evolve.cli"]


def check_skill_package(skill_dir: Path) -> Dict[str, Any]:
    errors: List[str] = []
    if not skill_dir.exists() or not skill_dir.is_dir():
        return {"ok": False, "errors": [f"Skill directory not found: {skill_dir}"]}

    for relative in REQUIRED_FILES:
        if not (skill_dir / relative).exists():
            errors.append(f"Missing required file: {relative}")

    for path in skill_dir.rglob("*"):
        if path.name in BANNED_NAMES:
            errors.append(f"Bundle contains banned path: {path.relative_to(skill_dir)}")

    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append("SKILL.md must start with YAML frontmatter")
        if "name: skill-evolver" not in text:
            errors.append("SKILL.md frontmatter must include `name: skill-evolver`")
        if "description:" not in text:
            errors.append("SKILL.md frontmatter must include `description`")
        for banned in BANNED_SKILL_TEXT:
            if banned in text:
                errors.append(f"SKILL.md contains repo-specific text: {banned}")

    for script in (skill_dir / "scripts").glob("*.py") if (skill_dir / "scripts").exists() else []:
        script_text = script.read_text(encoding="utf-8")
        if "skill" + "_evolve" in script_text:
            errors.append(f"Script imports or references repo package: {script.name}")

    return {"ok": not errors, "errors": errors, "checked_files": len(REQUIRED_FILES)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a distributed skill-evolver bundle.")
    parser.add_argument("skill_dir")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = check_skill_package(Path(args.skill_dir).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["ok"]:
        print("Skill package validation passed.")
    else:
        print("Skill package validation failed:", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
