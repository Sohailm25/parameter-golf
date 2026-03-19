# ABOUTME: Reviews official Parameter Golf pull requests, stores deduped state, and derives candidate atomic experiments.
# ABOUTME: Keeps the repo's frontier intelligence persistent so Sohail does not repeatedly reread the same PRs.

from __future__ import annotations

import argparse
import copy
import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "research" / "pr_review_state.json"
LOG_PATH = ROOT / "research" / "pr_review_log.md"
BACKLOG_PATH = ROOT / "research" / "atomic_experiment_backlog.md"
SNAPSHOT_DIR = ROOT / "research" / "pr_snapshots"

DEFAULT_REPO = "openai/parameter-golf"
DEFAULT_API_URL = "https://api.github.com/repos/{repo}/pulls?state=open&per_page={limit}"


CANDIDATE_RULES = [
    {
        "id": "eval-sliding-window-context-accounting",
        "lane": "evaluation",
        "title": "Sliding-window context accounting",
        "status": "candidate",
        "atomic_change": "Compare standard non-overlapping eval against stride-based sliding-window eval under fixed checkpoints.",
        "why": "Public PRs repeatedly show that sliding windows move BPB materially with zero artifact-cost changes.",
        "match_any": ["sliding window", "stride=64", "stride-64", "stride=256", "overlapping windows"],
    },
    {
        "id": "eval-document-isolated-sliding-window",
        "lane": "evaluation",
        "title": "Document-isolated sliding-window accounting",
        "status": "candidate",
        "atomic_change": "Measure flat-stream eval versus per-document eval with sliding windows before adding any evaluation-time adaptation.",
        "why": "PR #77's ablation suggests much of the gain comes from document isolation and windowing before TTT itself.",
        "match_all_groups": [
            ["document", "doc isolated", "doc-isolated", "document masking", "document boundaries"],
            ["sliding window", "stride-64", "stride=64", "overlapping windows", "chunk_size=256"],
        ],
    },
    {
        "id": "eval-document-reset-ttt",
        "lane": "evaluation",
        "title": "Document-reset TTT / dynamic-eval lane",
        "status": "candidate",
        "atomic_change": "Starting from document-isolated sliding-window eval, add score-before-update TTT with resets between documents using the smallest practical adapter or parameter subset.",
        "why": "The dynamic-eval memo and PR #77 both support reset-per-document adaptation as a real lane, but one that should stay separate from pure eval-accounting gains.",
        "match_all_groups": [
            [
                "ttt",
                "test-time training",
                "parameter nudging",
                "dynamic eval",
                "dynamic evaluation",
                "lora ttt",
            ],
            [
                "reset between documents",
                "reset per document",
                "per-document",
                "document masking",
                "document boundaries",
                "document",
            ],
        ],
    },
    {
        "id": "tok-vocab-scaling",
        "lane": "tokenizer",
        "title": "Tokenizer and vocabulary scaling",
        "status": "candidate",
        "atomic_change": "Compare `sp1024` against larger vocab variants such as `sp4096` and `sp8192` with explicit BPB accounting.",
        "why": "The frontier now shows real BPB improvements from larger vocabularies, and tokenizer cost accounting is still a live rules question.",
        "match_any": ["sp4096", "sp-4096", "sp8192", "8192 vocab", "vocab size", "larger vocabulary"],
    },
    {
        "id": "quant-selective-int6-fp16-embed",
        "lane": "quantization",
        "title": "Selective int6 plus fp16 embedding passthrough",
        "status": "candidate",
        "atomic_change": "Try int6 on large weight matrices while keeping the tied embedding or logit-sensitive tensors at higher precision.",
        "why": "Several PRs point to selective precision, not uniform quantization, as the practical near-term gain.",
        "match_any": [
            "int6",
            "mixed quantization",
            "selective quantization",
            "fp16 tied embedding",
            "fp16 embed",
            "mixed precision",
        ],
    },
    {
        "id": "ctx-seq4096-train-eval",
        "lane": "evaluation",
        "title": "Long-context seq4096 train/eval lane",
        "status": "candidate",
        "atomic_change": "Run a controlled `seq_len=4096` lane with matching evaluation to test whether fewer, richer steps beat shorter contexts locally.",
        "why": "Multiple PRs use `seq4096` and long-context evaluation as a strong baseline improvement path.",
        "match_any": ["seq4096", "train_seq_len=4096", "seq_len=4096", "eval@4096"],
    },
    {
        "id": "arch-depth-recurrence-iteration-embeddings",
        "lane": "architecture",
        "title": "Depth recurrence with iteration awareness",
        "status": "candidate",
        "atomic_change": "Test one recurrence design at a time: shared blocks plus iteration embeddings or per-pass normalization under fixed width and budget.",
        "why": "Recurrence remains a live architecture lane, but the public evidence is mixed enough that it should stay atomic and controlled.",
        "match_any": [
            "depth recurrence",
            "recurrent",
            "iteration embedding",
            "shared blocks",
            "weight sharing",
            "looped",
        ],
    },
    {
        "id": "quant-ternary-qat",
        "lane": "quantization",
        "title": "Ternary QAT stress test",
        "status": "candidate",
        "atomic_change": "Build one narrow ternary QAT lane and test whether the compression win survives practical training and evaluation under challenge constraints.",
        "why": "Ternary QAT is still high-upside but not yet grounded enough to be the repo default.",
        "match_any": ["ternary", "bitlinear", "1.58-bit", "{-1, 0, +1}", "{-1,0,+1}"],
    },
    {
        "id": "init-ntk-overtone-rope",
        "lane": "architecture",
        "title": "Initialization and NTK-aware RoPE lane",
        "status": "candidate",
        "atomic_change": "Test overtone-style embedding init, residual-mix initialization, and NTK-aware RoPE scaling independently before stacking.",
        "why": "PR #60 suggests there may still be cheap initialization and eval-context wins outside the dominant sliding-window recipes.",
        "match_any": ["overtone", "ntk", "rope scaling", "resid_mix", "phase-transition residual mixing"],
    },
    {
        "id": "tooling-local-sweeps-and-autoresearch",
        "lane": "autoresearch",
        "title": "Local sweep tooling and autoresearch ingestion",
        "status": "candidate",
        "atomic_change": "Create a trustworthy local proxy and let agentic or scripted sweeps explore only one controlled subspace at a time.",
        "why": "PRs #66 and #80 show that better local tooling can change iteration speed even when absolute BPB is not competitive yet.",
        "match_any": ["autoresearch", "local sweep", "fast local dataset", "aria", "agent harness"],
    },
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_empty_state(repo: str = DEFAULT_REPO) -> dict[str, Any]:
    return {
        "repo": repo,
        "last_full_scan_at": "",
        "last_reviewed_updated_at": "",
        "seen_pr_numbers": [],
        "seen_commit_shas": [],
        "pull_requests": {},
        "candidate_experiments": {},
    }


def load_state(path: Path = STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        return build_empty_state()
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any], path: Path = STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_open_pull_requests(repo: str = DEFAULT_REPO, limit: int = 100) -> list[dict[str, Any]]:
    url = DEFAULT_API_URL.format(repo=repo, limit=limit)
    request = Request(url, headers={"User-Agent": "parametergolf-pr-review"})
    with urlopen(request) as response:
        return json.load(response)


def normalize_text(value: str | None) -> str:
    return (value or "").lower()


def primary_body_text(body: str | None) -> str:
    body = body or ""
    lowered = normalize_text(body)
    cut_markers = [
        "## what we tried and rejected",
        "### what we tried and rejected",
        "## rejected",
        "### rejected",
    ]
    cutoff = len(body)
    for marker in cut_markers:
        index = lowered.find(marker)
        if index != -1:
            cutoff = min(cutoff, index)
    return body[:cutoff]


def match_any(text: str, patterns: list[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def match_all_groups(text: str, groups: list[list[str]]) -> bool:
    return all(any(pattern in text for pattern in group) for group in groups)


def derive_candidate_matches(pr: dict[str, Any]) -> list[dict[str, Any]]:
    body = primary_body_text(pr.get("body", ""))
    text = normalize_text(f"{pr.get('title', '')}\n{body}")
    matches: list[dict[str, Any]] = []
    for rule in CANDIDATE_RULES:
        matched = False
        if rule.get("match_any"):
            matched = match_any(text, rule["match_any"])
        if rule.get("match_all_groups"):
            matched = matched or match_all_groups(text, rule["match_all_groups"])
        if matched:
            matches.append(rule)
    return matches


def derive_lane_tags(pr: dict[str, Any]) -> list[str]:
    return sorted({rule["lane"] for rule in derive_candidate_matches(pr)})


def merge_candidate_experiment(
    state: dict[str, Any],
    rule: dict[str, Any],
    pr_number: int,
) -> None:
    candidate_experiments = state["candidate_experiments"]
    experiment = candidate_experiments.get(rule["id"])
    existing_source_prs = [] if experiment is None else list(experiment.get("source_prs", []))
    existing_bd_issue_id = "" if experiment is None else experiment.get("bd_issue_id", "")
    experiment = {
        "title": rule["title"],
        "lane": rule["lane"],
        "status": rule["status"],
        "atomic_change": rule["atomic_change"],
        "why_it_matters": rule["why"],
        "source_prs": existing_source_prs,
        "bd_issue_id": existing_bd_issue_id,
    }
    if pr_number not in experiment["source_prs"]:
        experiment["source_prs"].append(pr_number)
        experiment["source_prs"].sort()
    candidate_experiments[rule["id"]] = experiment


def merge_pull_request_into_state(
    state: dict[str, Any],
    pr: dict[str, Any],
    scan_time: str,
) -> dict[str, Any]:
    state = copy.deepcopy(state)
    pr_number = str(pr["number"])
    head_sha = pr["head"]["sha"]
    updated_at = pr["updated_at"]
    existing = state["pull_requests"].get(pr_number)

    if existing is None:
        status = "new"
        first_seen_at = scan_time
    else:
        first_seen_at = existing["first_seen_at"]
        if existing["head_sha"] != head_sha or existing["updated_at"] != updated_at:
            status = "recheck_needed"
        else:
            status = existing["status"]

    candidate_matches = derive_candidate_matches(pr)
    candidate_ids: list[str] = []
    for rule in candidate_matches:
        merge_candidate_experiment(state, rule, pr["number"])
        candidate_ids.append(rule["id"])

    state["pull_requests"][pr_number] = {
        "number": pr["number"],
        "title": pr["title"],
        "url": pr["html_url"],
        "author": pr["user"]["login"],
        "updated_at": updated_at,
        "head_sha": head_sha,
        "status": status,
        "lane_tags": derive_lane_tags(pr),
        "candidate_experiment_ids": candidate_ids,
        "notes_path": f"research/pr_snapshots/pr-{pr['number']:04d}.md",
        "first_seen_at": first_seen_at,
        "last_seen_at": scan_time,
    }
    return state


def finalize_state(
    state: dict[str, Any],
    scan_time: str,
    mark_reviewed: bool,
) -> dict[str, Any]:
    state = copy.deepcopy(state)
    state["last_full_scan_at"] = scan_time
    state["last_reviewed_updated_at"] = max(
        (pr["updated_at"] for pr in state["pull_requests"].values()),
        default="",
    )
    state["seen_pr_numbers"] = sorted(int(number) for number in state["pull_requests"].keys())
    state["seen_commit_shas"] = sorted(
        {pr["head_sha"] for pr in state["pull_requests"].values() if pr.get("head_sha")}
    )
    if mark_reviewed:
        for pr in state["pull_requests"].values():
            if pr["status"] in {"new", "recheck_needed"}:
                pr["status"] = "reviewed"
    return state


def render_snapshot_markdown(pr_entry: dict[str, Any]) -> str:
    candidates = ", ".join(f"`{item}`" for item in pr_entry["candidate_experiment_ids"]) or "none"
    lanes = ", ".join(f"`{item}`" for item in pr_entry["lane_tags"]) or "none"
    return textwrap.dedent(
        f"""\
        # PR #{pr_entry['number']}

        - Title: {pr_entry['title']}
        - URL: {pr_entry['url']}
        - Author: `{pr_entry['author']}`
        - Updated at: `{pr_entry['updated_at']}`
        - Head SHA: `{pr_entry['head_sha']}`
        - Status: `{pr_entry['status']}`
        - Lane tags: {lanes}
        - Candidate experiment IDs: {candidates}
        """
    )


def write_snapshots(state: dict[str, Any], snapshot_dir: Path = SNAPSHOT_DIR) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for pr in state["pull_requests"].values():
        path = snapshot_dir / f"pr-{pr['number']:04d}.md"
        path.write_text(render_snapshot_markdown(pr), encoding="utf-8")


def render_backlog_markdown(state: dict[str, Any]) -> str:
    header = textwrap.dedent(
        """\
        # Atomic Experiment Backlog

        This file is deduped from the official PR review state. It is planning input, not a result ledger.

        | Experiment ID | Lane | Status | Source PRs | Atomic change to test | Why it matters | bd issue |
        |---|---|---|---|---|---|---|
        """
    )
    rows = []
    for experiment_id in sorted(state["candidate_experiments"].keys()):
        experiment = state["candidate_experiments"][experiment_id]
        source_prs = ", ".join(f"#{number}" for number in experiment["source_prs"])
        bd_issue = experiment.get("bd_issue_id") or ""
        rows.append(
            f"| `{experiment_id}` | `{experiment['lane']}` | `{experiment['status']}` | {source_prs} | "
            f"{experiment['atomic_change']} | {experiment['why_it_matters']} | {bd_issue} |"
        )
    return header + ("\n".join(rows) + "\n" if rows else "")


def write_backlog(state: dict[str, Any], path: Path = BACKLOG_PATH) -> None:
    path.write_text(render_backlog_markdown(state), encoding="utf-8")


def summarize_scan(
    previous_state: dict[str, Any],
    new_state: dict[str, Any],
) -> tuple[list[int], list[int], list[str]]:
    previous_prs = previous_state["pull_requests"]
    new_prs = new_state["pull_requests"]
    new_numbers = sorted(int(number) for number in new_prs.keys() if number not in previous_prs)
    rereview_numbers = sorted(
        int(number)
        for number, pr in new_prs.items()
        if previous_prs.get(number) and previous_prs[number]["head_sha"] != pr["head_sha"]
    )
    previous_candidates = set(previous_state["candidate_experiments"].keys())
    new_candidates = sorted(set(new_state["candidate_experiments"].keys()) - previous_candidates)
    return new_numbers, rereview_numbers, new_candidates


def append_review_log(
    previous_state: dict[str, Any],
    new_state: dict[str, Any],
    scan_time: str,
    path: Path = LOG_PATH,
) -> None:
    new_numbers, rereview_numbers, new_candidates = summarize_scan(previous_state, new_state)
    lines = []
    if path.exists():
        lines.append(path.read_text(encoding="utf-8").rstrip())
    else:
        lines.append("# PR Review Log\n")
    lines.append(f"\n## {scan_time} official PR review")
    if not new_numbers and not rereview_numbers and not new_candidates:
        lines.append("- Result: no new PRs or re-review triggers.")
    else:
        if new_numbers:
            lines.append("- New PRs: " + ", ".join(f"#{number}" for number in new_numbers))
        if rereview_numbers:
            lines.append("- Re-review needed: " + ", ".join(f"#{number}" for number in rereview_numbers))
        if new_candidates:
            lines.append("- New candidate experiments: " + ", ".join(f"`{item}`" for item in new_candidates))
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument(
        "--no-mark-reviewed",
        action="store_true",
        help="leave touched PRs as new or recheck_needed after the scan",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    scan_time = utc_now_iso()
    previous_state = load_state()
    state = copy.deepcopy(previous_state)
    state["repo"] = args.repo
    for pr in fetch_open_pull_requests(repo=args.repo, limit=args.limit):
        state = merge_pull_request_into_state(state, pr, scan_time=scan_time)
    state = finalize_state(state, scan_time=scan_time, mark_reviewed=not args.no_mark_reviewed)
    save_state(state)
    write_snapshots(state)
    write_backlog(state)
    append_review_log(previous_state, state, scan_time=scan_time)


if __name__ == "__main__":
    main()
