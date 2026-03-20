# Current State

**Last updated:** 2026-03-20
**Updated by:** codex-gpt5
**Status:** in_progress
**Current phase:** Phase 2 - the standalone research scaffold is established, the official challenge code is already the workspace root, and the repo now has `bd` state, hooks, tests, PR-intelligence workflow, public-signal hooks, a dynamic-eval review artifact, append-only telemetry, local paper caching, a `main` source-of-truth branch, a canonical `START_HERE.md`, a launch/promote runner, minimal validation helpers, and a confirmed local baseline promoted into the first golden candidate.

## Active Strategy Lock

- `known`: `parametergolf/` is now a standalone git repository.
- `known`: the active and source-of-truth branch is `main`.
- `known`: `origin` now points at `https://github.com/Sohailm25/parameter-golf.git`.
- `known`: `bd` is initialized locally with issue prefix `parametergolf`.
- `known`: the scaffold task `parametergolf-70m` is closed, the official challenge code now lives directly in this workspace root, and the stale import-strategy task should be treated as resolved.
- `known`: after `parametergolf-75u`, the next ready tasks are `parametergolf-7b2` and `parametergolf-2km`.
- `known`: `bd` git hooks and `pre-commit` are installed locally, and the current scaffold test suite is green.
- `known`: the imported `researchdocs/` conversation artifacts were reviewed before scaffold changes.
- `known`: the official README confirms a decimal `16,000,000` byte artifact cap, a separate `10` minute evaluation budget on `8xH100`, tokenizer scrutiny, and a required `0.005` nat improvement at `p < 0.01` for new records.
- `observed`: as of 2026-03-19, the public PR frontier is already clustering around sliding-window evaluation, larger vocabularies, mixed quantization, recurrence, and `autoresearch`-style sweep tooling.
- `observed`: some open PRs report extremely strong scores that rely on validation-set training or related evaluation-side behavior; issue `#67` confirms that this is already a live community concern, so those approaches are relevant to the open-rules landscape but not safe to treat as the default spirit-first lane.
- `observed`: tokenizer accounting is strategically important partly because issue `#43` notes that tokenizer artifacts are not currently counted toward submission size.
- `observed`: PR `#77` makes the current public TTT picture clearer: document isolation and sliding-window scoring account for most of the visible gain, while reset-per-document TTT is real but smaller and should be tested as a distinct lane.
- `observed`: newer PRs through `#131` keep reinforcing the same live frontier: sliding-window evaluation, longer context, selective precision, recurrence variants, and better local sweep tooling still matter enough that the PR-intelligence loop is already paying for itself.
- `observed`: Vuk Rosic's public `BPB@500` warning is useful as a methodology caution against over-reading `50-step` or `5s` wins, but it is not strong enough evidence to treat `500` steps as a universal truth across lanes.
- `inferred`: the strongest early local research path is not to jump straight into ternary QAT or heroic recurrence stacks. It is to establish a trustworthy baseline workflow, short-run optimizer and schedule probes, evaluation-window accounting, and a robust iteration archive first.
- `known`: `leaderboard.md` plus `iterations/archive/` is the required promotion path for any meaningful script revision in this repo.
- `known`: `research/pr_review_state.json`, `research/pr_review_log.md`, `research/pr_snapshots/`, and `research/atomic_experiment_backlog.md` now persist official PR review state and deduped candidate experiments.
- `known`: `research/x_review_state.json`, `research/x_review_log.md`, `research/arxiv_review_state.json`, `research/arxiv_review_log.md`, and `research/research-queries.md` now exist to keep X and arXiv signal review persistent between iterations.
- `known`: the live bird-cli X hook works on this machine, and the arXiv hook works after a same-session query/filter bug fix that is now covered by tests.
- `known`: `results/telemetry/` now stores append-only run, metric, link, and render registries, with `scripts/register_run.py` and `scripts/render_progress_dashboard.py` as the write/render path.
- `known`: `scripts/experiment_runner.py` is now the canonical launch/promote path: it runs PR/X/arXiv review, writes scratchpad entries, registers `run_id`s, ingests log metrics, records run-log lineage, appends outcome metrics, and refreshes the dashboard.
- `known`: `validation/log_audit.py` and `validation/artifact_size.py` now provide the minimum reusable log-parsing and artifact-accounting helpers required by the prereg.
- `known`: `START_HERE.md` is now the canonical fresh-agent bootstrap path.
- `known`: this machine now has the local `sp1024` challenge cache under `data/datasets/` and `data/tokenizers/` with one local training shard plus the fixed public validation shard.
- `known`: a live infrastructure smoke run through `scripts/experiment_runner.py launch` succeeded with run id `20260319-152013-infrastructure-runner-smoke`; it produced a log, auto-ingested `5` parsed metric rows plus run-outcome metadata, recorded a `run -> run_log` link, and rendered `results/figures/renders/20260319-152021-dashboard/index.html`.
- `known`: the baseline-workflow task `parametergolf-7cm` is now closed with artifact `results/baselines/20260319-local-baseline-smoke-and-workflow-freeze.md`.
- `observed`: the first attempted real MLX smoke run (`20260319-154032-baselines-baseline-smoke`) exposed a workflow bug rather than a model bug: `VAL_BATCH_SIZE=8192` with default `GRAD_ACCUM_STEPS=8` reduced validation to one sequence per batch and made the smoke gate impractical.
- `known`: a corrected real local baseline smoke run through `scripts/experiment_runner.py launch` succeeded with run id `20260319-155403-baselines-baseline-smoke`; it reached `step:200/200 val_bpb=2.4090`, finished the quantized roundtrip at `val_bpb=2.40962829`, produced an `11260722`-byte int8 artifact, and rendered `results/figures/renders/20260319-160759-dashboard/index.html`.
- `known`: the local MLX smoke gate is now frozen around `VAL_BATCH_SIZE=524288`, and the workflow explicitly accounts for two full end-of-run validation passes.
- `known`: the first real medium-horizon proxy run through `scripts/experiment_runner.py launch` succeeded with run id `20260319-161653-baselines-baseline-proxy`; it reached `step:500/500 val_bpb=2.1827`, finished the quantized roundtrip at `val_bpb=2.18376301`, produced a `12730412`-byte int8 artifact, and rendered `results/figures/renders/20260319-163215-dashboard/index.html`.
- `known`: the proxy task `parametergolf-6yf` is now closed with artifact `results/baselines/20260319-local-baseline-proxy-500.md`.
- `known`: the confirmatory task `parametergolf-75u` is now closed; run `20260319-213359-baselines-baseline-confirmatory` completed on isolated shard `000001`, reached `step:1000/1000 val_bpb=2.0087`, finished the quantized roundtrip at `val_bpb=2.00936634`, produced a `13642279`-byte int8 artifact, and rendered `results/figures/renders/20260320-024538-dashboard/index.html`.
- `known`: the confirmatory baseline artifact is `results/baselines/20260320-local-baseline-confirmatory-1000.md`.
- `known`: the first promoted model iteration is `baseline-sp1024-mlx-confirmed-s1`, registered in `leaderboard.md`, archived under `iterations/archive/`, and mirrored into `iterations/golden/`.
- `known`: populated dashboard renders already exist at `results/figures/renders/20260319-163500-dashboard/index.html` and `results/figures/renders/20260319-152021-dashboard/index.html`.
- `observed`: because render directories are append-only history, use `results/telemetry/render_registry.jsonl` append order as the source of truth rather than lexicographic path ordering.
- `known`: the retained arXiv state now records local PDF/text paths for all retained papers.
- `observed`: the paper cache under `background-work/papers/files/arxiv/` and `background-work/papers/files/arxiv_text/` is machine-local and gitignored except for the tracked `.gitkeep` directory placeholders.
- `known`: the current deduped backlog includes ten candidate lanes, now with `eval-document-reset-ttt` split out from pure document-isolated sliding-window accounting.
- `known`: the experiment stack now has three horizons: smoke/elimination, medium-horizon proxy, and confirmatory.
- `known`: the current golden set now mirrors `baseline-sp1024-mlx-confirmed-s1` as the best-known integrated candidate.
- `unknown`: whether the first serious submission lane should center on evaluation accounting, document-reset TTT, tokenizer/vocab, or mixed quantization after the baseline lands.
- `unknown`: whether `autoresearch` should operate against a local proxy harness inside this repo or against a lightweight fork of the official challenge code in a separate sibling workspace.

## Immediate Next Steps

1. Resolve `parametergolf-7b2`: choose the first high-signal lane after the baseline path is frozen, likely starting with evaluation accounting, document-reset TTT, tokenizer scaling, or selective precision.
2. Resolve `parametergolf-2km`: bound `autoresearch` against the now-stable local proxy and confirmed baseline rather than against a moving target.
3. Keep the PR, X, and arXiv hook state/logs current at the start of each iteration.
4. Continue using `scripts/experiment_runner.py promote` so `run -> iteration -> result artifact` lineage stays intact for post-baseline lanes.
