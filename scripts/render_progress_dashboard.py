# ABOUTME: Renders a repeatable HTML dashboard from append-only experiment telemetry.
# ABOUTME: Gives Sohail a durable visualization of research progression without overwriting prior renders.

from __future__ import annotations

import argparse
import html
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TELEMETRY_ROOT = ROOT / "results" / "telemetry"
RUN_REGISTRY = TELEMETRY_ROOT / "run_registry.jsonl"
METRIC_REGISTRY = TELEMETRY_ROOT / "metric_observations.jsonl"
LINK_REGISTRY = TELEMETRY_ROOT / "id_links.jsonl"
RENDER_REGISTRY = TELEMETRY_ROOT / "render_registry.jsonl"
FIGURES_ROOT = ROOT / "results" / "figures" / "renders"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def append_jsonl_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def build_line_chart_svg(observations: list[dict[str, Any]]) -> str:
    width = 700
    height = 260
    margin = 28
    val_bpb = [
        item
        for item in observations
        if item.get("metric_name") == "val_bpb" and item.get("metric_value") is not None
    ]
    if not val_bpb:
        return "<p>No val_bpb observations yet.</p>"
    sorted_points = sorted(
        val_bpb,
        key=lambda item: (item.get("recorded_at", ""), item.get("step") if item.get("step") is not None else -1),
    )
    best_so_far: list[tuple[int, float]] = []
    running_best: float | None = None
    for index, item in enumerate(sorted_points):
        value = float(item["metric_value"])
        running_best = value if running_best is None else min(running_best, value)
        best_so_far.append((index, running_best))
    x_values = [point[0] for point in best_so_far]
    y_values = [point[1] for point in best_so_far]
    x_min = min(x_values)
    x_max = max(x_values)
    y_min = min(y_values)
    y_max = max(y_values)
    if x_min == x_max:
        x_max += 1
    if y_min == y_max:
        y_max += 1
    coords: list[str] = []
    for x_raw, y_raw in best_so_far:
        x = margin + ((x_raw - x_min) / (x_max - x_min)) * (width - (margin * 2))
        y = height - margin - ((y_raw - y_min) / (y_max - y_min)) * (height - (margin * 2))
        coords.append(f"{x:.1f},{y:.1f}")
    points = " ".join(coords)
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="best val_bpb over time">'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#f7f2e8" rx="18"/>'
        f'<line x1="{margin}" y1="{height - margin}" x2="{width - margin}" y2="{height - margin}" stroke="#6b5c4c" stroke-width="2"/>'
        f'<line x1="{margin}" y1="{margin}" x2="{margin}" y2="{height - margin}" stroke="#6b5c4c" stroke-width="2"/>'
        f'<polyline fill="none" stroke="#115e59" stroke-width="4" points="{points}"/>'
        "</svg>"
    )


def build_lane_bar_chart_svg(runs: list[dict[str, Any]]) -> str:
    width = 700
    height = 260
    margin = 28
    counts = Counter(run.get("lane", "unknown") for run in runs)
    if not counts:
        return "<p>No runs registered yet.</p>"
    lanes = sorted(counts)
    max_count = max(counts.values()) or 1
    bar_width = max(40, int((width - margin * 2) / max(len(lanes), 1)) - 18)
    bars: list[str] = []
    labels: list[str] = []
    for index, lane in enumerate(lanes):
        value = counts[lane]
        x = margin + index * (bar_width + 18)
        usable_height = height - margin * 2 - 30
        bar_height = (value / max_count) * usable_height
        y = height - margin - bar_height - 20
        bars.append(
            f'<rect x="{x}" y="{y:.1f}" width="{bar_width}" height="{bar_height:.1f}" fill="#b45309" rx="10"/>'
        )
        labels.append(
            f'<text x="{x + (bar_width / 2):.1f}" y="{height - margin}" text-anchor="middle" fill="#3f2d1f" font-size="12">{html.escape(lane)}</text>'
        )
        labels.append(
            f'<text x="{x + (bar_width / 2):.1f}" y="{y - 6:.1f}" text-anchor="middle" fill="#3f2d1f" font-size="12">{value}</text>'
        )
    return (
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="run count by lane">'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#f7f2e8" rx="18"/>'
        f'<line x1="{margin}" y1="{height - margin - 20}" x2="{width - margin}" y2="{height - margin - 20}" stroke="#6b5c4c" stroke-width="2"/>'
        + "".join(bars)
        + "".join(labels)
        + "</svg>"
    )


