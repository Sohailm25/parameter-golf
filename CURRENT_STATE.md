# Current State

**Last updated:** 2026-03-19
**Updated by:** codex-gpt5
**Status:** in_progress
**Current phase:** Phase 0 - the standalone research scaffold is established, the official challenge constraints have been re-grounded from the live README and open PRs, and the repo now has a dedicated branch, `bd` state, hooks, tests, and a local-first experiment structure. No baseline reproduction or golden-set candidate exists yet.

## Active Strategy Lock

- `known`: `parametergolf/` is now a standalone git repository.
- `known`: the active branch is `scaffold-parameter-golf-research`.
- `known`: `bd` is initialized locally with issue prefix `parametergolf`.
- `known`: the scaffold task `parametergolf-70m` is closed; the next ready tasks are `parametergolf-mem`, `parametergolf-7cm`, `parametergolf-2km`, and `parametergolf-7b2`.
- `known`: `bd` git hooks and `pre-commit` are installed locally, and the current scaffold test suite is green.
- `known`: the imported `researchdocs/` conversation artifacts were reviewed before scaffold changes.
- `known`: the official README confirms a decimal `16,000,000` byte artifact cap, a separate `10` minute evaluation budget on `8xH100`, tokenizer scrutiny, and a required `0.005` nat improvement at `p < 0.01` for new records.
- `observed`: as of 2026-03-19, the public PR frontier is already clustering around sliding-window evaluation, larger vocabularies, mixed quantization, recurrence, and `autoresearch`-style sweep tooling.
- `observed`: some open PRs report extremely strong scores that rely on validation-set training or related evaluation-side behavior; those approaches are therefore relevant to the open-rules landscape but not safe to treat as the default spirit-first lane.
- `inferred`: the strongest early local research path is not to jump straight into ternary QAT or heroic recurrence stacks. It is to establish a trustworthy baseline workflow, short-run optimizer and schedule probes, evaluation-window accounting, and a robust iteration archive first.
- `known`: `leaderboard.md` plus `iterations/archive/` is the required promotion path for any meaningful script revision in this repo.
- `known`: the current golden set is empty by design. No candidate has earned promotion yet.
- `unknown`: whether the first serious submission lane should center on tokenizer/vocab, evaluation context, mixed quantization, or recurrence after the baseline lands.
- `unknown`: whether `autoresearch` should operate against a local proxy harness inside this repo or against a lightweight fork of the official challenge code in a separate sibling workspace.

## Immediate Next Steps

1. Resolve `parametergolf-mem`: decide how the official Parameter Golf code enters this workspace.
2. Resolve `parametergolf-7cm`: define the first `pilot` and `confirmatory split` methodology for local experimentation.
3. Resolve `parametergolf-7b2`: choose the first high-signal lane after the baseline path is frozen.
4. Resolve `parametergolf-2km`: specify the bounded `autoresearch` workflow.
