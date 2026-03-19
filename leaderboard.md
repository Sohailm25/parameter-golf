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
| pending | none | infrastructure | planning | n/a | scaffold only; no promoted model iteration yet | `iterations/archive/` |
<!-- leaderboard:entries:end -->
