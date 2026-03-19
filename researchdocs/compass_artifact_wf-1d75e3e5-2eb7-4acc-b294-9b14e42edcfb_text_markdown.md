# Winning strategies for OpenAI's Parameter Golf challenge

**The most impactful path to minimizing BPB within 16MB combines ternary quantization-aware training (QAT) with a byte-level tokenizer, depth recurrence, and test-time training at evaluation.** This strategy can pack ~95M effective parameters into the 16MB artifact—a 4× advantage over the int8 baseline's ~24M—while TTT at evaluation time adds a further 2–5% BPB reduction. The critical finding across all six research areas is that these techniques are multiplicatively composable: ternary QAT expands the parameter budget, depth recurrence converts those parameters into deeper effective networks, and TTT exploits the generous 10-minute evaluation window. Below is a detailed synthesis with concrete numbers and recommendations.

---

## Area 1: Depth recurrence yields compute, not memorization gains

Layer looping is the most parameter-efficient way to build depth, but the literature reveals a crucial caveat for BPB optimization. **Ouro/LoopLM (Oct 2025)** found that "reasoning skills benefit more from looping than memorization skills"—language modeling perplexity depends primarily on total parameter count, not effective depth. At a 1.4B parameter scale, their looped model matched 4B models on reasoning benchmarks but showed no perplexity advantage over non-looped baselines at equal parameters.

That said, looping still provides meaningful value for parameter golf through two mechanisms. First, it converts parameter budget into compute: a 10M-parameter model with 4 shared blocks looped 8× behaves like a 32-layer network during forward passes, extracting more value from the 10-minute training window. Second, with per-iteration adaptation, the quality gap narrows substantially. The **Relaxed Recursive Transformer (ICLR 2025)** achieved 22% error reduction using LoRA adapters per loop iteration, while **RingFormer (EMNLP 2025)** matched vanilla Transformers at 20% of parameters using input-dependent level signals with per-iteration LayerNorm.

The optimal configuration for 5–15M parameter models based on converging evidence: **2–4 unique transformer blocks, looped 4–8 times**, with per-iteration RMSNorm (nearly free) and either tiny LoRA adapters (rank 2–4, adding ~1–3% overhead) or learned depth embeddings. MoEUT's finding that **layer groups of G=2 outperform both G=1 and fully unshared** at the same parameter count is directly applicable. Input injection—re-adding the embedded input at each iteration—is critical to prevent representation collapse at high loop counts.

Training stability requires sandwich normalization (RMSNorm before both attention and FFN sublayers), gradient clipping at 1.0, and a recurrence curriculum starting with 2–4 loops and ramping up. **No published work combines Muon with depth recurrence**, but Muon's spectral norm control likely helps: the Newton-Schulz orthogonalization should produce well-conditioned gradient updates even when accumulated across multiple loop iterations. The 0.7% FLOP overhead of Muon's Newton-Schulz iteration is negligible. Backpropagation through all iterations is feasible for ≤8 loops; beyond that, truncated BPTT through the last k iterations is recommended.

---

## Area 2: Ternary QAT is the single highest-leverage technique

The compression arithmetic is decisive. At int8 with zlib, roughly **20–24M parameters** fit in 16MB. At ternary (1.58-bit) with zlib, the effective storage drops to approximately **1.2–1.5 bits per parameter**, yielding **86–112M parameters** in the same budget. With a byte-level tokenizer (vocab=256), the embedding table shrinks to ~200K parameters at int8, leaving nearly the entire 16MB for ternary transformer weights—up to **~95M parameters**. This is a **4× parameter advantage** over the int8 baseline.

**BitNet b1.58 Reloaded (DeLTA 2024)** confirmed that ternary QAT works for models as small as 6–48M parameters, though with a meaningful quality gap versus FP16 at these scales. The study introduced AbsMedian quantization (using median instead of mean for thresholds), which proved competitive or superior for small models. **QuEST (ICML 2025)** pushed the frontier further, demonstrating stable W4A4 training that is **Pareto-dominant over BF16**—their 4-bit models achieve lower loss at lower model size than full-precision baselines. QuEST's trust gradient estimator explicitly minimizes the error between quantized and true gradients, resolving STE instability below 4-bit.

