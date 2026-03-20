#!/bin/zsh
# ABOUTME: Runs the first bounded LR-scale proxy batch for parametergolf-gci in one scratch directory.
# ABOUTME: Keeps the search local and reversible so only one winner, if any, gets canonicalized later.

set -euo pipefail

ROOT="/Users/sohailmo/parametergolf"
BATCH_DIR="$ROOT/scratch/autoresearch/20260320-gci-lr-scale-batch"
DATA_PATH="$ROOT/data/datasets/fineweb10B_sp1024"
TOKENIZER_PATH="$ROOT/data/tokenizers/fineweb_1024_bpe.model"

run_candidate() {
  local run_id="$1"
  local tied_embed_lr="$2"
  local matrix_lr="$3"
  local scalar_lr="$4"
  local out_dir="$BATCH_DIR/$run_id"

  mkdir -p "$out_dir"

  (
    cd "$ROOT"
    RUN_ID="$run_id" \
    OUT_DIR="$out_dir" \
    DATA_PATH="$DATA_PATH" \
    TOKENIZER_PATH="$TOKENIZER_PATH" \
    ITERATIONS=500 \
    TRAIN_BATCH_TOKENS=8192 \
    TRAIN_LOG_EVERY=50 \
    VAL_BATCH_SIZE=524288 \
    VAL_LOSS_EVERY=0 \
    TIED_EMBED_LR="$tied_embed_lr" \
    MATRIX_LR="$matrix_lr" \
    SCALAR_LR="$scalar_lr" \
    .venv/bin/python train_gpt_mlx.py
  )
}

run_candidate "lr100-control" "0.05" "0.04" "0.04"
run_candidate "lr090-down10" "0.045" "0.036" "0.036"
run_candidate "lr110-up10" "0.055" "0.044" "0.044"
