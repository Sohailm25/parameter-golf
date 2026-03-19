# Implementation Grounding

This file translates the challenge and the imported ideation notes into concrete work lanes for this repo.

## What Must Be True Before We Trust Any Improvement

1. We can reproduce a local baseline or at least a stable proxy baseline.
2. We can explain whether a gain came from training, architecture, tokenizer, compression, or evaluation.
3. We can map the gain to an archived full file snapshot and one atomic change.
4. We can say whether the gain belongs to the `spirit-first` lane, the `open-rules` lane, or both.

## Default Local Workflow

1. Start from a simple, runnable baseline path.
2. Run the smallest experiment that changes one thing.
3. Save the run artifact under the correct `results/` lane.
4. If the revision is worth preserving, register it in `leaderboard.md`.
5. Promote to the golden set only after a confirmatory split or equivalent second check.

## Current Best-Justified Early Lanes

### 1. Optimizer And Schedule Probes

- Why first: fast local feedback, low integration cost, already validated by the challenge community
- Examples: LR range tests, warmdown shape, Muon vs NorMuon, batch-equivalent simulation, short-run elimination sweeps

### 2. Evaluation Context And Accounting

- Why first: sliding-window and doc-isolated eval are already showing large gains in public PRs
- Examples: stride studies, document boundary masking, long-context local accounting, explicit reset logic

### 3. Tokenizer And Vocabulary

- Why first: public evidence already suggests larger vocab can materially shift BPB
- Examples: `sp2048`, `sp4096`, `sp8192`, tokenizer accounting checks, embedding budget tradeoffs

### 4. Mixed Precision And Compression

- Why first: selective int6 or int8 is already competitive and easier to validate than ternary from day one
- Examples: per-module precision maps, entropy coding experiments, artifact-size audits

## Lanes To Delay Slightly

- aggressive recurrence stacks before the baseline and compression path are trustworthy
- ternary QAT as the default lane before int4 or int6 serialization is understood
- validation-set training as a default strategy

## Role Of `autoresearch`

- Strong fit: local search over hyperparameters, schedule, and bounded architecture knobs once a stable proxy exists
- Weak fit: first-principles strategy, evaluation-policy choices, and multi-file repo design
