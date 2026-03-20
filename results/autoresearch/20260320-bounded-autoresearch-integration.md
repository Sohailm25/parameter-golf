# Bounded Autoresearch Integration - 2026-03-20

## Status

- `status`: `planning`
- `lane`: `autoresearch`
- `issue`: `parametergolf-2km`
- `recommended_followup_issue`: `parametergolf-gci`
- `default_lane_label`: `spirit-first`

## Bottom Line

`autoresearch` should stay inside this repo as a bounded sidecar search loop, not as a sibling workspace and not as a direct path to `leaderboard.md`.

The first allowed use is narrow:

- substantive lane: `optimizer_sweeps`
- parent reference: `baseline-sp1024-mlx-confirmed-s1`
- scoring reference: `eval-flat-sw64-confirmed-16m`
- mutable file: `train_gpt_mlx.py`
- batch scope: one optimizer or schedule subspace at a time

Any winning autoresearch candidate must be rerun through the repo's normal launch and promotion discipline before it can count as a real iteration.

## Why The Boundary Is In-Repo

- The repo already has the hard parts that keep experimentation honest: `bd`, append-only telemetry, `leaderboard.md`, immutable iteration snapshots, `SCRATCHPAD.md`, and the PR/X/arXiv hooks.
- A sibling workspace would make it too easy to lose `run -> artifact -> iteration` lineage, blur branch truth, and let multi-file drift hide inside an overnight search batch.
- Recent frontier updates still support better local sweep tooling, including the newer MLX reliability PR `#234`, but that is evidence for better bounded search hygiene, not for handing strategy ownership to an external agent loop.

## Target File Contract

Each autoresearch batch must declare all of the following up front:

1. One parent iteration or baseline commit.
2. One substantive lane.
3. One mutable tracked source file.
4. One bounded search subspace.

For the first bounded phase, that means:

- parent: `baseline-sp1024-mlx-confirmed-s1`
- lane: `optimizer_sweeps`
- file: `train_gpt_mlx.py`
- allowed subspace example: learning-rate scalar and warmup/decay schedule
- allowed subspace example: optimizer hyperparameters already expressed in `train_gpt_mlx.py`
- allowed subspace example: batch/accumulation tradeoffs only if they remain a single-file change and are run as their own separate batch

Not allowed in the same batch:

- mixing optimizer and architecture edits
- mutating `train_gpt_mlx.py` and `scripts/eval_mlx_checkpoint.py` together
- editing telemetry files, `leaderboard.md`, state docs, or issue files as part of the search loop
- collapsing `spirit-first` and `open-rules`

Raw candidate files and batch-local notes should live under `scratch/autoresearch/<batch_id>/`. Durable summaries belong under `results/autoresearch/`.

## Proxy Metric Contract

The inner-loop search metric is the frozen Tier 1 local proxy on the current MLX training path:

- command family: local `train_gpt_mlx.py` proxy runs
- horizon: `500` steps
- data: `fineweb_train_000000.bin` plus the fixed public validation shard
- tokenizer: local `sp1024`
- training regime: `TRAIN_BATCH_TOKENS=8192`, `VAL_BATCH_SIZE=524288`, `VAL_LOSS_EVERY=0`
- primary search score: lower `final_int8_zlib_roundtrip_exact val_bpb`

Hard gates for a candidate to leave the search batch:

- `validation.log_audit` must recover a clean final exact score
- `validation.artifact_size` must remain within the `16,000,000` byte cap
- the candidate must beat the parent on the same proxy path, not only on a custom batch-local metric

This keeps the search metric fast enough for local sweeps while still tied to the repo's existing baseline workflow instead of a new private objective.

## Relationship To The Promoted Evaluation Iteration

The repo now has a promoted evaluation-only reference point, `eval-flat-sw64-confirmed-16m`. That should inform import decisions, but it should not become the inner-loop training metric for the first autoresearch batch.

Use the two references this way:

- `baseline-sp1024-mlx-confirmed-s1` stays the parent for training-path proxy and confirmatory reruns.
- `eval-flat-sw64-confirmed-16m` stays the current scoring reference for any candidate checkpoint that looks worth preserving.

If an autoresearch-discovered training change survives the canonical proxy rerun, score its checkpoint with the standalone sliding-window evaluator before making stronger claims about its ranking.

## Import Path Back To `leaderboard.md`

Autoresearch does not get to write directly into the leaderboard path.

The import path is:

1. Preserve the batch summary as an autoresearch artifact under `results/autoresearch/`.
2. Pick one understandable candidate diff and restate it as a single atomic change.
3. Reapply that change on a clean task branch outside the search scratch directory.
4. Rerun it through `scripts/experiment_runner.py launch` in the substantive lane, not the `autoresearch` lane.
5. Audit the log and artifact size with the existing validation helpers.
6. If the candidate still looks real, run the repo's Tier 2 confirmatory check on the isolated shard `000001`.
7. Only then use `scripts/experiment_runner.py promote`.

If a candidate needs multiple simultaneous edits to stay alive, it is not promotion-ready. Split it or discard it.

## When An Autoresearch Result Is Promotion-Worthy

An autoresearch result is only promotion-worthy when all of the following are true:

- the diff is one atomic change that Sohail can describe plainly
- the result is reproduced outside the batch-local search loop
- the canonical proxy rerun beats the parent on the frozen `500`-step metric
- the confirmatory split on shard `000001` preserves the direction of the win
- artifact-size and log-audit gates pass
- lane labeling remains explicit: `spirit-first` by default, `open-rules` only when intentionally declared

Autoresearch-only evidence is enough to keep searching. It is not enough for `leaderboard.md`.

## First Concrete Follow-Up

Resolve `parametergolf-gci` with a first bounded batch that:

- mutates only `train_gpt_mlx.py`
- stays in `optimizer_sweeps`
- searches only the LR/schedule subspace
- uses the frozen `500`-step proxy metric
- imports at most one winning candidate back through the canonical runner

That is the smallest real test of whether bounded autoresearch helps this repo instead of just generating noisy diffs.
