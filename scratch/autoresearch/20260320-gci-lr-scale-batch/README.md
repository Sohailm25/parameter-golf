# GCI LR Scale Batch - 2026-03-20

## Purpose

Run the first bounded `autoresearch`-style local batch defined by `parametergolf-gci`.

This batch stays inside one subspace:

- parent reference: `baseline-sp1024-mlx-confirmed-s1`
- scoring reference: `eval-flat-sw64-confirmed-16m`
- substantive lane: `optimizer_sweeps`
- mutable surface: optimizer/LR env knobs already exposed by `train_gpt_mlx.py`
- search subspace: global LR scale only

## Candidates

- `lr100-control`
  - `TIED_EMBED_LR=0.05`
  - `MATRIX_LR=0.04`
  - `SCALAR_LR=0.04`
- `lr090-down10`
  - `TIED_EMBED_LR=0.045`
  - `MATRIX_LR=0.036`
  - `SCALAR_LR=0.036`
- `lr110-up10`
  - `TIED_EMBED_LR=0.055`
  - `MATRIX_LR=0.044`
  - `SCALAR_LR=0.044`

## Fixed Proxy Regime

- `ITERATIONS=500`
- `TRAIN_BATCH_TOKENS=8192`
- `TRAIN_LOG_EVERY=50`
- `VAL_BATCH_SIZE=524288`
- `VAL_LOSS_EVERY=0`
- local `sp1024` cache under `data/datasets/` and `data/tokenizers/`
- fixed public validation shard

## Batch Rule

Only one candidate can leave this directory for a canonical rerun. If none beat the control cleanly, the batch result is `fail` and the repo should move on without promoting anything.

## Observed Outcome

- `lr100-control`
  - final exact `val_bpb=2.18594291`
  - int8 artifact `12727508` bytes
- `lr090-down10`
  - batch-local final exact `val_bpb=2.10816927`
  - int8 artifact `10592244` bytes
  - canonical rerun later shrank the same LR tuple to `2.17839092`
- `lr110-up10`
  - truncated at `step:100/500`
  - reason: the repo switched to the canonical rerun once the down-10 tuple cleared the batch-local audit by a wide margin
