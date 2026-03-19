# Telemetry Spine, Paper Ingestion, And Branch Policy - 2026-03-19

## Bottom Line

The repo now has an append-only telemetry spine, a reproducible dashboard renderer, local arXiv PDF/text materialization, and an explicit `main` source-of-truth branch policy.

## Repo Changes

- Added append-only telemetry registries under `results/telemetry/`:
  - `run_registry.jsonl`
  - `metric_observations.jsonl`
  - `id_links.jsonl`
  - `render_registry.jsonl`
- Added `scripts/register_run.py` to register runs, metrics, and cross-artifact links without overwriting history.
- Added `scripts/render_progress_dashboard.py` to build HTML dashboards into unique directories under `results/figures/renders/`.
- Updated `scripts/review_arxiv.py` so selected and carried-forward papers now get cached local PDFs plus extracted text files.
- Updated `AGENTS.md` so telemetry logging, local paper reading, and `main` branch consolidation are part of the repo contract.

## Live Smoke Checks

- Registered a live infrastructure run: `20260319-infrastructure-telemetry-dashboard-smoke`
- Appended live telemetry rows to `results/telemetry/run_registry.jsonl` and `results/telemetry/metric_observations.jsonl`
- Rendered dashboard bundles under `results/figures/renders/`
- Latest populated dashboard render: `results/figures/renders/20260319-163500-dashboard/index.html`
- Ran the arXiv hook live and confirmed local PDF/text materialization for the retained paper set:
  - `1904.08378v1`
  - `2212.02475v1`
  - `2403.01518v1`
  - `2502.07985v2`
  - `2502.17521v2`
  - `2510.00071v2`

## Observations

- The first dashboard render landed before the telemetry rows because I launched it in parallel with registration. The append-only registry kept that history instead of hiding it.
- The later render used the populated telemetry files correctly and now shows run, metric, and link counts from the smoke state.
- The arXiv cache now includes the current retained state, not only the most recently selected papers.

## Current Value

- We now have stable IDs for runs plus an append-only place to accumulate metrics over multiple horizons.
- We now have a visualization surface that can show progression without overwriting old renders.
- We now have a local paper cache, which removes the excuse of citing papers from abstracts alone.
