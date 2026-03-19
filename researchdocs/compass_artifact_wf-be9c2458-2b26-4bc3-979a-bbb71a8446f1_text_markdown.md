# Compression math for Parameter Golf: fitting maximum quality into 16 MB

**The dominant strategy for OpenAI's Parameter Golf challenge is not int8 + zlib.** Quantized neural network weights carry far less entropy than their bit-width implies — int4 weights average just **1.1–1.5 bits** of Shannon entropy, and int8 weights average **4.5–5.5 bits** — meaning custom entropy coding can unlock 2–4× more parameters than zlib within the same 16 MB budget. The challenge permits any compression scheme, and the gap between zlib and optimal entropy coding is enormous: **~17 M parameters at int8 + zlib versus ~90 M parameters at int4 + Huffman/ANS.** Combined with quantization-aware training results showing int4 QAT is Pareto-dominant over BF16 even at 30 M parameters, this creates a clear path to dramatically beating the 1.2244 BPB baseline.

## zlib captures barely half the available compression on quantized weights

The core problem with zlib (DEFLATE) for neural network weights is structural. DEFLATE combines LZ77 dictionary matching with Huffman coding, but neural network weights have **zero spatial locality** — neighboring parameters encode unrelated features, so LZ77 finds essentially no byte-level repetitions. Only the Huffman component provides benefit, and it operates at byte granularity, which is suboptimal for sub-byte formats. ZipNN's research confirmed this directly: on GPTQ/AWQ quantized models, zlib achieves only **85–91% of original size** (9–15% savings), while GGUF models that already use block quantization show **~0% additional compression**.

The empirical entropy measurements tell a striking story. EntroLLM (2025) measured the effective information content of quantized weight tensors using Huffman coding:

| Format | Stored bits/weight | Empirical entropy | zlib achieves | Huffman achieves | ANS achieves |
|--------|-------------------|-------------------|---------------|-----------------|--------------|
| INT8 | 8.0 | ~4.5–5.5 bits | ~6.8–7.3 bits | **5.58 bits** | ~4.5 bits |
| INT4 (packed) | 4.0 | ~1.1–1.5 bits | ~3.4–4.0 bits | **1.39 bits** | ~1.1–1.5 bits |
| Ternary (uniform) | 1.585 | 1.25–1.585 bits | ~1.2–2.0 bits | ~1.19 bits | ~1.25 bits |
| Binary | 1.0 | ~0.95–1.0 bits | ~1.0 bits | ~1.0 bits | ~0.95 bits |

The key finding from ECQ's rANS measurements across multiple models: **Qwen2.5-1.5B at int4 has just 1.12 bits of entropy, GPT-2 137M has 1.17 bits, and SmolLM-135M has 1.54 bits.** The bell-curved distribution of quantized weights — heavily concentrated near zero — creates massive compressibility that zlib barely exploits. At int4, Huffman coding achieves **1.39 bits effective** (a 65% reduction over raw 4-bit storage), while zlib captures at best 10–15% savings.

For ternary weights, the distribution matters enormously. BitNet b1.58 models produce roughly **66% zeros** with 17% each for ±1, yielding an entropy of approximately **1.25 bits** — well below the theoretical maximum of log₂(3) ≈ 1.585 bits. Training methods that produce 85% zeros (as in structured sparse ternary networks) push entropy down to **~0.77 bits per weight**. Since ternary values stored as int8 only occupy 3 of 256 possible byte values, zlib's Huffman actually performs reasonably well here — an estimated **0.12–0.25 bytes/param** — because the byte-level distribution is extremely skewed.

## How many parameters actually fit in 16 MB under each strategy

The 16,000,000-byte budget (decimal, not MiB) must cover both compressed weights and code. Assuming ~15,000 bytes for code and overhead leaves roughly **15.985 MB for weights**. The achievable parameter counts differ dramatically by strategy:

