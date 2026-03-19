# Challenge Review - 2026-03-19

## Official Constraints Confirmed

From the official Parameter Golf README:

- Objective: minimize `val_bpb` on the fixed FineWeb validation set
- Artifact cap: `16,000,000` bytes total, decimal, including code and compressed weights
- Training budget: `10` minutes on `8xH100`
- Evaluation budget: separate `10` minutes on `8xH100`
- Tokenizer changes are allowed but scrutinized closely
- New records must improve by at least `0.005` nats with `p < 0.01`

## Baseline State

- Official leaderboard baseline: `1.2244` BPB
- Official notable non-record: `4-hour baseline` at `1.2074` BPB

That gap is meaningful but not huge. It suggests the contest is not just "train longer"; evaluation, compression, and architecture all matter.

## Public Frontier Snapshot On 2026-03-19

Representative open PRs:

- `#53`: `SP-4096` tokenizer plus stride-64 sliding window, `1.1888` BPB
- `#61`: long-context train/eval with sliding window, approximately `1.1793` BPB
- `#65`: mixed quantization plus sliding window, `1.1630` BPB
- `#77`: document-isolated eval plus sliding window plus LoRA TTT, about `1.191`; the public ablation says most of that gain comes from document isolation and stride, with TTT adding a smaller extra step
- `#78`: `sp8192` tokenizer, NorMuon, selective quantization, `1.186`
- `#79`: depth recurrence local-first non-record exploration
- `#81`: depth recurrence plus int6 plus sliding window, non-record
- `#84`: mirrored-recurrence MLX non-record submission for local Apple Silicon experimentation
- `#85`: autoresearch-style local sweep pipeline plus sliding-window eval, pending final quantized score
- `#64`: extremely strong `1.0149` BPB record claim that explicitly includes validation-only training; relevant to the open-rules frontier, but not safe to treat as the default spirit-first lane

Second-pass additions and rule-edge signals:

- `#74` and `#75`: `seq4096` plus fp16 tied-embedding export and a stronger sliding-window variant
- `#76`: WIP stacking wider MLP, int6, fp16 tied embedding passthrough, and sliding-window eval
- `#80`: local sweep tooling and fast local dataset generation for rule-safe iteration
- `#85`: another reminder that better local sweep tooling matters, but its current test plan also uses `TRAIN_ON_VAL=1`, which strengthens the need to keep spirit-first and open-rules lanes distinct
- issue `#67`: explicit community concern that current rules incentivize training on the public validation set
- issue `#43`: tokenizer files do not currently count toward artifact size, which changes the practical vocabulary tradeoff

## What The Frontier Seems To Be Saying

1. Evaluation is not a footnote. Sliding-window scoring and document handling change outcomes a lot.
2. TTT is real, but the current public evidence says it should be measured after document isolation and sliding-window accounting, not instead of them.
3. Vocabulary is an active lever. `1024` is not obviously the best fixed point.
4. Selective precision is already practical. Int6 or mixed precision is not just theory.
5. Recurrence is promising but not yet clearly dominant relative to tokenizer and eval gains.
6. `autoresearch`-style tooling is already entering the ecosystem, but as tooling and search infrastructure, not as the main scientific claim.
7. Tokenizer accounting is philosophically unsettled because tokenizer artifacts are not currently counted.

## Local Development Implications

For this M4 MacBook repo:

- use local runs for directionality and tooling
- do not confuse local absolute BPB with official 8xH100 quality
- prioritize experiments where local rank-order signal is likely to survive
- be especially careful with evaluation changes because they can dominate scores fast
- do not treat `document-reset TTT` and `cross-document dynamic evaluation` as the same thing when planning or reporting experiments

## Working Repo Conclusion

The first strong lane for this repo should probably not be "invent the most exotic model." It should be:

1. trustworthy baseline and proxy harness
2. optimizer and schedule lane
3. evaluation-window and document-isolation lane
4. document-reset TTT sanity lane
5. tokenizer or selective-quantization lane before deeper recurrence bets
