# First Bounded Optimizer Proxy Batch - 2026-03-20

## Status

- `status`: `mixed`
- `lane`: `autoresearch`
- `issue`: `parametergolf-gci`
- `followup_issue`: `parametergolf-2s4`

## Bottom Line

The first bounded `autoresearch` batch did what it was supposed to do as a search tool and failed where it was supposed to fail as a claim path.

- The batch-local control reproduced the frozen proxy at `final_int8_zlib_roundtrip_exact val_bpb=2.18594291`.
- The batch-local down-10 LR candidate looked dramatically better at `2.10816927`.
- The canonical rerun of that same LR tuple through `scripts/experiment_runner.py launch` only improved to `2.17839092`.

That means the batch discovered a real direction, but the batch-local magnitude was inflated by `0.07022165` BPB. The contract held: the batch is useful for search, not for claims.

## Batch Design

- parent reference: `baseline-sp1024-mlx-confirmed-s1`
- substantive lane: `optimizer_sweeps`
- search subspace: global LR scale only
- fixed proxy regime: `500` steps, `TRAIN_BATCH_TOKENS=8192`, `VAL_BATCH_SIZE=524288`, `VAL_LOSS_EVERY=0`
- scratch directory: `scratch/autoresearch/20260320-gci-lr-scale-batch/`

## Candidate Outcomes

- `lr100-control`
  - final exact `val_bpb=2.18594291`
  - int8 artifact `12727508` bytes
- `lr090-down10`
  - batch-local final exact `val_bpb=2.10816927`
  - int8 artifact `10592244` bytes
  - batch-local gain over control `0.07777364` BPB
- `lr110-up10`
  - stopped at `step:100/500`
  - reason: once `lr090-down10` cleared the batch-local audit with a very large lead, the next meaningful question became canonical reproduction, not another full local branch of the same subspace

## Interpretation

- The bounded search loop was worth running.
- The batch-local search loop was not trustworthy for ranking magnitude.
- The canonical rerun is now the source of truth for the LR-down10 tuple, not the batch-local run.

## Promotion Decision

- Do not promote anything from this artifact.
- Reason: `autoresearch` batch-local results are explicitly non-promotion paths in this repo, and the batch-local winner already proved that point by shrinking materially on canonical rerun.

## Next Step

- Resolve `parametergolf-2s4`: rerun the canonical down-10 LR tuple on the isolated shard `000001` confirmatory path and check current evaluation accounting before any promotion discussion.
