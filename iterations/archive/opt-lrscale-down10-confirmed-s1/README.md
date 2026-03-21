# opt-lrscale-down10-confirmed-s1

## Metadata

- Parent: `baseline-sp1024-mlx-confirmed-s1`
- Lane: `optimizer_sweeps`
- Status: `pass`
- Metric: `val_bpb=1.96768084`
- Atomic change: scale the tied/embed/matrix/scalar learning-rate tuple down 10x to 0.045/0.036/0.036 on the frozen shard-000001 sp1024 MLX baseline path
- Notes: The shard-000001 confirmatory run improved the promoted baseline by 0.04168550 BPB and the current 16M stride-64 accounting reference preserved a 0.04225360 BPB gain versus the baseline checkpoint.

## Snapshot Contents

- `train_gpt_mlx.py`
- `scripts/eval_mlx_checkpoint.py`
- `validation/eval_windowing.py`
- `results/optimizer_sweeps/20260320-lr-scale-down10-confirmatory.md`
