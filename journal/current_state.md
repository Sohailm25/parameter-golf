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
- The next tracked baseline task is `parametergolf-75u`, which will run the confirmatory split on shard `000001`.
- The local arXiv cache now materializes PDF/text files for retained papers, but the downloaded files are machine-local cache files rather than versioned artifacts.

## What Is Missing

- No confirmatory split execution and no promoted iteration exist yet.

## Next Delta To Close

1. Extend the cache to a second train shard and isolate the confirmatory slice.
2. Run the `1000`-step confirmatory baseline path on shard `000001`.
3. Register and inspect the confirmatory run in the telemetry spine.
4. Promote the first genuinely informative baseline iteration through the archive path once it clears the gate.