For the competition, the key tradeoff is quality degradation versus parameter count advantage:

| Precision | Params in 16MB | Expected quality | Recommendation |
|-----------|---------------|-----------------|----------------|
| INT8 + zlib | ~24M | Baseline | Safe default |
| INT4 + zlib | ~53M | ~5–15% perplexity increase | Strong choice via QuEST |
| Ternary + zlib | ~95M (byte vocab) | ~20–40% perplexity increase | High-risk, high-reward |
| Mixed (int8 embed + ternary body) | ~50M | Moderate degradation | Best balance |

**Muon-trained models show enhanced quantization robustness.** Two 2025 studies confirmed that Muon's spectral norm constraint produces smoother weight distributions that degrade less under quantization. No direct study of Muon + ternary QAT exists, but the evidence strongly suggests compatibility—Muon's orthogonalized updates operate on the latent FP16 weights, while STE passes gradients through the ternary quantization function.

Critical implementation details: use standard STE (ICLR 2025 proved exotic gradient estimators are equivalent to STE after adjusting initialization); remove weight decay in the second half of training (BitNet's key trick—decay causes ternary weights to flip too often); keep embeddings at int8 minimum; and note that **overtrained models are more sensitive to quantization** (Kumar et al., ICLR 2025), which matters for the 10-minute training regime.

---

## Area 3: Test-time training offers ~0.03–0.06 BPB for free

TTT is explicitly encouraged by the Parameter Golf rules, and the 10-minute evaluation budget on 8×H100 is generous for a 16MB model. **The @samacqua approach (Jan 23, 2026)** demonstrated "parameter nudging" on modded-nanogpt: for each validation document, perform gradient updates using the first ~500 tokens with Adam, then evaluate on the remaining tokens, resetting parameters between documents.

Historical results on dynamic evaluation of transformers suggest **0.03–0.06 BPB improvement** (2–5% relative) is achievable. Krause et al. showed enwik8 improved from 0.99 to 0.94 bits/char (~5% relative), while WikiText-103 perplexity dropped from 18.3 to 16.4 (~10%). FineWeb's diverse web text—with significant per-document topic variation—is favorable for TTT since each document can meaningfully adapt the model.

The **TTT-E2E paper (Sun et al., Dec 2025)** provides the most practical recipe: adapt only MLP layers in the last quarter of blocks, using a dual MLP design (one static, one dynamic) to prevent catastrophic forgetting. Key hyperparameters from the literature: Adam optimizer with learning rate 1e-4 to 3e-4, chunk documents into ~512-token subsequences, and reset to original weights between documents.

Parallelization is trivial: distribute validation documents across 8 GPUs via data parallelism. Each GPU independently evaluates its document subset, then aggregate BPB scores. Memory overhead is ~3× model size for full TTT (a 16MB model needs ~48MB of optimizer states—well within H100's 80GB), dropping to ~0.5× with selective layer adaptation.

**TTT works with quantized base models** via the QLoRA pattern: keep the base model frozen in its quantized format, upcast to FP16 for the backward pass, and apply LoRA-style adapters in full precision. The memory overhead remains tiny. Key failure mode to avoid: updating attention layers or normalization layers causes instability (TTT-E2E finding). Stick to MLP layers only.

---

## Area 4: The sp1024 tokenizer is near-optimal for 16MB

The BPB formula—`BPB = avg_loss_per_token × tokens_per_byte / ln(2)`—creates a fundamental tradeoff between vocabulary size, embedding cost, and prediction difficulty. The Parameter Golf baseline uses a SentencePiece 1024-token vocabulary trained on FineWeb, which is a strong default.

At 16MB with tied embeddings and int8 storage, the embedding cost scales linearly:

| Vocab | Dim | Embed params (tied) | % of 16M budget | Tokens/byte (English) |
|-------|-----|--------------------|-----------------|-----------------------|
| 256 | 768 | 197K | 1.2% | ~1.0 |
| 1024 | 768 | 786K | 4.9% | ~0.5 |
| 2048 | 768 | 1.57M | 9.8% | ~0.35 |
| 4096 | 768 | 3.15M | 19.7% | ~0.28 |

**Vocab sizes above 2048 consume a ruinous fraction of the parameter budget at this scale.** The 1024 default hits a sweet spot: only 5% of budget with tied embeddings, while halving the sequence length relative to byte-level. However, if using ternary QAT (which expands the effective parameter budget to ~95M), the calculus shifts: byte-level tokenization (vocab=256) costs only 197K parameters while freeing the maximum budget for the transformer body. The 5× longer sequences are offset by having 4× more transformer parameters.

**TokenMonster** demonstrated that vocabulary efficiency can be dramatically improved—achieving the same compression ratio as GPT-2's 50K vocabulary with only ~25K tokens—but this was optimized for larger vocab ranges. At 1024 tokens, the gains from tokenizer optimization are smaller. **LZ-aware BPE (2025)** achieves 11.5% better compression than standard BPE at vocab 256–1024 by greedily minimizing gzip-compressed length during merge selection, but at higher computational cost.

Tied embeddings are mandatory at this scale—they save V×D parameters while also improving quality (acting as a regularizer). The modded-nanogpt community found that only **9,483 of GPT-2's 50,304 tokens** cover 99.999% of FineWeb data, confirming that a domain-specific 1024-token vocabulary wastes nothing.

---

## Area 5: Muon and FlexAttention are the training throughput pillars

The 10-minute training constraint demands extracting maximum tokens from 8×H100 GPUs. The modded-nanogpt community has driven the GPT-2 124M training time from 45 minutes to under 90 seconds, providing a rich playbook.

**Muon optimizer** delivers a **1.35× speedup over AdamW** through superior sample efficiency (not raw throughput). Its Newton-Schulz orthogonalization costs only 0.7% extra FLOPs at 124M scale. Optimal settings: lr=0.02 for hidden weights, momentum=0.95 with Nesterov, 5 Newton-Schulz steps with coefficients (3.4445, -4.7750, 2.0315), weight decay 0.01, trapezoidal LR schedule. Apply Muon to all 2D parameters (Q, K, V, O projections and MLP layers separately), and AdamW (lr=3e-4, betas=(0.9, 0.95)) to embeddings, LM head, and scalar parameters.

**FlexAttention with sliding window warmup** enabled 10× longer context windows. The window schedule—starting at 128/384 (short/long) and ramping to 768/2560 via YaRN extensions—provides both speed (smaller windows are cheaper) and a curriculum effect. This was ranked the #2 ML improvement. However, each window size change triggers torch.compile recompilation, adding ~7 minutes of one-time cost. For parameter golf, pre-compilation or cached kernels are essential.

**FP8 training provides marginal gains for small models.** Keller Jordan explicitly found that 768×768 matrices are too small to benefit from FP8 matmuls. FP8 is used only for the LM head (larger vocab dimension) in modded-nanogpt. For parameter golf with a 1024-token vocabulary, even the LM head may not benefit. **torch.compile is mandatory**—it provides ~40% throughput improvement by fusing operations and eliminating Python overhead.

For multi-GPU strategy, **custom DDP with manual gradient synchronization** outperforms standard PyTorch DDP and FSDP for small models. The key optimization: parameters reshaped to `[d_model, 4*d_model]` for efficient reduce_scatter across 8 GPUs, with Muon's Newton-Schulz iteration performed locally on each GPU's parameter shard. Sequence length warmup (linear increase over first 30% of training) enables 8× larger batch sizes and reduces wall-clock time by up to 3.7×.

---

## Area 6: Proven architecture components for the parameter budget

The modded-nanogpt community has battle-tested dozens of architectural innovations at the 124M scale. For parameter golf, the following have the best impact-to-cost ratio:

**ReLU² is the clear activation winner** for parameter-constrained models. It requires only 2 weight matrices versus SwiGLU's 3—a 33% FFN parameter savings—while achieving 80–85% neuron sparsity (enabling faster inference). ReLU² is equivalent to ReGLU when U and V weight matrices are identical, giving GLU-like gating benefits for free.

**QK-Norm with learnable gain** prevents attention logit growth from saturating softmax, enables higher learning rates, and costs only 2 × num_heads × head_dim parameters. Combined with logit softcapping at t=30 (`30 * tanh(logits/30)`), this achieves 3% lower perplexity than bf16 baseline at 830M scale. Both are zero-cost in parameters and negligible in compute.

**U-Net skip connections** from modded-nanogpt connect early layers to late layers (layer 2→11, 4→10, 6→9) with learned sigmoid gates initialized at -1.5. Analysis shows middle layers contribute relatively little to output—the skip connections let the model bypass them. Combined with **x0-mixin** (adding input embeddings to every layer's residual stream via learned weights), these provide shorter gradient paths and act as gradient-level data augmentation.

**The smear module** (token peeking 1 position back) replaces an expensive attention head pattern with a simple gated shift operation: `x[t] += λ * sigmoid(gate(x[t])) * x[t-1]`. It costs ~12 parameters and provides ~1.5s improvement at 124M scale. **Value embeddings** (Zhou et al., ACL 2025) provide direct token-level information to attention value vectors, achieving equivalent performance with 16% fewer parameters. However, at 5×vocab×dim parameters, they may be too expensive for the 16MB budget unless vocabulary is small.

**LAWA (checkpoint averaging)** improves validation loss by 0.046–0.069 at GPT-2 scales (1.5–2.3% relative) at zero parameter cost—just average the k most recent checkpoints. Models trained with higher learning rates benefit more. For a 10-minute training run, averaging the last 3–5 checkpoints taken at regular intervals is practically free and recommended.

**YaRN enables training at shorter context and evaluating at longer context**, which is directly applicable to parameter golf. Dynamic-YaRN allows >2× context extension without any fine-tuning. This means training at shorter (faster) sequences and evaluating with the full window budget.

---

## Concrete integrated strategy

Based on the synthesis across all six areas, here is a recommended configuration ranked by expected BPB impact:

**Tier 1 (highest impact, implement first):**
- Ternary or INT4 QAT via QuEST with byte-level or sp1024 tokenizer, expanding effective parameters to 50–95M within 16MB
- Test-time training during evaluation: Adam on MLP layers, lr=2e-4, reset per document, ~500-token warmup per document
- Muon optimizer with trapezoidal LR schedule, lr=0.02 for hidden weights
- Tied embeddings, ReLU² activation, QK-Norm + softcap at 30

**Tier 2 (significant impact, implement second):**
- Depth recurrence: 4 unique blocks × 4–8 loops with per-iteration RMSNorm and rank-2 LoRA
- FlexAttention sliding window with YaRN warmup schedule
- Sequence length warmup over first 30% of training
- U-Net skip connections + x0-mixin

**Tier 3 (marginal but free, polish phase):**
- LAWA checkpoint averaging (last 5 checkpoints)
- Smear module (previous token peek)
- torch.compile for all operations
- Custom DDP with parameter reshaping for efficient reduce_scatter

The expected BPB progression: **baseline ~1.22 → ternary QAT parameter expansion ~1.15 → architecture optimization ~1.10 → TTT ~1.05–1.07**. The aggressive strategy (ternary + byte-level + TTT) carries higher risk from QAT quality degradation at small scales, but the 4× parameter advantage creates headroom that conservative int8 approaches cannot match.
