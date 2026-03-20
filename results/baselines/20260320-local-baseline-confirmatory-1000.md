# Local Baseline Confirmatory 1000 - 2026-03-20

## Status

- `status`: `pass`
- `lane`: `baselines`
- `lane_label`: `spirit-first`
- `issue`: `parametergolf-75u`
- `iteration`: `baseline-sp1024-mlx-confirmed-s1`

## Bottom Line

The first real confirmatory baseline run on an isolated local shard `000001` completed successfully. The frozen local MLX `sp1024` path held up on the confirmatory split, improved materially over both the smoke and proxy runs, and stayed under the `16,000,000` byte artifact cap after the quantized roundtrip.

## Run

- Run ID: `20260319-213359-baselines-baseline-confirmatory`
- Training config: `ITERATIONS=1000`, `TRAIN_BATCH_TOKENS=8192`, `TRAIN_LOG_EVERY=50`, `VAL_BATCH_SIZE=524288`, `VAL_LOSS_EVERY=0`
- Data: isolated local confirmatory slice `data/datasets/fineweb10B_sp1024_confirmatory_shard1/` with `fineweb_train_000001.bin` plus the fixed public validation shard
- Step-1000 validation: `val_loss=3.3916`, `val_bpb=2.0087`
- Final quantized roundtrip: `val_loss=3.39273090`, `val_bpb=2.00936634`
- Train runtime: `387694ms`
- Quantized artifact: `13642279` bytes (`within_cap=true`)

## Comparison Against Earlier Gates

- Corrected smoke final quantized `val_bpb`: `2.40962829`
- Proxy final quantized `val_bpb`: `2.18376301`
- Confirmatory final quantized `val_bpb`: `2.00936634`
- Absolute improvement over smoke: `0.40026195` BPB
- Absolute improvement over proxy: `0.17439667` BPB
- Artifact growth over proxy: `911867` bytes, still below the `16000000`-byte cap

## Audit

- `validation.log_audit` reported `best_step_val_bpb=2.0087` at `step=1000/1000`
- `validation.log_audit` reported `final_exact val_bpb=2.00936634`
- `validation.artifact_size` reported `total_bytes=13642279` and `within_cap=true`

## Interpretation

- The frozen local baseline path is no longer only a pilot-shard proxy. It now survives a longer run on a distinct local train shard.
- The confirmatory split materially reduces the risk that the earlier smoke and proxy wins were only shard-`000000` artifacts.
- The run remains clearly `spirit-first`: same tokenizer, same public validation shard, same training script, same evaluation path, with only the local train shard changed for confirmation.

## Promotion Decision

- Promote this run as iteration `baseline-sp1024-mlx-confirmed-s1`.
- Mirror that promoted iteration into `iterations/golden/` as the current best-known candidate.

## Next Step

- Move to `parametergolf-7b2` and choose the first high-signal post-baseline lane, most likely evaluation accounting, document-reset TTT, tokenizer scaling, or selective precision.

## Files And Logs

- Confirmatory log: `logs/20260319-213359-baselines-baseline-confirmatory.txt`
- Confirmatory quantized artifact: `logs/20260319-213359-baselines-baseline-confirmatory_mlx_model.int8.ptz`
- Confirmatory dashboard: `results/figures/renders/20260320-024538-dashboard/index.html`
- Runner stdout capture: `scratch/confirmatory-launch-75u.stdout`
