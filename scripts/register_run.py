# ABOUTME: Registers append-only run, metric, and ID-link telemetry for Parameter Golf experiments.
# ABOUTME: Keeps Sohail's experiment history queryable across runs, iterations, papers, and rendered dashboards.

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TELEMETRY_ROOT = ROOT / "results" / "telemetry"
RUN_REGISTRY = TELEMETRY_ROOT / "run_registry.jsonl"
METRIC_REGISTRY = TELEMETRY_ROOT / "metric_observations.jsonl"
LINK_REGISTRY = TELEMETRY_ROOT / "id_links.jsonl"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-") or "run"


def build_run_id(lane: str, label: str, created_at: str | None = None) -> str:
    timestamp = (created_at or utc_now_iso()).replace(":", "").replace("-", "").lower()
    timestamp = timestamp.replace("t", "-").replace("z", "")
    return f"{timestamp}-{slugify(lane)}-{slugify(label)}"


def load_jsonl_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def append_jsonl_record(path: Path, record: dict[str, Any], unique_key: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if unique_key:
        existing_records = load_jsonl_records(path)
        existing_values = {item.get(unique_key) for item in existing_records}
        value = record.get(unique_key)
        if value in existing_values:
            raise SystemExit(f"duplicate {unique_key}: {value}")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def build_run_record(
    *,
    run_id: str,
    lane: str,
    label: str,
    horizon: str,
    status: str,
    created_at: str,
    notes: str,
    issue_id: str,
    branch: str,
    commit: str,
    device: str,
    script_paths: list[str],
    config_paths: list[str],
    tags: list[str],
    train_budget_seconds: int | None,
    artifact_budget_mb: float | None,
    seed: int | None,
) -> dict[str, Any]:
    return {
        "artifact_budget_mb": artifact_budget_mb,
        "branch": branch,
        "commit": commit,
        "config_paths": config_paths,
        "created_at": created_at,
        "device": device,
        "horizon": horizon,
        "issue_id": issue_id,
        "label": label,
        "lane": lane,
        "notes": notes,
        "run_id": run_id,
        "script_paths": script_paths,
        "seed": seed,
        "status": status,
        "tags": tags,
        "train_budget_seconds": train_budget_seconds,
    }


def build_metric_record(
    *,
    run_id: str,
    metric_name: str,
    metric_value: float,
    step: int | None,
    split: str,
    axis_scale: str,
    objective: str,
    note: str,
    recorded_at: str,
) -> dict[str, Any]:
    observation_id = (
        f"{run_id}:{metric_name}:{step if step is not None else 'na'}:{recorded_at}"
    )
    return {
        "axis_scale": axis_scale,
        "metric_name": metric_name,
        "metric_value": metric_value,
        "note": note,
        "objective": objective,
        "observation_id": observation_id,
        "recorded_at": recorded_at,
        "run_id": run_id,
        "split": split,
        "step": step,
    }


def build_link_record(
    *,
    source_type: str,
    source_id: str,
    relation: str,
    target_type: str,
    target_id: str,
    note: str,
    created_at: str,
) -> dict[str, Any]:
    return {
        "created_at": created_at,
        "link_id": f"{source_type}:{source_id}:{relation}:{target_type}:{target_id}",
        "note": note,
        "relation": relation,
        "source_id": source_id,
        "source_type": source_type,
        "target_id": target_id,
        "target_type": target_type,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--run-id", default="")
    run_parser.add_argument("--lane", required=True)
    run_parser.add_argument("--label", required=True)
    run_parser.add_argument("--horizon", default="proxy")
    run_parser.add_argument("--status", default="planned")
    run_parser.add_argument("--notes", default="")
    run_parser.add_argument("--issue-id", default="")
    run_parser.add_argument("--branch", default="")
    run_parser.add_argument("--commit", default="")
    run_parser.add_argument("--device", default="local")
    run_parser.add_argument("--script-path", action="append", default=[])
    run_parser.add_argument("--config-path", action="append", default=[])
    run_parser.add_argument("--tag", action="append", default=[])
    run_parser.add_argument("--train-budget-seconds", type=int)
    run_parser.add_argument("--artifact-budget-mb", type=float)
    run_parser.add_argument("--seed", type=int)

    metric_parser = subparsers.add_parser("metric")
    metric_parser.add_argument("--run-id", required=True)
    metric_parser.add_argument("--metric-name", required=True)
    metric_parser.add_argument("--metric-value", required=True, type=float)
    metric_parser.add_argument("--step", type=int)
    metric_parser.add_argument("--split", default="unspecified")
    metric_parser.add_argument("--axis-scale", default="linear", choices=["linear", "log"])
    metric_parser.add_argument("--objective", default="unknown", choices=["min", "max", "unknown"])
    metric_parser.add_argument("--note", default="")

    link_parser = subparsers.add_parser("link")
    link_parser.add_argument("--source-type", required=True)
    link_parser.add_argument("--source-id", required=True)
    link_parser.add_argument("--relation", required=True)
    link_parser.add_argument("--target-type", required=True)
    link_parser.add_argument("--target-id", required=True)
    link_parser.add_argument("--note", default="")

    return parser


def register_run(args: argparse.Namespace) -> None:
    created_at = utc_now_iso()
    run_id = args.run_id or build_run_id(args.lane, args.label, created_at=created_at)
    record = build_run_record(
        run_id=run_id,
        lane=args.lane,
        label=args.label,
        horizon=args.horizon,
        status=args.status,
        created_at=created_at,
        notes=args.notes,
        issue_id=args.issue_id,
        branch=args.branch,
        commit=args.commit,
        device=args.device,
        script_paths=args.script_path,
        config_paths=args.config_path,
        tags=args.tag,
        train_budget_seconds=args.train_budget_seconds,
        artifact_budget_mb=args.artifact_budget_mb,
        seed=args.seed,
    )
    append_jsonl_record(RUN_REGISTRY, record, unique_key="run_id")
    print(run_id)


def register_metric(args: argparse.Namespace) -> None:
    record = build_metric_record(
        run_id=args.run_id,
        metric_name=args.metric_name,
        metric_value=args.metric_value,
        step=args.step,
        split=args.split,
        axis_scale=args.axis_scale,
        objective=args.objective,
        note=args.note,
        recorded_at=utc_now_iso(),
    )
    append_jsonl_record(METRIC_REGISTRY, record, unique_key="observation_id")
    print(record["observation_id"])


def register_link(args: argparse.Namespace) -> None:
    record = build_link_record(
        source_type=args.source_type,
        source_id=args.source_id,
        relation=args.relation,
        target_type=args.target_type,
        target_id=args.target_id,
        note=args.note,
        created_at=utc_now_iso(),
    )
    append_jsonl_record(LINK_REGISTRY, record, unique_key="link_id")
    print(record["link_id"])


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "run":
        register_run(args)
        return
    if args.command == "metric":
        register_metric(args)
        return
    if args.command == "link":
        register_link(args)
        return
    raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
