# Distribution Contract

The distributed zip should unpack to one top-level directory named `skill-evolver/`.

Required bundle contents:

- `SKILL.md`
- `references/artifacts.md`
- `references/dataset-format.md`
- `references/distribution.md`
- `references/runbook.md`
- `scripts/check_skill_package.py`
- `scripts/setup_workspace.py`
- `scripts/validate_dataset.py`
- `assets/example/target_skill/SKILL.md`
- `assets/example/dataset/gt.jsonl`
- `assets/example/dataset/dev.jsonl`
- `assets/example/dataset/holdout.jsonl`
- `assets/example/dataset/regression.jsonl`

The bundle must not include:

- `.DS_Store`
- `.git/`
- `__pycache__/`
- `.pytest_cache/`
- repo-level tests, PDFs, build artifacts, or temporary smoke outputs

All bundled scripts must use only the Python standard library and must not import project-specific packages. A recipient should be able to unzip the bundle, run `python3 scripts/check_skill_package.py . --json`, and get a successful result without installing anything else.
