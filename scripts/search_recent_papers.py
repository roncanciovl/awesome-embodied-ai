"""
Searches recent (2025-2026) arXiv papers on Embodied AI, VLA and ROS 2 + AI.
"""

import urllib.request
import urllib.parse
import re
import time

HEADERS = {"User-Agent": "paper-search/1.0 (research)"}

QUERIES = [
    ("ROS 2 + Language Models", 'all:"ROS 2" AND all:"language model"'),
    ("LLM + Robot Manipulation 2025-2026", 'all:"large language model" AND all:"robot manipulation" AND submittedDate:[202501 TO 202612]'),
    ("VLA + ROS", 'all:"vision-language-action" AND all:"ROS"'),
    ("LLM + Robot Navigation 2025-2026", 'all:"large language model" AND all:"robot navigation" AND submittedDate:[202501 TO 202612]'),
]


def search_arxiv(query: str, max_results: int = 10):
    """Search the arXiv API and return a list of (id, date, title)."""
    url = (
        "http://export.arxiv.org/api/query?"
        + urllib.parse.urlencode({
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        })
    )
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read().decode("utf-8")
    except Exception as e:
        print(f"  [ERR] {e}")
        return []

    entries = re.findall(r"<entry>.*?</entry>", data, re.DOTALL)
    results = []
    for e in entries:
        arxiv_id = re.search(r"<id>(.*?)</id>", e)
        published = re.search(r"<published>(.*?)</published>", e)
        title = re.search(r"<title>(.*?)</title>", e, re.DOTALL)
        if arxiv_id and published and title:
            aid = arxiv_id.group(1).split("/abs/")[-1]
            # Remove version suffix (v1, v2...)
            aid = re.sub(r"v\d+$", "", aid)
            date = published.group(1)[:10]
            ttl = " ".join(title.group(1).split())[:100]
            results.append((aid, date, ttl))
    return results


def main():
    for label, query in QUERIES:
        print(f"\n{'='*70}")
        print(f"[{label}]")
        print("=" * 70)
        results = search_arxiv(query)
        for aid, date, ttl in results:
            print(f"  {aid} | {date} | {ttl}")
        time.sleep(3)  # Respect the API rate limit


if __name__ == "__main__":
    main()