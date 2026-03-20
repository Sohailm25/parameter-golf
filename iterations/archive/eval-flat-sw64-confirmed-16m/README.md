# eval-flat-sw64-confirmed-16m

## Metadata

- Parent: `baseline-sp1024-mlx-confirmed-s1`
- Lane: `evaluation`
- Status: `pass`
- Metric: `val_bpb@16777216=2.02013120`
- Atomic change: apply flat-stream stride-64 sliding-window accounting on a 16,777,216-target confirmatory prefix
- Notes: Evaluation-only promotion after the 16M confirmatory prefix reproduced the 1M proxy gain; golden baseline intentionally unchanged.

## Snapshot Contents

- `scripts/eval_mlx_checkpoint.py`
- `validation/eval_windowing.py`
- `tests/test_eval_windowing.py`
- `results/evaluation/20260320-flat-stream-sliding-window-confirmatory-16m.md`
