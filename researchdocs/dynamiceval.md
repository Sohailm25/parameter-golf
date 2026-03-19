# Dynamic evaluation and test-time training for Parameter Golf

**Dynamic evaluation can reduce BPB by an estimated 3–8% relative (~0.03–0.10 absolute) for a 16MB model on FineWeb, at minimal computational cost within the 10-minute budget.** This technique adapts model parameters online during evaluation by performing gradient updates on each test segment before moving to the next. Smaller, weaker models benefit disproportionately—exactly the regime Parameter Golf targets. The approach is computationally cheap for a ~10M parameter model on 8×H100 (under 30 seconds for a single adapted pass through all 50K documents), leaving ample budget for multi-pass strategies. Combined with sliding-window evaluation, longer contexts, and careful layer selection, dynamic evaluation represents one of the highest-leverage techniques available in this challenge.

---

## Part 1: Paper-by-paper review

### Krause et al. (2018) — the foundational dynamic evaluation algorithm

**"Dynamic Evaluation of Neural Sequence Models" (ICML 2018, arXiv:1709.07432)** introduced the modern formulation of dynamic evaluation. The core idea: during evaluation, split the test sequence into short segments of length *n*, and after predicting each segment, perform a gradient-based update to the model parameters before predicting the next segment. Crucially, predictions are scored *before* the update—so each log-probability remains valid.

The algorithm proceeds as follows. Initialize adapted parameters θ = θ_g (the pretrained weights). For each segment s_i: (1) compute P(s_i | θ) and the cross-entropy loss L(s_i); (2) compute ∇L(s_i) via backpropagation truncated to the segment; (3) update parameters using the RMS rule with decay toward original weights; (4) record the loss computed in step 1. The update rule in its final form is:

**θ ← θ − η · ∇L / √(MS_g + ε) + λ · (θ_g − θ) ⊙ RMSnorm**

Here MS_g is the mean-squared gradient pre-computed across the *training data* (not a running average on test data, since early test segments provide too few samples). RMSnorm = √MS_g / mean(√MS_g), clipped so no value exceeds 1/λ. The decay term λ(θ_g − θ) pulls weights back toward pretrained values exponentially, preventing catastrophic forgetting. Parameters with larger typical gradients decay faster (via the RMSnorm scaling), since they influence network dynamics more.

**Hyperparameters** for AWD-LSTM on PTB: lr=0.002, λ=0.02, ε=0.001, segment length=5 tokens. For character-level tasks: segment length=20. Learning rate tuning is by far the most important; λ tuning gives smaller additional benefit.

**Results show dramatic improvements, especially on smaller/weaker models.** On Penn Treebank (24M-param AWD-LSTM), perplexity dropped from **57.7 → 51.1** (11.4% relative). On WikiText-2 (33M params), **66.1 → 44.3** (33% relative—the largest gain, attributed to non-shuffled article order and rich vocabulary). On enwik8 character-level (46M-param mLSTM), bits-per-character dropped from **1.24 → 1.08** (12.9% relative). On text8 character-level, **1.27 → 1.19** (6.3%). Sparse dynamic evaluation—adapting only a 500×500 matrix (250K params, 0.5% of total)—achieved intermediate results: 1.24 → 1.13 bpc on enwik8. Computational overhead is roughly **2× wall-clock time** versus static evaluation (one forward + one backward pass per segment).

### Krause et al. (2019) — adapting dynamic evaluation for Transformers

**"Dynamic Evaluation of Transformer Language Models" (arXiv:1904.08378)** applied the technique to the Transformer-XL architecture with segment-level recurrence (memory cache of 3800 for character-level models). Segment length was fixed at **128 tokens**, aligned with Transformer-XL's native segment processing.

Results on a **277M-parameter Transformer-XL**: enwik8 dropped from **0.993 → 0.940 bpc** (5.3% relative); text8 from **1.085 → 1.038 bpc** (4.3%); WikiText-103 perplexity from **18.1 → 16.4** (9.4%). RMS dynamic evaluation consistently outperformed plain SGD dynamic evaluation (e.g., 0.940 vs 0.946 on enwik8). On WikiText-103, the optimal decay rate λ was tuned to 0 (no decay benefit).

