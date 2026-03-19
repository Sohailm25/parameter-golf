# Proposal Review

This note reviews the imported `researchdocs/` proposals against the official challenge state as of 2026-03-19.

## Ideas To Keep Alive

- depth recurrence as a real architecture lane
- mixed precision and QAT as likely major levers
- test-time training as a meaningful evaluation lane
- `autoresearch` for bounded sweep automation

## Ideas To Downgrade From "Plan" To "Hypothesis"

- ternary QAT as the first serious lane
- byte-level tokenization as the obvious tokenizer winner
- the assumption that looping is automatically the dominant architecture move
- claims that TTT alone is the main breakthrough rather than a smaller layer on top of document isolation and sliding windows

## What Public PRs Changed

- larger vocab is already a live and competitive lever, so `1024` should not be treated as the default optimum
- sliding-window evaluation is already delivering large practical gains
- selective quantization is competitive now, not speculative future work
- recurrence is active but not yet clearly dominant over tokenizer and eval improvements

## Repo-Level Conclusion

The first strong version of this repo should not be a giant moonshot architecture rewrite. It should be a disciplined system that can compare:

1. evaluation changes
2. tokenizer changes
3. mixed-precision changes
4. recurrence changes

without losing track of which category actually caused the gain.
