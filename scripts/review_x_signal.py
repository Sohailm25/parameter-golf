# ABOUTME: Reviews public X discussion about Parameter Golf using bird-cli and persists only higher-utility signal.
# ABOUTME: Keeps Sohail's iteration loop aware of public approach chatter without drowning the repo in promo noise.

from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "research" / "x_review_state.json"
LOG_PATH = ROOT / "research" / "x_review_log.md"
SNAPSHOT_DIR = ROOT / "research" / "x_snapshots"

DEFAULT_QUERIES = [
    '"parameter-golf" OR "parameter golf" OR val_bpb',
    '("parameter-golf" OR "parameter golf") (sliding window OR seq4096 OR tokenizer OR vocab OR int6 OR quantization OR recurrence OR ttt OR "test-time training" OR autoresearch)',
    '(fineweb OR val_bpb) ("bits per byte" OR bpb OR quantization OR tokenizer OR recurrence)',
]

SIGNAL_KEYWORDS = [
    "val_bpb",
    "bpb",
    "val_loss",
    "steps",
    "sliding window",
    "stride",
    "seq4096",
    "tokenizer",
    "vocab",
    "quantization",
    "int6",
    "ternary",
    "recurrence",
    "recurrent",
    "ttt",
    "test-time training",
    "dynamic eval",
    "autoresearch",
    "l40s",
    "h100",
    "relu^2",
    "silu",
    "swiglu",
    "geglu",
    "attnres",
]

