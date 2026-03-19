# References

## Official Challenge Sources

- OpenAI Parameter Golf repo: `https://github.com/openai/parameter-golf`
- Official challenge README: `https://raw.githubusercontent.com/openai/parameter-golf/main/README.md`

## Competition Snapshot Sources Checked On 2026-03-19

- PR `#53`: `SP-4096` plus stride-64 sliding window, `1.1888` BPB
- PR `#61`: long-context train/eval with sliding window, `1.1793` BPB
- PR `#65`: mixed quantization plus sliding window, `1.1630` BPB
- PR `#77`: doc-isolated evaluation plus sliding window plus LoRA TTT, approximately `1.191` BPB
- PR `#78`: `sp8192` tokenizer, NorMuon, selective quantization, `1.186` BPB
- PR `#79`: depth recurrence local-first non-record exploration
- PR `#81`: depth recurrence plus SwiGLU plus int6 plus sliding window, non-record

## Related Tooling

- Karpathy `autoresearch`: `https://github.com/karpathy/autoresearch`
- `modded-nanogpt`: `https://github.com/KellerJordan/modded-nanogpt`

## Papers And Research Directions Worth Caching

- BitNet / ternary training
- QuEST / low-bit QAT
- Dynamic evaluation / test-time training for language models
- Neural weight entropy coding / entropy-aware quantization
- Long-context evaluation and sliding-window scoring
