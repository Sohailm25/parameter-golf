# Gaps Synthesis

## What We Know

- The official challenge is real and moving fast.
- Evaluation design is already a first-class lever, not an afterthought.
- Mixed precision and tokenizer changes are already beating the naive baseline substantially.
- `researchdocs/` contains several plausible high-upside ideas, but not all of them are equally grounded.

## What We Do Not Know Yet

- The best local proxy that predicts official 8xH100 ranking
- Whether vocab, evaluation, or mixed quantization should be the first integrated lane
- How much `autoresearch` helps once the repo is pointed at a trustworthy proxy
- Whether recurrence is actually worth the integration cost relative to simpler wins

## Biggest Risks

1. Confusing evaluation-policy improvements with model improvements
2. Tuning directly on public validation behavior until every local claim is contaminated
3. Archiving diffs without archiving runnable full files
4. Letting speculative high-upside ideas crowd out strong boring baselines

## Current Mitigations

- separate `spirit-first` and `open-rules` lanes
- require a confirmatory split before golden-set promotion
- require immutable full file snapshots for promoted iterations
- keep current strategy grounded in the official README and current public PRs
