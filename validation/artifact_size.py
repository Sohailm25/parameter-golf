# ABOUTME: Computes simple artifact-size audits for files that may count toward Parameter Golf limits.
# ABOUTME: Gives Sohail a reusable byte-accounting helper before promotions or submission packaging.

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Any


DEFAULT_BYTE_CAP = 16_000_000


def total_bytes(paths: Iterable[Path]) -> int:
    return sum(path.stat().st_size for path in paths)


def build_artifact_audit(paths: Iterable[Path], byte_cap: int = DEFAULT_BYTE_CAP) -> dict[str, Any]:
    normalized_paths = [Path(path) for path in paths]
    total = total_bytes(normalized_paths)
    return {
        "byte_cap": byte_cap,
        "files": [str(path) for path in normalized_paths],
        "total_bytes": total,
        "within_cap": total <= byte_cap,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--byte-cap", type=int, default=DEFAULT_BYTE_CAP)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    audit = build_artifact_audit([Path(path) for path in args.paths], byte_cap=args.byte_cap)
    print(json.dumps(audit, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
