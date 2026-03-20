# ABOUTME: Plans flat-stream evaluation windows for non-overlapping and sliding-window accounting.
# ABOUTME: Keeps evaluation semantics explicit so Sohail can verify which targets are scored exactly once.

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class EvalWindow:
    begin: int
    end: int
    score_start: int


def build_flat_stream_windows(*, total_targets: int, seq_len: int, stride: int) -> list[EvalWindow]:
    if total_targets <= 0:
        raise ValueError(f"total_targets must be positive, got {total_targets}")
    if seq_len <= 0:
        raise ValueError(f"seq_len must be positive, got {seq_len}")
    if stride <= 0:
        raise ValueError(f"stride must be positive, got {stride}")
    if stride > seq_len:
        raise ValueError(f"stride must be <= seq_len, got stride={stride} seq_len={seq_len}")

    windows: list[EvalWindow] = []
    previous_end = 0
    cursor = seq_len
    while previous_end < total_targets:
        end = min(cursor, total_targets)
        begin = max(end - seq_len, 0)
        windows.append(EvalWindow(begin=begin, end=end, score_start=previous_end))
        previous_end = end
        cursor += stride
    return windows


def local_score_starts(windows: list[EvalWindow]) -> list[int]:
    return [window.score_start - window.begin for window in windows]


def build_suffix_mask(local_starts: list[int], window_len: int) -> np.ndarray:
    if window_len <= 0:
        raise ValueError(f"window_len must be positive, got {window_len}")
    if not local_starts:
        raise ValueError("local_starts must not be empty")
    starts = np.asarray(local_starts, dtype=np.int32)
    if np.any(starts < 0):
        raise ValueError(f"local_starts must be non-negative, got {local_starts}")
    if np.any(starts > window_len):
        raise ValueError(f"local_starts must be <= window_len, got {local_starts} window_len={window_len}")
    columns = np.arange(window_len, dtype=np.int32)
    return columns[None, :] >= starts[:, None]
