#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


REQUIRED_FILES = ["gt.jsonl", "dev.jsonl", "holdout.jsonl", "regression.jsonl"]


def _read_jsonl(path: Path) -> tuple[List[Dict[str, Any]], List[str]]:
    rows: List[Dict[str, Any]] = []
    errors: List[str] = []
    if not path.exists():
        return rows, [f"Missing required file: {path}"]

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path}:{line_number}: row must be a JSON object")
            continue
        rows.append(value)
    if not rows:
        errors.append(f"{path}: file must contain at least one case")
    return rows, errors


def validate_dataset(dataset_dir: Path) -> Dict[str, Any]:
    errors: List[str] = []
    summary: Dict[str, int] = {}

    if not dataset_dir.exists() or not dataset_dir.is_dir():
        errors.append(f"Dataset directory not found: {dataset_dir}")
        return {"ok": False, "errors": errors, "summary": summary}

    for filename in REQUIRED_FILES:
        path = dataset_dir / filename
        rows, row_errors = _read_jsonl(path)
        errors.extend(row_errors)
        summary[filename] = len(rows)

        for index, row in enumerate(rows, 1):
            prefix = f"{path}:{index}"
            if not row.get("id"):
                errors.append(f"{prefix}: missing `id`")
            if "expected" not in row:
                errors.append(f"{prefix}: missing `expected`")
            if "actual" not in row and "input" not in row:
                errors.append(f"{prefix}: missing both `actual` and `input`")
            trace = row.get("trace")
            if not trace:
                errors.append(f"{prefix}: missing `trace`")
            elif "://" not in str(trace):
                trace_path = dataset_dir / str(trace)
                if not trace_path.exists():
                    errors.append(f"{prefix}: trace path does not exist: {trace_path}")

    return {"ok": not errors, "errors": errors, "summary": summary}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a skill-evolver dataset directory.")
    parser.add_argument("dataset_dir")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = validate_dataset(Path(args.dataset_dir).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["ok"]:
        print("Dataset validation passed.")
    else:
        print("Dataset validation failed:", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
