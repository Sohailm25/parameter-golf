# AGENTS.md - Codex Agent Directives for Parameter Golf Research

## Scope and Precedence

This file governs all work within `parametergolf/` and supersedes any AGENTS.md found in parent directories for this workspace.

Parent-workspace assumptions that do not apply here:

- this repository is standalone; its git history, issue tracking, and branches belong to `parametergolf/`
- no inherited thesis, benchmark framing, or phase names from `~/creativedecomp` or `~/resattn` belong here
- the default machine is Sohail's local M4 MacBook Pro with 128GB unified memory
- this repo is for Parameter Golf research, submission engineering, and iteration tracking, not a generic LLM sandbox
- remote 8xH100 verification is part of the competition environment, but it is not assumed as the default daily workflow here

Everything below this section is the authoritative directive set for this experiment.

This workspace is grounded in the official Parameter Golf repo, the imported `researchdocs/` conversation artifacts, and the local research notes created here.

## Mission

Execute the Parameter Golf research program defined by:

- `researchdocs/parameter_golf_strategy.md`
- `researchdocs/dynamiceval.md`
- `researchdocs/compass_artifact_wf-1d75e3e5-2eb7-4acc-b294-9b14e42edcfb_text_markdown.md`
- `researchdocs/compass_artifact_wf-7f912b62-af2f-4a6b-8858-875fb22f1adb_text_markdown.md`
- `researchdocs/compass_artifact_wf-be9c2458-2b26-4bc3-979a-bbb71a8446f1_text_markdown.md`
- `research/challenge-review-20260319.md`
- `research/approach-space-20260319.md`
- `research/autoresearch-fit-20260319.md`
- `validation/EXPERIMENT_GATES.md`

The goal is to build a disciplined local research repo for OpenAI's Parameter Golf challenge: understand the true constraints, map the live approach space, run the smallest experiment that can falsify one idea, and archive every meaningful iteration as a full file snapshot tied to `leaderboard.md`.

The default framing is not "we found a winning trick." It is: we are building a credible local system for discovering, evaluating, and formatting a strong submission while keeping challenge-spirit risk and self-deception visible.

## Issue Tracking

This project uses **bd** (beads) for issue tracking.
Run `bd prime` for workflow context, or install hooks with `bd hooks install`.

Quick reference:

- `bd ready` - find unblocked work
- `bd create "Title" --type task --priority 2` - create issue
- `bd update <id> --status in_progress` - claim work
- `bd close <id>` - complete work
- `bd sync` - sync issue state at session end

## Competition Locks

These are not optional. Every implementation and write-up must preserve them.

1. The primary deliverable is a credible Parameter Golf submission strategy plus a reproducible local research system, not a pile of untracked hacks.
2. Every promoted result must map to exactly one archived iteration with a full file snapshot and an atomic change note in `leaderboard.md`.
3. The public FineWeb validation set is a fragile target. The default workflow is `pilot -> confirmatory split -> submission` so we do not mistake leaderboard overfitting for progress.
4. Keep two lanes distinct: `spirit-first` and `open-rules`. Anything involving validation-set training or aggressive eval-time adaptation must stay clearly labeled and cannot silently become the default lane.
5. Local proxy wins are not leaderboard claims. Do not write as if an M4 result or a short local proxy run proves 8xH100 submission quality.
6. `autoresearch` is a bounded tuning multiplier, not the main source of architecture ideas.
7. The current golden set must stay runnable. Do not let speculative work break the repo's best known candidate.
8. Every iteration begins with an official PR intelligence pass. Launch a bounded `subagent` to review new `openai/parameter-golf` PRs first; if subagents are unavailable, run `scripts/review_openai_prs.py` directly and log the fallback.
9. Every iteration also runs the public-signal hooks: `bird-cli` search via `scripts/review_x_signal.py` and arXiv review via `scripts/review_arxiv.py` or the combined wrapper `scripts/review_iteration_signal.py`.
10. Every experiment run worth comparing gets a `run_id` in `results/telemetry/run_registry.jsonl`, append-only metric rows in `results/telemetry/metric_observations.jsonl`, and append-only artifact links in `results/telemetry/id_links.jsonl`.
11. `research/research-queries.md` is a drain queue, not a notebook. Any pending query there must be executed by the next arXiv review and then cleared.
12. A session that finds `no new PRs` must still record that result explicitly. Silence is not a PR review.

## Runtime Assumptions

- Primary machine: local M4 MacBook Pro with 128GB unified memory
- Python environment: `.venv`
- Default local backends: MLX, PyTorch CPU, or lightweight local tooling
- No cloud-first assumptions in day-to-day work
- Any later 8xH100 validation must be treated as a separate reproducibility step, not hand-waved from local runs

