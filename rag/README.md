# Local RAG — awesome-embodied-ai

Retrieval-augmented generation (**RAG**) over this repo's paper collection,
100 % local and **credential-free**: ChromaDB persisted on disk + ONNX embeddings
`all-MiniLM-L6-v2` (384 dims) run with `onnxruntime` on CPU.

> This folder lives inside a OneDrive-synced repository, so by design **there are
> no API keys, tokens or `.env` files here**. The script returns cited evidence
> and, with `--prompt`, a context block ready to paste into whichever LLM you
> choose.

---

## Contents

| File | Role |
|------|------|
| `raglib.py` | Paths, text cleaning, PDF extraction, chunking, metadata, Chroma client |
| `build_index.py` | Builds / updates the vector index |
| `query.py` | Queries the index (CLI) |
| `marco.py` | Theoretical-framework-shaped evidence + citation verification |
| `serve.py` | Local web UI (`http.server`, read-only) |
| `web/index.html` | That UI's front end (self-contained, no CDN) |
| `web/README.md` | Web UI user guide (controls, filters, recipes, troubleshooting) |
| `requirements.txt` | Dependencies (`chromadb`, `PyMuPDF`) |
| `ask.ps1` | PowerShell shortcut with the console pinned to UTF-8 |

Generated artifacts (**git-ignored**, regenerable):

| Folder | Contents |
|--------|----------|
| `.venv/` | Python virtual environment |
| `chroma_db/` | Persisted vector index (collection `embodied_ai`) |
| `cache/` | Text extracted from each PDF (speeds up re-indexing) |
| `models/` | ONNX model `all-MiniLM-L6-v2` (downloaded once, ~80 MB) |

---

## Installation (one-off)

From the repository root:

```powershell
py -3.14 -m venv awesome-embodied-ai\rag\.venv
awesome-embodied-ai\rag\.venv\Scripts\python.exe -m pip install -r awesome-embodied-ai\rag\requirements.txt
```

The first run of `build_index.py` downloads the embedding model into
`rag/models/` (never outside the workspace).

---

## Build / update the index

```powershell
# From the repository root
rag\.venv\Scripts\python.exe rag\build_index.py              # incremental upsert
rag\.venv\Scripts\python.exe rag\build_index.py --rebuild    # from scratch
rag\.venv\Scripts\python.exe rag\build_index.py --stats      # statistics
rag\.venv\Scripts\python.exe rag\build_index.py --include-retired
rag\.venv\Scripts\python.exe rag\build_index.py --only *VLA* --limit 3
```

Chunk IDs are deterministic (`sha1(path)::index`), so re-running the script
**updates without duplicating** and prunes the chunks of documents that
disappeared from disk.

### What gets indexed

1. **The 62 PDFs in `papers/`** (excluding `papers/_retirados/` unless
   `--include-retired`), enriched with the 20 columns of
   [`papers.csv`](../papers.csv).
2. **The repo's curated Markdown**: `README.md`, `GLOSSARY.md`,
   `CONTRIBUTING.md`, `research-protocol.md`, `research-gaps.md`,
   `tactile-sota.md`, `papers/PAPERS.md`.
   (`PLAN_PUBLICACIONES_HENRY.md` is excluded on purpose.)

### Chunking

* Blocks of ~1400 characters with ~220 of overlap, cut at paragraph boundaries.
* The page range (`page_start` / `page_end`) is preserved so hits can be cited.
* Markdown keeps its heading path (`heading_path`).
* Pages with no useful prose (covers, number-only pages) are dropped.

---

## Local web UI (the most comfortable way)

```powershell
# From the repository root
rag\.venv\Scripts\python.exe rag\serve.py       # http://127.0.0.1:8757/
rag\.venv\Scripts\python.exe rag\serve.py --port 9000 --no-browser
```

Opens `web/index.html`: search box, filters, result cards with similarity and
citable metadata, and a **"Contexto LLM"** button that produces the same block as
`--prompt`.