def build_recent_run_rows(runs: list[dict[str, Any]], observations: list[dict[str, Any]]) -> str:
    metric_by_run: dict[str, dict[str, Any]] = {}
    for observation in observations:
        if observation.get("metric_name") != "val_bpb":
            continue
        run_id = observation.get("run_id", "")
        current = metric_by_run.get(run_id)
        if current is None or float(observation["metric_value"]) < float(current["metric_value"]):
            metric_by_run[run_id] = observation
    sorted_runs = sorted(runs, key=lambda item: item.get("created_at", ""), reverse=True)
    rows: list[str] = []
    for run in sorted_runs[:10]:
        best = metric_by_run.get(run.get("run_id", ""))
        best_value = "" if best is None else best.get("metric_value", "")
        rows.append(
            "<tr>"
            f"<td>{html.escape(run.get('run_id', ''))}</td>"
            f"<td>{html.escape(run.get('lane', ''))}</td>"
            f"<td>{html.escape(run.get('horizon', ''))}</td>"
            f"<td>{html.escape(run.get('label', ''))}</td>"
            f"<td>{html.escape(str(best_value))}</td>"
            "</tr>"
        )
    return "".join(rows) or "<tr><td colspan='5'>No runs registered yet.</td></tr>"


def build_dashboard_html(
    *,
    runs: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    links: list[dict[str, Any]],
    generated_at: str,
) -> str:
    summary_items = {
        "run_count": len(runs),
        "metric_count": len(observations),
        "link_count": len(links),
    }
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Telemetry Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f2eadf;
      --panel: #fff8ef;
      --ink: #1f2933;
      --muted: #6b7280;
      --accent: #115e59;
      --accent-2: #b45309;
      --stroke: #d7c8b6;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", serif;
      background:
        radial-gradient(circle at top left, rgba(17,94,89,0.15), transparent 35%),
        radial-gradient(circle at top right, rgba(180,83,9,0.18), transparent 30%),
        var(--bg);
      color: var(--ink);
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 40px 20px 64px;
    }}
    h1, h2 {{ margin: 0 0 14px; }}
    p {{ line-height: 1.5; }}
    .hero {{
      background: rgba(255,248,239,0.82);
      border: 1px solid var(--stroke);
      border-radius: 28px;
      padding: 28px;
      backdrop-filter: blur(14px);
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-top: 18px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--stroke);
      border-radius: 22px;
      padding: 18px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 18px;
      margin-top: 18px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      padding: 10px 8px;
      border-bottom: 1px solid var(--stroke);
      vertical-align: top;
    }}
    .muted {{ color: var(--muted); }}
    svg {{ width: 100%; height: auto; display: block; }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>Telemetry Dashboard</h1>
      <p class="muted">Generated at {html.escape(generated_at)}. All charts are built from append-only JSONL telemetry.</p>
      <div class="summary">
        <article class="card"><h2>{summary_items["run_count"]}</h2><p class="muted">Registered runs</p></article>
        <article class="card"><h2>{summary_items["metric_count"]}</h2><p class="muted">Metric observations</p></article>
        <article class="card"><h2>{summary_items["link_count"]}</h2><p class="muted">Cross-artifact links</p></article>
      </div>
    </section>
    <section class="grid">
      <article class="card">
        <h2>Best val_bpb Over Time</h2>
        {build_line_chart_svg(observations)}
      </article>
      <article class="card">
        <h2>Run Count By Lane</h2>
        {build_lane_bar_chart_svg(runs)}
      </article>
    </section>
    <section class="card" style="margin-top: 18px;">
      <h2>Recent Runs</h2>
      <table>
        <thead>
          <tr>
            <th>Run ID</th>
            <th>Lane</th>
            <th>Horizon</th>
            <th>Label</th>
            <th>Best val_bpb</th>
          </tr>
        </thead>
        <tbody>
          {build_recent_run_rows(runs, observations)}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def render_dashboard(
    *,
    runs: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    links: list[dict[str, Any]],
    manifest_path: Path,
    figures_root: Path,
    generated_at: str,
) -> Path:
    safe_stamp = generated_at.replace(":", "").replace("-", "").lower().replace("t", "-").replace("z", "")
    render_dir = figures_root / f"{safe_stamp}-dashboard"
    suffix = 1
    while render_dir.exists():
        suffix += 1
        render_dir = figures_root / f"{safe_stamp}-dashboard-{suffix}"
    render_dir.mkdir(parents=True, exist_ok=False)
    render_path = render_dir / "index.html"
    render_path.write_text(
        build_dashboard_html(
            runs=runs,
            observations=observations,
            links=links,
            generated_at=generated_at,
        ),
        encoding="utf-8",
    )
    append_jsonl_record(
        manifest_path,
        {
            "dashboard_path": str(render_path.relative_to(ROOT)) if render_path.is_relative_to(ROOT) else str(render_path),
            "generated_at": generated_at,
            "link_count": len(links),
            "observation_count": len(observations),
            "render_id": render_dir.name,
            "run_count": len(runs),
        },
    )
    return render_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated-at", default="")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    generated_at = args.generated_at or utc_now_iso()
    render_path = render_dashboard(
        runs=load_jsonl_records(RUN_REGISTRY),
        observations=load_jsonl_records(METRIC_REGISTRY),
        links=load_jsonl_records(LINK_REGISTRY),
        manifest_path=RENDER_REGISTRY,
        figures_root=FIGURES_ROOT,
        generated_at=generated_at,
    )
    print(render_path)


if __name__ == "__main__":
    main()
