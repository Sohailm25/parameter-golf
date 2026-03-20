# Decisions Log

## [2026-03-19T08:15:00-0500] DECISION: Make `parametergolf/` a standalone repository

- Trigger: the directory existed inside the home-directory git repo, while the reference projects were standalone repos with their own branches, hooks, and issue tracking.
- Decision: initialize `parametergolf/` as its own git repository and create the task branch `scaffold-parameter-golf-research`.
- Rationale: the research history, iteration archive, and issue tracker must belong to this workspace rather than leaking into an unrelated parent repo.
- Impact: git state, `bd`, hooks, and future pushes now belong to this repo.

## [2026-03-19T08:20:00-0500] DECISION: Reuse the strongest scaffold ideas from `creativedecomp` and `resattn`, but not their thesis language

- Trigger: Sohail asked for the directory to match the structural rigor of those repos without copying their content focus.
- Decision: copy the operating pattern: state docs, prereg, session logs, results index, tests, and issue discipline; adapt all content to Parameter Golf research.
- Rationale: the value is in the operating system around the work, not in cargo-culting another project's thesis.
- Impact: this repo now treats structure, journaling, and iteration tracking as first-class engineering artifacts.

## [2026-03-19T08:30:00-0500] DECISION: Split the competition into `spirit-first` and `open-rules` lanes

- Trigger: the live PR frontier already includes evaluation-side approaches that may be technically allowed but challenge-spirit-sensitive.
- Decision: document and preserve two lanes explicitly. The default lane for this repo is `spirit-first`; controversial validation-set training or aggressive eval adaptation stays visible but separate.
- Rationale: collapsing those lanes would blur methodology and make self-deception much easier.
- Impact: the strategy docs, prereg, and AGENTS contract now require explicit labeling of lane choice.

## [2026-03-19T08:35:00-0500] DECISION: Make `leaderboard.md` and immutable full file snapshots the promotion contract

- Trigger: Sohail asked for every meaningful script iteration to be archived as a whole file and mapped to its unique change in a leaderboard view.
- Decision: every promoted iteration must create a full file snapshot under `iterations/archive/` and register an atomic change row in `leaderboard.md`; the current best candidate lives in `iterations/golden/`.
- Rationale: diffs alone are not enough for this competition. The experiment history needs runnable whole-file checkpoints.
- Impact: the repo now has a concrete promotion path for script revisions, not just ad hoc commits.

## [2026-03-19T08:45:00-0500] DECISION: Use `autoresearch` as a bounded tuning tool, not as the main research brain

- Trigger: the imported conversation suggested using `karpathy/autoresearch`, and the live challenge repo already contains an `autoresearch`-inspired WIP.
- Decision: keep `autoresearch` in scope for local sweep automation, especially around short-run optimizer and hyperparameter probes, but do not let it define the core architecture strategy.
- Rationale: `autoresearch` is strong at local search over a fixed training file. It is not strong enough on its own to define the repo's scientific direction.
- Impact: the repo now has a dedicated `autoresearch` lane and prompt template, but the main strategy still comes from the local research docs.

## [2026-03-19T13:55:00-0500] DECISION: Make official PR review a persistent repo step, not ad hoc browsing

- Trigger: Sohail asked for each iteration to begin with a review of `openai/parameter-golf/pulls`, using a subagent when available, and to dedupe already seen PRs.
- Decision: add a persistent PR-review workflow centered on `research/pr_review_state.json`, `research/pr_review_log.md`, `research/pr_snapshots/`, `research/atomic_experiment_backlog.md`, and `scripts/review_openai_prs.py`; update `AGENTS.md` so every iteration starts with this step or an explicit `no new PRs` result.
- Rationale: the public frontier is moving quickly enough that rereading PRs by memory will waste time and create blind spots. We need durable state and a deduped backlog of atomic experiments.
- Impact: the repo now has a machine-readable frontier state, a human-readable review log, and a backlog seeded from current official PRs.

## [2026-03-19T14:00:00-0500] DECISION: Treat the second-pass frontier as stronger evidence for evaluation and tokenizer priority than for recurrence priority

- Trigger: the second grounded review covered new PRs, issue `#67` on validation-set training pressure, issue `#43` on tokenizer accounting, and the newer seq4096/fp16/int6 records.
- Decision: keep recurrence alive, but elevate three near-term priorities ahead of it: sliding-window/document accounting, tokenizer and vocabulary scaling, and selective int6 plus fp16 embedding precision.
- Rationale: the live frontier now contains more concrete and reproducible evidence for those lanes than for recurrence as the first integrated bet.
- Impact: the backlog and current-state docs now point the next lane selection toward evaluation, tokenizer, or selective-precision work first.

