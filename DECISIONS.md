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
