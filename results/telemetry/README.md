# Telemetry

This directory is the append-only telemetry spine for local Parameter Golf research.

## Files

- `run_registry.jsonl`: one immutable record per planned or executed run
- `metric_observations.jsonl`: append-only metric observations keyed back to `run_id`
- `id_links.jsonl`: append-only links between runs, iterations, papers, tweets, PRs, and result artifacts
- `render_registry.jsonl`: append-only registry of generated dashboards and figure bundles

## Rules

- Never edit prior JSONL rows in place.
- Never reuse a `run_id` for a different run.
- Prefer `scripts/experiment_runner.py launch` so runs automatically register scratchpad notes, metric ingestion, log links, and run-outcome metadata.
- Every promoted result should have a link from `run` to `iteration`.
- Every dashboard render writes to a unique directory under `results/figures/renders/`.
- Add new rows instead of overwriting prior measurements.
