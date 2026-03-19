# Parameter Golf Autoresearch Template

Use this as a starting `program.md` if running `karpathy/autoresearch` against a local Parameter Golf proxy.

## Goal

Improve `val_bpb` on the local proxy while preserving:

- one edited training file
- fixed wallclock per experiment
- a reversible experiment log
- easy import back into `leaderboard.md`

## Guardrails

- Prefer one atomic change at a time.
- Do not silently change the scoring method.
- Do not introduce validation leakage by default.
- Keep artifact-size accounting visible if serialization changes.
- If a result only wins through evaluation changes, label it as such.

## Suggested Search Order

1. LR and schedule
2. batch and sequence length tradeoffs
3. optimizer hyperparameters
4. small architecture knobs
5. selective precision

## Keep Or Revert Rule

Keep a change only if:

1. it improves the chosen proxy metric,
2. the change is attributable,
3. the resulting file is still readable enough to archive as a full file snapshot.
