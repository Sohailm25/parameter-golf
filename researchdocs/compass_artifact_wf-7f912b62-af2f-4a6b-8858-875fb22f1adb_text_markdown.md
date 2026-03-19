# Winning Parameter Golf: the unconventional playbook

**The single highest-impact technique most competitors will miss is dynamic evaluation — continuing to train on evaluation data during inference — which is explicitly allowed by the rules and is the defining trick of the world's best text compressors.** Combined with mechanistic-interpretability-informed initialization, ternary quantization for massive parameter capacity, and hybrid neural+classical compression, a competitor can exploit under-explored intersections that the mainstream NanoGPT speedrun community has never needed. This report catalogs and assesses every unconventional angle, prioritized by expected BPB impact, feasibility within the 16MB/10-minute constraints, and how likely competitors are to overlook it.

## The competition landscape on day one

OpenAI's Parameter Golf launched March 18, 2026. The constraints are precise: **16,000,000 bytes** (decimal, not MiB) for the full artifact (code + compressed weights), **10 minutes training on 8×H100**, and **10 minutes evaluation on 8×H100**, minimizing bits-per-byte on the first 50,000 FineWeb documents. The official baseline — a 9-layer, 512-dim transformer with 1024-token BPE vocabulary, tied embeddings, and 4 KV heads — scores **1.2244 BPB**. An unlimited-compute (4-hour) run only reaches 1.2074, suggesting that architecture and evaluation strategy matter far more than brute-force training. One unverified PR claims **1.1833 BPB** via longer context, optimizer tuning, and sliding-window evaluation.

Early PRs cluster around predictable ideas: recursive weight sharing, looped transformers with LoRA adapters, depth recurrence with SwiGLU, and Muon optimizer ports from the NanoGPT speedrun. These are the obvious moves. The approaches below are not.

## Dynamic evaluation is the secret weapon from compression

The rules state: *"you aren't allowed to access any training data during evaluation, unless you pay for those bits in the <16MB limit."* Crucially, the evaluation data itself is not training data. The rules also list **"test-time training"** as an explicitly desired creative approach. This opens the door to dynamic evaluation — the technique that separates world-class compressors from static language models.

Dynamic evaluation, formalized by Krause et al. (2018), works by taking gradient steps on the evaluation data as you process it. For each segment of tokens, you compute the prediction, record the loss, backpropagate, update parameters, then move to the next segment. Because predictions are computed *before* updating on each token, this remains a valid probability model — no peeking. Fabrice Bellard's NNCP, the best single-pass neural text compressor, uses this exact technique: a Transformer-XL that trains from scratch during compression, achieving **~0.83 BPB on enwik9** (though with a much larger model). On smaller models, Krause et al. showed dynamic evaluation improved Transformer-XL from **0.99 to 0.94 bits/char on enwik8** — a 5% reduction for free.

For Parameter Golf, the implementation looks like this: process evaluation documents sequentially, updating model weights every 256–1024 tokens via a lightweight optimizer (SGD with momentum or Adam with aggressive decay toward original weights). Recent work ("Revisiting Dynamic Evaluation," 2024) shows that adapting **middle transformer layers only** is most effective, and LoRA-based adaptation reduces optimizer state memory. The compute cost is roughly 2× per token (forward + backward), but with 10 minutes on 8×H100 for a tiny model, this is comfortably feasible. The expected impact is **0.05–0.15 BPB improvement** — potentially the single largest gain available. The NanoGPT speedrun community already demonstrated a primitive version ("parameter nudging" using ~500 tokens of each validation document), proving the concept works in this exact codebase.

The key engineering subtlety: optimizer states don't count toward the 16MB limit because they're generated at eval time. You can maintain full Adam states for the adapted layers at zero artifact cost.

## Encoding known circuits into initial weights

From Anthropic's mathematical framework for transformer circuits, we know that a **zero-layer transformer is exactly a bigram model**: the product W_E^T · W_U directly encodes a bigram probability table. This gives us a precise recipe for data-dependent initialization that goes far beyond Xavier/Kaiming.

**Step 1: Output bias from byte unigram frequencies.** Compute the log-frequency of each byte value in FineWeb (takes seconds offline). Initialize the output bias vector to these log-frequencies. This moves initial loss from ~log(256) ≈ **5.55 bits** down to roughly **4.5 bits** (the entropy of the English byte distribution) — saving the model from wasting hundreds of early training steps learning what a trivially computable prior already knows. This is almost certainly not in any competitor's initial submission.