| Strategy | Effective bytes/param | Parameters in 16 MB | Quality method |
|----------|----------------------|---------------------|----------------|
| INT8 + zlib (baseline) | ~0.90–0.95 | **16.8–17.8 M** | PTQ |
| INT8 + Huffman (EntroLLM) | ~0.70 | **22.8 M** | PTQ |
| INT8 + rANS | ~0.56 | **28.5 M** | PTQ |
| INT4 packed + zlib | ~0.45–0.50 | **32–35.5 M** | PTQ/QAT |
| INT4 + Huffman | ~0.174 | **91.9 M** | QAT |
| INT4 + rANS | ~0.14–0.19 | **84–114 M** | QAT |
| Ternary 2-bit packed + zlib | ~0.15–0.20 | **80–107 M** | QAT only |
| Ternary base-3 (TQ1_0) | ~0.198 | **80.7 M** | QAT only |
| Ternary + ANS (66% sparse) | ~0.156 | **~102 M** | QAT only |
| Binary bit-packed | ~0.125 | **~128 M** | QAT only |

These numbers exclude scale factor overhead, which ranges from negligible (per-tensor: <0.001 bytes/param) to moderate (per-group with group_size=64: 0.03 bytes/param). For a 20 M parameter model with per-row scaling, scale overhead is roughly **0.4%** of total size. For group quantization with group_size=128, it rises to about **5.7%**. Double quantization (à la QLoRA) can reduce group-scale overhead from 0.5 to **0.127 bits/param**.

The headline result: **int4 + entropy coding fits 5–6× more parameters than the int8 + zlib baseline.** Even the simpler int4 + Huffman approach (EntroLLM-style) achieves ~92 M parameters — enough to fit a model larger than GPT-2 124M into 16 MB.

## Quantization quality at 5–20 M parameters: QAT changes everything

The critical question is whether cramming more parameters at lower precision produces better models than fewer parameters at higher precision. The evidence strongly favors more parameters with QAT, but the picture is nuanced.

**Post-training quantization degrades rapidly at small scale.** The Scaling Laws for Precision paper (Kumar et al., ICLR 2025) provides the most rigorous measurements. For a 30 M parameter model, the validated scaling law is:

```
δ_PTQ(N, D, P_post) = 0.0598 × (D^0.507 / N^0.344) × e^(-P_post / 0.591)
```

At 30 M parameters with Chinchilla-level training (D/N ≈ 50), INT4 PTQ adds ~0.01–0.05 to validation loss, but with heavy overtraining (D/N ≈ 500), the degradation balloons to **0.1–0.3**. INT3 PTQ at high D/N ratios can cause loss to *increase* with more training data — a catastrophic failure mode. INT8 PTQ remains safe at all scales, adding less than 0.02 loss even for 30 M models.

**Quantization-aware training fundamentally changes the calculus.** QuEST (ICML 2025) demonstrated that W4A4 QAT is **Pareto-dominant over BF16 at every scale tested, including 30 M parameters**. At equivalent memory budgets on C4 validation:

- BF16 30 M model: loss ≈ 3.6–3.8
- QuEST W4A4 ~100 M model (same memory): loss ≈ **3.3–3.4**
- QuEST W2A2 ~200 M model (same memory): loss ≈ 3.4–3.5

The mechanism is straightforward: QAT lets the optimizer adapt to quantization noise during training, and the additional parameters more than compensate for reduced per-parameter expressiveness. QuEST's key innovations — Hadamard normalization for better distribution fitting and a "trust gradient estimator" that masks updates for badly-quantized weights — make this practical.

**Ternary QAT (BitNet b1.58 style) has a measurable capacity tax at small scale.** The BitNet b1.58 Reloaded paper studied Mistral-like models from 6 M to 48 M parameters and found a **constant offset** between 1.58-bit and 16-bit loss across all tested sizes. The follow-up "When are 1.58 bits enough?" paper quantified this precisely: **a ternary model needs approximately 2× the hidden dimension (4× the linear-layer parameters) to match a 16-bit model's quality.** At 3B+ parameters, the gap closes and ternary matches full precision at the same parameter count.

