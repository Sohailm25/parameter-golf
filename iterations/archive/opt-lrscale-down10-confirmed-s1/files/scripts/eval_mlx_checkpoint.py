# ABOUTME: Evaluates a saved MLX checkpoint on the flat validation stream with configurable sliding-window accounting.
# ABOUTME: Lets Sohail compare non-overlapping and overlapping evaluation semantics without retraining the baseline.

from __future__ import annotations

import argparse
import math
import os
import pickle
import sys
import uuid
import zlib
from pathlib import Path
from typing import Callable

import numpy as np
import sentencepiece as spm

import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_unflatten

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from train_gpt_mlx import (
    GPT,
    build_sentencepiece_luts,
    dequantize_state_dict_int8,
    load_validation_tokens,
    validate_dataset_tokenizer_pair,
)
from validation.eval_windowing import build_flat_stream_windows, build_suffix_mask, local_score_starts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoint-path",
        required=True,
        help="Path to the saved .int8.ptz checkpoint to evaluate.",
    )
    parser.add_argument("--data-path", default="./data/datasets/fineweb10B_sp1024")
    parser.add_argument("--tokenizer-path", default="./data/tokenizers/fineweb_1024_bpe.model")
    parser.add_argument("--run-id", default=os.environ.get("RUN_ID", ""))
    parser.add_argument("--out-dir", default=os.environ.get("OUT_DIR", "logs"))
    parser.add_argument("--seq-len", type=int, default=1024)
    parser.add_argument("--window-batch-seqs", type=int, default=16)
    parser.add_argument("--max-targets", type=int, default=0)
    parser.add_argument("--stride", action="append", type=int, required=True)
    parser.add_argument("--vocab-size", type=int, default=1024)
    parser.add_argument("--num-layers", type=int, default=9)
    parser.add_argument("--model-dim", type=int, default=512)
    parser.add_argument("--num-heads", type=int, default=8)
    parser.add_argument("--num-kv-heads", type=int, default=4)
    parser.add_argument("--mlp-mult", type=int, default=2)
    parser.add_argument("--logit-chunk-tokens", type=int, default=0)
    parser.add_argument("--logit-softcap", type=float, default=30.0)
    parser.add_argument("--rope-base", type=float, default=10000.0)
    parser.add_argument("--tied-embed-init-std", type=float, default=0.005)
    parser.add_argument("--qk-gain-init", type=float, default=1.5)
    return parser


def compile_token_losses(model: GPT) -> Callable[[mx.array, mx.array], mx.array]:
    def token_losses(input_ids: mx.array, target_ids: mx.array) -> mx.array:
        x = model(input_ids).reshape(-1, model.tok_emb.weight.shape[1])
        y = target_ids.reshape(-1)
        logits_proj = x @ model.tok_emb.weight.astype(x.dtype).T
        logits = model.softcap(logits_proj)
        return nn.losses.cross_entropy(logits.astype(mx.float32), y, reduction="none")

    return mx.compile(token_losses)


def load_quantized_model(args: argparse.Namespace) -> GPT:
    model = GPT(
        vocab_size=args.vocab_size,
        num_layers=args.num_layers,
        dim=args.model_dim,
        num_heads=args.num_heads,
        num_kv_heads=args.num_kv_heads,
        mlp_mult=args.mlp_mult,
        logit_chunk_tokens=args.logit_chunk_tokens,
        logit_softcap=args.logit_softcap,
        rope_base=args.rope_base,
        tied_embed_init_std=args.tied_embed_init_std,
        qk_gain_init=args.qk_gain_init,
    )
    checkpoint_path = Path(args.checkpoint_path)
    quant_blob = checkpoint_path.read_bytes()
    quant_obj = pickle.loads(zlib.decompress(quant_blob))
    quant_flat = dequantize_state_dict_int8(quant_obj)
    model.update(tree_unflatten(list(quant_flat.items())))
    return model


def compute_bytes(
    *,
    prev_ids: np.ndarray,
    target_ids: np.ndarray,
    base_bytes_lut: np.ndarray,
    has_leading_space_lut: np.ndarray,
    is_boundary_token_lut: np.ndarray,
) -> np.ndarray:
    bytes_np = base_bytes_lut[target_ids].astype(np.int16, copy=True)
    bytes_np += (
        has_leading_space_lut[target_ids] & ~is_boundary_token_lut[prev_ids]
    ).astype(np.int16, copy=False)
    return bytes_np


def batch_windows(windows, batch_size: int):
    batch = []
    current_window_len = None
    for window in windows:
        window_len = window.end - window.begin
        if current_window_len is None:
            current_window_len = window_len
        if batch and (len(batch) >= batch_size or window_len != current_window_len):
            yield batch
            batch = []
            current_window_len = window_len
        batch.append(window)
    if batch:
        yield batch


