# Parameter Golf Scaffold Adaptation

## Why This Exists

Sohail asked for `parametergolf/` to inherit the strongest structural properties of `~/creativedecomp` and `~/resattn` without inheriting their subject matter.

## What Was Reused

- standalone repo boundary
- `bd` issue tracking
- state docs: `CURRENT_STATE.md`, `DECISIONS.md`, `SCRATCHPAD.md`, `THOUGHT_LOG.md`
- preregistration
- results index
- session template
- scaffold regression tests

## What Was Changed

- replaced thesis-specific research language with Parameter Golf competition framing
- added `leaderboard.md` and `iterations/` as first-class repo features
- added a two-lane competition policy: `spirit-first` and `open-rules`
- centered the repo on local M4 development rather than Gemma/SAE experiments

## Why The New Pieces Matter

The reference repos were strong at research discipline, but this challenge needs additional machinery:

- immutable full file snapshots
- a golden set
- explicit competition-lane labeling
- a clear bridge between local experimentation and submission packaging