The paper explicitly notes that **improvements are smaller for Transformers than for RNNs**, stating: "These improvements are not nearly as large as when dynamic evaluation has been applied to weaker models, suggesting that Transformers are by themselves somewhat more capable of modeling re-occurring patterns." The pattern is unambiguous: dynamic eval helps weaker models more. A 46M mLSTM gains 12.9% on enwik8; a 277M Transformer-XL gains 5.3%. All parameters were updated—no per-layer ablation was performed in this paper. GPT-2 117M evaluated on WikiText-2 showed perplexity dropping from **29.0 → 24.5** (15.5% relative), demonstrating the technique generalizes to other Transformer architectures.

### Bellard's NNCP v2 — state-of-the-art neural compression via online learning

**NNCP (Neural Network based lossless data Compressor)** takes dynamic evaluation to its logical extreme: the model trains entirely from scratch during compression, with **no pretrained weights at all**. The encoder predicts each symbol, encodes it with an arithmetic coder, then updates the model. The decoder performs the identical predict-update loop, so no model parameters need to be transmitted—only the compressed bitstream and a ~60KB preprocessing dictionary.

NNCP v2 (February 2021) uses a modified Transformer-XL with GELU activations, learned relative positional embeddings, and untied input/output embeddings. The base model has **56M parameters** and the large model **187M parameters**. The optimizer is Adam with **β₁ = 0** (effectively RMSProp with bias correction), β₂ = 0.9999, learning rate linearly decreased during training. Training segments are 192 symbols long with large overlap (advancing 1 symbol per step) and batch size 64 across independent data streams.

A critical innovation is **periodic retraining**: every 500,000 symbols, the model retrains on the past 10 million symbols (~20 epochs), using dropout only during this retraining phase. This compensates for the Transformer's slower convergence versus LSTMs. The approach also uses gradient normalization (not clipping) described as "essential to avoid divergence." NNCP v2 achieves **1.20 bpb on enwik8** (large model) and **0.898 bpb on enwik9**. NNCP v3.3 (June 2024) pushes this to **1.193 bpb on enwik8** and **0.853 bpb on enwik9**—the current state of the art on the Large Text Compression Benchmark.

