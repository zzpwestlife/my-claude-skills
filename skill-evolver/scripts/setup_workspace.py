#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict


def detect_git_status(skill_dir: Path) -> str:
    try:
        git_check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=skill_dir,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return "git_unavailable"

    if git_check.returncode != 0:
        return "not_initialized"

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=skill_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    return "clean" if status.stdout.strip() == "" else "dirty"


def setup_workspace(skill_dir: Path, dataset_dir: Path, output_dir: Path) -> Dict[str, str]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"Missing required file: {skill_md}")
    if not dataset_dir.exists() or not dataset_dir.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    workspace_root = output_dir / "workspace"
    workspace_root.mkdir(parents=True, exist_ok=True)
    logs_dir = output_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    workspace_dir = workspace_root / skill_dir.name
    if workspace_dir.exists():
        shutil.rmtree(workspace_dir)
    shutil.copytree(skill_dir, workspace_dir)

    git_status = detect_git_status(skill_dir)
    baseline = {
        "skill_dir": str(skill_dir),
        "dataset_dir": str(dataset_dir),
        "workspace_dir": str(workspace_dir),
        "git_status": git_status,
        "baseline_eval": {
            "status": "not_run",
            "reason": "Setup captured workspace and paths only.",
        },
    }
    (output_dir / "baseline.json").write_text(
        json.dumps(baseline, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    plan_text = "\n".join(
        [
            "# Evolve Plan",
            "",
            "## Paths",
            f"- Skill dir: `{skill_dir}`",
            f"- Dataset dir: `{dataset_dir}`",
            f"- Workspace dir: `{workspace_dir}`",
            f"- Output dir: `{output_dir}`",
            "",
            "## Target Metric",
            "- Improve dev pass rate without strict regression.",
            "",
            "## Evaluation Strategy",
            "- L1: structure, safety, and GT smoke checks",
            "- L2: full dev split with per-case traces",
            "- L3: holdout and regression checks when triggered",
            "",
            "## Gate Thresholds",
            "- Keep only when all five gate dimensions pass",
            "",
            "## Mutation Strategy",
            "- Starting layer: `layer1`",
            "- Promote layer after repeated no-keep iterations",
            "",
            "## Stop Conditions",
            "- Stop on iteration budget, exhausted layers, no trace evidence, or target metric reached",
            f"- Git status: `{git_status}`",
        ]
    )
    (output_dir / "evolve_plan.md").write_text(plan_text + "\n", encoding="utf-8")

    return {
        "git_status": git_status,
        "workspace_dir": str(workspace_dir),
        "output_dir": str(output_dir),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a local skill-evolver workspace.")
    parser.add_argument("--skill-dir", required=True)
    parser.add_argument("--dataset-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = setup_workspace(
        Path(args.skill_dir).resolve(),
        Path(args.dataset_dir).resolve(),
        Path(args.output_dir).resolve(),
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Workspace: {result['workspace_dir']}")
        print(f"Output: {result['output_dir']}")
        print(f"Git status: {result['git_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
