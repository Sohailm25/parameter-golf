# LR Scale Down10 Confirmatory - 2026-03-20

## Status

- `status`: `pass`
- `lane`: `optimizer_sweeps`
- `lane_label`: `spirit-first`
- `issue`: `parametergolf-2s4`
- `iteration`: `opt-lrscale-down10-confirmed-s1`

## Bottom Line

The LR-down10 tuple did not collapse on the isolated shard-`000001` confirmatory path. It improved the baseline confirmatory run by `0.04168550` BPB, reduced the quantized artifact size by `699815` bytes, and the current `16M` stride-`64` accounting reference preserved essentially the same gain size.

## Confirmatory Training Run

- Run ID: `20260321-000650-optimizer-sweeps-lr-scale-down10-confirmatory`
- Training config: `ITERATIONS=1000`, `TRAIN_BATCH_TOKENS=8192`, `TRAIN_LOG_EVERY=50`, `VAL_BATCH_SIZE=524288`, `VAL_LOSS_EVERY=0`
- LR tuple: `TIED_EMBED_LR=0.045`, `MATRIX_LR=0.036`, `SCALAR_LR=0.036`
- Data: isolated local confirmatory slice `data/datasets/fineweb10B_sp1024_confirmatory_shard1/` with `fineweb_train_000001.bin` plus the fixed public validation shard
- Step-1000 validation: `val_loss=3.3220`, `val_bpb=1.9675`
- Final quantized roundtrip: `val_loss=3.32234668`, `val_bpb=1.96768084`
- Quantized artifact: `12942464` bytes (`within_cap=true`)
- Dashboard: `results/figures/renders/20260321-003313-dashboard/index.html`

## Current Evaluation Accounting

- Rescore run ID: `20260321-003451-optimizer-sweeps-lr-scale-down10-confirmatory-accounting-16m`
- Validation prefix: `16,777,216` targets from the flat cached validation stream
- Non-overlapping reference: `val_loss=3.33066069`, `val_bpb=1.98197651`
- Stride-`64` reference: `val_loss=3.32377258`, `val_bpb=1.97787760`
- Stride gain on the new checkpoint: `0.00409891` BPB
- Baseline checkpoint non-overlap reference: `2.02398643`
- Baseline checkpoint stride-`64` reference: `2.02013120`
- Gain versus baseline under current non-overlap accounting: `0.04200992` BPB
- Gain versus baseline under current stride-`64` accounting: `0.04225360` BPB
- Accounting dashboard: `results/figures/renders/20260321-011224-dashboard/index.html`

## Comparison Against The Promoted Baseline

- Baseline confirmatory final exact `val_bpb`: `2.00936634`
- LR-down10 confirmatory final exact `val_bpb`: `1.96768084`
- Absolute gain on the confirmatory training path: `0.04168550` BPB
- Baseline confirmatory artifact: `13642279` bytes
- LR-down10 confirmatory artifact: `12942464` bytes
- Artifact bytes saved: `699815`

## Audit

- `validation.log_audit` on the training log reported `best_step_val_bpb=1.9675` at `step=1000/1000`
- `validation.log_audit` on the training log reported `final_exact val_bpb=1.96768084`
- `validation.artifact_size` reported `total_bytes=12942464` and `within_cap=true`
- `validation.log_audit` on the accounting log reported step `1/2 val_bpb=1.9820` and step `2/2 val_bpb=1.9779`
- `validation.log_audit` on the accounting log reported `final_exact val_bpb=1.97787760`

## Interpretation

- The LR-down10 direction is no longer just a proxy or batch-local hint. It survives the real shard-`000001` confirmatory path by a large margin.
- The current accounting reference does not erase the win. It preserves essentially the same `~0.042` BPB gain relative to the baseline checkpoint.
- This remains a single atomic change: same tokenizer, same model code, same data contract, same evaluation scripts, only the LR tuple changed.

## Promotion Decision

- Promote this run as iteration `opt-lrscale-down10-confirmed-s1`.
- Mirror the promoted iteration into `iterations/golden/` as the new best-known integrated candidate.

## Next Step

- Open the next atomic issue for document-isolated sliding-window accounting by materializing the missing local docs cache instead of bundling that data step into a broader lane jump.

## Files And Logs

- Confirmatory training log: `logs/20260321-000650-optimizer-sweeps-lr-scale-down10-confirmatory.txt`
- Confirmatory int8 checkpoint: `logs/20260321-000650-optimizer-sweeps-lr-scale-down10-confirmatory_mlx_model.int8.ptz`
- Confirmatory accounting log: `logs/20260321-003451-optimizer-sweeps-lr-scale-down10-confirmatory-accounting-16m.txt`
- Confirmatory training dashboard: `results/figures/renders/20260321-003313-dashboard/index.html`
- Confirmatory accounting dashboard: `results/figures/renders/20260321-011224-dashboard/index.html`
