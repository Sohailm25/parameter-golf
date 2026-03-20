# LR Scale Down10 Canonical Proxy - 2026-03-20

## Status

- `status`: `pass`
- `lane`: `optimizer_sweeps`
- `lane_label`: `spirit-first`
- `issue`: `parametergolf-gci`
- `followup_issue`: `parametergolf-2s4`

## Bottom Line

The canonical rerun of the first bounded autoresearch winner survived the normal repo path and produced a real medium-horizon proxy improvement, but the gain was much smaller than the batch-local search run implied.

## Run

- Run ID: `20260320-191223-optimizer-sweeps-lr-scale-down10-proxy-rerun`
- Training config: `ITERATIONS=500`, `TRAIN_BATCH_TOKENS=8192`, `TRAIN_LOG_EVERY=50`, `VAL_BATCH_SIZE=524288`, `VAL_LOSS_EVERY=0`
- LR tuple: `TIED_EMBED_LR=0.045`, `MATRIX_LR=0.036`, `SCALAR_LR=0.036`
- Data: local `sp1024` cache on the standard proxy path plus the fixed public validation shard
- Step-500 validation: `val_loss=3.6777`, `val_bpb=2.1782`
- Final quantized roundtrip: `val_loss=3.67812182`, `val_bpb=2.17839092`
- Quantized artifact: `12601637` bytes (`within_cap=true`)

## Comparison

- In-batch control final exact `val_bpb`: `2.18594291`
- Archived baseline proxy final exact `val_bpb`: `2.18376301`
- Canonical down-10 final exact `val_bpb`: `2.17839092`
- Gain over in-batch control: `0.00755199` BPB
- Gain over archived baseline proxy: `0.00537209` BPB
- Batch-local down-10 exact `val_bpb`: `2.10816927`
- Batch-local exaggeration versus canonical rerun: `0.07022165` BPB

## Audit

- `validation.log_audit` recovered `best_step_val_bpb=2.1782` at `step=500/500`
- `validation.log_audit` recovered `final_exact val_bpb=2.17839092`
- `validation.artifact_size` reported `total_bytes=12601637` and `within_cap=true`

## Interpretation

- The LR-down10 direction is real enough to preserve.
- The batch-local search loop badly overstated the size of the win, so future autoresearch batches should be treated as proposal generators, not rankers.
- This is still only a Tier 1 proxy result. It is not ready for `leaderboard.md`.

## Promotion Decision

- Do not promote this result.
- Reason: the repo still requires a Tier 2 confirmatory run on shard `000001`, and the contract also expects current evaluation accounting to stay visible before stronger claims.

## Next Step

- Resolve `parametergolf-2s4` with the same LR tuple on the isolated confirmatory shard path.
