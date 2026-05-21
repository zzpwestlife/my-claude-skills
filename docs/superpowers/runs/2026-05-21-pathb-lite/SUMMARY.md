# Path B-Lite Run Summary — 2026-05-21

## Outcome
- Iterations: 3 (Iter 1 deliberate reject, Iter 2 atomic fix, Iter 3 probe)
- Verdicts: 1 DISCARD, 1 KEEP, 1 PROBE
- Final dataset pass-rate: 5/5 = 1.00 (was 4/5 at baseline)
- Stop reason: iteration_budget_reached
- Best checkpoint: iter-2

## What was validated
- 8-phase loop **walks** end-to-end with discard/keep/probe verdicts each producing the expected artifacts
- 5-dim AND gate **rejects** a cross-layer multi-file mutation (Iter 1) and the rollback path is followed (`git revert HEAD` in workspace, route-hints.md removed, SKILL.md restored byte-identical to fixture)
- Atomic Layer 1 fix on a single Routes line **flips** dev-1 from fail → pass without disturbing other splits (5/5 simulated re-eval)
- All artifacts (`baseline.json`, `evolve_plan.md`, `results.tsv`, `experiments.jsonl`, `iterations/`, `.skill_evolve/traces/`, `final_report.json`) are produced in the schema declared by `skill-evolver/SKILL.md`

## What was simulated (caveat)
- skill-creator's `quick_validate`, `grader`, and `comparator` were all Claude-simulated — see `evolve_plan.md` `Simulations` section and `final_report.json` `simulations` field.
- Agent traces were stubs only; trace-driven proposer protocol fell back to {input, expected, actual} triple as evidence per evolve_plan trace policy.
- Cost budget is N/A: this session has no token metering.

## What this run does NOT prove
- That skill-evolver is correct on a non-toy workload
- That the reject path for non-`atomic_auditability` dimensions (e.g. `dev_quality` regression, `cost_budget` overrun) behaves equivalently
- That the multi-iteration escalation rules (stuck_state, aggressive strategy, layer exhaustion) trigger as designed — those need ≥ 5 iterations to even appear

## Lessons
1. The toy fixture has only 5 cases and stub traces; the trace-driven proposer protocol is **structurally** exercised but not **semantically** stressed. To stress it, advance to B-Build (≥20 GT cases + real traces) or B-Real (a non-toy target skill).
2. `atomic_auditability` doubles as both a layer guard and a multi-file guard. Iter 1 confirmed that a violation in either is sufficient to reject; we did not separate the two reasons.
3. `cost_budget` becomes N/A in any session-mode run. This is fine if the gate is documented as such, but a real run needs external metering or it cannot exercise that dimension.

## Workspace timeline (workspace git)
```
dc49104 final: report + iterations + experiments
e7149be iter-2: add permissions/role/sign-in routing line   (KEEP)
fd3139c Revert "iter-1: cross-layer multi-file mutation"    (rollback)
5da02f9 iter-1: cross-layer multi-file mutation             (DISCARD)
20ef06a phase-0: baseline + evolve_plan
a542a6f fixture: initial copy
```

## Artifacts in this directory
- `baseline.json` — Phase 0 baseline pass-rates
- `final_report.json` — end-of-run report (with `simulations` disclosure)
- `iterations/iter-1.md` — deliberate reject + rollback
- `iterations/iter-2.md` — atomic fix
- `iterations/iter-3.md` — probe + boundary observation

The full ephemeral workspace lived at `/tmp/skill-evolver-pathb-workspace/` and is not version-controlled.

## Next recommendation
- If the next priority is **stronger validation**: Path B-Build (richer GT + disambiguation cases).
- If the next priority is **real-world feel**: Path B-Real (point skill-evolver at a real skill in this repo).
- If the next priority is **cost realism**: instrument a thin token-meter wrapper before running with skill-creator engaged.
