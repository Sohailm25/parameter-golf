# Start Here

Use this when a fresh agent needs to begin work without guessing the repo workflow.

## First Read

1. Read `CURRENT_STATE.md`
2. Read `journal/current_state.md`
3. Read the latest session log under `sessions/`
4. Read `AGENTS.md`

## First Commands

```bash
bd ready
.venv/bin/python -m unittest discover -s tests -p 'test*.py'
.venv/bin/python scripts/review_iteration_signal.py --lane baselines --phase pre --topic "baseline reproduction"
```

If `data/datasets/` or `data/tokenizers/` is missing, materialize the local challenge cache before the first real baseline run:

```bash
.venv/bin/python data/cached_challenge_fineweb.py --variant sp1024 --train-shards 1
```

## Standard Experiment Launch

Use the launch runner instead of doing the loop manually:

```bash
.venv/bin/python scripts/experiment_runner.py launch \
  --lane baselines \
  --label "baseline smoke" \
  --issue-id parametergolf-7cm \
  --topic "baseline reproduction" \
  --script-path train_gpt_mlx.py \
  --env ITERATIONS=200
```

This does the PR/X/arXiv review, writes the scratchpad pre-run note, registers a `run_id`, launches the training script, ingests log metrics into telemetry, writes the post-run note, and renders the dashboard.

## Promotion Path

If a run deserves durable promotion, use:

```bash
.venv/bin/python scripts/experiment_runner.py promote \
  --run-id <run_id> \
  --iteration-id <iteration_id> \
  --lane baselines \
  --status pass \
  --metric "val_bpb=..." \
  --change "one atomic change summary" \
  --source train_gpt.py \
  --result-path results/baselines/<artifact>.md
```

This snapshots the full files through `scripts/register_iteration.py`, links the run to the new iteration, and refreshes the dashboard.

## Useful Follow-Up Commands

```bash
.venv/bin/python scripts/render_progress_dashboard.py
.venv/bin/python -m validation.log_audit logs/<run_id>.txt
.venv/bin/python -m validation.artifact_size train_gpt.py
```

## Local Prerequisites

- `.venv`
- `bd`
- `bird`
- `pdftotext`
- `tmux`
- local challenge cache under `data/datasets/` and `data/tokenizers/` for real baseline runs

If one of those is missing, fix the environment before starting a real experiment loop.
