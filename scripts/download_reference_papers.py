# ABOUTME: Downloads papers listed in the local markdown manifest into the tracked papers cache directory.
# ABOUTME: Keeps reference acquisition reproducible and avoids ad hoc one-off paper downloads.

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from urllib.request import urlretrieve


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "background-work" / "papers" / "DOWNLOAD_MANIFEST.md"
OUTPUT_DIR = ROOT / "background-work" / "papers" / "files"


@dataclass(frozen=True)
class ManifestEntry:
    filename: str
    url: str
    note: str


def parse_manifest(path: Path) -> list[ManifestEntry]:
    entries: list[ManifestEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        stripped = line.strip()
        if stripped.startswith("|---") or "filename" in stripped.lower():
            continue
        columns = [part.strip() for part in stripped.strip("|").split("|")]
        if len(columns) != 3:
            continue
        filename, url, note = columns
        if not filename or not url:
            continue
        entries.append(ManifestEntry(filename=filename, url=url, note=note))
    return entries


def download_entries(entries: list[ManifestEntry], force: bool) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        target = OUTPUT_DIR / entry.filename
        if target.exists() and not force:
            print(f"skip {target.name} (already exists)")
            continue
        print(f"download {entry.filename} <- {entry.url}")
        urlretrieve(entry.url, target)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        action="store_true",
        help="re-download files even if they already exist",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    entries = parse_manifest(MANIFEST)
    if not entries:
        raise SystemExit("no manifest entries found")
    download_entries(entries, force=args.force)


if __name__ == "__main__":
    main()