def evaluate_stride(
    *,
    val_tokens: np.ndarray,
    seq_len: int,
    stride: int,
    window_batch_seqs: int,
    compiled_token_losses: Callable[[mx.array, mx.array], mx.array],
    base_bytes_lut: np.ndarray,
    has_leading_space_lut: np.ndarray,
    is_boundary_token_lut: np.ndarray,
    log_fn: Callable[[str], None],
    max_targets: int,
) -> dict[str, float | int]:
    total_targets = val_tokens.size - 1
    if max_targets > 0:
        total_targets = min(total_targets, max_targets)
    windows = build_flat_stream_windows(total_targets=total_targets, seq_len=seq_len, stride=stride)
    batches = list(batch_windows(windows, window_batch_seqs))
    total_loss_sum = 0.0
    total_bytes = 0.0
    total_scored_targets = 0
    total_batches = len(batches)
    for batch_index, batch in enumerate(batches, start=1):
        window_len = batch[0].end - batch[0].begin
        x_np = np.stack([val_tokens[window.begin : window.end] for window in batch], axis=0)
        y_np = np.stack([val_tokens[window.begin + 1 : window.end + 1] for window in batch], axis=0)
        losses = compiled_token_losses(
            mx.array(x_np, dtype=mx.int32),
            mx.array(y_np, dtype=mx.int32),
        )
        losses_np = np.asarray(losses).reshape(len(batch), window_len)
        suffix_mask = build_suffix_mask(local_score_starts(batch), window_len=window_len)
        bytes_np = compute_bytes(
            prev_ids=x_np,
            target_ids=y_np,
            base_bytes_lut=base_bytes_lut,
            has_leading_space_lut=has_leading_space_lut,
            is_boundary_token_lut=is_boundary_token_lut,
        )
        total_loss_sum += float(losses_np[suffix_mask].sum(dtype=np.float64))
        total_bytes += float(bytes_np[suffix_mask].sum(dtype=np.float64))
        total_scored_targets += int(suffix_mask.sum())
        if total_batches > 1 and (batch_index == 1 or batch_index == total_batches or batch_index % 25 == 0):
            log_fn(f"val_progress stride:{stride} batch:{batch_index}/{total_batches}")
    val_loss = total_loss_sum / float(total_scored_targets)
    bits_per_token = val_loss / math.log(2.0)
    val_bpb = bits_per_token * (float(total_scored_targets) / total_bytes)
    return {
        "stride": stride,
        "val_loss": val_loss,
        "val_bpb": val_bpb,
        "targets": total_scored_targets,
        "windows": len(windows),
    }


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.window_batch_seqs <= 0:
        raise SystemExit(f"--window-batch-seqs must be positive, got {args.window_batch_seqs}")
    checkpoint_path = Path(args.checkpoint_path)
    if not checkpoint_path.is_file():
        raise SystemExit(f"checkpoint not found: {checkpoint_path}")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = args.run_id or str(uuid.uuid4())
    logfile = out_dir / f"{run_id}.txt"
    print(logfile)

    def log(message: str, console: bool = True) -> None:
        line = str(message)
        if console:
            print(line)
        with logfile.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    dataset_name, train_files, expected_train_files = validate_dataset_tokenizer_pair(args.data_path, args.tokenizer_path)
    log(
        "eval_windowing:enabled "
        f"checkpoint_path={checkpoint_path} checkpoint_bytes={checkpoint_path.stat().st_size} "
        f"dataset={dataset_name} observed_train_files={train_files} expected_train_files={expected_train_files}"
    )
    log(
        "eval_windowing:plan "
        f"seq_len={args.seq_len} strides={','.join(str(item) for item in args.stride)} "
        f"window_batch_seqs={args.window_batch_seqs} max_targets={args.max_targets or 'full'}"
    )
    sp = spm.SentencePieceProcessor(model_file=args.tokenizer_path)
    base_bytes_lut, has_leading_space_lut, is_boundary_token_lut = build_sentencepiece_luts(sp, args.vocab_size)
    val_tokens = load_validation_tokens(f"{args.data_path}/fineweb_val_*.bin", args.seq_len)
    model = load_quantized_model(args)
    compiled_token_losses = compile_token_losses(model)
    stride_results = []
    total_steps = len(args.stride)
    for step_index, stride in enumerate(args.stride, start=1):
        result = evaluate_stride(
            val_tokens=val_tokens,
            seq_len=args.seq_len,
            stride=stride,
            window_batch_seqs=args.window_batch_seqs,
            compiled_token_losses=compiled_token_losses,
            base_bytes_lut=base_bytes_lut,
            has_leading_space_lut=has_leading_space_lut,
            is_boundary_token_lut=is_boundary_token_lut,
            log_fn=log,
            max_targets=args.max_targets,
        )
        stride_results.append(result)
        extra = ""
        if step_index > 1:
            delta_bpb = result["val_bpb"] - stride_results[0]["val_bpb"]
            extra = f" delta_vs_step1:{delta_bpb:.8f}"
        log(
            f"step:{step_index}/{total_steps} val_loss:{result['val_loss']:.4f} "
            f"val_bpb:{result['val_bpb']:.4f} stride:{result['stride']} "
            f"windows:{result['windows']} targets:{result['targets']}{extra}"
        )
        log(
            f"stride_exact stride:{result['stride']} val_loss:{result['val_loss']:.8f} "
            f"val_bpb:{result['val_bpb']:.8f} windows:{result['windows']} targets:{result['targets']}"
        )
    final_result = stride_results[-1]
    log(
        f"final_int8_zlib_roundtrip val_loss:{final_result['val_loss']:.4f} "
        f"val_bpb:{final_result['val_bpb']:.4f} stride:{final_result['stride']}"
    )
    log(
        f"final_int8_zlib_roundtrip_exact val_loss:{final_result['val_loss']:.8f} "
        f"val_bpb:{final_result['val_bpb']:.8f}"
    )


if __name__ == "__main__":
    main()