> The interface chrome is in **Spanish** (the buttons read `Buscar`, `Copiar`…),
> but write your **queries in English**: the corpus and the embedding model are
> English. Measured on the same intent, "which VLAs run as native ROS 2 nodes"
> scores 0.660 while its Spanish translation scores 0.482 and loses the relevant
> curated documents. The full guide — every control, its recipes and its
> troubleshooting — is in [`web/README.md`](web/README.md).

The server uses only the standard library (`http.server`), is **read-only**, and
listens on `127.0.0.1`: it does not write to disk and uses no credentials.

### JSON API (read-only, loopback only)

| Endpoint | Parameters |
|----------|------------|
| `GET /api/search?q=…` | `k`, `category`, `folder`, `source`, `year_min`, `year_max`, `min_sim`, `contains`, `include_retired=1` |
| `GET /api/marco?q=…` | theoretical-framework sections + BibTeX (see below) |
| `GET /api/verify?ref=…` | does this reference exist in the corpus? |
| `GET /api/prompt?q=…` | same parameters, returns the context block |
| `GET /api/facets` | categories, folders, years and counts |
| `GET /api/stats` | chunk and document counts |
| `GET /healthz` | `{"ok": true}` — cheap liveness check for scripts |

HTTP and CLI filters are **the same code**: `serve.py` reuses `build_where()`
from `query.py`, so one query returns the same on the web, over HTTP and in the
terminal. There is no authentication because there is no network exposure.

---

## Querying from the CLI

```powershell
# From the repository root
rag\.venv\Scripts\python.exe rag\query.py "contact-rich manipulation with force/torque sensing"
rag\.venv\Scripts\python.exe rag\query.py "VLA models for ROS 2 manipulation" -k 10 --prompt
rag\.venv\Scripts\python.exe rag\query.py "quantization edge deployment" --category VLA_Models --min-sim 0.4
rag\.venv\Scripts\python.exe rag\query.py "failure detection manipulation" --source pdf --year-min 2024
rag\.venv\Scripts\python.exe rag\query.py "dexterous grasping" --json --export resultados.json
rag\.venv\Scripts\python.exe rag\ask.ps1 "Which VLAs run as native ROS 2 nodes?"
```

| Flag | Purpose |
|------|---------|
| `-k N` | how many chunks to return (default 6) |
| `--category CAT` | filter by the `papers.csv` category (repeatable) |
| `--folder SUB` | filter by `papers/` subfolder (repeatable) |
| `--source {all,pdf,markdown}` | by document type |
| `--year-min YYYY` / `--year-max YYYY` | filter by publication year |
| `--min-sim F` | minimum cosine similarity (0–1) |
| `--contains TXT` | require that text in the chunk |
| `--include-retired` | include retired papers (excluded by default) |
| `--prompt` | emit the context block, ready to paste into an LLM |
| `--marco` | theoretical-framework sections + BibTeX |
| `--verify` | check whether a reference exists in the corpus |
| `--json` / `--export FILE` | machine-readable output / save to file |

---

## Theoretical framework and citation verification

The `--marco` + `--verify` combination (also over HTTP, see
[`AGENTS.md`](../AGENTS.md)) turns the RAG from "a search engine" into "a
citation pipeline":

```powershell
rag\.venv\Scripts\python.exe rag\query.py "VLA models for ROS 2 manipulation" --marco
rag\.venv\Scripts\python.exe rag\query.py "sim2real transfer safety" --marco --json --export marco.json
rag\.venv\Scripts\python.exe rag\query.py "OpenVLA: An Open-Source Vision-Language-Action Model" --verify
```

### `--marco`: evidence by sections

Instead of a flat ranking of similar chunks, it assembles the evidence with the
shape of a theoretical framework:

