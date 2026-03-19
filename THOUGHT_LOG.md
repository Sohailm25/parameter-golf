# Thought Log

Research reflections for the Parameter Golf experiment.

Purpose:

- capture the qualitative feel of the competition as it unfolds
- preserve hunches, predictions, and confidence shifts
- note when the live frontier changes faster than the local plan
- separate intuition from claim-bearing evidence

Important rule:

- entries here are not claim-bearing evidence
- validated conclusions belong in `CURRENT_STATE.md`, `DECISIONS.md`, run artifacts, and the prereg-aware result docs

Suggested entry format:

```text
## [TIMESTAMP] [short title]
- Stage: [planning / implementation / analysis / synthesis]
- Feel of the Experiment: [1-3 sentences]
- Working Hypotheses:
  - [hypothesis]
- Hunches and Guesses:
  - [guess]
- Predictions:
  - [what I think will happen]
- Surprises and Tensions:
  - [unexpected fact or inconsistency]
- Confidence:
  - [low / medium / high] in [what]
- Interesting facts:
  - [competition fact, engineering note, or pattern worth remembering]
```

## Working Hypotheses

- [ ] Sliding-window and long-context evaluation effects are large enough that eval design deserves early priority.
- [ ] Vocabulary choice is still underexplored enough to matter materially for BPB.
- [ ] Mixed quantization and entropy coding are more robust early lanes than jumping straight to ternary QAT.
- [ ] `autoresearch` will help most on learning-rate, schedule, and throughput tuning, not on first-principles architecture invention.
- [ ] The biggest local risk is optimizing for public validation behavior faster than we optimize for real submission quality.

## Hunches and Guesses

- The first solid improvement will probably come from evaluation/context accounting or optimizer scheduling, not from exotic architecture.
- Public PRs that look too strong too early are more likely to be evaluation-policy edge cases than universally dominant model designs.
- The most valuable thing this repo can do early is stay honest about lane separation and iteration bookkeeping.

## Feel of the Experiment

- The challenge is closer to compression engineering plus evaluation design than to ordinary small-model training.
- The researchdocs ideas are strong raw material, but many of them still need to be downgraded from "strategy" to "hypothesis".

## Predictions

- A trustworthy local baseline and confirmatory split will be more valuable than rushing into a big recurrence or ternary rewrite.
- `leaderboard.md` will end up being one of the most important files in the repo because it forces the experiment history to stay intelligible.

## Surprises and Tensions

- The public frontier moved toward sliding windows and larger vocabularies almost immediately.
- The challenge encourages weird evaluation methods, but the line between creative evaluation and validation leakage is already blurry.

## Interesting Facts

- The official README explicitly treats evaluation as a separate 10-minute budget.
- The repo already has an `autoresearch`-inspired PR, which means that lane is not hypothetical anymore.
