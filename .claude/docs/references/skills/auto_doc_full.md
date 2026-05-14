# Auto-Doc Skill: Recursive Documentation Maintenance

## Purpose
Ensure documentation is always synchronized with code changes through a mandatory 3-layer update process.

## The 3-Layer Documentation Structure

### Level 1: `ARCHITECTURE.md` (Root)
- **Scope**: Entire Project
- **Content**: High-level system design, module relationships, and technology stack.
- **Update Trigger**: Only when adding/removing modules or changing core architecture.

### Level 2: `CLAUDE.md` (Per Directory)
- **Scope**: Specific Directory (e.g., `scripts/`, `src/backend/`)
- **Role**: Combines **Context Injection** (Rules) and **Directory Manifest** (Index).
- **Content**:
  - **Directory Responsibilities**: 1-3 lines describing what this directory does.
  - **File Inventory**: A Markdown table listing every file, its role, and key dependencies.
  - **Context Rules**: Coding standards and guidelines specific to this directory.
- **Update Trigger**: Whenever a file is added, removed, or its primary purpose changes.

### Level 3: Header Comments (Per File)
- **Scope**: Single File
- **Content**: Structured metadata block at the top of the file.
- **Format**:
  ```python
  """
  @module: [Module Name]
  @desc: [Brief description of what this file does]
  @input: [Key inputs, arguments, or dependencies]
  @output: [Return values, artifacts, or side effects]
  @role: [Architecture Component, e.g., "Utility", "Service", "Controller"]
  """
  ```
  (Adapt comment syntax for different languages: `//` for Go/JS, `#` for Shell/Python)

## Workflow Rules (Mandatory)

When modifying code, you MUST follow this sequence:

1.  **Update Level 3 (Header)**: If logic changes, update `@input`/`@output`/`@desc` in the file header.
2.  **Update Level 2 (CLAUDE.md)**:
    - If a file is added/deleted -> Update the "File Inventory" table.
    - If a file's role changes -> Update the description in the table.
3.  **Update Level 1 (ARCHITECTURE.md)**:
    - Only if a new major module is introduced or removed.

## Trigger Table

| Event | Update Header? | Update CLAUDE.md? | Update ARCHITECTURE.md? |
| :--- | :---: | :---: | :---: |
| Modify Logic | ✅ | ❌ | ❌ |
| Change I/O | ✅ | ✅ (if desc changes) | ❌ |
| Add File | ✅ (Create) | ✅ | ❌ |
| Remove File | N/A | ✅ | ❌ |
| New Module | N/A | ✅ (Create) | ✅ |

## Instruction for AI
If you are asked to "implement feature X" or "refactor Y":
1.  Perform the code changes.
2.  **IMMEDIATELY** check if the file has a compliant header. If not, add it.
3.  Check if `CLAUDE.md` exists in the directory. If not, create it.
4.  Update the **File Inventory** section in `CLAUDE.md` to reflect the current state of the directory.
5.  If the change is structural, check `ARCHITECTURE.md`.
