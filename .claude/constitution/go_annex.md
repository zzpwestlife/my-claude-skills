# Constitution Annex: Go Language Implementation Details

**Scope**: All Go language backend projects
**Constitution Version**: 2.0+

This annex defines the specific execution standards for the [Project Development Constitution](constitution.md) in Go projects.

---

## 1. Simplicity Principle Implementation
- **1.1 Stdlib First**: Outside framework constraints, prioritize Go standard library (`stdlib`).
- **1.2 Dependency Management**: Strictly prohibit introducing unused dependencies. Use `go mod tidy` to keep clean.

## 2. Testing Quality Implementation
- **2.1 Table-Driven Tests**: Unit tests **MUST** adopt Table-Driven Tests pattern.
- **2.2 Framework Selection**: 
    - Unit tests: `testing` (stdlib) or `goconvey` (if already integrated).
    - Mock: Prioritize interface injection, avoid complex mock frameworks; use `gomock` only when necessary.
- **2.3 Concurrent Testing**: Code involving concurrency must be verified using `go test -race`.

## 3. Clarity Principle Implementation
- **3.1 Error Handling**:
    - **Prohibited**: Strictly forbid using `_` to ignore errors.
    - **Wrapping**: Error propagation must use `fmt.Errorf("context: %w", err)` for wrapping, preserving stack or context.
    - **Panic**: Strictly forbid using `panic` in business logic; must return errors. Panic only allowed during `main` startup phase.
- **3.2 Dependency Injection**: All dependencies (DB, Cache, Config) must be passed through struct fields or function parameters; strictly prohibit global variables.
- **3.3 GoDoc**: Exported functions and types must have comments following Go official specifications.

## 4. Code Style & Structure
- **4.1 Formatting**: Mandatory use of `gofumpt` (stricter than `gofmt`).
- **4.2 Concurrency Model**: 
    - Use `errgroup` to manage concurrent tasks.
    - Strictly forbid using `time.Sleep` in production code (tests excepted).
    - Context must be passed as first parameter for timeout and cancellation control.
- **4.3 Naming Conventions**: Follow `Effective Go` guidelines. Concrete types preferred over `any`/`interface{}`.
- **4.4 File Limits**: 
    - Single file recommended < 200 lines.
    - Single function recommended < 20 lines (excluding error handling).

## 5. Architecture Patterns
- **5.1 ETL Pattern**: Data processing follows `Query` -> `Clean` -> `Export` pipeline.
- **5.2 Optimistic Locking**: Use `UpdateRecordIfMatchStatus` to handle concurrent updates.
- **5.3 Entity Isolation**: Support multi-entity (`Futunn`, `MooMoo`) logic separation.
