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
