#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def has_file(name: str) -> bool:
    return Path(name).exists()


def run(cmd: list[str]) -> int:
    result = subprocess.run(cmd, check=False)
    return result.returncode


def main() -> int:
    if has_file("go.mod"):
        if shutil.which("go") is None:
            return 2
        return run(["go", "vet", "./..."])
    if has_file("requirements.txt") or has_file("pyproject.toml"):
        if shutil.which("flake8") is None:
            return 3
        return run(["flake8", "."])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
