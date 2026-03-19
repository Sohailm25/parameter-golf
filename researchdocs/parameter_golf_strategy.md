# Parameter Golf: Competitive Submission Strategy

## Challenge Anatomy

**Objective:** Minimize bits-per-byte (BPB) on FineWeb validation set.
**Hard Constraints:**
- 16,000,000 bytes total artifact (code + int8-zlib compressed weights)
- 10 minutes wall-clock on 8×H100
- No network calls or external data during eval
- Tokenizer-agnostic: scored on BPB, not token-level loss
- Must beat current SOTA by ≥0.005 nats with p < 0.01

**Current Leaderboard (as of March 19, 2026):**

| Entry | BPB | Notes |
|-------|-----|-------|
| Naive Baseline | 1.2244 | 9L, 512dim, 1024vocab, tied embed, post-quant |
| 4-Hour Baseline (non-record) | 1.2074 | Same arch, 4hrs compute |

The gap between 10min and 4hr is only ~0.017 BPB — meaning the baseline architecture is already reasonably saturated on compute. **The wins are in architecture, compression, and evaluation**, not just more training steps.

---

## Constraint Decomposition

### The 16MB Budget

The baseline uses ~15.86MB. Breakdown:
- ~4.2M parameters (9 layers × 512dim with 2x MLP, GQA 8/4 heads)
- Tied embeddings (1024 vocab × 512 = 524K params shared)
- int8 quantization + zlib ≈ ~1 byte/param effective
- Code: ~47KB

**Key insight:** 16MB ≈ 16M bytes. With int8+zlib, each parameter costs roughly 0.9–1.0 bytes after compression. So we have a budget of roughly **16M effective parameters** if we use int8+zlib, or far more if we can use lower-bit representations.

### The 10-Minute Budget

On 8×H100 at ~43ms/step with 524K tokens/step, the baseline processes ~7.2B tokens in 13,780 steps before hitting the wall-clock cap. That's **~1.7 epochs** over the 8B token dataset (80 shards).

### The BPB Metric

BPB = (cross-entropy in bits) × (tokens per byte). A smaller vocab means more tokens per byte but potentially lower per-token loss. This creates a **tokenizer optimization surface** that the baseline hasn't explored.

---

## Strategy Pillars (Ranked by Expected Impact)

### 1. Depth Recurrence / Layer Looping (HIGH IMPACT — Primary Architecture Change)

**The core idea:** Instead of 9 unique layers, use 3-4 unique layers looped 3-4× each. This cuts parameter count by ~50-60% while maintaining or increasing effective depth.

**Why this is the #1 lever for Parameter Golf:**
- The challenge is L(N) optimization — best loss for fixed parameter count
- Looping gives you 2-3× effective depth for the same parameter budget
- With freed parameters, increase model width (512 → 640-768) or add more KV heads
- RingFormer-style per-iteration LoRA signals (tiny overhead) restore per-depth adaptability
- The baseline already has skip connections (encoder-decoder structure) that map naturally to a looped architecture

**Implementation sketch:**
```
# 4 unique blocks, looped 3× each = 12 effective layers
# With LoRA-style depth signals (rank 4-8)
for loop_iter in range(num_loops):
    depth_signal = depth_lora[loop_iter](x)  # Low-rank adaptation
    for block in shared_blocks:
        x = block(x + depth_signal, x0)
```

**Parameter savings:** 9 unique blocks → 4 shared blocks saves ~55% of transformer parameters. Reinvest in width: 512 → 700+ dim fits in same budget with better representational capacity.

**Risk:** Training instability with deep looping. Mitigation: input injection (x0 at each loop), gradient checkpointing, careful warmup.

### 2. Aggressive Quantization-Aware Training (HIGH IMPACT — Compression)

**The current approach:** Train in bf16/fp32, post-training quantize to int8+zlib.
**The opportunity:** Train with QAT so the model *expects* low-precision, then serialize at 4-bit or even 2-bit.