## Epistemic Standards

You are doing scientific and engineering work. Act like it.

1. Assumption quarantine. Any unverified statement is a hypothesis, not a fact. Label claims with `known`, `observed`, `inferred`, or `unknown`.
2. Evidence-first reasoning. Base conclusions on inspectable artifacts: run logs, artifact sizes, saved scripts, saved score tables, official README text, and archived iteration files.
3. No score mysticism. If a result looks unusually strong, check leakage, scoring changes, context-window effects, and evaluation protocol before celebrating.
4. Claim-evidence proportionality. Never write `ready`, `best`, `submission-quality`, or `SOTA-relevant` without the metric, setting, and comparison.
5. Adversarial self-questioning is mandatory:
   - Is this a real model improvement or just a metric/eval artifact?
   - Did we change more than one thing at once?
   - Does this improve the spirit-first lane, the open-rules lane, or only one controversial corner?
   - If this looks too good, is the probability of a bug or leakage actually higher than the probability of a breakthrough?
6. Pre-register before claim-bearing runs. The local prereg lives in `history/PREREG.md`.
7. Official repo state changes quickly. Re-check the official challenge repo before making "current landscape" claims in new work.

## Directory Map

```text
parametergolf/
├── AGENTS.md
├── CURRENT_STATE.md
├── DECISIONS.md
├── README.md
├── SCRATCHPAD.md
├── THOUGHT_LOG.md
├── leaderboard.md
├── background-work/
│   ├── COMPETITION_POLICY.md
│   ├── REFERENCES.md
│   ├── IMPLEMENTATION_GROUNDING.md
│   ├── GAPS_SYNTHESIS.md
│   ├── PROPOSAL_REVIEW.md
│   ├── RESEARCH_POSITIONING.md
│   └── papers/
├── configs/
├── history/
├── iterations/
│   ├── archive/
│   ├── golden/
│   └── templates/
├── journal/
├── knowledge/
├── prompts/
├── research/
├── researchdocs/
├── results/
├── scratch/
├── scripts/
├── sessions/
├── tests/
└── validation/
```

## Research Navigation Guide

Do not re-read everything blindly every session.

### Always read first in a fresh session

1. `CURRENT_STATE.md`
2. `journal/current_state.md`
3. `SCRATCHPAD.md`
4. `THOUGHT_LOG.md`
5. `DECISIONS.md`
6. `history/PREREG.md`
7. `leaderboard.md`
8. `research/pr_review_state.json`
9. `research/atomic_experiment_backlog.md`
10. `research/x_review_log.md`
11. `research/arxiv_review_log.md`
12. `research/research-queries.md`

### Read by question

- What are the official constraints and live competition state?
  - `research/challenge-review-20260319.md`
- Which experiment lanes matter most right now?
  - `research/approach-space-20260319.md`
- How should `autoresearch` fit into this repo?
  - `research/autoresearch-fit-20260319.md`
- What is the repo's current position on dynamic evaluation and TTT?
  - `results/evaluation/20260319-dynamic-eval-review.md`
- What is the repo's current position on medium-horizon experiment ranking and external-signal hooks?
  - `results/infrastructure/20260319-vukrosic-opinion-and-research-hooks.md`
- What did the imported back-and-forth already propose?
  - `researchdocs/*`

### Read only when needed

- `background-work/REFERENCES.md` when you need an official URL, PR link, or paper
- `background-work/COMPETITION_POLICY.md` when evaluation-time tricks or challenge spirit feel blurry
- `background-work/IMPLEMENTATION_GROUNDING.md` when deciding the next lane or experiment format
- `background-work/PROPOSAL_REVIEW.md` when a speculative idea from `researchdocs/` starts sounding more proven than it is
- `iterations/README.md` when adding or promoting archived full file snapshots

## Operating Rules

### 1. Document Discipline

Before starting a non-trivial work session:

1. Read `CURRENT_STATE.md`
2. Create or update a session log in `sessions/`
3. Confirm the next task against the active phase and prereg

During work:

