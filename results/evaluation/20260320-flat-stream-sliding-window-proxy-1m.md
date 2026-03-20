# Flat-Stream Sliding-Window Proxy 1M - 2026-03-20

## Status

- `status`: `partial`
- `lane`: `evaluation`
- `lane_label`: `spirit-first`
- `issue`: `parametergolf-2r3`
- `iteration`: `none`

## Bottom Line

The repo now has a standalone MLX evaluation harness that can load the promoted baseline checkpoint and compare flat-stream evaluation accounting modes without retraining.

On the first `1,048,576` targets of the cached validation stream, stride-`64` sliding-window accounting improved BPB from `2.02717341` to `2.02328090` against the same `baseline-sp1024-mlx-confirmed-s1` checkpoint, a `0.00389251` BPB gain with zero artifact-size change.

This result is worth preserving, but not promoting. The proxy is only `1.69%` of the full local flat validation stream (`62,021,632` targets), and the first attempted full-val confirmatory run exposed that the local compute budget was larger than expected.

## Harness

- Script: `scripts/eval_mlx_checkpoint.py`
- Window planner: `validation/eval_windowing.py`
- Unit tests: `tests/test_eval_windowing.py`
- Fixed checkpoint: `logs/20260319-213359-baselines-baseline-confirmatory_mlx_model.int8.ptz`

## Proxy Run

- Run ID: `20260320-160758-evaluation-sliding-window-accounting-proxy-1m`
- Horizon: `proxy`
- Validation prefix: `1,048,576` targets from the flat cached validation stream
- Reference stride: `1024` (`1024` windows, `64` batches at `window_batch_seqs=16`)
- Sliding stride: `64` (`16,369` windows, `1,024` batches at `window_batch_seqs=16`)
- Non-overlapping metric: `val_loss=3.38343398`, `val_bpb=2.02717341`
- Sliding-window metric: `val_loss=3.37693723`, `val_bpb=2.02328090`
- Absolute BPB improvement: `0.00389251`
- Relative BPB improvement: `0.1920%`
- Dashboard: `results/figures/renders/20260320-160938-dashboard/index.html`

## Aborted Full-Val Attempt

- Run ID: `20260320-160536-evaluation-sliding-window-accounting`
- Intended target set: full cached flat validation stream, `62,021,632` targets
- Reference stride cost: `60,568` windows, `3,786` batches at `window_batch_seqs=16`
- Sliding stride cost: `969,073` windows, `60,568` batches at `window_batch_seqs=16`
- Observed outcome: aborted intentionally during the non-overlapping pass after the local budget error became obvious

This was the correct stop. Treating the full-val stride-`64` run as the first local evaluation experiment would have violated the repo's "smallest experiment" discipline.

## Audit

- `validation.log_audit` on the proxy log reported `best_step_val_bpb=2.0233` at `step=2/2`
- `validation.log_audit` reported `final_exact val_bpb=2.02328090`
- `validation.artifact_size` is not applicable here because this was an evaluation-only comparison against an existing saved artifact

## Interpretation

- The gain is clearly an evaluation-accounting gain, not a model-improvement claim.
- The harness successfully reproduces the non-overlapping metric on the same checkpoint and then shows a better stride-`64` flat-stream score on the same token prefix.
- The proxy is large enough to be interesting, but not large enough to justify promotion into `leaderboard.md` or `iterations/golden/`.

## Promotion Decision

- Do not promote.
- Keep `baseline-sp1024-mlx-confirmed-s1` as the golden candidate.
- Open a separate confirmatory follow-up for a larger-budget flat-stream sliding-window check.

## Next Step

- Resolve `parametergolf-8o4`: run a larger-budget confirmatory flat-stream sliding-window accounting check with explicit tmux/budget planning before any promotion discussion.

## Files And Logs

- Proxy log: `logs/20260320-160758-evaluation-sliding-window-accounting-proxy-1m.txt`
- Proxy dashboard: `results/figures/renders/20260320-160938-dashboard/index.html`
- Aborted full-val log: `logs/20260320-160536-evaluation-sliding-window-accounting.txt`
