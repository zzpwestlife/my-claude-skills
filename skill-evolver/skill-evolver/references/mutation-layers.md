# Mutation Layers

Each iteration mutates exactly one layer. Cross-layer changes must be split into another iteration.

## Layer 1 — Trigger and routing (lowest cost)

**May edit:** trigger rules, invocation boundaries, routing hints, short examples, compact usage guards inside `SKILL.md`.

- Do: tighten the `description:` to better reflect when to invoke.
- Do: add a one-line guard like "do not use when X".
- Don't: rewrite multi-paragraph workflow logic — that is Layer 2.

## Layer 2 — Skill body (medium cost)

**May edit:** substantive workflow instructions, examples, refusal behavior, failure handling, decision policy inside `SKILL.md`.

- Do: rewrite a phase's procedure when trace evidence shows the current procedure mis-routes.
- Don't: edit `scripts/` or `references/` — that is Layer 3.

## Layer 3 — Support material (highest cost)

**May edit:** `scripts/*`, `references/*`, dataset adapters, bundled helper resources.

- Do: change `scripts/setup_workspace.py` only when trace evidence proves the failure lives in the helper.
- Don't: jump here just because Layer 1/2 felt slow — exhaust them first.

## Promotion rules

A layer is exhausted when **all three** are true:

1. ≥ 3 trace-backed atomic attempts in that layer
2. None produced a keep
3. Review cannot name a new counterfactual in that layer that is meaningfully different from prior failed patterns

When all lower layers are exhausted, the next higher layer becomes eligible. Do not skip directly to Layer 3 unless lower layers are exhausted **or** trace evidence already proves the failure lives in helper material.

## Atomic enforcement

Default: a single iteration touches at most **one file**. When `target_files` explicitly declares a pattern (e.g. "all warning rules in `references/safety-rules.md`"), up to **5 files** is permitted. Anything beyond 5 fails `atomic_auditability`.
