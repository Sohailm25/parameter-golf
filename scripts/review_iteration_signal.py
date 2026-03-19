# ABOUTME: Runs the repo's iteration-intelligence hooks in one stable sequence.
# ABOUTME: Gives Sohail a single command for PR, X, and arXiv review before or after atomic experiments.

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def build_commands(
    lane: str,
    phase: str,
    topic: str,
    skip_pr: bool = False,
    skip_x: bool = False,
    skip_arxiv: bool = False,
) -> list[list[str]]:
    python_bin = sys.executable
    commands: list[list[str]] = []
    if not skip_pr:
        commands.append([python_bin, str(ROOT / "scripts" / "review_openai_prs.py")])
    if not skip_x:
        commands.append([python_bin, str(ROOT / "scripts" / "review_x_signal.py")])
    if not skip_arxiv:
        command = [
            python_bin,
            str(ROOT / "scripts" / "review_arxiv.py"),
            "--lane",
            lane,
            "--phase",
            phase,
        ]
        if topic:
            command.extend(["--topic", topic])
        commands.append(command)
    return commands


def run_commands(commands: list[list[str]]) -> None:
    for command in commands:
        subprocess.run(command, check=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", default="evaluation")
    parser.add_argument("--phase", default="pre", choices=["pre", "post"])
    parser.add_argument("--topic", default="")
    parser.add_argument("--skip-pr", action="store_true")
    parser.add_argument("--skip-x", action="store_true")
    parser.add_argument("--skip-arxiv", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    commands = build_commands(
        lane=args.lane,
        phase=args.phase,
        topic=args.topic,
        skip_pr=args.skip_pr,
        skip_x=args.skip_x,
        skip_arxiv=args.skip_arxiv,
    )
    run_commands(commands)


if __name__ == "__main__":
    main()