For the Parameter Golf calculation, this means a 100 M ternary model (fitting in 16 MB with entropy coding) would perform roughly like a **25–50 M FP16 model** — still substantially larger than the ~17 M int8 + zlib baseline, but not the full 6× improvement the raw parameter count might suggest. The Scaling Laws for Precision paper provides the effective parameter formula:

```
N_eff = N × (1 - e^(-P_w/2.67)) × (1 - e^(-P_a/2.21)) × (1 - e^(-P_kv/0.96))
```

At 1.58-bit weights with 8-bit activations, the weight efficiency factor is (1 - e^(-1.58/2.67)) ≈ **0.45**, meaning each ternary parameter is worth about 45% of a full-precision parameter.

## The Pareto frontier favors int4 QAT with entropy coding

Combining the compression arithmetic with quality scaling laws reveals the optimal strategy. The key tradeoff is that lower precision gives more parameters but each parameter is less effective:

| Strategy | Params in 16 MB | N_eff/N ratio | Effective params | Relative quality |
|----------|----------------|---------------|-----------------|-----------------|
| INT8 + zlib (baseline) | ~17 M | ~0.95 | ~16 M | Baseline |
| INT8 + ANS | ~28 M | ~0.95 | ~27 M | Better |
| INT4 QAT + Huffman | ~92 M | ~0.78 | ~72 M | **Much better** |
| INT4 QAT + ANS | ~100 M | ~0.78 | ~78 M | **Much better** |
| Ternary QAT + ANS | ~102 M | ~0.45 | ~46 M | Better |
| Binary QAT | ~128 M | ~0.25 | ~32 M | Comparable |

**INT4 QAT + entropy coding emerges as the clear winner**, delivering approximately **4.5× more effective parameters** than the baseline. The 0.78 efficiency factor for int4 weights is mild enough that the 5–6× parameter advantage dominates. Ternary's 0.45 efficiency factor means it needs ~2.2× more raw parameters to match int4's effective capacity — but since it only provides ~1.1× more parameters in practice (102 M vs 92 M), it loses to int4 on the Pareto frontier. Binary is even worse: the extreme capacity penalty (0.25 efficiency) outweighs the parameter advantage.

This analysis aligns with QuEST's experimental finding and the Scaling Laws for Precision paper's conclusion that **"16-bit has many unnecessary bits, and 4-bit requires increasing the model size disproportionately (>4×) to maintain loss scaling"** — but at 4-bit with QAT, the required increase is only ~1.3×, while compression delivers 5×.

## Practical serialization: how to implement sub-byte packing

The implementation landscape for sub-byte quantization is mature. Three approaches dominate in practice:

**For ternary weights**, llama.cpp's TQ1_0 format uses base-3 encoding: 5 ternary values pack into one byte (3⁵ = 243 < 256), achieving **1.69 bits per weight** at 99.06% information-theoretic efficiency. BitNet's I2_S format uses simpler 2-bit encoding (4 values per byte, 2.0 bpw) for faster SIMD unpacking. The 2-bit approach wastes 21% of space but offers better hardware alignment. Both have AVX2 and ARM NEON implementations.

**For int4 weights**, GPTQ packs 8 values into one int32, with per-group FP16 scales at group_size=128 adding 0.25 bits/param overhead (total ~4.25 bpw). bitsandbytes uses NF4 (non-uniform 16-level quantization optimized for normal distributions) with block_size=64 and double quantization that reduces scale overhead to **0.127 bits/param** (total ~4.13 bpw).

