# Local Baseline Proxy 500 - 2026-03-19

## Status

- `status`: `pass`
- `lane`: `baselines`
- `lane_label`: `spirit-first`
- `issue`: `parametergolf-6yf`

## Bottom Line

The first `500`-step medium-horizon proxy on the frozen local MLX `sp1024` baseline path completed successfully. It materially improved over the corrected `200`-step smoke run while preserving the same training script, tokenizer, public validation split, and validation-batch regime.

## Run

- Run ID: `20260319-161653-baselines-baseline-proxy`
- Training config: `ITERATIONS=500`, `TRAIN_BATCH_TOKENS=8192`, `TRAIN_LOG_EVERY=50`, `VAL_BATCH_SIZE=524288`, `VAL_LOSS_EVERY=0`
- Data: `fineweb_train_000000.bin` plus the fixed public validation shard under `data/datasets/fineweb10B_sp1024/`
- Step-500 validation: `val_loss=3.6853`, `val_bpb=2.1827`
- Final quantized roundtrip: `val_loss=3.68719236`, `val_bpb=2.18376301`
- Quantized artifact: `12730412` bytes (`within_cap=true`)
- Train time: `181447ms`
- Local wallclock: about `15m22s` from the scratchpad timestamps

## Comparison Against Smoke

- Corrected smoke final quantized `val_bpb`: `2.40962829`
- Proxy final quantized `val_bpb`: `2.18376301`
- Absolute improvement over smoke: `0.22586528` BPB
- Quantized artifact growth over smoke: `1469690` bytes, still below the `16000000`-byte cap

## Interpretation

- The frozen local MLX baseline path remains stable at the medium-horizon proxy.
- The proxy confirms that the earlier smoke gate was not a fluke: the same path gets materially better by `500` steps.
- Validation still dominates local wallclock because `train_gpt_mlx.py` performs both a full-float end-of-training validation and a second quantized roundtrip validation.

## Promotion Decision

- Do not promote this proxy result into `leaderboard.md`.
- Reason: the prereg still requires a confirmatory split on a distinct local train slice before any golden-path or promotion claim.

## Next Step

- Execute `parametergolf-75u`: extend the cache to a second training shard, isolate `fineweb_train_000001.bin`, and run the `1000`-step confirmatory split on the same frozen baseline path.

## Files And Logs

- Proxy log: `logs/20260319-161653-baselines-baseline-proxy.txt`
- Proxy quantized artifact: `logs/20260319-161653-baselines-baseline-proxy_mlx_model.int8.ptz`
- Proxy dashboard: `results/figures/renders/20260319-163215-dashboard/index.html`
