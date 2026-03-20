# Journal Current State

## Repo Reality

- Standalone repo and branch are initialized.
- `main` is now the source-of-truth branch.
- `bd` exists locally and the scaffold tests define the repo contract.
- Hooks and `pre-commit` are installed.
- `origin` now points at Sohail's fork.
- The official Parameter Golf code is already this workspace root; there is no unresolved import boundary anymore.
- The imported `researchdocs/` notes are preserved as source inputs.
- The PR-review system now tracks a separate `eval-document-reset-ttt` lane instead of burying TTT inside generic document-isolated eval notes.
- The repo now also has persistent X and arXiv review hooks plus a drained `research/research-queries.md` queue.
- The live hook smoke run succeeded after one arXiv-query bug fix; that fix is now covered by tests.
- The repo now has append-only telemetry registries plus a dashboard renderer under `results/figures/renders/`.
- The canonical run path is now `scripts/experiment_runner.py launch`, and the canonical promotion path is `scripts/experiment_runner.py promote`.
- Minimal reusable validation helpers now exist in `validation/log_audit.py` and `validation/artifact_size.py`.
- `START_HERE.md` now gives a single bootstrap path for fresh agents.
- This repo now defaults `bd` to direct storage mode because the daemon-backed checkout import path was unstable on this machine.
- This machine now has the local `sp1024` challenge cache under `data/datasets/` and `data/tokenizers/`.
- A live smoke run through `scripts/experiment_runner.py launch` succeeded and proved the CLI path, telemetry ingestion, log-link registration, outcome metrics, and dashboard refresh against a deterministic mock log writer.
- The first real local MLX smoke run also succeeded after one workflow correction: keep `VAL_BATCH_SIZE` large or the validator becomes the bottleneck.
- The baseline workflow is now frozen in `results/baselines/20260319-local-baseline-smoke-and-workflow-freeze.md`.
- The first `500`-step proxy also succeeded and now has its own result artifact under `results/baselines/20260319-local-baseline-proxy-500.md`.
- The `1000`-step confirmatory run on isolated shard `000001` also succeeded and now has its own result artifact under `results/baselines/20260320-local-baseline-confirmatory-1000.md`.
- The repo now has its first promoted baseline iteration, `baseline-sp1024-mlx-confirmed-s1`, mirrored into `iterations/golden/`.
- The first post-baseline planning pass selected `evaluation` as the next lane and wrote that recommendation to `results/evaluation/20260320-post-baseline-lane-selection.md`.
- The repo now has a standalone MLX checkpoint evaluator plus a tested flat-stream window planner under `scripts/eval_mlx_checkpoint.py` and `validation/eval_windowing.py`.
- The first preserved post-baseline result is `results/evaluation/20260320-flat-stream-sliding-window-proxy-1m.md`.
- On the first `1,048,576` validation targets, stride-`64` flat-stream sliding-window accounting improved the promoted baseline checkpoint from `2.02717341` to `2.02328090` BPB.
- The first attempt at a full flat-stream confirmatory run was intentionally aborted once the local budget mistake became obvious: the cached validation stream has `62,021,632` targets after trimming, so full stride-`64` evaluation is a separate budgeted step, not an incidental first check.
- The immediate execution follow-up is `parametergolf-8o4`, a larger-budget confirmatory sliding-window accounting check against the promoted baseline.
- The local arXiv cache now materializes PDF/text files for retained papers, but the downloaded files are machine-local cache files rather than versioned artifacts.

## What Is Missing

- No post-baseline evaluation result has been confirmed at a larger-than-proxy budget yet.

## Next Delta To Close

1. Resolve `parametergolf-8o4` and run the larger-budget confirmatory sliding-window accounting check against `baseline-sp1024-mlx-confirmed-s1`.
2. Decide whether document-isolated evaluation should follow immediately or only after a separate docs-cache materialization step.
3. Bound `autoresearch` under `parametergolf-2km` now that the local baseline and proxy reference points are stable.
