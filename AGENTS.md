# AGENTS.md — Instructions for AI Agents

**Read this before querying, summarising, or citing anything in this repository.**

This repo is a curated, **closed** corpus: 62 papers on Embodied AI,
Vision-Language-Action (VLA) models, Sim2Real and ROS 2, plus curated Markdown
(glossary, research protocol, research gaps). It ships a **local,
dependency-free RAG** over its own contents.

If you are writing a literature review, a related-work section or a theoretical
framework (*marco teórico*), **query the RAG**. Do not infer content from folder
names, and do not answer from prior knowledge alone.

---

## 1. Quick start

All commands run from the repository root (PowerShell shown):

```powershell
# One-off question
rag\.venv\Scripts\python.exe rag\query.py "Which VLAs run as ROS 2 nodes?"

# Evidence shaped as theoretical-framework sections, with BibTeX
rag\.venv\Scripts\python.exe rag\query.py "VLA models for manipulation" --marco

# Is this reference actually in the corpus? (fast: does not load the index)
rag\.venv\Scripts\python.exe rag\query.py "OpenVLA: An Open-Source VLA Model" --verify
```

`rag\ask.ps1 "..."` is a wrapper that forwards to `query.py` with the console
pinned to UTF-8 — prefer it on Windows, where the default codepage mangles
accents and symbols.

Or start the read-only local server (loopback only) and use the JSON API:

```powershell
rag\.venv\Scripts\python.exe rag\serve.py --no-browser   # http://127.0.0.1:8757/
```

| Endpoint | Purpose |
|---|---|
| `GET /api/search?q=…` | ranked chunks with full metadata |
| `GET /api/marco?q=…` | evidence organised by framework sections + BibTeX |
| `GET /api/verify?ref=…` | citation check — repeat `ref`, or `refs=a\|b` for a batch |
| `GET /api/prompt?q=…` | ready-to-paste context block for an LLM |
| `GET /api/facets`, `GET /api/stats` | corpus inventory |

First-time setup (once): create `rag\.venv` from `rag\requirements.txt`, then run
`rag\build_index.py`. Queries need no network access. Full details in
[`rag/README.md`](rag/README.md).

---

## 2. Citation discipline (non-negotiable)

1. **Retrieve before you write.** Every claim must trace back to a chunk you
   actually retrieved. No "as is well known", no reconstruction from memory.
2. **Verify every reference** with `--verify` / `/api/verify` before it enters a
   bibliography. The corpus is closed, so the verdict is deterministic:
   - `confirmed` → cite it.
   - `probable` → ambiguous. Add the year or the `arxiv_id` and re-verify.
     **Never pick one of the tied candidates at random.**
   - `not_found` → the reference is **not in this corpus**. Do not attribute it
     to this collection; mark it as an external source and check it yourself.
3. **Quote with a location.** Chunks carry `page_start`/`page_end`. Write
   "Kim et al. (2024, pp. 8-9)", not "Kim et al. (2024)".
4. **Do not invent metadata.** `papers.csv` stores `authors_first` as
   "Surname et al.", so generated BibTeX says `Surname and others`. Complete the
   given names from arXiv before submitting anything.
5. **Cite the collection itself** if you rely on it as a whole —
   DOI [`10.5281/zenodo.22984143`](https://doi.org/10.5281/zenodo.22984143),
   see [`CITATION.cff`](CITATION.cff).

---

## 3. What `--marco` gives you

`--marco` (or `/api/marco`) is the mode designed for a theoretical framework. It
does **not** return a flat ranking of similar chunks; it returns the sections you
would otherwise have to assemble by hand:

| Section | Where it comes from |
|---|---|
| State of the art | semantic search over `papers/` (PDFs only, deduplicated per paper) |
| Documented limitations | `limitations` column of [`papers.csv`](papers.csv) |
| Research gaps | `gap_category` column + [`research-gaps.md`](research-gaps.md) |
| Theoretical bases / definitions | [`GLOSSARY.md`](GLOSSARY.md) |
| Methodological protocol | [`research-protocol.md`](research-protocol.md) |
| Quantitative comparison | `latency_ms`, `compute_resources`, `sim2real`, `ros_integration` |
| BibTeX | one entry per retrieved paper, plus the collection entry |

The design note that matters: semantic search decides **which** papers are
relevant; `papers.csv` then supplies the analysis of those papers. The first step
is approximate, the second is exact. That split is deliberate — inverting it is
how you end up with a plausible-looking framework that cites nothing real.

Useful flags:

```powershell
--json                 # machine-readable output
--export marco.json    # save instead of printing
-k 10                  # how many papers to consider
--per-section 5        # curated fragments per section (default 3)
--category VLA_Models  # honour the usual filters
--folder vla
```

`/api/marco` accepts the same parameters as query strings: `q`, `k` (capped at
50), `per_section` (1–10), `min_sim`, `category`, `folder`, `include_retired`.
**Year filters are not applied in marco mode** — `build_marco()` has no
`year_min`/`year_max` — so `--year-min`/`year_min` are silently ignored there.
Use them with plain `query.py` / `/api/search`, where they do work.

---

## 4. Known limits — plan around them

- **62 papers is not a complete literature.** It is a strong evidence base for
  Embodied AI / VLA / Sim2Real / ROS 2 and little else. `--marco` emits a
  `COBERTURA BAJA` (low coverage) warning when fewer than three papers match:
  read that as "go search outside and label those sources as external", never as
  "there is nothing to say".
- **Coverage is uneven.** `07_Recent_2025_2026` and `06_ROS2_AI_LLMs` are heavily
  chunked, so recency can dominate a naive query. `--marco` warns when more than
  60% of matches are from 2025-2026. Counteract it with `--year-min`/`--year-max`
  and query the foundational categories (`01_VLA_Models`, `03_Sim2Real_RL`)
  explicitly.
- **The embedding model is `all-MiniLM-L6-v2`** (384 dims, English-centric).
  Spanish queries work but retrieve better in English. Keep technical terms in
  English even when you write in Spanish.
- **Retired papers are excluded by default** (`papers/_retirados/`). Pass
  `--include-retired` only when you deliberately want them.
- **Similitud scores are cosine similarities** from a small multilingual-weak
  model. Use them to rank, not as a truth threshold: a 0.45 hit can be the right
  paper and a 0.65 hit can be noise.

---

## 5. Hard rules for agents

- **Read-only.** Never modify `papers/`, `papers.csv`, `GLOSSARY.md` or
  `rag/chroma_db/` as a side effect of answering a question.
- **No credentials, ever.** This folder syncs to OneDrive. Never create `.env`,
  `.dev.vars`, `wrangler.toml`, or any file containing tokens, keys or secrets.
- **No deployment.** Never run `wrangler` (in any form) or publish this folder to
  Cloudflare, Vercel, Netlify or similar.
- **No new dependencies.** The RAG is stdlib + ChromaDB + PyMuPDF on purpose.
  `serve.py` and `marco.py` deliberately use only the Python standard library.
- **Stay inside the repository.** Do not read from or write to paths outside it.

---

## 6. Further reading

- [`rag/README.md`](rag/README.md) — full RAG documentation: every CLI flag, the
  API, the security model.
- [`research-protocol.md`](research-protocol.md) — inclusion criteria and method.
- [`research-gaps.md`](research-gaps.md) — the four open research sublines.
- [`GLOSSARY.md`](GLOSSARY.md) — VLA/VLM/LLM, Sim2Real and ROS 2 definitions.
- [`papers/PAPERS.md`](papers/PAPERS.md) — the paper library.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to add a paper correctly.