## [2026-03-19T14:20:00-0500] DECISION: Split dynamic evaluation into a document-reset TTT lane and a separate cross-document risk lane

- Trigger: Sohail asked for a review of `researchdocs/dynamiceval.md`, and the live PR review showed that PR `#77`'s own ablation attributes most of its gain to document isolation plus sliding-window scoring rather than TTT itself.
- Decision: treat dynamic evaluation as two different things. `document-reset TTT` stays in the default research backlog as a disciplined evaluation lane; `cross-document or repeated-pass held-out adaptation` remains visible but belongs to the repo's higher-risk open-rules framing unless proven otherwise.
- Rationale: collapsing those regimes would overstate what the public evidence currently supports and make it easier to confuse eval-accounting gains with true adaptation gains.
- Impact: the PR-review system now derives a distinct `eval-document-reset-ttt` experiment, the strategy docs now stage TTT after evaluation-accounting sanity checks, and the repo's policy docs now make the boundary explicit.

## [2026-03-19T15:05:00-0500] DECISION: Treat BPB@500 as a repo proxy gate, not as a universal law

- Trigger: Sohail asked for a review of Vuk Rosic's public `BPB@500` warning and whether it should affect the experimentation stack.
- Decision: add a medium-horizon proxy gate to the repo's experiment design, but do not canonize `500` steps as universally decisive across all lanes.
- Rationale: the early-vs-late reversal warning is valuable, but the current evidence is a public opinion plus anecdotal examples, not a documented multi-lane study we should treat as fact.
- Impact: `validation/EXPERIMENT_GATES.md` now defines smoke, proxy, and confirmatory horizons; AGENTS and prereg now warn against trusting ultra-short wins.

## [2026-03-19T15:10:00-0500] DECISION: Add persistent bird-cli and arXiv hooks to every iteration

- Trigger: Sohail asked for each pass to include a broad X search via bird-cli plus a lane-aware arXiv searcher with a drained query queue.
- Decision: add `scripts/review_x_signal.py`, `scripts/review_arxiv.py`, and `scripts/review_iteration_signal.py` plus persistent state, logs, snapshots, and `research/research-queries.md`.
- Rationale: public frontier chatter and nearby papers are useful inputs, but only if they become stateful, reviewable artifacts instead of ad hoc browsing.
- Impact: the repo now has a tested external-signal workflow and AGENTS requires it on every iteration.

## [2026-03-19T16:00:00-0500] DECISION: Make telemetry append-only and make `main` the enforced branch landing zone

- Trigger: Sohail asked for durable cross-metric visualization, strong ID mapping, local paper ingestion, and a single branch left open at task end.
- Decision: add append-only JSONL registries for runs, metrics, links, and renders; render dashboards into unique directories; cache local arXiv PDFs plus extracted text; codify `main` as the source-of-truth branch that every task branch must merge into before session end.
- Rationale: research progression becomes unreadable if metric history is overwritten, if papers are cited from abstracts alone, or if branches accumulate as semi-canonical histories.
- Impact: the repo now has a telemetry spine, a dashboard renderer, a local paper cache, and an explicit branch-consolidation rule.

## [2026-03-19T10:33:00-0500] DECISION: Default this repo's `bd` workflow to direct storage mode

- Trigger: the first branch checkout for `parametergolf-7cm` reproduced a `bd` post-checkout failure: daemon-backed `sync --import-only` emitted `no database store available for inline import`, even after the repo fingerprint and chained hooks were repaired.
- Decision: set `no-daemon: true` in `.beads/config.yaml` so the repo's `bd` commands and installed hooks use direct database access by default.
- Rationale: the failure was in the daemon-backed sync wrapper, not in direct `bd import` or `bd --no-daemon sync --import-only`. Versioning the no-daemon default is cleaner than patching local `.git/hooks` by hand.
- Impact: branch checkout/import is stable again on this machine, and future fresh sessions inherit the working `bd` mode from tracked repo config.

## [2026-03-19T11:00:00-0500] DECISION: Freeze the local MLX smoke gate around a wide validation batch and explicit double-validation cost

