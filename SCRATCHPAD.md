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

## [2026-03-19T16:30:00-0500] PRE-RUN: telemetry-and-paper-cache-smoke
- tmux session: N/A
- Script: `scripts/register_run.py`, `scripts/render_progress_dashboard.py`, `scripts/review_arxiv.py`
- Command: `.venv/bin/python scripts/register_run.py ...` and `.venv/bin/python scripts/render_progress_dashboard.py ...` and `.venv/bin/python scripts/review_arxiv.py --lane evaluation --phase pre --topic "dynamic evaluation transformer language model" --results-per-query 2 --max-papers 3`
- Device: `cpu`
- Lane: `infrastructure`
- Data slice: `metadata-only telemetry and literature cache smoke`
- Output path: `results/telemetry/`, `results/figures/renders/`, `background-work/papers/files/arxiv/`, `background-work/papers/files/arxiv_text/`
- Iteration target: N/A
- What I'm testing: verify append-only telemetry, unique render directories, and local PDF/text materialization for the retained arXiv state.
- Expected outcome: telemetry JSONL rows append, a dashboard bundle is rendered, and all retained papers get local PDF/text paths.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `results/telemetry/render_registry.jsonl` and `research/arxiv_review_log.md`
- Resume command: rerun the same three scripts sequentially
- Main confound to watch: parallel execution order can create valid but misleading early render snapshots.
- Implementation verified: YES - telemetry and arXiv unit tests are green before the live smoke.
- Status: LAUNCHING

## [2026-03-19T16:40:00-0500] POST-RUN: telemetry-and-paper-cache-smoke
- Command: `.venv/bin/python scripts/register_run.py ...`, `.venv/bin/python scripts/render_progress_dashboard.py --generated-at 2026-03-19T16:35:00Z`, `.venv/bin/python scripts/review_arxiv.py --lane evaluation --phase pre --topic "dynamic evaluation transformer language model" --results-per-query 2 --max-papers 3`
- Outcome: SUCCESS
- Key metric: `1` live run, `2` metric observations, `2` cross-artifact links, and `6` retained arXiv papers with local PDF/text files
- Artifacts saved: `results/telemetry/*.jsonl`, `results/figures/renders/20260319-163500-dashboard/index.html`, `background-work/papers/files/arxiv/`, `background-work/papers/files/arxiv_text/`
- Iteration registered: no
- Latest checkpoint: none
- Anomalies: the first dashboard render happened before telemetry registration because I launched it in parallel; that row was intentionally kept as append-only history and a later render captured the populated state.
- Next step: run the full test and hook gates, then merge the task history into `main`

## [2026-03-19T15:20:13Z] PRE-RUN: runner smoke
- Command: `RUN_ID=20260319-152013-infrastructure-runner-smoke /Users/sohailmo/parametergolf/.venv/bin/python /Users/sohailmo/parametergolf/scripts/mock_train_log.py`
- Device: `local-m4`
- Lane: `infrastructure`
- Issue: `parametergolf-kvg`
- Horizon: `smoke`
- Topic: `automation smoke`
- Log path: `logs/20260319-152013-infrastructure-runner-smoke.txt`
- What I'm testing: runner smoke

## [2026-03-19T15:20:21Z] POST-RUN: runner smoke
- Run ID: `20260319-152013-infrastructure-runner-smoke`
- Outcome: `SUCCESS`
- Log path: `logs/20260319-152013-infrastructure-runner-smoke.txt`
- Metric rows ingested: `5`
- Dashboard: `/Users/sohailmo/parametergolf/results/figures/renders/20260319-152021-dashboard/index.html`
- Next step: inspect the run, then promote with `scripts/experiment_runner.py promote` if warranted
