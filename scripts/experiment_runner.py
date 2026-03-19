# ABOUTME: Runs the repo's standard experiment loop from preflight review through telemetry ingestion and optional promotion.
# ABOUTME: Prevents Sohail's experiment discipline from depending on memory or ad hoc shell history.

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validation.log_audit import build_metric_rows, summarize_log_file

SCRATCHPAD_PATH = ROOT / "SCRATCHPAD.md"
RESULTS_INDEX_PATH = ROOT / "results" / "RESULTS_INDEX.md"
REGISTER_RUN_PATH = ROOT / "scripts" / "register_run.py"
REGISTER_ITERATION_PATH = ROOT / "scripts" / "register_iteration.py"
REVIEW_SIGNAL_PATH = ROOT / "scripts" / "review_iteration_signal.py"
RENDER_DASHBOARD_PATH = ROOT / "scripts" / "render_progress_dashboard.py"
RESULTS_INDEX_SECTIONS = {
    "architecture": "Architecture",
    "autoresearch": "Autoresearch",
    "baselines": "Baselines",
    "compression": "Compression",
    "evaluation": "Evaluation",
    "figures": "Figures",
    "golden": "Golden",
    "infrastructure": "Infrastructure",
    "optimizer_sweeps": "Optimizer Sweeps",
    "quantization": "Quantization",
    "tokenizer": "Tokenizer",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name} module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_env_pairs(pairs: list[str]) -> dict[str, str]:
    env: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"env pair must be KEY=VALUE: {pair}")
        key, value = pair.split("=", maxsplit=1)
        if not key.strip():
            raise SystemExit(f"env key missing: {pair}")
        env[key.strip()] = value
    return env


def current_git_branch() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def current_git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def resolve_script_path(script_path: str) -> Path:
    candidate = Path(script_path)
    if candidate.is_absolute():
        return candidate
    return (ROOT / candidate).resolve()


def default_log_path(script_path: str, run_id: str, env: dict[str, str]) -> str:
    script_name = Path(script_path).name
    if script_name == "train_gpt_mlx.py":
        out_dir = env.get("OUT_DIR", "logs")
        return str(Path(out_dir) / f"{run_id}.txt")
    return str(Path("logs") / f"{run_id}.txt")


def build_launch_plan(
    *,
    lane: str,
    label: str,
    issue_id: str,
    topic: str,
    script_path: str,
    script_args: list[str],
    env_pairs: list[str],
    branch: str,
    commit: str,
    device: str,
    horizon: str,
    phase: str,
) -> dict[str, Any]:
    register_run = load_module(REGISTER_RUN_PATH, "register_run")
    env = parse_env_pairs(env_pairs)
    run_id = register_run.build_run_id(lane, label)
    env["RUN_ID"] = run_id
    command = [sys.executable, str(resolve_script_path(script_path))]
    command.extend(script_args)
    return {
        "branch": branch,
        "command": command,
        "commit": commit,
        "device": device,
        "env": env,
        "horizon": horizon,
        "issue_id": issue_id,
        "label": label,
        "lane": lane,
        "log_path": default_log_path(script_path, run_id=run_id, env=env),
        "phase": phase,
        "run_id": run_id,
        "script_path": script_path,
        "topic": topic,
    }


def append_scratchpad_entry(scratchpad_path: Path, heading: str, lines: list[str]) -> None:
    scratchpad_path.parent.mkdir(parents=True, exist_ok=True)
    existing = scratchpad_path.read_text(encoding="utf-8") if scratchpad_path.exists() else "# Scratchpad\n"
    timestamp = utc_now_iso()
    section = [f"\n## [{timestamp}] {heading}"]
    section.extend(lines)
    scratchpad_path.write_text(existing.rstrip() + "\n" + "\n".join(section) + "\n", encoding="utf-8")