- Trigger: the first real MLX smoke run followed the small-batch local smoke pattern and became impractical because `VAL_BATCH_SIZE=8192` with default `GRAD_ACCUM_STEPS=8` reduced validation to one sequence per batch.
- Decision: define the local smoke gate with `VAL_BATCH_SIZE=524288` and document that `train_gpt_mlx.py` performs two full end-of-run validation passes: one full-float final pass and one quantized roundtrip pass.
- Rationale: small validation batches create a wallclock artifact unrelated to model quality and make the baseline loop misleading. The baseline workflow needs to measure the model, not the validator footgun.
- Impact: `START_HERE.md`, the local README smoke command, and the baseline workflow artifact now use the corrected validation regime, and later proxy/confirmatory runs can compare model changes instead of batch-shape accidents.

## [2026-03-19T16:30:35-0500] DECISION: Isolate the confirmatory baseline on a separate local shard-slice directory

- Trigger: `parametergolf-75u` requires a confirmatory run on `fineweb_train_000001.bin`, while the frozen smoke/proxy path still depends on `fineweb_train_000000.bin`.
- Decision: extend the local cache to two training shards, then launch the confirmatory run from a separate local dataset directory that exposes only `fineweb_train_000001.bin` plus the fixed public validation shard.
- Rationale: mutating the pilot cache in place would blur the baseline lineage and make the confirmatory split less trustworthy. An isolated slice keeps the frozen pilot path intact.
- Impact: the confirmatory run will remain reproducible as a distinct local data slice without overwriting or hiding the pilot-shard baseline.

## [2026-03-20T10:10:00-0500] DECISION: Promote the confirmed local MLX baseline as the first golden candidate

- Trigger: the shard-`000001` confirmatory run finished with `final_int8_zlib_roundtrip_exact val_bpb=2.00936634` and a `13642279`-byte artifact, materially improving on the smoke and proxy baselines while clearing the audit gates.
- Decision: register the run as iteration `baseline-sp1024-mlx-confirmed-s1` and mirror it into `iterations/golden/` as the current best-known candidate.
- Rationale: the repo now has the minimum evidence required by the prereg for a baseline promotion: a frozen workflow, a medium-horizon proxy, and a stronger confirmatory split on a distinct local train shard.
- Impact: the repo is no longer in a pre-promotion baseline state; post-baseline work should now compare new lanes against this promoted candidate rather than against only the smoke or proxy artifacts.

## [2026-03-20T10:45:00-0500] DECISION: Start Phase 2 with flat-stream sliding-window evaluation accounting

- Trigger: `parametergolf-7b2` required choosing the first post-baseline lane after the promoted baseline landed, and the refreshed frontier through PR `#224` still weighted evaluation most heavily.
- Decision: choose `evaluation` as the first post-baseline lane, and start with `eval-sliding-window-context-accounting` rather than document-isolated eval or TTT.
- Rationale: sliding-window accounting has the strongest public support and is the smallest implementable experiment on the current local cache. The current cache does not include `docs_selected.jsonl`, so leading with document-isolated eval would bundle metric logic with new data plumbing and violate the repo's atomicity preference.
- Impact: the immediate follow-up is `parametergolf-2r3`, a flat-stream sliding-window accounting check against `baseline-sp1024-mlx-confirmed-s1`. Document isolation stays next in line once the docs cache is materialized or the flat-stream harness is trusted.

## [2026-03-20T16:08:00Z] DECISION: Treat full flat-stream sliding-window evaluation as a separate confirmatory budget, not the first local iteration

- Trigger: the first attempted full-val flat-stream sliding-window accounting run (`20260320-160536-evaluation-sliding-window-accounting`) revealed that the cached validation stream contains `62,021,632` targets after trimming, so stride-`64` evaluation would require `969,073` windows and `60,568` local batches at `window_batch_seqs=16`.
- Decision: stop the unintended full-val run, preserve the harness plus a bounded `1,048,576`-target proxy result under `parametergolf-2r3`, and open a separate confirmatory follow-up issue (`parametergolf-8o4`) for the larger-budget check.
- Rationale: letting the first local evaluation iteration silently expand into a surprise multi-order-of-magnitude budget jump would violate the repo's smallest-experiment discipline and blur the meaning of the first preserved result.
- Impact: the repo now treats the bounded prefix run as the first preserved evaluation proxy, and any promotion discussion for sliding-window accounting requires an explicitly budgeted confirmatory step.