**Step 2: Bigram table in the embedding–unembedding product.** Compute the 256×256 byte-bigram log-probability matrix B from a FineWeb sample. Take its truncated SVD: B ≈ U·S·V^T at rank d_model. Set W_E = (S^{1/2}·V^T)^T and W_U = U·S^{1/2}. Now the model's "zero-layer" prediction (the direct path through the residual stream) already captures bigram statistics. For a 1024-token BPE vocabulary, the same principle applies to the token-bigram table.

**Step 3: T-Fixup initialization to eliminate warmup.** Scale initial attention and FFN weights by (9N)^{-1/4} where N is the number of layers. This theoretically-grounded technique (Huang et al., ICML 2020) allows removing both learning rate warmup AND LayerNorm — reclaiming those wasted early steps and reducing per-step compute. In a 10-minute training window, eliminating even 10% of warmup steps is meaningful. T-Fixup has been validated in Kaggle competitions (top-3 in Riiid challenge).

**Step 4: Hand-initialize a previous-token head.** From mechanistic interpretability research, we know induction heads require a "previous token head" in an early layer whose QK circuit attends to position i-1 and whose OV circuit copies the attended token's embedding to a dedicated residual stream subspace. With rotary positional embeddings, this means initializing Q and K weight subspaces so their dot product after RoPE rotation peaks at relative offset -1. The remaining heads stay randomly initialized and learn freely. This pre-seeds the model with the beginning of an induction circuit, which is the primary mechanism transformers use for in-context pattern matching.

**Feasibility**: Steps 1–3 are trivial (hours of engineering). Step 4 is moderate complexity and somewhat fragile — the benefit depends on whether the optimizer preserves or destroys the hand-designed circuit during training. No one has published results combining all four steps, making this a genuinely novel intersection of mechanistic interpretability and training optimization. Expected cumulative impact: **0.03–0.08 BPB** from faster convergence to a better early loss landscape.

## Ternary quantization unlocks 5× more parameters

The baseline stores int8 weights compressed with zlib. At 8 bits per weight, 16MB holds roughly **16M parameters**. BitNet b1.58 (Microsoft, 2024) trains ternary {-1, 0, +1} weights from scratch at **1.58 bits per weight**, meaning 16MB could store approximately **80M ternary weight values**. Even after accounting for scale factors, codebook overhead, and code, this is a **4–5× increase in raw parameter capacity**.

At the 3B+ parameter scale, BitNet b1.58 matches full-precision transformers. At the sub-100M scale relevant here, the quality gap is less well-characterized, but the parameter advantage is enormous. Ternary weights are also extraordinarily compressible: with only three distinct values, entropy coding can compress them well below the theoretical 1.58 bits. Combined with zlib (already in the baseline), the effective bits-per-weight could drop below 1.2, potentially fitting **100M+ parameters in 16MB**.

The training procedure uses quantization-aware training (QAT) throughout: maintain full-precision optimizer states and "shadow" weights, but quantize to ternary on every forward pass using absmean scaling. This is a drop-in replacement for nn.Linear and is fully compatible with Muon optimizer and the existing training loop. The engineering cost is moderate — BitLinear implementations exist — but the payoff in parameter capacity is transformative.

For competitors already exploring weight sharing (which most early PRs do), **ternary quantization is strictly better**: weight sharing reuses N layers' worth of parameters across 3N effective layers, but ternary quantization gives you 5× more unique parameters to distribute across those layers. The optimal strategy combines both: a modest 2–3× weight-sharing factor with ternary quantization, yielding effectively **160–240M parameter-operations** from a 16MB artifact.

## Hybrid neural + classical compression within 16MB

BPB is literally a compression metric. The best text compressors in the world — cmix (0.88 BPB on enwik9), NNCP (0.83 BPB) — are not pure neural models. They are ensembles of hundreds of statistical models mixed by a neural network. The lesson: **classical statistical models (PPM, n-gram tables) provide complementary signal that neural models miss**, especially at sequence boundaries and for rare patterns.

A concrete budget allocation within 16MB:

- **12–14MB**: Ternary-quantized neural transformer (~50–70M parameters)
- **1–2MB**: Compressed byte-trigram PPM table (~500K entries with pruning)
- **0.5–1MB**: Evaluation code including mixing logic and dynamic evaluation loop

