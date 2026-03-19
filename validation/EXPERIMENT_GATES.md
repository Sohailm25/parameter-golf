# Experiment Gates

This file defines the default comparison horizons for local experiments in this repo.

## Tier 0: Smoke / Elimination

- Purpose: reject crashes, obvious bugs, broken learning rates, and clearly bad ideas
- Typical scale: very short wallclock or `sub-100-step` runs
- Allowed claim: `this looks broken` or `this survives the first few steps`
- Forbidden claim: `this beats baseline`

## Tier 1: Medium-Horizon Proxy

- Purpose: compare atomic changes after warmup noise has mostly cleared
- Typical scale: around `500` steps or the lane-equivalent medium horizon on the current device
- Allowed claim: `this ranks better at the current proxy horizon`
- Forbidden claim: `this will win the full submission run`

## Tier 2: Confirmatory

- Purpose: decide whether a candidate deserves promotion into the golden path
- Typical scale: materially longer than the proxy horizon, with the repo's confirmatory split and reproducible logging
- Allowed claim: `this survived a stronger check`
- Required before: golden-set promotion, strong architecture claims, or submission-style messaging

## Interpretation Rules

- If Tier 0 and Tier 1 disagree, trust Tier 1.
- If Tier 1 and Tier 2 disagree, trust Tier 2.
- If an idea only wins at Tier 0, treat it as a false-positive candidate until stronger evidence appears.
- The `BPB@500` idea is a useful guardrail for this repo, not a universal law. Revisit the proxy horizon if a lane shows a different stabilization pattern.