| Section | Content |
|---------|---------|
| State of the art | dominant approaches and their representatives |
| Documented limitations | what the papers themselves admit they do not solve |
| Gaps | categories without a clear dominant method |
| Theoretical bases | formal foundations cited by the corpus |
| Quantitative comparison | metrics reported by each paper |
| Robotics / ROS 2 integration | the `ros_integration` column |
| BibTeX | one entry per retrieved paper, plus the collection entry |

The key design point: semantic search decides **which** papers matter, and
`papers.csv` supplies the analysis of those papers. The first step is
approximate, the second is exact; mixing them the other way round is how you end
up citing hearsay.

`--marco` also emits **warnings** for whoever is writing: low coverage (<3
papers), a bias towards 2025-2026, and the reminder that `authors_first` only
carries "Surname et al." (so the BibTeX comes out as `Surname and others`).

### `--verify`: anti-hallucination guardrail

The corpus is closed (62 papers), so "does this reference exist?" has a
deterministic answer. This is the number-one risk of an AI-written theoretical
framework:

```powershell
rag\.venv\Scripts\python.exe rag\query.py "OpenVLA: An Open-Source Vision-Language-Action Model" --verify
rag\.venv\Scripts\python.exe rag\query.py "arXiv:2212.06817" --verify
rag\.venv\Scripts\python.exe rag\query.py "Kim et al. 2024" --verify
```

| Verdict | Meaning |
|---------|---------|
| `confirmed` | It is in the corpus. Citable; the attached BibTeX is the correct entry. |
| `probable` | Ambiguous: several papers match almost equally. Add the year or the `arxiv_id` and repeat. |
| `not_found` | **Not in the corpus.** Mark it as an external source and verify it yourself. |

It always returns nearby candidates, including on failure: that is what lets you
self-correct a badly written citation instead of insisting on an invented
reference. Exit code `0` if `confirmed`, `1` in any other case (useful in
scripts).

> `--verify` **does not load Chroma**: it only reads `papers.csv`, so it answers
> in milliseconds instead of the 15-25 s it costs to start the index.

Over HTTP, `/api/verify` accepts a repeated `ref` or `refs=a|b|c` to verify a
whole bibliography at once. Commas are **not** used as a separator, because a
legitimate reference contains them ("Kim et al., 2024").

---

## Using it from Python

```python
import sys
sys.path.insert(0, "awesome-embodied-ai/rag")
import raglib as R

client = R.get_client()
collection = R.get_collection(client, create=False)

res = collection.query(
    query_texts=["contact-rich manipulation with force/torque sensing"],
    n_results=5,
    where={"year": {"$gte": 2024}},
    include=["documents", "metadatas", "distances"],
)
for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
    print(f"{1 - dist:.3f}  {meta['title']}  pp.{meta['page_start']}-{meta['page_end']}")
```

---

## Notes and limitations

* **Retrieval only.** There is no automatic generation: `--prompt` hands you the
  context with its citations so that you paste it into your LLM. That is a
  deliberate decision (the rule about not storing secrets in a OneDrive-synced
  folder).
* `all-MiniLM-L6-v2` is a general-purpose English model with 384 dims and a
  256-token window: chunks are trimmed to ~1400 characters so the tail is not
  lost. **Spanish queries work but retrieve noticeably worse** — measured on the
  same intent, 0.482 in Spanish versus 0.660 in English — because the corpus is
  in English. Keep technical terms in English even when you write in Spanish.
* Extraction is of **text**, not of figures or tables: result tables come back as
  plain text and may arrive out of order.
* `papers/_retirados/` is out by default; those 7 PDFs are in neither
  `PAPERS.md` nor `papers.csv`, so they are indexed without enriched metadata.
* `rag/chroma_db/`, `rag/cache/`, `rag/models/` and `rag/.venv/` are in
  `.gitignore`. OneDrive still syncs them: if you do not want to upload them,
  mark the `rag/` folder as excluded in OneDrive, or move it out and adjust
  `raglib.py`.
