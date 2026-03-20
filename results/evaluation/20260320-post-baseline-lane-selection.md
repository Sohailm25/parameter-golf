# Post-Baseline Lane Selection - 2026-03-20

## Status

- `status`: `planning`
- `issue`: `parametergolf-7b2`
- `recommended_lane`: `evaluation`
- `recommended_followup_issue`: `parametergolf-2r3`

## Bottom Line

The first post-baseline experiment lane should be `evaluation`, not tokenizer, quantization, or architecture.

The first atomic experiment to run is:

- `eval-sliding-window-context-accounting`
- concretely: compare the current flat-stream, non-overlapping validation metric against a flat-stream sliding-window validation metric on the same promoted baseline checkpoint, with no document reset and no test-time training

## Why This Lane First

- The refreshed official PR frontier through `#224` still concentrates most heavily around evaluation-side wins, especially sliding-window accounting.
- The deduped backlog gives `eval-sliding-window-context-accounting` the broadest public support of any single candidate experiment.
- This lane changes the reported metric without changing training or artifact size, which makes it the cleanest first post-baseline stress test against `baseline-sp1024-mlx-confirmed-s1`.
- The repo already treats evaluation as the highest-priority lane in `research/approach-space-20260319.md`, and the latest frontier sweep did not weaken that conclusion.

## Why This Atomic Experiment First

- It is the smallest implementable evaluation experiment on the current local cache.
- The current cache does **not** include `data/docs_selected.jsonl` or `data/docs_selected.source_manifest.json`, so a true document-isolated eval lane would currently require an extra docs-cache materialization step before the metric work starts.
- Folding docs reconstruction into the first evaluation experiment would confound the result: we would be testing both evaluation semantics and new data plumbing at once.
- A flat-stream sliding-window comparison can run against the existing validation shard immediately and still answers a real competition question with strong public support.

## Why Not The Other Leading Lanes First

- `document-isolated sliding-window`
  - still high priority, but it should come after a clean flat-stream sliding-window harness or after the docs cache is materialized explicitly as a separate enabling step
- `document-reset TTT`
  - explicitly deferred until plain evaluation accounting is trustworthy; the repo already recorded this sequencing in the dynamic-eval review
- `tokenizer`
  - still strong, but it changes both data/token accounting assumptions and model training at once, which is a worse first post-baseline control than eval-only accounting
- `quantization`
  - still strong, but selective precision interacts with artifact budgeting and serialization choices, which is a bigger engineering surface than a pure eval-accounting comparison
- `architecture`
  - still promising, but the public evidence remains less clean than the evaluation frontier, and the local baseline just became reliable enough to test cheaper ideas first

## Exact Next Experiment

Use `baseline-sp1024-mlx-confirmed-s1` as the fixed reference and implement `parametergolf-2r3`:

1. Add a standalone evaluation harness or equivalent path that can load the confirmed baseline checkpoint without retraining.
2. Reproduce the current flat-stream non-overlapping metric on the promoted baseline as a harness sanity check.
3. Add stride-based sliding-window accounting on the same token stream and compare BPB directly.
4. Preserve the outcome as an evaluation artifact and only consider promotion if the lineage stays clean and the metric change is clearly labeled as evaluation-only.

## Reporting Guardrail

- If sliding-window accounting wins, report it as an `evaluation` improvement, not as a model improvement.
- Keep this work in the repo's `spirit-first` lane unless a later experiment introduces more controversial evaluation-time adaptation.
