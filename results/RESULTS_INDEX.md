# Results Index

Register every durable artifact under `results/` here. Never delete entries; mark superseded artifacts explicitly.

## Rules

- Every artifact saved under `results/` must appear here.
- Every entry should state the lane.
- Every entry should state `pass`, `fail`, `mixed`, `partial`, or `planning`.
- Every summary should be consistent with the current prereg and lane labeling.
- Telemetry-generated dashboard bundles are canonically indexed in `results/telemetry/render_registry.jsonl`; call out notable renders here.

## Infrastructure

| Artifact | Lane | Status | Path |
|---|---|---|---|
| Standalone scaffold adaptation from the reference repos into a Parameter Golf local-first workspace | infrastructure | pass | `results/infrastructure/20260319-scaffold-adaptation.md` |
| Initial challenge and strategy grounding against the official README plus live public PR landscape | infrastructure | pass | `results/infrastructure/20260319-initial-strategy-synthesis.md` |
| Official PR intelligence automation plus second-pass frontier review and deduped atomic-experiment backlog | infrastructure | pass | `results/infrastructure/20260319-pr-intelligence-second-pass.md` |
| Review of Vuk Rosic's `BPB@500` opinion plus installation of bird-cli and arXiv research hooks | infrastructure | pass | `results/infrastructure/20260319-vukrosic-opinion-and-research-hooks.md` |
| Append-only telemetry spine, local arXiv PDF/text ingestion, and `main` source-of-truth branch policy | infrastructure | pass | `results/infrastructure/20260319-telemetry-pdf-ingestion-and-branch-policy.md` |
| Launch/promotion automation, bootstrap hardening, and live runner smoke validation | infrastructure | pass | `results/infrastructure/20260319-launch-automation-and-bootstrap-hardening.md` |

## Baselines

| Artifact | Lane | Status | Path |
|---|---|---|---|
| First real local MLX baseline smoke run plus the frozen smoke/proxy/confirmatory workflow for `sp1024` | baselines | partial | `results/baselines/20260319-local-baseline-smoke-and-workflow-freeze.md` |
| First `500`-step medium-horizon proxy on the frozen local MLX `sp1024` baseline path | baselines | pass | `results/baselines/20260319-local-baseline-proxy-500.md` |
| First `1000`-step confirmatory baseline on isolated shard `000001` for the frozen local MLX `sp1024` path | baselines | pass | `results/baselines/20260320-local-baseline-confirmatory-1000.md` |
## Optimizer Sweeps

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Architecture

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Quantization

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Compression

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Tokenizer

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Evaluation

| Artifact | Lane | Status | Path |
|---|---|---|---|
| Dynamic-eval and TTT review grounded against `researchdocs/dynamiceval.md`, the official README, and PR `#77`/`#85` | evaluation | pass | `results/evaluation/20260319-dynamic-eval-review.md` |
| Post-baseline lane selection choosing flat-stream sliding-window accounting as the first atomic evaluation experiment | evaluation | planning | `results/evaluation/20260320-post-baseline-lane-selection.md` |
| First flat-stream sliding-window accounting proxy on `baseline-sp1024-mlx-confirmed-s1`, including the aborted full-val budget mistake and the bounded `1,048,576`-target comparison | evaluation | partial | `results/evaluation/20260320-flat-stream-sliding-window-proxy-1m.md` |

| apply flat-stream stride-64 sliding-window accounting on a 16,777,216-target confirmatory prefix | evaluation | pass | `results/evaluation/20260320-flat-stream-sliding-window-confirmatory-16m.md` |
## Autoresearch

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Golden

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Figures

| Artifact | Lane | Status | Path |
|---|---|---|---|
| Populated telemetry dashboard render after live run registration, metric append, and cross-artifact links | infrastructure | pass | `results/figures/renders/20260319-163500-dashboard/index.html` |