def append_results_index_note(
    *,
    results_index_path: Path,
    result_path: str,
    lane: str,
    status: str,
    summary: str,
) -> None:
    text = results_index_path.read_text(encoding="utf-8")
    row = f"| {summary} | {lane} | {status} | `{result_path}` |"
    if row in text:
        return
    section_title = RESULTS_INDEX_SECTIONS.get(lane)
    if section_title is None:
        raise SystemExit(f"unknown results lane: {lane}")
    lines = text.splitlines()
    section_header = f"## {section_title}"
    try:
        section_index = lines.index(section_header)
    except ValueError as error:
        raise SystemExit(f"results section missing: {section_header}") from error
    insert_at = section_index + 3
    while insert_at < len(lines) and not lines[insert_at].startswith("## "):
        insert_at += 1
    lines.insert(insert_at, row)
    results_index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_promotion_link_records(
    *,
    run_id: str,
    iteration_id: str,
    result_path: str,
    created_at: str,
) -> list[dict[str, Any]]:
    register_run = load_module(REGISTER_RUN_PATH, "register_run")
    records = [
        register_run.build_link_record(
            source_type="run",
            source_id=run_id,
            relation="promoted_to",
            target_type="iteration",
            target_id=iteration_id,
            note="promoted via experiment runner",
            created_at=created_at,
        )
    ]
    if result_path:
        records.append(
            register_run.build_link_record(
                source_type="run",
                source_id=run_id,
                relation="documented_in",
                target_type="result_artifact",
                target_id=result_path,
                note="result artifact cited during promotion",
                created_at=created_at,
            )
        )
    return records


def build_log_link_record(*, run_id: str, log_path: str, created_at: str) -> dict[str, Any]:
    register_run = load_module(REGISTER_RUN_PATH, "register_run")
    return register_run.build_link_record(
        source_type="run",
        source_id=run_id,
        relation="logged_to",
        target_type="run_log",
        target_id=log_path,
        note="training log produced via experiment runner",
        created_at=created_at,
    )


def build_run_outcome_metric_rows(
    *,
    returncode: int,
    ingested_metric_rows: int,
    log_bytes: int | None,
) -> list[dict[str, Any]]:
    rows = [
        {
            "metric_name": "process_returncode",
            "metric_value": float(returncode),
            "step": None,
            "split": "meta",
            "objective": "min",
            "note": "subprocess exit code",
        },
        {
            "metric_name": "ingested_metric_rows",
            "metric_value": float(ingested_metric_rows),
            "step": None,
            "split": "meta",
            "objective": "max",
            "note": "number of metric observations parsed from the log",
        },
    ]
    if log_bytes is not None:
        rows.append(
            {
                "metric_name": "log_bytes",
                "metric_value": float(log_bytes),
                "step": None,
                "split": "meta",
                "objective": "max",
                "note": "training log size in bytes",
            }
        )
    return rows


def register_run_record(plan: dict[str, Any], notes: str) -> None:
    register_run = load_module(REGISTER_RUN_PATH, "register_run")
    record = register_run.build_run_record(
        run_id=plan["run_id"],
        lane=plan["lane"],
        label=plan["label"],
        horizon=plan["horizon"],
        status="launched",
        created_at=utc_now_iso(),
        notes=notes,
        issue_id=plan["issue_id"],
        branch=plan["branch"],
        commit=plan["commit"],
        device=plan["device"],
        script_paths=[plan["script_path"]],
        config_paths=[],
        tags=[plan["phase"]],
        train_budget_seconds=None,
        artifact_budget_mb=None,
        seed=None,
    )
    register_run.append_jsonl_record(register_run.RUN_REGISTRY, record, unique_key="run_id")


def register_log_metrics(run_id: str, log_path: Path) -> int:
    register_run = load_module(REGISTER_RUN_PATH, "register_run")
    rows = build_metric_rows(log_path.read_text(encoding="utf-8"))
    recorded_at = utc_now_iso()
    count = 0
    for row in rows:
        record = register_run.build_metric_record(
            run_id=run_id,
            metric_name=row["metric_name"],
            metric_value=row["metric_value"],
            step=row["step"],
            split=row["split"],
            axis_scale="linear",
            objective=row["objective"],
            note=row["note"],
            recorded_at=recorded_at,
        )
        register_run.append_jsonl_record(
            register_run.METRIC_REGISTRY,
            record,
            unique_key="observation_id",
        )
        count += 1
    return count


