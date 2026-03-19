# Iteration Archive

This directory is the promotion boundary between local tinkering and repo-tracked progress.

## Rules

- Every promoted iteration must have a **full file snapshot** under `iterations/archive/<iteration-id>/`.
- Every promoted iteration must be registered in `leaderboard.md`.
- Every entry should explain the **atomic change** that distinguishes the iteration from its `Parent`.
- The `golden set` lives under `iterations/golden/` and should always mirror the current best integrated candidate.

## Layout

- `iterations/archive/` - immutable historical snapshots
- `iterations/golden/` - current best integrated candidate
- `iterations/templates/` - starter templates for submission packaging or snapshot metadata

## Promotion Workflow

1. Run or inspect a candidate that is worth preserving.
2. Snapshot the full files with `scripts/register_iteration.py`.
3. Verify the new row in `leaderboard.md`.
4. If the candidate is best-known, update the `golden set`.
