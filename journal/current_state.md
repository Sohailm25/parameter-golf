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
- The larger-budget confirmatory follow-up `parametergolf-8o4` is now closed after a `16,777,216`-target prefix preserved the same stride-`64` gain and promoted evaluation iteration `eval-flat-sw64-confirmed-16m`.
- The promoted evaluation iteration is archived, but the conservative golden baseline remains `baseline-sp1024-mlx-confirmed-s1`.
- `parametergolf-2km` now fixes the repo boundary for `autoresearch`: keep it in-repo as a sidecar search loop, not as a sibling workspace.
- The first bounded `autoresearch` phase is now defined as an `optimizer_sweeps` batch on `train_gpt_mlx.py`, one optimizer/schedule subspace at a time, against the frozen `500`-step MLX proxy.
- Any `autoresearch` candidate now has an explicit import path: summarize the batch under `results/autoresearch/`, rerun the best atomic change through `scripts/experiment_runner.py launch`, audit it, and only then consider promotion in the substantive lane.
- `parametergolf-gci` is now closed after the first bounded LR-scale batch and the canonical rerun of the down-10 winner.
- The batch-local down-10 result was directionally useful but numerically untrustworthy: `2.10816927` batch-local shrank to `2.17839092` on the canonical rerun.
- Even after that shrinkage, the canonical down-10 rerun still beat both the in-batch control and the archived baseline proxy, so the optimizer lane now has a real confirmatory follow-up instead of only a search hunch.
- `parametergolf-2s4` is now closed after the shard-`000001` confirmatory rerun of the same LR-down10 tuple.
- The confirmatory LR-down10 training run finished at `1.96768084` BPB with a `12942464`-byte int8 artifact, beating the promoted baseline confirmatory run by `0.04168550` BPB while shrinking the artifact.
- The matching `16M` current-accounting rescore also held up: `1.98197651` non-overlap and `1.97787760` stride-`64`, which preserves `~0.042` BPB gains versus the baseline checkpoint under the repo's current scoring reference.
- The repo now has a promoted optimizer iteration, `opt-lrscale-down10-confirmed-s1`, and that iteration is now mirrored into `iterations/golden/`.
- The local arXiv cache now materializes PDF/text files for retained papers, but the downloaded files are machine-local cache files rather than versioned artifacts.

## What Is Missing

- No post-baseline document-isolated or full-cache evaluation result has been confirmed yet.
- No next atomic issue is open yet after promoting the optimizer confirmatory candidate.

## Next Delta To Close

1. Decide whether document-isolated sliding-window accounting still deserves to be the next atomic lane, or whether a different non-eval lane should jump ahead after the optimizer promotion.
2. If document-isolated evaluation stays next, open the missing docs-cache materialization task rather than bundling new data plumbing into the accounting claim itself.
3. Keep the official PR/X/arXiv frontier fresh before opening the next lane issue.
