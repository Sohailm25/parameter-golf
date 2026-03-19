# Autoresearch Fit - 2026-03-19

## What `autoresearch` Actually Is

Karpathy's `autoresearch` is a small repo where an agent repeatedly edits one training file, runs a fixed-time experiment, keeps or reverts based on `val_bpb`, and iterates overnight.

## Where It Fits Here

Strong fit:

- LR and schedule sweeps
- batch and throughput tradeoffs
- bounded optimizer ablations
- small architecture knob search after a stable baseline exists

Weak fit:

- first-principles challenge strategy
- evaluation-policy decisions
- tokenizer validation and BPB accounting
- multi-file repo structure

## Recommended Use In This Repo

1. Build a stable local proxy harness first.
2. Point `autoresearch` at one target file and one metric.
3. Use it to prune bad ideas, not to define the whole roadmap.
4. Import only promoted whole-file snapshots back through `leaderboard.md`.

## Practical Recommendation

Treat `autoresearch` as a sidecar search engine for `optimizer_sweeps` and maybe `architecture`, not as the top-level owner of the repo.