def register_metric_rows(run_id: str, rows: list[dict[str, Any]]) -> int:
    register_run = load_module(REGISTER_RUN_PATH, "register_run")
    recorded_at = utc_now_iso()
    count = 0
    for row in rows:
        record = register_run.build_metric_record(
            run_id=run_id,
            metric_name=row["metric_name"],
            metric_value=row["metric_value"],
            step=row["step"],
            split=row["split"],
            axis_scale="linear",
            objective=row["objective"],
            note=row["note"],
            recorded_at=recorded_at,
        )
        register_run.append_jsonl_record(
            register_run.METRIC_REGISTRY,
            record,
            unique_key="observation_id",
        )
        count += 1
    return count


def register_link_record(record: dict[str, Any]) -> None:
    register_run = load_module(REGISTER_RUN_PATH, "register_run")
    register_run.append_jsonl_record(register_run.LINK_REGISTRY, record, unique_key="link_id")


def run_review_hooks(lane: str, phase: str, topic: str) -> None:
    subprocess.run(
        [
            sys.executable,
            str(REVIEW_SIGNAL_PATH),
            "--lane",
            lane,
            "--phase",
            phase,
            "--topic",
            topic,
        ],
        cwd=ROOT,
        check=True,
    )


def render_dashboard() -> Path:
    result = subprocess.run(
        [sys.executable, str(RENDER_DASHBOARD_PATH)],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
    )
    return Path(result.stdout.strip())