PROMO_KEYWORDS = [
    "free trial",
    "$49",
    "skool",
    "course",
    "live deep dive",
    "learn ai research",
    "subscribe",
    "link in description",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_text(value: str | None) -> str:
    return (value or "").lower()


def build_empty_state() -> dict[str, Any]:
    return {
        "last_full_scan_at": "",
        "queries": list(DEFAULT_QUERIES),
        "seen_tweet_ids": [],
        "tweets": {},
    }


def load_state(path: Path = STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        return build_empty_state()
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any], path: Path = STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_bird_output(raw_output: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    for index, char in enumerate(raw_output):
        if char != "[":
            continue
        try:
            payload, _ = decoder.raw_decode(raw_output[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, list):
            return payload
    raise ValueError("could not parse JSON payload from bird output")


def score_tweet_signal(tweet: dict[str, Any]) -> int:
    text = normalize_text(tweet.get("text"))
    score = 0
    if any(keyword in text for keyword in SIGNAL_KEYWORDS):
        score += sum(1 for keyword in SIGNAL_KEYWORDS if keyword in text[:500])
    if re.search(r"\b1\.\d{3,4}\b", text):
        score += 3
    if re.search(r"\b\d+\s*steps?\b", text):
        score += 2
    if "github.com" in text or "arxiv.org" in text:
        score += 2
    if tweet.get("likeCount", 0) >= 5:
        score += 1
    if any(keyword in text for keyword in PROMO_KEYWORDS):
        score -= 5
    return score


def utility_label(signal_score: int) -> str:
    if signal_score >= 7:
        return "high"
    if signal_score >= 3:
        return "medium"
    return "low"


def tweet_url(tweet: dict[str, Any]) -> str:
    username = tweet.get("author", {}).get("username", "unknown")
    return f"https://x.com/{username}/status/{tweet['id']}"


def run_bird_search(
    query: str,
    count: int = 10,
    bird_bin: str = "bird",
) -> list[dict[str, Any]]:
    completed = subprocess.run(
        [bird_bin, "search", "--json", "-n", str(count), query],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "bird search failed")
    return parse_bird_output(completed.stdout)


def merge_tweet_into_state(
    state: dict[str, Any],
    tweet: dict[str, Any],
    query: str,
    scan_time: str,
) -> dict[str, Any]:
    state = copy.deepcopy(state)
    tweet_id = str(tweet["id"])
    existing = state["tweets"].get(tweet_id)
    source_queries = [] if existing is None else list(existing.get("source_queries", []))
    if query not in source_queries:
        source_queries.append(query)
    signal_score = score_tweet_signal(tweet)
    state["tweets"][tweet_id] = {
        "id": tweet_id,
        "text": tweet.get("text", ""),
        "author_username": tweet.get("author", {}).get("username", ""),
        "author_name": tweet.get("author", {}).get("name", ""),
        "created_at": tweet.get("createdAt", ""),
        "reply_count": tweet.get("replyCount", 0),
        "retweet_count": tweet.get("retweetCount", 0),
        "like_count": tweet.get("likeCount", 0),
        "signal_score": signal_score,
        "utility": utility_label(signal_score),
        "url": tweet_url(tweet),
        "source_queries": source_queries,
        "first_seen_at": scan_time if existing is None else existing["first_seen_at"],
        "last_seen_at": scan_time,
        "notes_path": f"research/x_snapshots/tweet-{tweet_id}.md",
    }
    return state


def finalize_state(state: dict[str, Any], scan_time: str, queries: list[str]) -> dict[str, Any]:
    state = copy.deepcopy(state)
    state["last_full_scan_at"] = scan_time
    state["queries"] = queries
    state["seen_tweet_ids"] = sorted(state["tweets"].keys())
    return state


def render_snapshot_markdown(entry: dict[str, Any]) -> str:
    source_queries = ", ".join(f"`{item}`" for item in entry["source_queries"]) or "none"
    return textwrap.dedent(
        f"""\
        # Tweet {entry['id']}

        - URL: {entry['url']}
        - Author: `{entry['author_username']}` ({entry['author_name']})
        - Created at: `{entry['created_at']}`
        - Utility: `{entry['utility']}`
        - Signal score: `{entry['signal_score']}`
        - Source queries: {source_queries}

        {entry['text']}
        """
    )


def write_snapshots(state: dict[str, Any], snapshot_dir: Path = SNAPSHOT_DIR) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for entry in state["tweets"].values():
        path = snapshot_dir / f"tweet-{entry['id']}.md"
        path.write_text(render_snapshot_markdown(entry), encoding="utf-8")


def summarize_scan(previous_state: dict[str, Any], new_state: dict[str, Any]) -> list[str]:
    previous_ids = set(previous_state["tweets"].keys())
    new_ids = [tweet_id for tweet_id in new_state["tweets"].keys() if tweet_id not in previous_ids]
    return sorted(new_ids)


def append_log(
    previous_state: dict[str, Any],
    new_state: dict[str, Any],
    scan_time: str,
    path: Path = LOG_PATH,
) -> None:
    lines = []
    if path.exists():
        lines.append(path.read_text(encoding="utf-8").rstrip())
    else:
        lines.append("# X Review Log\n")
    new_ids = summarize_scan(previous_state, new_state)
    surfaced = [
        entry for entry in new_state["tweets"].values() if entry["last_seen_at"] == scan_time
    ]
    surfaced.sort(key=lambda item: (-item["signal_score"], item["id"]))
    lines.append(f"\n## {scan_time} X review")
    if not surfaced:
        lines.append("- Result: no high-utility tweets passed the current filter.")
    else:
        if new_ids:
            lines.append("- New tweet IDs: " + ", ".join(f"`{tweet_id}`" for tweet_id in new_ids))
        for entry in surfaced[:5]:
            lines.append(
                f"- `{entry['utility']}` score `{entry['signal_score']}`: "
                f"[{entry['author_username']}]({entry['url']})"
            )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--min-score", type=int, default=3)
    parser.add_argument("--bird-bin", default="bird")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    scan_time = utc_now_iso()
    queries = args.query or list(DEFAULT_QUERIES)
    previous_state = load_state()
    state = build_empty_state()
    kept_ids: set[str] = set()
    for query in queries:
        for tweet in run_bird_search(query=query, count=args.count, bird_bin=args.bird_bin):
            if score_tweet_signal(tweet) < args.min_score:
                continue
            state = merge_tweet_into_state(state, tweet, query=query, scan_time=scan_time)
            kept_ids.add(str(tweet["id"]))
    for tweet_id, entry in previous_state.get("tweets", {}).items():
        if tweet_id not in kept_ids:
            state["tweets"][tweet_id] = entry
    state = finalize_state(state, scan_time=scan_time, queries=queries)
    save_state(state)
    write_snapshots(state)
    append_log(previous_state, state, scan_time=scan_time)


if __name__ == "__main__":
    main()
