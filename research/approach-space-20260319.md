# Approach Space - 2026-03-19

## Ranked Lanes

| Lane | Current Priority | Why | First local move |
|---|---|---|---|
| evaluation | very high | public PRs show large gains already | validate doc-isolated and sliding-window accounting locally |
| optimizer_sweeps | very high | fast local signal, low integration cost | short LR and schedule elimination runs |
| tokenizer | high | `sp4096` and `sp8192` are already competitive | compare vocab cost and BPB accounting assumptions |
| quantization | high | mixed precision is live and practical | test selective precision budgeting and artifact-size scripts |
| compression | medium-high | likely needed for serious later candidates | build artifact-size and entropy-coding audit tools |
| architecture | medium | recurrence is promising but not yet clearly dominant | keep width/depth/recurrence as a controlled lane |
| autoresearch | medium | good multiplier once proxy exists | define a local prompt and target file contract |

## What Not To Do First

- rewrite the whole model around ternary QAT before local measurement is trustworthy
- mix tokenizer, eval, and architecture changes in one early candidate
- use public validation as the only feedback loop

## First Three Concrete Experiments

1. Baseline proxy plus short LR range test
2. Sliding-window and document-isolation accounting check
3. Tokenizer-size tradeoff memo with artifact-budget math
