#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".claude",
    ".venv",
    "node_modules",
    "dist",
    "build",
}


def is_text_file(path: Path) -> bool:
    return path.suffix in {".py", ".go", ".php", ".js", ".ts", ".tsx", ".sh"}


def scan_module_readme(root: Path) -> list[str]:
    missing = []
    for path in root.rglob("README.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        required = ["## Role", "## Logic", "## Constraints", "## Submodules"]
        if not all(section in content for section in required):
            missing.append(str(path))
    return missing


def scan_headers(root: Path) -> list[str]:
    missing = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and is_text_file(path):
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            if len(lines) < 3:
                missing.append(str(path))
                continue
            if not (lines[0].startswith("INPUT:") and lines[1].startswith("OUTPUT:") and lines[2].startswith("POS:")):
                missing.append(str(path))
    return missing


def main() -> int:
    root = Path(".")
    readme_missing = scan_module_readme(root)
    header_missing = scan_headers(root)

    if readme_missing:
        print("Missing module README sections:")
        for path in readme_missing:
            print(f"- {path}")
    if header_missing:
        print("Missing source file headers:")
        for path in header_missing:
            print(f"- {path}")

    return 1 if readme_missing or header_missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
