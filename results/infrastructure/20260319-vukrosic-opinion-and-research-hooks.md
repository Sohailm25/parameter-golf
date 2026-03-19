# External Signal Review And Hook Installation - 2026-03-19

## Inputs Reviewed

- Vuk Rosic fork: `https://github.com/vukrosic/parameter-golf`
- Vuk Rosic X opinion on early-vs-late reversals: `https://x.com/VukRosic99/status/2034622264889463256`
- public `bird` search results on Parameter Golf

## Bottom Line

The opinion contains one good methodological warning and two claims we should not over-promote.

## Signal We Are Adopting

1. Early wins are cheap to hallucinate.
   - We should not rank architecture or activation changes on `5s`, `15s`, `30s`, or `~50-step` results alone.
2. A medium-horizon proxy belongs in the experiment stack.
   - The repo now treats `sub-100-step` runs as smoke only and `~500-step` runs as a useful proxy horizon.
3. Public chatter is worth harvesting, but it needs filtering.
   - The repo now has bird-cli and arXiv hooks so outside ideas become stateful inputs instead of forgotten tweets.

## Claims We Are Not Adopting As Repo Truth

1. `The baseline seems hyperoptimized`
   - Too strong. The live frontier already shows major gains from evaluation, tokenizer, and quantization changes.
2. `BPB@500 is the reliable comparison metric`
   - Not yet proven here. We have a tweet-level claim, not a documented study across lanes and seeds.
3. `Single-GPU very short runs are enough for theory`
   - Good for elimination. Not good enough for promotion.

## Repo Changes Triggered By This Review

- Added `validation/EXPERIMENT_GATES.md`
- Added bird-cli X review hook: `scripts/review_x_signal.py`
- Added arXiv review hook with query draining: `scripts/review_arxiv.py`
- Added combined wrapper: `scripts/review_iteration_signal.py`
- Added persistent state/log files under `research/` for both hook systems

## Live Smoke Check

- `bird check --plain` succeeded with local Firefox-backed credentials.
- `.venv/bin/python scripts/review_iteration_signal.py --lane evaluation --phase pre --topic "parameter golf methodology"` ran end-to-end.
- The first arXiv run surfaced irrelevant papers because the initial query builder was too loose and the category filter was too broad.
- That bug was fixed in the same session, covered by unit tests, and re-run successfully.