**Scale factor overhead at small model sizes is negligible for per-tensor and per-row granularity.** A 20 M parameter model with ~100 weight matrices and per-row scaling needs only ~20 KB for scales — under 0.4% of the weight budget. Group quantization with group_size=128 adds ~305 KB (5.7%), which is noticeable but manageable. The hierarchical approach from llama.cpp K-quants — quantizing sub-block scales to 4–6 bits with a single FP16 super-scale per 256-element block — effectively minimizes this overhead.

For entropy coding implementation, rANS (range variant of Asymmetric Numeral Systems) is the most practical choice. It achieves near-Shannon-entropy compression, handles fractional bits naturally, is GPU-friendly (used in NVIDIA nvCOMP), and implementations exist in ECQ and EntQuant. The key advantage over Huffman is that ANS can represent symbols at fractional bit costs — critical when int4 weights have 1.1–1.5 bits of entropy, which Huffman must round up to integer codeword lengths.

## Beyond the baseline: compression alternatives and what the rules allow

Parameter Golf explicitly permits **any compression scheme**. The baseline uses `zlib.compress(quant_raw, level=9)`, but the README encourages "low precision, QAT, bitnets, novel tokenizers" and other creative approaches. The only constraints are the 16,000,000-byte total artifact size, 10-minute training on 8×H100s, and self-contained reproducibility (no network calls or external downloads during evaluation).

The compression alternatives rank as follows for neural network weights:

- **zstd** offers marginal improvement over zlib (~0–5% better on weights) because both rely on LZ77 matching that finds nothing useful. ZipNN found Huffman outperforms zstd for weight exponents in most cases, with zstd's FSE encoder providing only 0–2% better compression at significant speed cost.
- **Custom Huffman** (EntroLLM-style) provides **30% savings on int8 weights and 65% savings on int4 weights**, far exceeding generic compressors. Implementation is straightforward and inference-time decompression adds minimal overhead.
- **rANS/tANS** approaches Shannon entropy, achieving the theoretical best compression. ECQ demonstrates 3.58× additional compression on 4-bit Qwen2.5-1.5B weights. The decompression kernel can run on GPU with hierarchical lookup tables (as in DFloat11).
- **EntQuant's approach** (Float8 → ~2 effective bits via ANS) offers an interesting middle ground: Float8 precision is much gentler on model quality than int4, while still achieving ~2 bpw after entropy coding — roughly matching int4's compressed density.

An additional architectural lever exists: **depth recurrence** (reusing the same transformer block N times) effectively multiplies parameter efficiency. A 10 M parameter model with 3× depth recurrence behaves like a ~25–30 M parameter model in expressiveness while storing only 10 M parameters. Combined with int4 QAT and entropy coding, this could push effective model capacity past 200 M equivalent parameters within 16 MB.

## Conclusion

The quantitative analysis points to a clear hierarchy: **int4 QAT + rANS entropy coding** maximizes effective model quality per compressed byte, fitting ~72 M effective parameters in 16 MB — a **4.5× improvement** over the int8 + zlib baseline's ~16 M effective parameters. The three key insights driving this conclusion are: (1) zlib wastes its LZ77 pass on spatially uncorrelated weights, leaving 40–60% of the entropy gap on the table compared to purpose-built entropy coding; (2) quantized weight distributions are dramatically more compressible than their bit-width suggests, with int4 weights carrying just 1.1–1.5 bits of true information; and (3) quantization-aware training at int4 precision is Pareto-dominant over full precision even at the 30 M parameter scale, making the quality-per-bit tradeoff decisively favorable.

The remaining open question is whether architectural innovations — depth recurrence, aggressive parameter tying, or mixture-of-experts — can further multiply the effective capacity within the budget. The Parameter Golf challenge launched only yesterday, and no community submissions have yet tested these strategies empirically. The theoretical analysis strongly suggests that the winning approach will combine int4 (or possibly ternary) QAT, custom entropy coding, and parameter-efficient architecture design to push well beyond the 1.2244 BPB baseline toward the 1.2074 BPB that the unlimited-compute 4-hour baseline achieved.
