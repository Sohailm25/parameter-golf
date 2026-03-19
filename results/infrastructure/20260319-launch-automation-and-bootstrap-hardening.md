# Launch Automation And Bootstrap Hardening

**Date:** 2026-03-19
**Lane:** infrastructure
**Status:** pass

## Scope

Close the last pre-experiment scaffolding gaps so a fresh agent can begin cleanly from either a brand-new session or a deep-in-progress session without relying on stale memory.

## What Changed

- Added `START_HERE.md` as the canonical bootstrap path.
- Added `scripts/experiment_runner.py` as the canonical launch/promote path for runs that matter.
- Added `validation/log_audit.py` and `validation/artifact_size.py` so prereg-required log parsing and byte accounting are no longer placeholders.
- Hardened telemetry by recording:
  - parsed metric rows from train logs
  - run-outcome metadata like `process_returncode`, `ingested_metric_rows`, and `log_bytes`
  - `run -> run_log` lineage in `results/telemetry/id_links.jsonl`
- Updated repo state/docs so agents no longer see the false claim that official Parameter Golf code is not wired into this workspace.

## Live Smoke Validation

The canonical CLI path was exercised with:

```bash
.venv/bin/python scripts/experiment_runner.py launch \
  --lane infrastructure \
  --label "runner smoke" \
  --issue-id parametergolf-kvg \
  --topic "automation smoke" \
  --script-path scripts/mock_train_log.py \
  --device local-m4 \
  --horizon smoke
```

Observed result:

- `run_id`: `20260319-152013-infrastructure-runner-smoke`
- `log_path`: `logs/20260319-152013-infrastructure-runner-smoke.txt`
- parsed metric rows: `5`
- appended outcome metrics: `process_returncode=0`, `ingested_metric_rows=5`, `log_bytes=271`
- logged lineage: `run -> run_log`
- dashboard render: `results/figures/renders/20260319-152021-dashboard/index.html`

## Remaining Real-Experiment Blocker

The repo workflow is ready, but this machine still lacks the local challenge cache under `data/datasets/` and `data/tokenizers/`. The first real baseline run should begin by materializing the local `sp1024` cache, then using `scripts/experiment_runner.py launch` instead of manual commands.
