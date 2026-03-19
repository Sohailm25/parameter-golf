# Parameter Golf Research Workspace

This workspace mirrors the operating discipline of `~/creativedecomp` and `~/resattn`, but it is adapted to OpenAI's Parameter Golf challenge and Sohail's requirement for strong local research structure, atomic iteration tracking, and a durable golden set.

## Source Documents

- `researchdocs/parameter_golf_strategy.md`
- `researchdocs/compass_artifact_wf-1d75e3e5-2eb7-4acc-b294-9b14e42edcfb_text_markdown.md`
- `researchdocs/compass_artifact_wf-7f912b62-af2f-4a6b-8858-875fb22f1adb_text_markdown.md`
- `researchdocs/compass_artifact_wf-be9c2458-2b26-4bc3-979a-bbb71a8446f1_text_markdown.md`
- `research/challenge-review-20260319.md`
- `research/approach-space-20260319.md`
- `research/autoresearch-fit-20260319.md`

## Local Runtime Assumptions

- Daily work happens on this M4 MacBook Pro with 128GB unified memory.
- Python runs through `.venv`.
- The repo is local-first. Cloud 8xH100 runs matter for final reproducibility, not for every experiment.
- The golden set is tracked locally and promoted only after confirmatory checks.

## Quick Start

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -p 'test*.py'
```

Optional setup:

```bash
.venv/bin/pip install pre-commit
.venv/bin/pre-commit install
bd hooks install
bd prime
```

## Operating Scaffold

- `AGENTS.md` is the local operating contract.
- `CURRENT_STATE.md` is the current single-source status file.
- `DECISIONS.md` records non-trivial decisions and pivots.
- `SCRATCHPAD.md` is the pre-run and post-run execution log.
- `THOUGHT_LOG.md` captures research reflections and confidence shifts.
- `history/PREREG.md` is the preregistered gate document.
- `leaderboard.md` tracks promoted iterations, parents, metrics, and atomic changes.
- `iterations/archive/` stores immutable full file snapshots for promoted iterations.
- `iterations/golden/` stores the current best integrated candidate.
- `results/RESULTS_INDEX.md` indexes durable artifacts under `results/`.
- `scripts/register_iteration.py` snapshots files into the archive and appends the leaderboard entry.

## What This Repo Is For

This repo is not yet a fork of the official challenge code. It is the research operating system around that work:

- understand the challenge and the live frontier as of March 19, 2026
- choose high-signal experiment lanes
- keep each promoted script revision archived and explainable
- use `autoresearch` as a bounded tool where it helps
- produce a clean golden set and an eventual submission-format package
