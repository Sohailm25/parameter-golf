# Journal Current State

## Repo Reality

- Standalone repo and branch are initialized.
- `main` is now the source-of-truth branch.
- `bd` exists locally and the scaffold tests define the repo contract.
- Hooks and `pre-commit` are installed.
- `origin` now points at Sohail's fork.
- The imported `researchdocs/` notes are preserved as source inputs.
- The PR-review system now tracks a separate `eval-document-reset-ttt` lane instead of burying TTT inside generic document-isolated eval notes.
- The repo now also has persistent X and arXiv review hooks plus a drained `research/research-queries.md` queue.
- The live hook smoke run succeeded after one arXiv-query bug fix; that fix is now covered by tests.
- The repo now has append-only telemetry registries plus a dashboard renderer under `results/figures/renders/`.
- The local arXiv cache now materializes PDF/text files for retained papers, but the downloaded files are machine-local cache files rather than versioned artifacts.

## What Is Missing

- No official Parameter Golf code is wired into this workspace yet.
- No baseline run, no confirmatory split, and no promoted iteration exist yet.

## Next Delta To Close

1. Decide how to bring the official challenge code under this repo's archive discipline.
2. Freeze the baseline proxy and confirmatory split.
3. Use the new hook sequence at the start of the next real experiment loop.
4. Register the first real experiment run in the telemetry spine instead of treating the smoke infrastructure run as the only record.
