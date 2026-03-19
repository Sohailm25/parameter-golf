# Initial Strategy Synthesis

## Snapshot Date

This strategy snapshot is grounded to March 19, 2026.

## Current Read

The challenge is already being pushed hardest by three families of changes:

1. evaluation design, especially sliding windows and document isolation
2. tokenizer and vocabulary changes
3. selective precision and mixed quantization

Recurrence is alive and promising, but the public evidence is not yet strong enough to justify making it the default first lane in this repo.

## Default Strategy For This Workspace

1. Establish a clean local baseline and proxy harness.
2. Validate evaluation accounting and longer-context effects.
3. Run small optimizer and schedule sweeps.
4. Compare tokenizer and mixed-precision lanes before committing to a recurrence-heavy design.
5. Use `autoresearch` only after the proxy harness is trustworthy.
6. Promote candidates through immutable snapshots and the golden set.

## Why This Order

- It keeps the repo honest while the public frontier is moving fast.
- It favors levers already showing real gains in public PRs.
- It avoids betting the whole repo on one speculative architecture story too early.
