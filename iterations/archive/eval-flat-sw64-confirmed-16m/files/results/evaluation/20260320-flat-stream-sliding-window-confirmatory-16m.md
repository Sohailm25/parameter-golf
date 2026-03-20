# Flat-Stream Sliding-Window Confirmatory 16M - 2026-03-20

## Status

- `status`: `pass`
- `lane`: `evaluation`
- `lane_label`: `spirit-first`
- `issue`: `parametergolf-8o4`
- `iteration`: `eval-flat-sw64-confirmed-16m`

## Bottom Line

The larger-budget confirmatory flat-stream evaluation check held up. On a `16,777,216`-target validation prefix, stride-`64` sliding-window accounting improved the promoted baseline checkpoint from `val_bpb=2.02398643` to `val_bpb=2.02013120`, a `0.00385523` BPB gain.

That gain is effectively the same size as the earlier `1,048,576`-target proxy (`0.00389251` BPB). The confirmatory delta differed from the proxy by only `0.00003728` BPB, so the earlier result was not a short-prefix artifact.

## Run

- Run ID: `20260320-162016-evaluation-sliding-window-accounting-confirmatory-16m`
- Horizon: `confirmatory`
- Validation prefix: `16,777,216` targets from the flat cached validation stream
- Reference stride: `1024` (`16,384` windows, `1,024` batches at `window_batch_seqs=16`)
- Sliding stride: `64` (`262,129` windows, `16,384` batches at `window_batch_seqs=16`)
- Non-overlapping metric: `val_loss=3.40125729`, `val_bpb=2.02398643`
- Sliding-window metric: `val_loss=3.39477867`, `val_bpb=2.02013120`
- Absolute BPB improvement: `0.00385523`
- Relative BPB improvement: `0.1905%`
- Dashboard: `results/figures/renders/20260320-165154-dashboard/index.html`

## Comparison Against Earlier Evaluation Gates

- Proxy prefix size: `1,048,576` targets (`1.69%` of the full flat validation stream)
- Confirmatory prefix size: `16,777,216` targets (`27.05%` of the full flat validation stream)
- Proxy delta (`1M`): `0.00389251` BPB
- Confirmatory delta (`16M`): `0.00385523` BPB
- Delta drift from proxy to confirmatory: `-0.00003728` BPB

## Audit

- `validation.log_audit` reported `best_step_val_bpb=2.0201` at `step=2/2`
- `validation.log_audit` reported `final_exact val_bpb=2.02013120`
- `validation.artifact_size` on the unchanged checkpoint `logs/20260319-213359-baselines-baseline-confirmatory_mlx_model.int8.ptz` reported `total_bytes=13642279` and `within_cap=true`

## Interpretation

- This remains an evaluation-accounting improvement, not a model-improvement claim.
- The larger-budget check makes the result much harder to dismiss as a tiny-prefix fluke.
- The repo still has not run the full `62,021,632`-target flat validation stream at stride `64`, so this is not a full-cache claim and should not be written up that way.

## Promotion Decision

- Promote this as evaluation iteration `eval-flat-sw64-confirmed-16m`.
- Do **not** mirror it into `iterations/golden/`; keep `baseline-sp1024-mlx-confirmed-s1` as the conservative golden baseline until a fuller submission-style evaluation path is locked down.

## Next Step

- Reassess whether the next evaluation task should be a full-cache flat-stream run, document-isolated accounting, or the next non-eval lane. The current confirmatory evidence is strong enough that the repo no longer needs to re-prove the 1M proxy.

## Files And Logs

- Confirmatory log: `logs/20260320-162016-evaluation-sliding-window-accounting-confirmatory-16m.txt`
- Confirmatory dashboard: `results/figures/renders/20260320-165154-dashboard/index.html`
- Proxy artifact for reference: `results/evaluation/20260320-flat-stream-sliding-window-proxy-1m.md`
