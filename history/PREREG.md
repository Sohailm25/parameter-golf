# Preregistration

## Scope

This preregistration covers the Parameter Golf research workflow in this repo.

## Framing Lock

- The primary claim is about building and comparing credible submission candidates under strong local discipline.
- The first goal is not "win at any cost." It is to build a repo that can tell the difference between real improvements and evaluation artifacts.
- Public-validation-friendly methods must be labeled by lane.
- `leaderboard.md` and immutable snapshots are part of the methodology, not paperwork.

## Primary Hypothesis

A local-first workflow built around atomic experiment changes, a confirmatory split, and full file snapshots will surface a stronger and cleaner early submission direction than jumping straight into large speculative rewrites.

## Secondary Hypotheses

1. Sliding-window or document-isolated evaluation is strong enough to deserve early priority.
2. Larger vocabularies and selective quantization are already competitive enough to outrank many exotic architecture ideas.
3. `autoresearch` helps most once a stable local proxy exists.
4. A clear spirit-first lane will reduce self-deception even if it slows apparent progress.
5. Document-reset TTT may be worthwhile, but only after document handling and sliding-window accounting are already clean.
6. Medium-horizon comparisons are more trustworthy than ultra-short runs when the two disagree.

## Null And Baseline Conditions

- naive baseline behavior
- local baseline proxy
- previous golden-set candidate
- document-reset TTT should be compared against a clean document-isolated sliding-window baseline, not only the flat-stream baseline
- any controversial eval method without document reset or clear accounting

## Required Methods

- one atomic change per promoted iteration
- full file snapshot before leaderboard registration
- explicit lane labeling: `spirit-first` or `open-rules`
- pilot runs before broader local sweeps
- a `confirmatory split` before golden-set promotion
- a medium-horizon proxy gate before trusting architecture or activation-function rankings
- explicit artifact-size accounting for any serialization change
- independent scoring checks for tokenizer or evaluation changes

## Phase Gates

### Phase 0: Scaffold And Grounding

- repo structure, tests, prereg, and issue tracker are live
- official challenge state is reviewed and written down

### Phase 1: Local Baseline And Proxy Harness

- baseline or stable proxy runs locally
- run artifacts are indexed under `results/`
- at least one confirmatory split design is frozen

### Phase 2: Single-Lane Sweeps

- each lane changes one major variable category at a time
- no golden-set promotion without a second check on the confirmatory split

### Phase 3: Integrated Candidate

- integration combines previously validated atomic changes
- all parent iterations are cited in the leaderboard row
- artifact-size and evaluation logic are both rechecked

### Phase 4: Submission Packaging

- candidate is runnable as a whole-file snapshot
- README, training log, and metadata are ready to map into upstream submission format

## Overclaim Guardrails

Do not claim:

- that a local proxy metric equals official leaderboard ranking
- that an eval-only trick is a training breakthrough
- that a public-validation-tuned method is automatically robust
- that a diff is enough to reproduce a candidate without a full file snapshot

## Reproducibility

- use `.venv`
- save commands and paths in `SCRATCHPAD.md`
- keep the current best candidate mirrored in `iterations/golden/`
- register every durable result in `results/RESULTS_INDEX.md`