For Parameter Golf, the most directly applicable NNCP techniques are: (1) the periodic retraining concept—process some documents, then retrain on recently seen data; (2) Adam with β₁ = 0 to save optimizer memory (no first-moment buffer); (3) gradient normalization for stability; (4) overlapping segments for efficient GPU utilization. The key difference is that Parameter Golf starts with pretrained weights (a massive advantage NNCP doesn't have), so the online learning serves as adaptation rather than learning from scratch.

### Rannen-Triki et al. (2024) — revisiting dynamic evaluation at scale

**"Revisiting Dynamic Evaluation: Online Adaptation for Large Language Models" (arXiv:2403.01518, Google DeepMind, NeurIPS 2024)** is the most directly relevant paper for Parameter Golf's implementation decisions. They tested dynamic evaluation on **150M, 400M, and 1B parameter** models pretrained on C4, evaluated on PG-19 (long-form books).

**Key finding on layers: MLP layers are the best targets for adaptation.** The authors state: "We applied adapters to multiple types of layers in the models, and adapting on the MLPs gave the best performance." This is notably different from LoRA's original application to attention layers (Wq, Wv). Furthermore, **middle transformer blocks are most effective**—adapting the topmost or bottommost blocks produces weaker results. They tested individual layers and pairs of successive layers in a 12-layer stack, finding that blocks around positions 5–8 provided the most adaptation benefit.

**LoRA was tested and works well**, applied specifically to MLP layers. It achieves lower performance than full fine-tuning but significantly higher than static evaluation, with substantially lower compute and memory costs. The regret (cumulative excess log-loss) grows slowly with LoRA, while the static model's regret grows steeply. They tested multiple LoRA ranks and found useful Pareto-optimal tradeoffs.

The paper's most striking result: **"Smaller models with online adaptation can achieve competitive and sometimes better performance than larger models" without adaptation.** This directly validates the Parameter Golf strategy—a small model with TTT can punch above its weight class. They also found that **models with shorter context windows plus online adaptation can match longer-context models without adaptation**, suggesting "memory in weights" (dynamic eval) partially substitutes for "memory in activations" (long context). Learning rates were swept over [1e-6, 3e-6, 1e-5, 3e-5] with no learning rate schedule.

### samacqua's test-time training on modded-nanogpt (January 23, 2026)

**@samacqua demonstrated TTT in the NanoGPT Speedrunning context**, described in the modded-nanogpt README as "parameter nudging." The method performs a training update on Adam-managed parameters based on the early portion (~500 tokens) of each document, then evaluates the later portions with adapted weights. **This process resets independently for each document.** The adaptation uses substantially fewer tokens (~500) than a normal training step (~262K tokens), yet still improves prediction on later tokens within the same document.

This was listed as a "Notable" result but **not an official record**—the README states: "While technically a valid probability model, we are not allowing untimed backward passes." The exact learning rate, loss improvement, and detailed code were not publicly documented. However, the approach directly validates the core dynamic evaluation concept for this architecture: a brief backward pass on ~500 early tokens meaningfully improves predictions on subsequent tokens.

For Parameter Golf, the rules explicitly allow backward passes during evaluation as long as they fit within the 10-minute budget. The challenge README encourages TTT: "We're excited to see... test-time training, long context, megakernels..." A current WIP submission (PR #69, "SubSixteen") combines ternary QAT + depth recurrence + TTT, though its val_bpb is still pending.

### Sun et al. (2024) — TTT-Linear and TTT-MLP layers

**"Learning to (Learn at Test Time): RNNs with Expressive Hidden States" (ICML 2025, arXiv:2407.04620)** introduces a fundamentally different approach where the hidden state *is itself a model* that gets updated at each timestep via self-supervised gradient descent. In TTT-Linear, the hidden state is a weight matrix W ∈ ℝ^{d×d} updated by minimizing a reconstruction loss ℓ(W; xₜ) = ‖f(x̃ₜ; W) − xₜ‖² on corrupted inputs. TTT-MLP uses a two-layer MLP as the hidden state for greater expressiveness.

Key differences from Krause-style dynamic evaluation: (1) the loss is a **per-layer self-supervised reconstruction loss**, not the end-to-end language modeling loss; (2) TTT layers **replace attention layers** in the architecture rather than being applied on top; (3) a **meta-learning outer loop** optimizes the initialization and projection matrices for efficient inner-loop learning; (4) the approach has **O(1) cost per token** like RNNs.

At 1.3B parameters, TTT-Linear outperforms Mamba in perplexity with fewer FLOPs and continues reducing perplexity as context grows (unlike Mamba, which plateaus after 16K). TTT-Linear matches Mamba's wall-clock time on H100 GPUs. While the architectural integration is elegant, **this approach requires designing TTT into the model from scratch**—it cannot be retrofitted onto an existing Transformer for Parameter Golf without retraining. The concepts are more relevant as design inspiration for future Parameter Golf submissions.

### Sun et al. (December 2025) — TTT-E2E for long context

**"End-to-End Test-Time Training for Long Context" (arXiv:2512.23675)** uses the end-to-end next-token prediction loss (not per-layer reconstruction) to update **dynamic MLP layers** in the top 25% of Transformer blocks at test time. Each updatable block contains two MLPs: a **static MLP** (frozen, preserving pretrained knowledge) and a **dynamic MLP** (updated at test time, storing compressed context). This dual-track design prevents catastrophic forgetting while enabling adaptation.

The training recipe uses meta-learning: during training, sequences are treated as if they were test sequences for the inner adaptation loop, optimizing the initialization for efficient test-time learning. TTT mini-batch size is 1K tokens, and only the dynamic MLP in the final quarter of blocks is updated—this gives a **5× larger effective hidden state** and **2× lower inference latency** compared to updating all layers with LoRA. At 3B parameters, TTT-E2E scales with context length identically to full-attention Transformers while being **2.7× faster** at 128K context.

For Parameter Golf, TTT-E2E's most applicable insight is the **dual-MLP architecture**: freeze most of the model and add a small dynamic MLP in the top layers that adapts at test time. This is architecturally compatible with the existing U-net skip-connected Transformer baseline.

---

## Part 2: Practical implementation guide

### The algorithm for dynamic evaluation in Parameter Golf

The eval loop must maintain a strict ordering: predict, score, then update. Here is a complete PyTorch implementation sketch:

```python
import torch
import torch.nn.functional as F
import math
import copy

def dynamic_eval(model, val_tokens, byte_counts, args, device):
    """
    Dynamic evaluation for Parameter Golf.

    Args:
        model: pretrained GPT model
        val_tokens: (N,) int tensor of tokenized validation data
        byte_counts: (N,) int tensor of byte count per token (for BPB)
        args: config with train_seq_len, etc.
    Returns:
        val_bpb: bits-per-byte with dynamic evaluation
    """
    seq_len = args.train_seq_len  # 1024 default

    # ---- Phase 0: Store original weights ----
    original_params = {}
    for name, p in model.named_parameters():
        original_params[name] = p.data.clone()

    # ---- Phase 1 (optional): Compute gradient RMS statistics ----
    # Skip if no training data is available at eval time (Parameter Golf
    # doesn't allow training data access). Instead, use uniform scaling
    # or Adam which adapts its own scale estimates.

    # ---- Phase 2: Set up optimizer for adapted parameters ----
    # Choose which parameters to adapt
    adapted_params = []
    for name, p in model.named_parameters():
        # Option A: Adapt all parameters
        # Option B: Adapt only MLP layers in middle/top blocks
        # Option C: Adapt only a LoRA adapter (if present)
        if should_adapt(name, args):
            p.requires_grad_(True)
            adapted_params.append(p)
        else:
            p.requires_grad_(False)

    # SGD with momentum is memory-efficient; Adam is more robust
    optimizer = torch.optim.SGD(adapted_params, lr=args.dyneval_lr,
                                 momentum=0.9)
    # Alternative: Adam uses 2x memory but adapts per-parameter scale
    # optimizer = torch.optim.Adam(adapted_params, lr=args.dyneval_lr)

    lamb = args.dyneval_decay  # decay rate toward original weights

    # ---- Phase 3: Process documents ----
    total_loss_bits = 0.0
    total_bytes = 0

    for doc_start, doc_end in document_boundaries(val_tokens):
        # Reset to original weights for each document
        if args.reset_per_document:
            for name, p in model.named_parameters():
                p.data.copy_(original_params[name])
            optimizer = torch.optim.SGD(adapted_params, lr=args.dyneval_lr,
                                         momentum=0.9)

        doc_tokens = val_tokens[doc_start:doc_end]
        doc_bytes = byte_counts[doc_start:doc_end]

        # Process document in segments of seq_len
        for seg_start in range(0, len(doc_tokens) - 1, seq_len):
            seg_end = min(seg_start + seq_len, len(doc_tokens) - 1)
            x = doc_tokens[seg_start:seg_end].unsqueeze(0).to(device)
            y = doc_tokens[seg_start+1:seg_end+1].unsqueeze(0).to(device)
            seg_bytes = doc_bytes[seg_start+1:seg_end+1]

            # STEP 1: Forward pass — PREDICT with current parameters
            with torch.enable_grad():
                logits = model(x)  # (1, seg_len, vocab_size)
                loss = F.cross_entropy(
                    logits.view(-1, logits.size(-1)),
                    y.view(-1),
                    reduction='sum'
                )

            # STEP 2: Record loss BEFORE any parameter update
            total_loss_bits += loss.item() / math.log(2.0)
            total_bytes += seg_bytes.sum().item()

            # STEP 3: Backward pass + parameter update
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # STEP 4: Decay toward original weights
            with torch.no_grad():
                for name, p in model.named_parameters():
                    if p.requires_grad:
                        p.data.add_(lamb * (original_params[name] - p.data))

    val_bpb = total_loss_bits / total_bytes
    return val_bpb
```

### Which parameters to adapt: the `should_adapt` function

Based on findings from Rannen-Triki et al. (2024), the recommended strategy is to adapt **MLP layers in the middle-to-upper blocks**:

```python
def should_adapt(name, args):
    """Select parameters for dynamic evaluation adaptation."""
    n_blocks = args.n_blocks  # e.g., 9 for Parameter Golf baseline

    # Strategy: adapt MLP layers in middle 50% of blocks
    # For 9 blocks: adapt blocks 3, 4, 5, 6 (0-indexed)
    start_block = n_blocks // 4       # block 2
    end_block = 3 * n_blocks // 4     # block 6

    for block_idx in range(start_block, end_block + 1):
        if f"blocks.{block_idx}.mlp" in name:
            return True
    return False
```

### The weight-decay-toward-original mechanism (two approaches)

**Approach A — Explicit L2 penalty (additive decay):** After each optimizer step, pull weights toward originals. This is Krause's approach.

```python
# After optimizer.step():
with torch.no_grad():
    for name, p in model.named_parameters():
        if p.requires_grad:
            p.data.add_(lamb * (original_params[name] - p.data))
            # Equivalent to: p.data = (1 - lamb) * p.data + lamb * original
```

**Approach B — Weight-space EMA:** Maintain an exponential moving average that mixes adapted and original weights.

```python
# After optimizer.step():
with torch.no_grad():
    for name, p in model.named_parameters():
        if p.requires_grad:
            p.data.lerp_(original_params[name], lamb)
```

Both are mathematically equivalent. The lerp formulation is slightly cleaner in PyTorch. Typical λ values: **0.001–0.02 per segment**. Higher λ means faster forgetting of adaptations.

### Parallelizing across 8 GPUs

Documents can be processed independently across GPUs with no inter-GPU communication:

```python
def dynamic_eval_distributed(model, val_tokens, documents, rank, world_size):
    """Each GPU processes its shard of documents independently."""
    # Split documents across GPUs
    my_docs = documents[rank::world_size]  # ~6,250 docs per GPU

    # Each GPU has its own model copy and optimizer
    local_model = copy.deepcopy(model).to(f'cuda:{rank}')

    total_loss_bits = 0.0
    total_bytes = 0

    for doc in my_docs:
        # Reset model to original weights
        load_original_weights(local_model, original_params)

        # Process document with dynamic eval
        doc_loss, doc_bytes = process_document(local_model, doc)
        total_loss_bits += doc_loss
        total_bytes += doc_bytes

    # All-reduce to aggregate across GPUs
    total_loss_bits = all_reduce_sum(total_loss_bits)
    total_bytes = all_reduce_sum(total_bytes)

    return total_loss_bits / total_bytes
```

### Memory budget analysis

For the Parameter Golf baseline (~10M parameters, 9 blocks, width 512):

| Component | Adam (all params) | SGD (MLP middle blocks only) |
|---|---|---|
| Model weights (fp16) | 20 MB | 20 MB |
| Adapted params count | 10M | ~2M (4 blocks × MLP) |
| Optimizer states | 80 MB (2 × 10M × 4B) | 8 MB (1 × 2M × 4B) |
| Gradients | 40 MB | 8 MB |
| Activations (seq 1024) | ~48 MB | ~48 MB |
| Original weights copy | 40 MB | 40 MB |
| **Total** | **~228 MB** | **~124 MB** |

**Memory is not a constraint.** Even the most expensive configuration uses under **0.3% of H100's 80 GB**. Gradient checkpointing is unnecessary at this model size.

### Time budget analysis

The FineWeb validation set contains approximately **34.4M tokens** across 50K documents (average ~687 tokens/doc). Key timing estimates for a 10M parameter model:

| Operation | Tokens/sec/GPU | 8-GPU throughput | Time for 34.4M tokens |
|---|---|---|---|
| Forward only | ~5M | ~40M | **~0.9 sec** |
| Forward + backward + update | ~1M | ~8M | **~4.3 sec** |
| With per-doc reset overhead | ~800K | ~6.4M | **~5.4 sec** |

A single dynamic evaluation pass takes roughly **5–10 seconds** on 8×H100. This means within the 10-minute budget, you could perform **~60–120 complete dynamic evaluation passes** through the data—far more than needed. The bottleneck is algorithmic design, not compute. Even with torch.compile overhead and CUDA graph warmup, there is enormous headroom.

### Handling ternary-quantized base models

If the base model uses ternary quantization ({-α, 0, +α} weights) to maximize parameters within 16MB:

```python
# Maintain latent fp32 weights for gradient updates
latent_weights = {name: p.data.float().clone()
                  for name, p in model.named_parameters()
                  if should_adapt(name)}

# Forward: use quantized weights (fast, already in model)
# Backward: STE passes gradients through quantization unchanged
# Update: apply gradient to latent fp32 weights, then re-quantize
def ternary_dynamic_step(model, loss, optimizer, latent_weights):
    loss.backward()  # STE: grads flow to quantized weights
    with torch.no_grad():
        for name, p in model.named_parameters():
            if name in latent_weights:
                # Update latent weights
                latent_weights[name] -= lr * p.grad
                # Re-quantize
                p.data.copy_(ternary_quantize(latent_weights[name]))
```

The extra memory for latent fp32 copies is ~40 MB for 10M parameters—trivial on H100. An important alternative: **skip quantization for the adapted layers entirely** and keep them in fp16, since the 16MB limit applies only to the stored artifact, not runtime memory.

### Integration with Parameter Golf's eval_val() function

The existing eval_val() function processes all validation tokens in a single flat stream. To add dynamic evaluation, wrap the inner loop:

```python
def eval_val_dynamic(args, model, rank, world_size, device, ...):
    """Modified eval_val with dynamic evaluation."""

    # Store original weights
    orig_state = {k: v.clone() for k, v in model.state_dict().items()}

    # Determine document boundaries in val_tokens
    # (FineWeb documents are concatenated; boundaries need detection
    #  or pre-computation from the validation shard metadata)

    val_loss_sum = 0.0
    val_byte_count = 0
    val_token_count = 0

    # Process each document on this rank's GPU
    for doc_tokens, doc_bytes in my_documents:
        # Reset model
        model.load_state_dict(orig_state)
        optimizer = torch.optim.SGD(get_adapted_params(model), lr=LR)

        for i in range(0, len(doc_tokens) - 1, args.train_seq_len):
            x = doc_tokens[i:i+args.train_seq_len].unsqueeze(0)
            y = doc_tokens[i+1:i+1+args.train_seq_len].unsqueeze(0)

            # Forward + loss (predictions BEFORE update)
            with torch.enable_grad():
                logits = model(x)
                loss = F.cross_entropy(logits.view(-1, V), y.view(-1))

            # Record loss
            seg_len = y.numel()
            val_loss_sum += loss.detach() * seg_len
            val_token_count += seg_len
            val_byte_count += compute_bytes(y, base_bytes_lut, ...)

            # Update parameters
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Decay toward original
            with torch.no_grad():
                for name, p in model.named_parameters():
                    if p.requires_grad:
                        p.data.lerp_(orig_state[name].to(device), LAMBDA)

    # Aggregate across GPUs
    val_loss = val_loss_sum / val_token_count
    bpt = val_loss.item() / math.log(2.0)
    tpb = val_token_count / val_byte_count
    return float(val_loss.item()), float(bpt * tpb)
```

---

## Part 3: Failure modes and gotchas

### When dynamic evaluation actively hurts

**Very short documents are the primary danger zone.** With fewer than ~50 tokens, the gradient signal is too noisy to provide useful adaptation—you're fitting to noise rather than local distribution structure. FineWeb's average document length is ~687 tokens, but the distribution has a heavy tail with many short documents. The recommended mitigation is to skip dynamic adaptation entirely for documents under 100 tokens, or concatenate adjacent short documents before adaptation.

**Already in-distribution models benefit less.** Rannen-Triki et al. (2024) found that as the amount of domain-specific finetuning increases, dynamic evaluation's advantage shrinks and can even invert. If the Parameter Golf model is already well-calibrated on web text (which FineWeb is), the improvement ceiling is lower than on out-of-domain benchmarks. This is a key reason the expected improvement is ~3–8% rather than the 33% seen on WikiText-2 (where article-level topic consistency creates strong adaptation signal).

### Learning rate sensitivity is the dominant failure mode

Krause's work and Rannen-Triki et al. both emphasize that **learning rate is the single most important hyperparameter** for dynamic evaluation. Too high, and the model overshoots—adapting too aggressively to recent tokens and degrading on subsequent ones. Too low, and adaptation is negligible. The optimal range for small Transformer models appears to be **1e-5 to 3e-4**, but this must be grid-searched on a validation subset. Krause's original code provides a `--grid` flag that searches over lr and λ in a single validation pass, which is cheap enough to run within the 10-minute budget (one full dynamic eval pass takes ~5–10 seconds).

### Catastrophic forgetting accumulates across segments

Without the decay term λ(θ_g − θ), adapted parameters drift farther from the pretrained optimum with each update. After processing many segments, the model can degrade catastrophically. The decay-toward-original mechanism is essential but introduces its own tradeoff: too-strong decay erases useful adaptations too quickly, while too-weak decay permits dangerous drift. **Resetting parameters between documents** (as samacqua does) is the cleanest solution and avoids the need to carry cross-document state, though it sacrifices the possibility of accumulating useful cross-document adaptation.

### Logit softcapping interaction

The Parameter Golf baseline uses **logit softcapping at 30.0**: `logits = 30.0 * tanh(logits / 30.0)`. The tanh derivative approaches 0 for large pre-cap logits, which dampens gradient flow for high-confidence predictions. During dynamic evaluation, this means the model adapts primarily on uncertain predictions (which is arguably desirable) but may fail to correct confidently wrong predictions. If this causes problems, options include: increasing the softcap value during adaptation, computing the adaptation loss before softcapping, or disabling softcapping during the backward pass only.

### torch.compile compatibility

Dynamic evaluation changes model parameters every step, which can trigger **recompilation** with `torch.compile`. The solution is to use `torch.compile(mode="reduce-overhead")` or CUDA graphs with explicit warm-up. A subtler issue: compiled forward+backward graphs may not efficiently handle the per-segment parameter update pattern. Testing suggests wrapping only the forward pass in `torch.compile` and performing the optimizer step outside the compiled region is the most robust approach. The 1.5–3× speedup from compilation is significant for small models where kernel launch overhead dominates.

### BPB computation correctness

The most dangerous implementation bug: **computing loss after the parameter update instead of before.** This produces optimistically biased BPB numbers that don't represent a valid probability model. The loss for each segment must be computed with the parameters that existed *before* seeing that segment. In Krause's code, this is enforced by the ordering: forward → record loss → backward → update. Any refactoring that disrupts this ordering will produce invalid results.

### Gradient accumulation across segments

If using segment lengths shorter than the Transformer's context window (e.g., 128-token segments in a 1024-context model), there's a question of how to handle the hidden state / KV cache. The KV cache should persist across segments within a document (to provide context), but gradients should be truncated to the current segment only. Truncating backpropagation to the segment avoids memory blowup while preserving the forward-pass benefit of long context.

### Per-document reset overhead

Resetting model parameters between documents requires copying ~20–40 MB of weights back to GPU. At ~3.35 TB/s memory bandwidth on H100, this takes ~6–12 microseconds per reset. With 50K documents across 8 GPUs (~6,250 resets per GPU), total reset overhead is ~40–75 milliseconds—completely negligible.

---

## Part 4: Expected BPB improvement estimates

### Calibrating from the literature

The literature provides a clear scaling pattern for dynamic evaluation improvements:

| Benchmark | Model size | Architecture | Relative improvement |
|---|---|---|---|
| WikiText-2 | 33M | LSTM | 33.0% |
| enwik8 | 46M | mLSTM | 12.9% |
| PTB | 24M | LSTM | 11.4% |
| WikiText-103 | 257M | Transformer-XL | 9.4% |
| WikiText-2 | 117M | GPT-2 | 15.5% |
| enwik8 | 277M | Transformer-XL | 5.3% |
| text8 | 277M | Transformer-XL | 4.3% |

Two patterns emerge. First, **smaller models benefit more**—the Parameter Golf ~10M parameter model is smaller than anything tested in the literature, which should push improvements higher. Second, **the dataset matters enormously**—WikiText-2 (non-shuffled, topic-consistent articles) shows 33% improvement, while text8 (diverse text) shows only 4–6%. FineWeb is diverse web text more similar to text8 than WikiText-2, pushing improvements lower.

### Estimating for Parameter Golf specifically

The Parameter Golf setup has several unique characteristics affecting the estimate:

**Factors pushing improvement higher:**
- Very small model (~10M params) → lower baseline capacity → more room for adaptation
- BPB metric is byte-level → the model must predict whitespace, punctuation, and formatting that are highly document-specific and benefit from adaptation
- Documents are independent → resetting between docs prevents cross-domain catastrophic forgetting
- Ample compute budget → no need to compromise on adaptation quality

**Factors pushing improvement lower:**
- FineWeb is diverse web text with weak intra-document topic consistency (compared to Wikipedia or books)
- The baseline model already uses modern architecture improvements (RoPE, QK-norm, GQA) that capture some patterns dynamic eval would exploit
- Short average document length (~687 tokens) limits adaptation depth
- Dynamic eval cannot use training-data gradient statistics (MS_g) in Parameter Golf since training data isn't available at eval time—must use Adam or plain SGD

**Estimate: 3–8% relative BPB improvement**, translating to roughly **0.03–0.10 absolute BPB** reduction from the ~1.2 baseline. The midpoint estimate is ~5%, or **~0.06 BPB**. This would bring the baseline from ~1.20 to ~1.14, or a current best of ~1.01 to ~0.96–0.98.

### Breakdown by technique variant

| Variant | Estimated BPB improvement | Implementation complexity |
|---|---|---|
| Basic SGD dynamic eval (all params, no decay) | 0.02–0.05 | Low |
| SGD + decay toward original weights | 0.03–0.06 | Low |
| Adam on MLP middle layers + per-doc reset | 0.04–0.08 | Medium |
| LoRA adapters on middle MLPs + Adam | 0.03–0.07 | Medium |
| Full dynamic eval + longer context (2048) | 0.05–0.10 | Medium |
| samacqua-style parameter nudging (~500 tokens) | 0.02–0.04 | Low |
| NNCP-style periodic retraining on recent docs | 0.04–0.08 | High |

### Compound gains with other techniques

Dynamic evaluation interacts favorably with other Parameter Golf optimizations:

**Dynamic eval + sliding window evaluation** (currently worth ~0.02 BPB from leaderboard data) likely stack partially—sliding window provides better context for the forward pass while dynamic eval provides parameter adaptation. Combined, expect 70–80% of the sum of individual improvements.

**Dynamic eval + longer context (2048 or 4096)** provides diminishing returns since both exploit the same signal (local document structure). The Rannen-Triki paper explicitly shows that shorter context + dynamic eval can match longer context without dynamic eval. Still, using both together should outperform either alone, with the marginal gain of dynamic eval shrinking as context grows.

**Dynamic eval + ternary quantization** is a particularly interesting combination. Ternary models have less capacity per parameter, meaning they benefit more from adaptation. The STE backward pass introduces some gradient noise, but the per-parameter learning rate adaptation of Adam handles this naturally.

### Recommended implementation priority

The highest-leverage approach for a Parameter Golf submission is:

1. **Start with per-document SGD on all parameters** with learning rate grid search (takes minutes to implement, ~30 seconds to run). Expected: +0.03–0.05 BPB.
2. **Add decay toward original weights** with λ grid search. Expected: additional +0.01–0.02.
3. **Restrict adaptation to MLP layers in middle blocks** and switch to Adam. Expected: equal or slightly better performance with lower compute cost.
4. **Combine with 2048+ context evaluation**. Expected: compound gain of +0.05–0.10 total over baseline.
5. **Fine-tune the segment length** (try 128, 256, 512, 1024 tokens per gradient step). Shorter segments mean more frequent updates but noisier gradients.

The grid search for hyperparameters (lr, λ, adapted layers, segment length) can itself be parallelized across 8 GPUs: each GPU evaluates a different hyperparameter configuration on a subset of validation documents, and the best configuration is selected for the final evaluation. With each configuration taking ~5 seconds, you can evaluate **~800 configurations** within the time budget—more than sufficient for thorough hyperparameter search.
