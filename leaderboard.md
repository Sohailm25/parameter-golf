# Iteration Leaderboard

This file tracks promoted experiment revisions for this repo. Every row here must correspond to an immutable **full file snapshot** under `iterations/archive/`.

## Rules

- Every promoted iteration gets a unique `Iteration ID`.
- Every row must describe the single **atomic change** that justified promotion.
- `Parent` may be one iteration or a comma-separated integration set.
- The current best integrated candidate should also be mirrored in `iterations/golden/`.
- If an experiment does not have a full file snapshot, it does not belong here.

## Snapshot Paths

- `iterations/archive` contains the immutable archived snapshots.
- `iterations/golden` contains the current golden set.

## Columns

| Iteration ID | Parent | Lane | Status | Metric | Atomic change | Snapshot |
|---|---|---|---|---|---|---|
<!-- leaderboard:entries:start -->
| baseline-sp1024-mlx-confirmed-s1 | none | baselines | pass | val_bpb=2.00936634 | confirm the frozen local MLX sp1024 baseline on isolated train shard 000001 | `iterations/archive/baseline-sp1024-mlx-confirmed-s1/` |
| eval-flat-sw64-confirmed-16m | baseline-sp1024-mlx-confirmed-s1 | evaluation | pass | val_bpb@16777216=2.02013120 | apply flat-stream stride-64 sliding-window accounting on a 16,777,216-target confirmatory prefix | `iterations/archive/eval-flat-sw64-confirmed-16m/` |
| opt-lrscale-down10-confirmed-s1 | baseline-sp1024-mlx-confirmed-s1 | optimizer_sweeps | pass | val_bpb=1.96768084 | scale the tied/embed/matrix/scalar learning-rate tuple down 10x to 0.045/0.036/0.036 on the frozen shard-000001 sp1024 MLX baseline path | `iterations/archive/opt-lrscale-down10-confirmed-s1/` |
<!-- leaderboard:entries:end -->