def launch_experiment(args: argparse.Namespace) -> None:
    plan = build_launch_plan(
        lane=args.lane,
        label=args.label,
        issue_id=args.issue_id,
        topic=args.topic,
        script_path=args.script_path,
        script_args=args.script_arg,
        env_pairs=args.env,
        branch=args.branch or current_git_branch(),
        commit=args.commit or current_git_commit(),
        device=args.device,
        horizon=args.horizon,
        phase=args.phase,
    )
    command_string = " ".join(shlex.quote(part) for part in plan["command"])
    env_string = " ".join(f"{key}={value}" for key, value in sorted(plan["env"].items()))
    append_scratchpad_entry(
        SCRATCHPAD_PATH,
        heading=f"PRE-RUN: {args.label}",
        lines=[
            f"- Command: `{env_string} {command_string}`",
            f"- Device: `{args.device}`",
            f"- Lane: `{args.lane}`",
            f"- Issue: `{args.issue_id}`",
            f"- Horizon: `{args.horizon}`",
            f"- Topic: `{args.topic or 'none'}`",
            f"- Log path: `{plan['log_path']}`",
            f"- What I'm testing: {args.notes or args.label}",
        ],
    )
    if not args.skip_review:
        run_review_hooks(lane=args.lane, phase=args.phase, topic=args.topic)
    register_run_record(plan, notes=args.notes)
    child_env = os.environ.copy()
    child_env.update(plan["env"])
    result = subprocess.run(plan["command"], cwd=ROOT, env=child_env, check=False)
    log_path = ROOT / plan["log_path"]
    ingested_count = 0
    if log_path.exists() and not args.skip_ingest:
        ingested_count = register_log_metrics(plan["run_id"], log_path)
    if log_path.exists():
        register_link_record(
            build_log_link_record(
                run_id=plan["run_id"],
                log_path=plan["log_path"],
                created_at=utc_now_iso(),
            )
        )
    outcome_metric_rows = build_run_outcome_metric_rows(
        returncode=result.returncode,
        ingested_metric_rows=ingested_count,
        log_bytes=log_path.stat().st_size if log_path.exists() else None,
    )
    register_metric_rows(plan["run_id"], outcome_metric_rows)
    dashboard_path = None
    if not args.skip_dashboard:
        dashboard_path = render_dashboard()
    append_scratchpad_entry(
        SCRATCHPAD_PATH,
        heading=f"POST-RUN: {args.label}",
        lines=[
            f"- Run ID: `{plan['run_id']}`",
            f"- Outcome: `{'SUCCESS' if result.returncode == 0 else 'FAILURE'}`",
            f"- Log path: `{plan['log_path']}`",
            f"- Metric rows ingested: `{ingested_count}`",
            f"- Dashboard: `{dashboard_path if dashboard_path is not None else 'skipped'}`",
            f"- Next step: inspect the run, then promote with `scripts/experiment_runner.py promote` if warranted",
        ],
    )
    print(
        json.dumps(
            {
                "dashboard_path": None if dashboard_path is None else str(dashboard_path),
                "ingested_metric_rows": ingested_count,
                "log_path": plan["log_path"],
                "returncode": result.returncode,
                "run_id": plan["run_id"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def promote_experiment(args: argparse.Namespace) -> None:
    subprocess.run(
        [
            sys.executable,
            str(REGISTER_ITERATION_PATH),
            "--iteration-id",
            args.iteration_id,
            "--parent",
            args.parent,
            "--lane",
            args.lane,
            "--status",
            args.status,
            "--metric",
            args.metric,
            "--change",
            args.change,
            "--notes",
            args.notes,
            *sum([["--source", source] for source in args.source], []),
            *(["--promote-golden"] if args.promote_golden else []),
        ],
        cwd=ROOT,
        check=True,
    )
    for record in build_promotion_link_records(
        run_id=args.run_id,
        iteration_id=args.iteration_id,
        result_path=args.result_path,
        created_at=utc_now_iso(),
    ):
        register_link_record(record)
    if args.result_path:
        append_results_index_note(
            results_index_path=RESULTS_INDEX_PATH,
            result_path=args.result_path,
            lane=args.lane,
            status=args.status,
            summary=args.change,
        )
    dashboard_path = None if args.skip_dashboard else render_dashboard()
    print(
        json.dumps(
            {
                "dashboard_path": None if dashboard_path is None else str(dashboard_path),
                "iteration_id": args.iteration_id,
                "run_id": args.run_id,
            },
            indent=2,
            sort_keys=True,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    launch = subparsers.add_parser("launch")
    launch.add_argument("--lane", required=True)
    launch.add_argument("--label", required=True)
    launch.add_argument("--issue-id", required=True)
    launch.add_argument("--topic", default="")
    launch.add_argument("--script-path", required=True)
    launch.add_argument("--script-arg", action="append", default=[])
    launch.add_argument("--env", action="append", default=[])
    launch.add_argument("--branch", default="")
    launch.add_argument("--commit", default="")
    launch.add_argument("--device", default="local-m4")
    launch.add_argument("--horizon", default="smoke")
    launch.add_argument("--phase", default="pre", choices=["pre", "post"])
    launch.add_argument("--notes", default="")
    launch.add_argument("--skip-review", action="store_true")
    launch.add_argument("--skip-ingest", action="store_true")
    launch.add_argument("--skip-dashboard", action="store_true")

    promote = subparsers.add_parser("promote")
    promote.add_argument("--run-id", required=True)
    promote.add_argument("--iteration-id", required=True)
    promote.add_argument("--parent", default="none")
    promote.add_argument("--lane", required=True)
    promote.add_argument("--status", required=True)
    promote.add_argument("--metric", required=True)
    promote.add_argument("--change", required=True)
    promote.add_argument("--notes", default="none")
    promote.add_argument("--source", action="append", required=True)
    promote.add_argument("--result-path", default="")
    promote.add_argument("--promote-golden", action="store_true")
    promote.add_argument("--skip-dashboard", action="store_true")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "launch":
        launch_experiment(args)
        return
    if args.command == "promote":
        promote_experiment(args)
        return
    raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