- Update `SCRATCHPAD.md` before and after any substantial local run.
- Use `THOUGHT_LOG.md` for research reflections throughout the project. Record hunches, surprises, confidence shifts, and worries about challenge-spirit drift.
- Log non-obvious pivots in `DECISIONS.md` before proceeding.
- Update `CURRENT_STATE.md` whenever the actual repo state changes.
- Register durable outputs in `results/RESULTS_INDEX.md`.
- Register promoted script iterations in `leaderboard.md`.
- Start each iteration by reviewing the official PR frontier. Preferred path: launch a `subagent` to review new PRs; fallback path: run `scripts/review_openai_prs.py` yourself and log whether there were updates or `no new PRs`.
- Run the public-signal hooks on every iteration:
  - `scripts/review_x_signal.py` for bird-cli X search
  - `scripts/review_arxiv.py` for lane-aware arXiv review and draining `research/research-queries.md`
  - or `scripts/review_iteration_signal.py` to run the full sequence in one command

Long-running process rules:

- Any run that is expensive enough to care about surviving laptop sleep, terminal closure, or disconnects must run inside `tmux`.
- Long-running runs must save resumable checkpoints when the code supports it.
- Before launch, record the `tmux` session name, checkpoint path, log path, and resume command in `SCRATCHPAD.md`.
- After launch, verify that checkpoints are actually being written.

### 2. Session Check-In Protocol

If context is thin or the session resumed after compaction:

1. Read `CURRENT_STATE.md`
2. Read the latest entries in `SCRATCHPAD.md`
3. Read the latest entries in `THOUGHT_LOG.md`
4. Read the latest entries in `DECISIONS.md`
5. Read the latest session log in `sessions/`
6. Check `results/RESULTS_INDEX.md`
7. Check `leaderboard.md`
8. Read `research/pr_review_state.json`
9. Read `research/atomic_experiment_backlog.md`
10. Read `research/x_review_log.md`
11. Read `research/arxiv_review_log.md`
12. Read `research/research-queries.md`

Do not re-explore the whole repo if the state docs already answer the question.

### 3. The Research Documents Are the Spec

- `research/challenge-review-20260319.md` is the current source of truth for official constraints and the live competition snapshot.
- `research/approach-space-20260319.md` defines the current lane prioritization.
- `research/autoresearch-fit-20260319.md` defines the intended role of `autoresearch`.
- `research/pr_review_state.json` is the machine-readable source of truth for which official PRs have been seen and whether they need re-review.
- `research/atomic_experiment_backlog.md` is the deduped backlog of candidate atomic experiments derived from official PR review.
- `research/pr_review_log.md` is the rolling human-readable summary of frontier changes.
- `history/PREREG.md` defines what counts as a claim-bearing run.
- `researchdocs/*` are imported ideation artifacts. They are useful inputs, not binding truth.

If these documents conflict, resolve the conflict explicitly in `DECISIONS.md` before coding.

### 3A. PR Frontier Intelligence

- The persistent official PR review state lives in `research/pr_review_state.json`.
- The rolling human summary lives in `research/pr_review_log.md`.
- The deduped backlog of candidate atomic experiments lives in `research/atomic_experiment_backlog.md`.
- The normalized per-PR notes live in `research/pr_snapshots/`.
- The preferred review path is a `subagent` sweep over the current PR frontier.
- If subagents fail or are unavailable, run `scripts/review_openai_prs.py` directly and log the fallback in `SCRATCHPAD.md` or the session log.
- Re-review any PR whose head SHA or `updated_at` changed.

### 3B. Public Signal Intelligence

- The bird-cli X review state lives in `research/x_review_state.json`.
- The rolling X summary lives in `research/x_review_log.md`.
- The normalized tweet notes live in `research/x_snapshots/`.
- The arXiv review state lives in `research/arxiv_review_state.json`.
- The rolling arXiv summary lives in `research/arxiv_review_log.md`.
- The normalized paper notes live in `research/arxiv_snapshots/`.
- The local arXiv PDF cache lives in `background-work/papers/files/arxiv/`.
- The extracted local paper text lives in `background-work/papers/files/arxiv_text/`.
- `research/research-queries.md` is the queue for questions that must be drained by the next arXiv review.
- The preferred one-shot hook is `scripts/review_iteration_signal.py`.
- If a hook finds no useful public signal, record that explicitly instead of silently skipping the step.
- If a paper is used to justify an experiment decision, read the saved local PDF or extracted text before writing the claim.

### 4. Execution Order

Use this as the default phase flow:

1. Phase 0: scaffold, issue tracking, official challenge review, and source-of-truth setup
2. Phase 1: local baseline reproduction, measurement harnesses, and confirmatory split design
3. Phase 2: smallest experiment sweeps across optimizer, tokenizer, evaluation, compression, and architecture lanes
4. Phase 3: integrated candidate assembly, confirmatory split checks, and golden set promotion
5. Phase 4: submission formatting, reproducibility hardening, and upstream record packaging

### 5. Experiment Design Defaults