**Tiered approach:**
1. **4-bit QAT (conservative):** Each param costs ~0.5 bytes + scales. Budget doubles to ~28-30M effective parameters. Well-studied, reliable.
2. **2-bit / Ternary QAT (aggressive):** BitNet b1.58 style — weights ∈ {-1, 0, +1}. Each param costs ~0.2 bytes. Budget explodes to ~60M+ effective parameters. Combined with looping, this could yield a model with enormous effective depth/width.
3. **Mixed precision:** Keep embeddings at int8 (they're already tiny with 1024 vocab), quantize transformer blocks more aggressively.

**Why this works here:** The baseline's int8+zlib already shows only a 0.007 BPB degradation from quant. Going lower-bit with QAT should preserve even more quality since the model learns to compensate during training.

**Implementation:** Replace `CastedLinear` with `BitLinear` or a 4-bit equivalent using STE (straight-through estimator) for gradients. Train normally with Muon optimizer.

### 3. Tokenizer Optimization (MEDIUM-HIGH IMPACT — Free BPB Improvement)

**The baseline uses a 1024-token SentencePiece BPE.**

The BPB metric is `bits_per_token × tokens_per_byte`. Optimizing the tokenizer is explicitly allowed but scrutinized heavily.

**Options:**
- **Byte-level (256 vocab):** Eliminates all tokenizer overhead, tokens_per_byte = 1.0 exactly. But each token carries less semantic info, so per-token loss is higher. Net effect is empirical.
- **Optimized BPE at 512-2048 vocab:** The modded-nanogpt speedrun showed that a TokenMonster-optimized tokenizer at ~half the vocab size preserved bytes-per-token while saving embedding parameters and FLOPs. A custom BPE trained specifically on FineWeb's byte distribution could outperform the default.
- **Byte-pair with frequency optimization:** Ensure the top-K tokens cover the highest-frequency byte sequences in FineWeb specifically.

**Key consideration:** With tied embeddings and 1024 vocab, the embedding table is only 512KB of parameters. Going to 512 vocab saves only 256K params. The savings are marginal in params but could be significant in BPB if the tokenizer is better calibrated.

**Recommendation:** Keep 1024 vocab but retrain the BPE specifically on the FineWeb training set to maximize bytes-per-token coverage. Low effort, moderate payoff, and a unique differentiation.

### 4. Test-Time Training (MEDIUM IMPACT — Evaluation Innovation)

**Explicitly allowed by the rules:** "we allow evaluation at any sequence length" and "you aren't allowed to access any training data during evaluation, unless you pay for those bits in the <16MB limit."

**The idea (from modded-nanogpt's @samacqua):** At eval time, for each validation document:
1. Take the first N tokens as a "context window"
2. Perform 1-3 gradient updates on the model using that context
3. Evaluate on the remaining tokens of that document
4. Reset model parameters for the next document

**Why this is powerful here:**
- The FineWeb validation set has document-level structure
- A small model can adapt to document-specific vocabulary, style, and topic in 1-3 steps
- The parameter budget for storing the base model + the TTT logic is still within 16MB
- The 10-minute eval constraint is generous — TTT adds maybe 2-3× eval time

**Implementation concerns:**
- Need to store Adam states during TTT (memory overhead)
- Must be careful not to overfit on the first few tokens
- eval time must stay under 10 minutes total on 8×H100

### 5. Training Efficiency & Optimization (MEDIUM IMPACT — More Steps in 10 Minutes)

**The baseline gets ~43ms/step.** Improvements here let you train more steps:

- **torch.compile with fullgraph=True** (already enabled)
- **FP8 matmuls:** H100s have FP8 tensor cores. Use `torch.float8_e4m3fn` for forward pass matmuls — potentially 2× throughput on the dominant compute
- **Gradient accumulation tuning:** The baseline uses 8//world_size = 1 accumulation step per GPU. Could reduce per-step overhead.
- **Sequence length warmup:** Start at seq_len=256, ramp to 1024. Faster early steps, more steps in the same wall-clock.
- **FlexAttention / window sizing:** Use short attention windows early in training (128-384 tokens), expand to full 1024 later. Direct import from modded-nanogpt.
- **Longer context at eval only:** Train at 1024, eval at 2048-4096 with YaRN RoPE rescaling. The rules explicitly allow any eval sequence length.

### 6. Architecture Tweaks (MEDIUM IMPACT — Incremental Gains)

These are the "polish" moves, each worth 0.001-0.005 BPB:

- **Smear module:** From modded-nanogpt. Tokens peek 1 position back, gated. Tiny parameter cost, consistent improvement.
- **Value embeddings:** Learnable embedding added to the value path of attention. Another modded-nanogpt innovation.
- **Logit softcapping tuning:** The baseline uses 30.0. Sweep 20-50.
- **ReLU² → SwiGLU:** SwiGLU is generally better at scale, but adds a gate projection (3× hidden instead of 2×). With the parameter savings from looping, this might fit.
- **Muon hyperparameter sweep:** The baseline's Muon config is conservative. Backend_steps, momentum, LR schedule, and warmdown timing all have room.
- **Skip connection structure:** The baseline has an encoder-decoder skip pattern. With looping, experiment with dense skip connections or a UNet-like topology.

---

## Proposed Architecture: "RecurseNet-16M"

### Configuration

```
# Core architecture
VOCAB_SIZE=1024          # Keep baseline tokenizer (retrained BPE)
MODEL_DIM=640            # Wider than baseline (was 512)
NUM_UNIQUE_BLOCKS=4      # Shared block pool
NUM_LOOPS=3              # Each block applied 3× = 12 effective layers
NUM_HEADS=10             # More heads (was 8)
NUM_KV_HEADS=5           # GQA 10/5 (was 8/4)
MLP_MULT=2               # Keep 2× expansion

# Quantization
QUANT_BITS=4             # 4-bit QAT during training, serialize as 4-bit
# OR QUANT_BITS=2 with ternary weights (more aggressive)

# Depth signals
DEPTH_LORA_RANK=8        # Per-loop-iteration LoRA for adaptability

# Training
TRAIN_SEQ_LEN=1024
EVAL_SEQ_LEN=2048        # YaRN RoPE extension at eval
TTT_STEPS=2              # Test-time training gradient steps per document
```

### Parameter Budget Estimate (4-bit QAT)

| Component | Params | Bytes (4-bit + overhead) |
|-----------|--------|--------------------------|
| Token embedding (1024 × 640, tied) | 655K | ~400KB |
| 4 unique transformer blocks (640dim, 10/5 heads, 2× MLP) | ~8.2M | ~4.6MB |
| Depth LoRA signals (3 loops × 4 blocks × rank 8) | ~245K | ~140KB |
| Skip weights, norms, scalars | ~50K | ~30KB |
| **Total params** | **~9.15M** | |
| **Compressed (4-bit + zlib)** | | **~5.5MB** |
| Code | | **~60KB** |
| **Total artifact** | | **~5.6MB** |

This leaves **~10MB of headroom**. Options:
- Increase width to 768+ or add more unique blocks
- Store a secondary model (ensemble at eval time)
- Use the headroom for a larger vocab with untied embeddings

With **int8+zlib** (simpler, less risk):

| Component | Params | Bytes (int8 + zlib) |
|-----------|--------|---------------------|
| 4 shared blocks at 640dim | ~8.2M | ~7.4MB |
| Embeddings + misc | ~700K | ~650KB |
| Depth LoRA | ~245K | ~220KB |
| Code | | ~60KB |
| **Total** | **~9.15M** | **~8.3MB** |

Still under 16MB with room to grow.

---

## Execution Roadmap

### Phase 1: Foundation (Days 1-3)
1. Fork repo, set up RunPod 1×H100 instance
2. Reproduce baseline: confirm 1.2244 BPB
3. Implement depth recurrence with 4 shared blocks × 3 loops
4. Add per-loop depth LoRA signals
5. Verify training stability, run at width 512 first

### Phase 2: Width Scaling (Days 4-6)
1. Scale width from 512 → 640 → 700 with loop architecture
2. Tune Muon hyperparameters for the new architecture
3. Implement sequence length warmup (256 → 1024)
4. Target: beat baseline by ~0.01 BPB

### Phase 3: Compression (Days 7-10)
1. Implement 4-bit QAT with STE gradients
2. OR: implement BitNet b1.58 ternary training
3. With 4-bit: scale width even further (768+) within 16MB
4. Verify round-trip: train → quantize → decompress → eval

### Phase 4: Evaluation Innovation (Days 11-14)
1. Implement test-time training at eval
2. Implement longer-context eval with YaRN RoPE rescaling
3. Tune TTT learning rate and step count
4. Implement FlexAttention with window sizing

### Phase 5: Polish & Submission (Days 15-20)
1. Full hyperparameter sweep on 8×H100
2. Statistical significance testing (multiple runs)
3. Combine all innovations, verify reproducibility
4. Write detailed README explaining approach
5. Submit PR

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Depth recurrence training instability | Input injection, careful LR warmup, gradient clipping |
| QAT quality degradation | Start with int8 (proven), graduate to 4-bit only if stable |
| Test-time training blows eval time budget | Profile TTT overhead early, cap at 2 steps, parallelize across GPUs |
| Tokenizer changes invalidate BPB calculation | Be extremely careful with BPE changes; default to baseline tokenizer |
| Statistical significance (p < 0.01) | Run 10+ seeds, report mean and CI |

---

## Differentiated Angle: Why This Wins

Most competitors will attack one axis — either architecture changes OR compression tricks. The winning strategy combines **three orthogonal improvements**:

1. **Depth recurrence** (more effective depth per parameter)
2. **Aggressive quantization** (more parameters per byte)
3. **Test-time training** (better evaluation per parameter)

Each independently gives ~0.005-0.02 BPB improvement. Combined, they compound.

The unique background here is key: production experience with vLLM/SGLang inference optimization maps directly to understanding the int8/4-bit quantization pipeline and eval-time compute budgeting. GPU cluster experience (50+ GPU distributed training) maps to understanding the 8×H100 DDP training dynamics. The systems engineering lens — treating this as a *full-stack optimization problem* from tokenizer to eval-time inference — is the competitive advantage.

---

## Quick Wins to Submit First (Non-Record, Build Credibility)

Before attempting SOTA, submit a non-record entry that demonstrates:
1. Depth recurrence working (even if not fully optimized)
2. A well-written README explaining the theory
3. Clean, readable code

This gets your name on the board, builds rapport with the OpenAI team reviewing PRs, and establishes you as a serious participant. Then iterate toward SOTA.

---

## References & Prior Art

- **Modded-nanogpt speedrun:** Muon, FlexAttention, smear module, value embeddings, window sizing, sequence warmup
- **BitNet b1.58 (Microsoft):** Ternary QAT for extreme compression
- **Relaxed Recursive Transformers (Google):** Layer-wise LoRA for looped architectures, up to 13.5% accuracy improvement
- **RingFormer:** Per-iteration low-rank adaptation signals, 2-4× parameter reduction
- **Universal Transformer (Dehghani et al.):** Foundational depth recurrence, ACT halting
- **TTT from modded-nanogpt (@samacqua):** Test-time training with Adam parameter nudging on ~500 tokens
- **AlgoFormer:** Pre-transformer + looped core + post-transformer hybrid
- **YaRN RoPE extension:** Extend context at eval without retraining
