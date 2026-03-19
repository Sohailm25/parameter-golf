# Scratchpad

Use this file for execution checkpoints and transient notes. Every substantial local run should have a pre-run and post-run entry.

## Pre-Run Template

```text
## [TIMESTAMP] PRE-RUN: [run name]
- tmux session: [session name or N/A]
- Script: `scripts/[filename].py`
- Command: `.venv/bin/python ...`
- Device: `mlx` / `cpu` / `cuda`
- Lane: `baselines` / `optimizer_sweeps` / `tokenizer` / `architecture` / `quantization` / `compression` / `evaluation` / `autoresearch` / `golden`
- Data slice: [pilot / confirmatory split / official validation / custom proxy]
- Output path: `results/...`
- Iteration target: [iteration id or N/A]
- What I'm testing: [one sentence]
- Expected outcome: [one sentence]
- Checkpoint path: [path or N/A]
- Checkpoint cadence: [every N steps / minutes / epochs]
- Log path: [path]
- Resume command: [exact command]
- Main confound to watch: [one sentence]
- Implementation verified: YES/NO - [what local check was run]
- Status: LAUNCHING
```

## Post-Run Template

```text
## [TIMESTAMP] POST-RUN: [run name]
- Command: `.venv/bin/python ...`
- Outcome: SUCCESS / FAILURE / PARTIAL
- Key metric: [main number]
- Artifacts saved: `results/...`
- Iteration registered: [iteration id or no]
- Latest checkpoint: [path or none]
- Anomalies: [unexpected behavior or `none`]
- Next step: [single next action]
```

## Bootstrap Notes

- No Parameter Golf baseline has been reproduced from this scaffold yet.
- The first completed verification step is the scaffold test suite.
- The current repo contains the imported `researchdocs/` conversation artifacts but not yet an official-code working copy.
- The first promotion-worthy code path should use the iteration archive contract rather than ad hoc local files.

## [2026-03-19T15:18:00-0500] PRE-RUN: iteration-signal-smoke
- tmux session: N/A
- Script: `scripts/review_iteration_signal.py`
- Command: `.venv/bin/python scripts/review_iteration_signal.py --lane evaluation --phase pre --topic "parameter golf methodology"`
- Device: `cpu`
- Lane: `evaluation`
- Data slice: `metadata-only public-signal review`
- Output path: `research/x_review_log.md`, `research/arxiv_review_log.md`
- Iteration target: N/A
- What I'm testing: verify that the PR, X, and arXiv hooks all run successfully and that the arXiv queue drains.
- Expected outcome: state/log/snapshot files update and `research/research-queries.md` returns to empty.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `research/x_review_log.md` and `research/arxiv_review_log.md`
- Resume command: `.venv/bin/python scripts/review_iteration_signal.py --lane evaluation --phase pre --topic "parameter golf methodology"`
- Main confound to watch: external APIs may return mostly noise or no new signal.
- Implementation verified: YES - unit tests for hook parsing, command building, and query draining are green.
- Status: LAUNCHING

## [2026-03-19T15:25:00-0500] POST-RUN: iteration-signal-smoke
- Command: `.venv/bin/python scripts/review_iteration_signal.py --lane evaluation --phase pre --topic "parameter golf methodology"`
- Outcome: SUCCESS
- Key metric: hook sequence ran end-to-end; `research/research-queries.md` drained back to empty
- Artifacts saved: `research/x_review_log.md`, `research/arxiv_review_log.md`, `research/x_review_state.json`, `research/arxiv_review_state.json`
- Iteration registered: no
- Latest checkpoint: none
- Anomalies: first arXiv run was too broad and surfaced irrelevant papers; query/category logic was fixed and re-run successfully in the same session
- Next step: run the full test suite, then commit and push the hook changes
