# ABOUTME: Parses Parameter Golf training logs into reusable metric summaries and observation rows.
# ABOUTME: Gives Sohail minimal score-audit helpers before confirmatory runs and promotions.

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


STEP_TRAIN_RE = re.compile(
    r"step:(?P<step>\d+)/(?P<total>\d+)\s+train_loss:(?P<train_loss>[-+]?\d+(?:\.\d+)?)"
)
STEP_VAL_RE = re.compile(
    r"step:(?P<step>\d+)/(?P<total>\d+)\s+val_loss:(?P<val_loss>[-+]?\d+(?:\.\d+)?)\s+val_bpb:(?P<val_bpb>[-+]?\d+(?:\.\d+)?)"
)
FINAL_EXACT_RE = re.compile(
    r"final_int8_zlib_roundtrip_exact\s+val_loss:(?P<val_loss>[-+]?\d+(?:\.\d+)?)\s+val_bpb:(?P<val_bpb>[-+]?\d+(?:\.\d+)?)"
)
FINAL_ROUNDED_RE = re.compile(
    r"final_int8_zlib_roundtrip\s+val_loss:(?P<val_loss>[-+]?\d+(?:\.\d+)?)\s+val_bpb:(?P<val_bpb>[-+]?\d+(?:\.\d+)?)"
)


def extract_train_points(log_text: str) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for match in STEP_TRAIN_RE.finditer(log_text):
        points.append(
            {
                "step": int(match.group("step")),
                "total_steps": int(match.group("total")),
                "train_loss": float(match.group("train_loss")),
            }
        )
    return points


def extract_val_points(log_text: str) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for match in STEP_VAL_RE.finditer(log_text):
        points.append(
            {
                "step": int(match.group("step")),
                "total_steps": int(match.group("total")),
                "val_loss": float(match.group("val_loss")),
                "val_bpb": float(match.group("val_bpb")),
            }
        )
    return points


def extract_final_exact(log_text: str) -> dict[str, float] | None:
    match = FINAL_EXACT_RE.search(log_text)
    if match is None:
        return None
    return {
        "val_loss": float(match.group("val_loss")),
        "val_bpb": float(match.group("val_bpb")),
    }


def extract_final_rounded(log_text: str) -> dict[str, float] | None:
    match = FINAL_ROUNDED_RE.search(log_text)
    if match is None:
        return None
    return {
        "val_loss": float(match.group("val_loss")),
        "val_bpb": float(match.group("val_bpb")),
    }


def summarize_log_text(log_text: str) -> dict[str, Any]:
    train_points = extract_train_points(log_text)
    val_points = extract_val_points(log_text)
    best_step = None if not val_points else min(val_points, key=lambda item: item["val_bpb"])
    return {
        "train_points": train_points,
        "val_points": val_points,
        "best_step_val_bpb": best_step,
        "final_exact": extract_final_exact(log_text),
        "final_rounded": extract_final_rounded(log_text),
    }


def summarize_log_file(path: Path) -> dict[str, Any]:
    return summarize_log_text(path.read_text(encoding="utf-8"))


def build_metric_rows(log_text: str) -> list[dict[str, Any]]:
    summary = summarize_log_text(log_text)
    rows: list[dict[str, Any]] = []
    for point in summary["train_points"]:
        rows.append(
            {
                "metric_name": "train_loss",
                "metric_value": point["train_loss"],
                "step": point["step"],
                "split": "train",
                "objective": "min",
                "note": "step log",
            }
        )
    for point in summary["val_points"]:
        rows.append(
            {
                "metric_name": "val_loss",
                "metric_value": point["val_loss"],
                "step": point["step"],
                "split": "validation",
                "objective": "min",
                "note": "step log",
            }
        )
        rows.append(
            {
                "metric_name": "val_bpb",
                "metric_value": point["val_bpb"],
                "step": point["step"],
                "split": "validation",
                "objective": "min",
                "note": "step log",
            }
        )
    final_exact = summary["final_exact"]
    if final_exact is not None:
        rows.append(
            {
                "metric_name": "val_loss",
                "metric_value": final_exact["val_loss"],
                "step": None,
                "split": "validation",
                "objective": "min",
                "note": "final exact",
            }
        )
        rows.append(
            {
                "metric_name": "val_bpb",
                "metric_value": final_exact["val_bpb"],
                "step": None,
                "split": "validation",
                "objective": "min",
                "note": "final exact",
            }
        )
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("log_path")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    summary = summarize_log_file(Path(args.log_path))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
