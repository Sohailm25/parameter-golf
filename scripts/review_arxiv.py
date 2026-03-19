# ABOUTME: Reviews relevant arXiv papers for the current experiment lane and drains Sohail's queued research questions.
# ABOUTME: Keeps iteration planning informed by recent papers while forcing queued curiosities to be executed and cleared.

from __future__ import annotations

import argparse
import copy
import json
import re
import textwrap
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "research" / "arxiv_review_state.json"
LOG_PATH = ROOT / "research" / "arxiv_review_log.md"
QUERY_PATH = ROOT / "research" / "research-queries.md"
SNAPSHOT_DIR = ROOT / "research" / "arxiv_snapshots"
ARXIV_API_URL = "https://export.arxiv.org/api/query?search_query={query}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
RELEVANT_CATEGORIES = {"cs.LG", "cs.CL", "stat.ML", "cs.AI", "cs.NE"}

LANE_QUERIES = {
    "evaluation": [
        '"dynamic evaluation" transformer language model',
        '"test-time training" transformer language model',
        '"online adaptation" "large language models"',
    ],
    "optimizer_sweeps": [
        '"large batch" language model optimization',
        'learning rate schedule transformer training',
        'small language model optimization',
    ],
    "tokenizer": [
        'tokenizer compression language model',
        '"sentencepiece" language model compression',
        '"bits per byte" tokenizer language model',
    ],
    "quantization": [
        'quantization-aware training language model',
        'ternary language model quantization',
        'low-bit transformer quantization',
    ],
    "architecture": [
        'recurrent transformer weight sharing',
        'depth recurrence transformer',
        'parameter sharing transformer language model',
    ],
    "autoresearch": [
        'automatic research agent machine learning experimentation',
        'hyperparameter search language model training',
        'experiment selection machine learning',
    ],
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_empty_state() -> dict[str, Any]:
    return {
        "last_full_scan_at": "",
        "seen_paper_ids": [],
        "last_drained_queries": [],
        "papers": {},
    }


def load_state(path: Path = STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        return build_empty_state()
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any], path: Path = STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def research_queries_template() -> str:
    return textwrap.dedent(
        """\
        # Research Queries

        Pending questions to drain on the next arXiv review. Add one bullet per query.

        ## Pending

        ## Notes

        - `scripts/review_arxiv.py` clears the pending section only after all queued queries were executed.
        - Use this file for follow-up questions that should not be forgotten between experiments.
        """
    )


def load_pending_queries(path: Path = QUERY_PATH) -> list[str]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(research_queries_template(), encoding="utf-8")
        return []
    queries: list[str] = []
    in_pending = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "## Pending":
            in_pending = True
            continue
        if line.startswith("## ") and line != "## Pending":
            in_pending = False
        if not in_pending:
            continue
        if line.startswith("- [ ] "):
            queries.append(line[6:].strip())
        elif line.startswith("- "):
            queries.append(line[2:].strip())
    return [query for query in queries if query]


def clear_pending_queries(path: Path = QUERY_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(research_queries_template(), encoding="utf-8")


def default_queries_for_lane(lane: str, topic: str) -> list[str]:
    queries = list(LANE_QUERIES.get(lane, LANE_QUERIES["evaluation"]))
    if topic:
        queries.insert(0, topic)
    deduped: list[str] = []
    for query in queries:
        if query not in deduped:
            deduped.append(query)
    return deduped


def build_arxiv_search_query(query: str) -> str:
    if "all:" in query:
        return urllib.parse.quote(query)
    phrase_matches = re.findall(r'"([^"]+)"', query)
    remainder = re.sub(r'"[^"]+"', " ", query)
    terms = []
    for phrase in phrase_matches:
        cleaned = phrase.strip()
        if cleaned and cleaned not in terms:
            terms.append(cleaned)
    for raw_term in re.split(r"[^a-zA-Z0-9\-\+]+", remainder):
        cleaned = raw_term.strip()
        if len(cleaned) < 3:
            continue
        lowered = cleaned.lower()
        if lowered in {"and", "the", "for", "with"}:
            continue
        if cleaned not in terms:
            terms.append(cleaned)
    return urllib.parse.quote(" AND ".join(f'all:"{term}"' for term in terms))


def parse_atom_feed(xml_text: str) -> list[dict[str, Any]]:
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    root = ElementTree.fromstring(xml_text)
    entries: list[dict[str, Any]] = []
    for entry in root.findall("atom:entry", namespace):
        links = entry.findall("atom:link", namespace)
        alternate_link = ""
        for link in links:
            if link.attrib.get("rel") == "alternate":
                alternate_link = link.attrib.get("href", "")
                break
        category_terms = [item.attrib.get("term", "") for item in entry.findall("atom:category", namespace)]
        paper_id = (entry.findtext("atom:id", default="", namespaces=namespace) or "").rsplit("/", maxsplit=1)[-1]
        entries.append(
            {
                "arxiv_id": paper_id,
                "title": " ".join((entry.findtext("atom:title", default="", namespaces=namespace) or "").split()),
                "summary": " ".join((entry.findtext("atom:summary", default="", namespaces=namespace) or "").split()),
                "updated": entry.findtext("atom:updated", default="", namespaces=namespace) or "",
                "published": entry.findtext("atom:published", default="", namespaces=namespace) or "",
                "authors": [
                    author.findtext("atom:name", default="", namespaces=namespace) or ""
                    for author in entry.findall("atom:author", namespace)
                ],
                "url": alternate_link,
                "categories": [term for term in category_terms if term],
            }
        )
    return entries


def fetch_arxiv_entries(query: str, max_results: int = 3) -> list[dict[str, Any]]:
    encoded_query = build_arxiv_search_query(query)
    url = ARXIV_API_URL.format(query=encoded_query, max_results=max_results)
    request = Request(url, headers={"User-Agent": "parametergolf-arxiv-review"})
    with urlopen(request) as response:
        xml_text = response.read().decode("utf-8")
    return parse_atom_feed(xml_text)


def normalize_text(value: str | None) -> str:
    return (value or "").lower()


def is_ml_relevant_paper(paper: dict[str, Any]) -> bool:
    return any(category in RELEVANT_CATEGORIES for category in paper.get("categories", []))


def score_paper(paper: dict[str, Any], lane: str, topic: str) -> int:
    text = normalize_text(" ".join([paper.get("title", ""), paper.get("summary", "")]))
    score = 0
    for term in normalize_text(topic).split():
        if term and term in text:
            score += 2
    for query in default_queries_for_lane(lane, topic=""):
        for term in normalize_text(query).replace('"', "").split():
            if term and term in text:
                score += 1
    if any(category.startswith("cs.") for category in paper.get("categories", [])):
        score += 1
    return score


def select_top_papers(
    papers: list[dict[str, Any]],
    lane: str,
    topic: str,
    max_papers: int,
) -> list[dict[str, Any]]:
    filtered = [paper for paper in papers if is_ml_relevant_paper(paper)]
    if filtered:
        papers = filtered
    scored = sorted(
        papers,
        key=lambda paper: (score_paper(paper, lane=lane, topic=topic), paper.get("updated", "")),
        reverse=True,
    )
    selected: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for paper in scored:
        if paper["arxiv_id"] in seen_ids:
            continue
        seen_ids.add(paper["arxiv_id"])
        selected.append(paper)
        if len(selected) >= max_papers:
            break
    return selected


def carry_forward_relevant_papers(
    previous_state: dict[str, Any],
    selected_ids: set[str],
) -> dict[str, dict[str, Any]]:
    carried: dict[str, dict[str, Any]] = {}
    for paper_id, entry in previous_state.get("papers", {}).items():
        if paper_id in selected_ids:
            continue
        if not is_ml_relevant_paper(entry):
            continue
        carried[paper_id] = entry
    return carried


def merge_paper_into_state(
    state: dict[str, Any],
    paper: dict[str, Any],
    query: str,
    scan_time: str,
) -> dict[str, Any]:
    state = copy.deepcopy(state)
    paper_id = paper["arxiv_id"]
    existing = state["papers"].get(paper_id)
    source_queries = [] if existing is None else list(existing.get("source_queries", []))
    if query not in source_queries:
        source_queries.append(query)
    state["papers"][paper_id] = {
        "arxiv_id": paper_id,
        "title": paper["title"],
        "summary": paper["summary"],
        "updated": paper["updated"],
        "published": paper["published"],
        "authors": paper["authors"],
        "url": paper["url"],
        "categories": paper["categories"],
        "source_queries": source_queries,
        "first_seen_at": scan_time if existing is None else existing["first_seen_at"],
        "last_seen_at": scan_time,
        "notes_path": f"research/arxiv_snapshots/{paper_id.replace('/', '_')}.md",
    }
    return state


def finalize_state(
    state: dict[str, Any],
    scan_time: str,
    drained_queries: list[str],
) -> dict[str, Any]:
    state = copy.deepcopy(state)
    state["last_full_scan_at"] = scan_time
    state["last_drained_queries"] = drained_queries
    state["seen_paper_ids"] = sorted(state["papers"].keys())
    return state


def render_snapshot_markdown(entry: dict[str, Any]) -> str:
    authors = ", ".join(entry["authors"]) or "unknown"
    categories = ", ".join(f"`{item}`" for item in entry["categories"]) or "none"
    source_queries = ", ".join(f"`{item}`" for item in entry["source_queries"]) or "none"
    return textwrap.dedent(
        f"""\
        # {entry['arxiv_id']}

        - Title: {entry['title']}
        - URL: {entry['url']}
        - Authors: {authors}
        - Updated: `{entry['updated']}`
        - Categories: {categories}
        - Source queries: {source_queries}

        {entry['summary']}
        """
    )


def write_snapshots(state: dict[str, Any], snapshot_dir: Path = SNAPSHOT_DIR) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for entry in state["papers"].values():
        path = snapshot_dir / f"{entry['arxiv_id'].replace('/', '_')}.md"
        path.write_text(render_snapshot_markdown(entry), encoding="utf-8")


def append_log(
    previous_state: dict[str, Any],
    new_state: dict[str, Any],
    scan_time: str,
    lane: str,
    phase: str,
    topic: str,
    drained_queries: list[str],
    path: Path = LOG_PATH,
) -> None:
    lines = []
    if path.exists():
        lines.append(path.read_text(encoding="utf-8").rstrip())
    else:
        lines.append("# arXiv Review Log\n")
    lines.append(f"\n## {scan_time} arXiv review")
    lines.append(f"- Lane: `{lane}`")
    lines.append(f"- Phase: `{phase}`")
    if topic:
        lines.append(f"- Topic: `{topic}`")
    if drained_queries:
        lines.append("- Drained research queries: " + ", ".join(f"`{item}`" for item in drained_queries))
    previous_ids = set(previous_state["papers"].keys())
    surfaced = [
        paper for paper in new_state["papers"].values() if paper["last_seen_at"] == scan_time
    ]
    if not surfaced:
        lines.append("- Result: no papers were selected.")
    else:
        new_ids = [paper["arxiv_id"] for paper in surfaced if paper["arxiv_id"] not in previous_ids]
        if new_ids:
            lines.append("- New paper IDs: " + ", ".join(f"`{item}`" for item in new_ids))
        for paper in surfaced:
            lines.append(f"- [{paper['title']}]({paper['url']})")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", default="evaluation")
    parser.add_argument("--phase", default="pre", choices=["pre", "post"])
    parser.add_argument("--topic", default="")
    parser.add_argument("--results-per-query", type=int, default=3)
    parser.add_argument("--max-papers", type=int, default=5)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    scan_time = utc_now_iso()
    pending_queries = load_pending_queries()
    base_queries = default_queries_for_lane(args.lane, args.topic)
    combined_queries = []
    for query in base_queries + pending_queries:
        if query not in combined_queries:
            combined_queries.append(query)
    all_papers: list[tuple[str, dict[str, Any]]] = []
    for query in combined_queries:
        for paper in fetch_arxiv_entries(query, max_results=args.results_per_query):
            all_papers.append((query, paper))
    clear_pending_queries()
    selected = select_top_papers(
        [paper for _, paper in all_papers],
        lane=args.lane,
        topic=args.topic,
        max_papers=args.max_papers,
    )
    selected_ids = {paper["arxiv_id"] for paper in selected}
    previous_state = load_state()
    state = build_empty_state()
    state["papers"].update(carry_forward_relevant_papers(previous_state, selected_ids=selected_ids))
    for query, paper in all_papers:
        if paper["arxiv_id"] not in selected_ids:
            continue
        state = merge_paper_into_state(state, paper, query=query, scan_time=scan_time)
    state = finalize_state(state, scan_time=scan_time, drained_queries=pending_queries)
    save_state(state)
    write_snapshots(state)
    append_log(
        previous_state,
        state,
        scan_time=scan_time,
        lane=args.lane,
        phase=args.phase,
        topic=args.topic,
        drained_queries=pending_queries,
    )


if __name__ == "__main__":
    main()