At inference time, for each token position, compute both the neural model's probability distribution and the PPM model's distribution, then combine them via learned interpolation weights (or a simple geometric mean). The PPM model is strongest at sequence starts (where the neural model has no context) and for local repetitive patterns. The neural model dominates for long-range dependencies. This complementarity means the ensemble outperforms either component alone.

A PPM model achieving ~2.0 BPB on English text can be implemented in under 500KB. When mixed with a neural model at ~1.2 BPB, the interpolated ensemble should yield roughly **0.01–0.03 BPB improvement** on average, with larger gains on the first tokens of each document (where the neural model is weakest and the PPM model's static statistics are most valuable). Engineering effort is medium — PPM implementations are well-understood, and the mixing can be as simple as: `log_p_combined = α * log_p_neural + (1-α) * log_p_ppm`.

The deeper version of this idea: implement a full cmix-style context mixer where the neural transformer IS the mixing network, consuming features from multiple statistical models (byte bigram, trigram, match model, word-level model) as additional inputs. This is substantially more complex but would push the approach toward what the world's best compressors actually do.

## Monarch matrices compound the savings from quantization

Monarch matrices (Dao et al., ICML 2022) parameterize weight matrices as products of two block-diagonal matrices with permutations, inspired by the FFT butterfly structure. They use **25–50% of dense parameters** while matching quality: GPT-2 trained with Monarch matrices on OpenWebText achieves the same perplexity at 2× faster training. M2-BERT matches standard BERT with 25% fewer parameters and 9× faster inference.

The power move is **stacking Monarch with ternary quantization**. A dense 512×512 weight matrix requires 262K parameters. With Monarch factorization (50% savings) → 131K parameters. With ternary quantization (1.58 bits each) → ~26KB of storage. The same matrix stored naively at FP16 takes 512KB — a **20× total compression ratio** with well-characterized quality retention. Applied across all linear layers, this means the 16MB budget could parameterize a model equivalent to a **~320MB dense FP16 model** in effective capacity.

Monarch matrices map well to GPU tensor cores via batch matrix multiply, so training speed isn't sacrificed. The engineering complexity is moderate — open-source implementations exist from Hazy Research — but the compound savings with quantization represent an underexplored frontier. Most competitors will try either quantization or structured matrices, not both simultaneously.

Kronecker-factored layers (W = A ⊗ B) offer even more extreme compression — a 512×512 matrix factored as 32×32 ⊗ 16×16 reduces from 262K to 1,280 parameters — but with significant quality degradation that makes them impractical as a primary approach. They could be useful for specific auxiliary components (e.g., routing networks in MoE) where extreme compression is acceptable.

## Systems engineering: squeezing every token from 10 minutes

At the sub-16M parameter scale on 8×H100 GPUs, pure data parallelism is optimal, and the model is compute-bound on the language model head projection. Key throughput optimizations:

**Muon optimizer** is non-negotiable. Developed for the NanoGPT speedrun, it achieves **35% faster convergence** than AdamW with <1% FLOP overhead by orthogonalizing momentum via Newton-Schulz iteration. Every competitive speedrun submission since October 2024 uses it. Apply Muon to all 2D hidden-layer weights; use AdamW for embeddings and biases.

**1-cycle learning rate schedule with aggressive peak** enables "super-convergence" — up to 10× fewer iterations in favorable cases. Combined with T-Fixup initialization (eliminating warmup), the model trains at maximum learning rate from step 1. The NanoGPT speedrun recipe — linear warmup (5%), sustained high LR (65%), linear cooldown (30%) — is proven to produce a loss "plummet" during cooldown.

**Curriculum learning** accelerates convergence by **18–45%** according to recent benchmarks (Zhang et al., 2025, testing over 200 models). Pre-score FineWeb training data by difficulty (compression ratio, lexical diversity), sort ascending, present easy data first. This is allowed as offline preprocessing and costs nothing at training time.

**Throughput estimate**: For a 4–16M parameter model on 8×H100 with Muon + BF16 + torch.compile, expect **3–5M tokens/second**, yielding **1.8–3B tokens processed in 10 minutes**. This is vastly more data than the model can memorize, making the challenge purely about extracting generalizable patterns efficiently.

**Parallel model search** is a creative use of the 8-GPU budget: train 8 different architecture configurations (varying depth, width, vocabulary size, quantization scheme) for 7 minutes on 1 GPU each, evaluate on a held-out shard, then retrain the best configuration on all 8 GPUs for the remaining 3 minutes. This is essentially an efficient hyperparameter sweep that exploits the embarrassingly parallel nature of the exploration phase. ASHA-style successive halving can further improve this — start 8 models, kill the worst 4 at minute 3, worst 2 at minute 5, then consolidate compute on the survivor.

## Multi-model routing and FineWeb-specific exploitation

FineWeb is web text processed through Trafilatura extraction, fastText language filtering (English score >0.65), and MinHash deduplication across 96 CommonCrawl snapshots. The validation set contains **50,000 documents** spanning diverse web content: articles, lists, forums, technical documentation, boilerplate headers/footers, and occasional HTML remnants.

A **mixture of tiny specialized experts** could exploit this diversity. Within 16MB using ternary quantization:
- 1 expert (~15M params) for narrative prose
- 1 expert (~15M params) for structured/list-like content
- 1 expert (~15M params) for technical/code-adjacent text
- Shared attention layers (~15M params) + lightweight router (~100K params)

The router examines the first N bytes of each document to select expert weights for FFN layers. With ternary quantization, these 60M parameters fit comfortably in ~12MB, leaving room for embeddings, routing logic, PPM tables, and evaluation code.

**FineWeb-specific patterns to exploit**: CommonCrawl-derived text has distinctive statistical regularities — URL fragments, navigation menus, cookie consent boilerplate, date formats, author bylines, and HTML entities. A model that recognizes and efficiently compresses these patterns (which appear across many documents) gains BPB on tokens that a general-purpose model wastes capacity on. Pre-computing a dictionary of common web boilerplate phrases and encoding them in the artifact could help a PPM component predict these patterns with near-zero bits.

## The information-theoretic endgame

Stepping back, the Parameter Golf challenge is asking: **what is the best compressor you can build in 16MB?** The information-theoretic optimum is the Kolmogorov complexity of the FineWeb validation set divided by its byte length — uncomputable, but the goal is to approach it.

The Hutter Prize leaderboard shows the path: the best compressors use **context mixing** — combining predictions from many diverse models (n-gram, match, dictionary, neural) via a learned mixer. cmix uses 2,077 models mixed by an LSTM. For 16MB, we can't have 2,077 models, but we can have 3–5 complementary models (neural transformer, PPM, byte-bigram, match model) mixed by the neural model's own attention mechanism.

**Context Tree Weighting (CTW)** deserves special mention as a component: it's a Bayesian-optimal model for tree sources that can be implemented in ~50KB and provides a principled probability estimate for short contexts. As a feature fed into the neural mixer, CTW provides the Bayes-optimal "prior" that the neural model refines with its learned long-range representations.

Temperature calibration is the simplest compression-aware adjustment: models trained with cross-entropy tend toward overconfidence. A single learned temperature parameter T (fit on a held-out split during the last minute of training) applied at eval time — dividing all logits by T — reliably improves BPB by **0.005–0.02**. This is free and should be done regardless of other choices.

## Architecture choices where the intersections are richest

The least-explored territory lies at the intersection of multiple domains. Here are the compound strategies no single-domain expert would naturally discover:

**Mech-interp + compression**: Initialize the model to already implement bigram compression (via embedding product), then use dynamic evaluation to adapt induction circuits to each document's repetition patterns. The model starts as a competent bigram compressor and progressively specializes during evaluation.

**Systems engineering + novel architecture**: Use Monarch-factored ternary BitNet layers with ALBERT-style weight sharing. This triple-compression stack (structured matrices × ternary quantization × parameter sharing) could yield effective capacity equivalent to a **500M+ parameter dense model** within 16MB. No one in the NanoGPT community has tried this combination.

**Compression theory + test-time compute**: Implement a mini context-mixing framework where the neural model at eval time receives features from a PPM component and a byte-bigram component, processes them through a single additional attention layer, and outputs mixed probabilities — while simultaneously performing dynamic evaluation to adapt the mixing weights to each document. This mirrors what cmix does but with a neural backbone.

**Byte Latent Transformer + dynamic eval**: Meta's BLT architecture groups bytes into variable-length patches based on next-byte entropy — allocating more compute to unpredictable regions. Combined with dynamic evaluation, the model would adaptively allocate both architectural compute and learning updates to the hardest-to-predict tokens. BLT's dynamic patching also reduces sequence length (and thus attention cost), enabling longer effective contexts within the eval time budget.

## Feasibility matrix for all approaches

| Approach | BPB impact | Engineering effort | Overlooked? | Tried before? |
|----------|-----------|-------------------|------------|---------------|
| Dynamic evaluation at test time | 0.05–0.15 | Medium | Somewhat — listed in rules but few will implement | Yes (NNCP, Krause et al.) |
| Bigram table in embeddings | 0.03–0.05 | Low | Yes — novel synthesis from interp research | No — never published |
| Output bias from unigram frequencies | 0.02–0.03 | Trivial | Yes | Partially (known but rarely done for byte LMs) |
| T-Fixup (eliminate warmup) | 0.01–0.03 | Low | Moderate | Yes (Kaggle, NLP) |
| BitNet 1.58-bit QAT | 0.03–0.08 | Medium | Yes — not in NanoGPT ecosystem | Yes (Microsoft, but not at tiny scale) |
| Monarch matrices | 0.01–0.03 | Medium | Yes | Yes (GPT-2 scale, not for compression) |
| Hybrid neural + PPM | 0.01–0.03 | Medium | Yes — compression experts know this, ML competitors don't | Yes (cmix concept) |
| Muon optimizer | 0.02–0.05 | Low | No — widely known | Yes (NanoGPT speedrun) |
| Curriculum learning | 0.01–0.03 | Low | Moderate | Yes (multiple papers) |
| Parallel model search (8 configs) | 0.01–0.03 | Medium | Yes | Not in this exact setting |
| Checkpoint averaging (LAWA) | 0.005–0.01 | Low | No | Yes (NanoGPT speedrun) |
| Temperature calibration | 0.005–0.02 | Trivial | No | Yes (standard) |
| MoE with specialized experts | 0.01–0.04 | High | Moderate | Not at 16MB scale |
| Previous-token head initialization | 0.005–0.02 | Medium | Yes | No — never published |
| Activation engineering at eval | 0.00–0.01 | High | Yes | Not for BPB optimization |
| Hypernetworks for weight generation | 0.01–0.03 | High | Yes | Yes (HyperLSTM, but not for compression) |

## The optimal compound strategy

If forced to prescribe a single integrated approach, it would stack these layers:

**Architecture**: 2-layer prelude + 4-layer shared core (looped 2×) + 2-layer coda, Monarch-factored linear layers, ternary QAT, 1024-token vocabulary with FineWeb-optimized BPE. Store ~60M ternary parameters in ~12MB after entropy coding.

**Initialization**: Output bias from log-unigram frequencies. Embedding–unembedding product initialized to token-bigram SVD. T-Fixup scaling to eliminate warmup. One attention head initialized as a previous-token head.

**Training (10 min)**: Muon optimizer for hidden weights, AdamW for embeddings. 1-cycle LR with aggressive peak. Curriculum-ordered FineWeb data (easy → hard). Progressive context window warmup. Checkpoint averaging over final 20% of training.

**Evaluation (10 min)**: Dynamic evaluation with LoRA-style adaptation of middle layers every 512 tokens. Hybrid prediction combining neural logits with a small PPM model (~1MB) via learned interpolation. Temperature-calibrated output. Longest feasible context window with sliding-window attention.

**Expected BPB**: The baseline is 1.2244. Muon + architectural improvements alone likely reach ~1.18. Adding ternary quantization (more parameters) could push to ~1.14–1.16. Dynamic evaluation could further reduce to ~1.08–1.12. The hybrid PPM component and smart initialization provide incremental gains toward **~1.05–1.10 BPB** — which would be a substantial lead over competitors focused only on the standard NanoGPT tricks.

## Conclusion

The Parameter Golf challenge rewards the competitor who recognizes it as a **compression contest**, not a language modeling contest. The deepest BPB gains come from three directions most ML engineers won't pursue: dynamic evaluation (importing the key technique from the compression community), ternary quantization compounded with structured matrices (maximizing information capacity per byte of artifact), and mechanistic-interpretability-informed initialization (giving the model a free head start). The most powerful strategies combine domains — compression theory provides the evaluation framework, systems engineering provides the throughput, and interpretability research provides the initialization — creating compound advantages at intersections where no single expert naturally operates. The competition explicitly rewards this kind of creative synthesis, and the 10-minute eval window is an underutilized second compute budget that can deliver the largest single improvement through dynamic evaluation alone.
