# ABOUTME: Snapshots promoted experiment files into the immutable iteration archive and updates leaderboard.md.
# ABOUTME: Enforces Sohail's requirement that meaningful revisions be tracked as full-file snapshots with atomic changes.

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = ROOT / "iterations" / "archive"
GOLDEN_ROOT = ROOT / "iterations" / "golden"
LEADERBOARD = ROOT / "leaderboard.md"
START_MARKER = "<!-- leaderboard:entries:start -->"
END_MARKER = "<!-- leaderboard:entries:end -->"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iteration-id", required=True)
    parser.add_argument("--parent", default="none")
    parser.add_argument("--lane", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--metric", default="n/a")
    parser.add_argument("--change", required=True, help="atomic change summary")
    parser.add_argument("--notes", default="none")
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help="file to snapshot; may be passed multiple times",
    )
    parser.add_argument(
        "--promote-golden",
        action="store_true",
        help="copy the archived snapshot into iterations/golden/<iteration-id>",
    )
    return parser


def resolve_source_paths(raw_paths: list[str]) -> list[Path]:
    resolved: list[Path] = []
    for raw_path in raw_paths:
        path = Path(raw_path)
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        if not path.is_file():
            raise SystemExit(f"source file not found: {raw_path}")
        resolved.append(path)
    return resolved


def relative_snapshot_path(path: Path) -> Path:
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return Path(path.name)


def write_iteration_readme(
    iteration_dir: Path,
    iteration_id: str,
    parent: str,
    lane: str,
    status: str,
    metric: str,
    change: str,
    notes: str,
    sources: list[Path],
) -> None:
    source_lines = "\n".join(f"- `{relative_snapshot_path(path)}`" for path in sources)
    contents = f"""# {iteration_id}

## Metadata

- Parent: `{parent}`
- Lane: `{lane}`
- Status: `{status}`
- Metric: `{metric}`
- Atomic change: {change}
- Notes: {notes}

## Snapshot Contents

{source_lines}
"""
    (iteration_dir / "README.md").write_text(contents, encoding="utf-8")


def snapshot_sources(iteration_dir: Path, sources: list[Path]) -> None:
    files_root = iteration_dir / "files"
    for source in sources:
        target = files_root / relative_snapshot_path(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def append_leaderboard_row(
    iteration_id: str,
    parent: str,
    lane: str,
    status: str,
    metric: str,
    change: str,
) -> None:
    text = LEADERBOARD.read_text(encoding="utf-8")
    if iteration_id in text:
        raise SystemExit(f"iteration already registered: {iteration_id}")
    row = (
        f"| {iteration_id} | {parent} | {lane} | {status} | {metric} | "
        f"{change} | `iterations/archive/{iteration_id}/` |"
    )
    if START_MARKER not in text or END_MARKER not in text:
        raise SystemExit("leaderboard markers missing")
    before, rest = text.split(START_MARKER, maxsplit=1)
    middle, after = rest.split(END_MARKER, maxsplit=1)
    existing_rows = middle.rstrip()
    if existing_rows:
        updated_middle = f"{existing_rows}\n{row}\n"
    else:
        updated_middle = f"\n{row}\n"
    updated = f"{before}{START_MARKER}{updated_middle}{END_MARKER}{after}"
    LEADERBOARD.write_text(updated, encoding="utf-8")


def promote_to_golden(iteration_id: str, iteration_dir: Path) -> None:
    target = GOLDEN_ROOT / iteration_id
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(iteration_dir, target)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    iteration_dir = ARCHIVE_ROOT / args.iteration_id
    if iteration_dir.exists():
        raise SystemExit(f"iteration already exists: {args.iteration_id}")
    sources = resolve_source_paths(args.source)
    snapshot_sources(iteration_dir, sources)
    write_iteration_readme(
        iteration_dir=iteration_dir,
        iteration_id=args.iteration_id,
        parent=args.parent,
        lane=args.lane,
        status=args.status,
        metric=args.metric,
        change=args.change,
        notes=args.notes,
        sources=sources,
    )
    append_leaderboard_row(
        iteration_id=args.iteration_id,
        parent=args.parent,
        lane=args.lane,
        status=args.status,
        metric=args.metric,
        change=args.change,
    )
    if args.promote_golden:
        promote_to_golden(args.iteration_id, iteration_dir)


if __name__ == "__main__":
    main()
