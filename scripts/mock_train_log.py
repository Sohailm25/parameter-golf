# ABOUTME: Writes a deterministic Parameter Golf-style training log for automation smoke tests.
# ABOUTME: Lets Sohail validate launch, ingestion, and dashboard plumbing without requiring the real dataset cache.

from __future__ import annotations

import os
from pathlib import Path


def main() -> None:
    run_id = os.environ.get("RUN_ID", "mock-run")
    out_dir = Path(os.environ.get("OUT_DIR", "logs"))
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / f"{run_id}.txt"
    lines = [
        "step:1/2 train_loss:2.5000 train_time:10ms step_avg:10.0ms",
        "step:2/2 val_loss:2.1000 val_bpb:1.2500 train_time:20ms step_avg:10.0ms",
        "final_int8_zlib_roundtrip val_loss:2.0500 val_bpb:1.2100 size:123456",
        "final_int8_zlib_roundtrip_exact val_loss:2.05000000 val_bpb:1.21000000",
    ]
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(log_path)


if __name__ == "__main__":
    main()
