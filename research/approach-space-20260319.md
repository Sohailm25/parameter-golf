# Approach Space - 2026-03-19

## Ranked Lanes

| Lane | Current Priority | Why | First local move |
|---|---|---|---|
| evaluation | very high | public PRs show large gains already, and PR `#77` shows TTT should be staged after eval accounting | validate doc-isolated and sliding-window accounting locally, then add a document-reset TTT sanity lane |
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
3. Document-reset TTT sanity lane on top of the best clean evaluation setup

## Second-Pass Frontier Adjustments

- `sliding window` should now be treated as a baseline comparison, not a quirky extension.
- `tokenizer size` deserves a first-class lane partly because the tokenizer artifact is not currently counted.
- `local sweep tooling` is worth real effort because PR `#80` and the autoresearch-style frontier show that iteration speed is itself becoming a lever.

## Dynamic-Eval Adjustment

- Treat `document-reset TTT` as a separate evaluation experiment, not as part of plain document-isolation accounting.
- The first dynamic-eval prototype should preserve `score -> record loss -> update`, reset between documents, and keep the adapted parameter subset small.
- `cross-document dynamic evaluation` is still research-interesting, but it belongs to the repo's higher-risk lane until we have a cleaner justification for it.
