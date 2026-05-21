# Local Evolution Runbook

1. Identify the target skill, dataset directory, and output directory.
2. Run Phase 0 setup: validate inputs, create workspace, capture baseline, and write `evolve_plan.md`.
3. Start at `layer1` unless `evolve_plan.md` says otherwise.
4. Review recent memory: git log, `results.tsv`, `experiments.jsonl`, failed cases, and traces.
5. Choose one failed case with trace evidence.
6. Write one mutation proposal with `case_id`, `trace_path`, `failure_reason`, `expected_fix`, `target_layer`, `target_scope`, and `target_files`.
7. Reject the iteration before editing if trace evidence is missing.
8. Apply one atomic mutation within the selected layer.
9. Create a checkpoint before verification.
10. Run L1. If L1 fails, discard immediately.
11. Run L2 dev eval when L1 passes.
12. Run L3 strict eval only when triggered by iteration count, high dev score, layer promotion, or final validation.
13. Apply the five-dimensional AND gate.
14. Keep only if all gate dimensions pass.
15. Roll back on any failed gate dimension.
16. Log `results.tsv`, `experiments.jsonl`, per-case traces, and iteration summary.
17. Continue, promote layer, switch aggressive strategy, or stop based on the loop rules.
18. On stop, write `final_report.json`.