- Prefer the **smallest experiment** that can falsify exactly one idea.
- Use one atomic change per archived iteration unless the task is explicitly an integration step.
- Default workflow is `pilot -> confirmatory split -> submission`. Do not skip the confirmatory split just because the official validation set is public.
- Treat official validation runs as expensive and contamination-prone. Spend most tuning budget on smaller local proxies first.
- Keep the local golden set conservative. A flashy side lane does not replace the golden set until its run path is cleaner and better documented.
- If the metric changes because evaluation changed, say so explicitly. Do not present eval-only gains as architecture gains.
- Treat `sub-100-step` or ultra-short wallclock runs as elimination-only. Use them to reject obviously bad ideas, not to rank promising ones.
- Treat `~500-step` runs or the lane-equivalent medium-horizon proxy from `validation/EXPERIMENT_GATES.md` as a useful comparison gate, not as final truth.

### 6. Run Design Guardrails

- Every substantial run must record: command, device, data slice, wallclock target, artifact-size method, and score method.
- Every substantial run or iteration plan must begin from the latest official PR scan result in `research/pr_review_state.json` and `research/atomic_experiment_backlog.md`.
- Any scoring or tokenizer change needs an independent validation check before it can influence the golden set.
- Do not bundle tokenizer, architecture, optimizer, and evaluation changes into one iteration unless the task is explicitly an integration checkpoint.
- If using test-time training, sliding windows, longer context, or document resets, log exactly what state changes during evaluation and exactly what resets between documents.
- Keep `document-reset TTT` separate from `cross-document dynamic evaluation`. They are different lanes and must not be reported as one result.
- If a short-run ranking and a medium-horizon ranking disagree, trust the medium-horizon result until a longer confirmatory run says otherwise.
- If a run cannot produce a reproducible full file snapshot, it is not ready for `leaderboard.md`.

### 7. Required Experiment Lanes

The repo must keep these lanes visible even if some are dormant:

1. `baselines` - faithful local baselines and measurement sanity checks
2. `optimizer_sweeps` - LR, schedule, batch, Muon, and short-run ablations
3. `tokenizer` - vocab and tokenization experiments with BPB accounting
4. `architecture` - recurrence, depth/width, attention, MLP, and tying changes
5. `quantization` - QAT and serialization-friendly weight formats
6. `compression` - entropy coding and artifact-size engineering
7. `evaluation` - context length, sliding windows, and clearly labeled TTT variants
8. `autoresearch` - bounded agentic tuning workflows
9. `golden` - the current best integrated candidate

### 8. Results Registration

- Every durable artifact saved under `results/` must appear in `results/RESULTS_INDEX.md`.
- Every summary must say whether the result is `pass`, `fail`, `mixed`, `partial`, or `planning`.
- Every promoted result should name the relevant iteration ID from `leaderboard.md`.
- Never delete entries; mark superseded artifacts explicitly.

### 8A. Telemetry And Visualization

- `results/telemetry/` is append-only. Do not rewrite old JSONL rows to "clean them up."
- Register every meaningful run with `scripts/register_run.py run` before or immediately after launch.
- Append metrics with `scripts/register_run.py metric` at the checkpoints that matter for comparison.
- Create explicit ID links with `scripts/register_run.py link` so runs, iterations, papers, PRs, tweets, and result artifacts stay connected.
- Render progress views with `scripts/render_progress_dashboard.py`; every render writes to a unique directory under `results/figures/renders/`.
- If a run is promoted to `leaderboard.md`, ensure the telemetry contains a link from `run` to `iteration`.

### 9. Iteration Archive And Golden Set

- `iterations/archive/` stores the immutable **full file snapshot** for each promoted iteration.
- `leaderboard.md` maps `Iteration ID`, `Parent`, metric, status, and the **atomic change** that distinguishes one iteration from another.
- `iterations/golden/` holds the current **golden set** candidate files.
- Once an iteration is registered, do not silently edit its archived files. Create a new iteration instead.
- If an integration step merges several atomic ideas, the leaderboard entry must say so and list the parents.

### 10. Branch Truth

- Keep branch names truthful to the active task.
- Do not pretend the parent home-directory repo or another branch is the source of truth for this work.
- If no remote is configured yet, say so explicitly in status docs instead of implying the repo is fully landed.
- When a remote exists, finishing a session includes `bd sync`, `git push`, and a clean `git status`.
- The source-of-truth branch is `main`.
- Before a task is done, merge the task branch into `main`.
- After that merge, delete the previous task branch locally and remotely.
- The end-state is one active remote branch for ongoing work: `main`.
