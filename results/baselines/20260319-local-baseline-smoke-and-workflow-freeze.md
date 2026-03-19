# Local Baseline Smoke And Workflow Freeze - 2026-03-19

## Status

- `status`: `partial`
- `lane`: `baselines`
- `lane_label`: `spirit-first`
- `issue`: `parametergolf-7cm`

## Bottom Line

The first real local baseline smoke run now exists and the local smoke gate is frozen. The usable MLX smoke config on this machine is:

- `ITERATIONS=200`
- `TRAIN_BATCH_TOKENS=8192`
- `TRAIN_LOG_EVERY=50`
- `VAL_BATCH_SIZE=524288`
- `VAL_LOSS_EVERY=0`

The first attempted smoke using `VAL_BATCH_SIZE=8192` was not a valid gate. With the default `GRAD_ACCUM_STEPS=8`, the MLX evaluator reduced that to one 1024-token sequence per validation batch, producing `60568` batches per validation pass. Because `train_gpt_mlx.py` performs both a full-float final validation and a second quantized roundtrip validation, that setting turned the smoke loop into a wallclock artifact instead of a quick sanity gate.

## Runs

### Failed gate definition

- Run ID: `20260319-154032-baselines-baseline-smoke`
- Result: `fail`
- Observed metric before termination: `step:200/200 val_loss=4.0628`, `val_bpb=2.4062`
- Reason stopped: validation batching was misconfigured, so the run was killed after the step-200 validation proved the gate was not practical.

### Corrected smoke

- Run ID: `20260319-155403-baselines-baseline-smoke`
- Result: `pass`
- Train runtime: `52147ms` for `200` steps (`step_avg ~= 260.74ms`)
- Step-200 validation: `val_loss=4.0676`, `val_bpb=2.4090`
- Final quantized roundtrip: `val_loss=4.06855643`, `val_bpb=2.40962829`
- Quantized artifact: `11260722` bytes (`within_cap=true` via `validation.artifact_size`)
- Total local wallclock: about `13m56s` from the runner timestamps, dominated by the two full validation passes

## Frozen Workflow

### 1. Smoke gate

- Launch path: `scripts/experiment_runner.py launch`
- Horizon: `smoke`
- Data: cached `sp1024` dataset with `fineweb_train_000000.bin` plus the fixed public validation shard
- Required env: `ITERATIONS=200`, `TRAIN_BATCH_TOKENS=8192`, `TRAIN_LOG_EVERY=50`, `VAL_BATCH_SIZE=524288`, `VAL_LOSS_EVERY=0`
- Allowed claim: the local MLX baseline trains, logs, serializes, and yields a parseable final `val_bpb`

### 2. Medium-horizon proxy

- Horizon: `proxy`
- Data: the same one-shard local pilot slice used by the smoke gate
- Required env: same as smoke except `ITERATIONS=500`
- Ranking metric: `final_int8_zlib_roundtrip_exact val_bpb`
- `inferred`: expected local wallclock is roughly `15-16` minutes because training remains short while the two full validation passes dominate

### 3. Confirmatory split

- Horizon: `confirmatory`
- Before launch: extend the local cache to at least two training shards and isolate `fineweb_train_000001.bin` as the confirmatory train slice while keeping the same tokenizer and public validation shard
- Required env: same as proxy with a materially longer horizon (`ITERATIONS=1000` by default unless a later proxy shows a better stabilization point)
- Promotion gate: run `validation.log_audit` on the final log, run `validation.artifact_size` on the produced quantized artifact, and do not promote if the result only exists on the pilot shard

## Promotion Guardrails

- Do not promote the current smoke run into `leaderboard.md`. It is a workflow baseline, not a confirmatory candidate.
- Keep this lane `spirit-first`. Public validation remains visible as the score source, but the confirmatory step must change the local train slice before any golden-path claim.
- Treat the corrected `VAL_BATCH_SIZE` as workflow hygiene, not as a model improvement.

## Files And Logs

- Corrected smoke log: `logs/20260319-155403-baselines-baseline-smoke.txt`
- Corrected smoke quantized artifact: `logs/20260319-155403-baselines-baseline-smoke_mlx_model.int8.ptz`
- Corrected smoke dashboard: `results/figures/renders/20260319-160759-dashboard/index.html`
- Failed smoke log: `logs/20260319-154032-baselines-baseline-smoke.txt`
