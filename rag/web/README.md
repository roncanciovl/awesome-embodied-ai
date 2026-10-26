# Local RAG web UI — user guide

The UI is **a single self-contained page** (`web/index.html`: HTML + CSS + JS in
one file, no CDN, no `npm`, no build) served by `rag/serve.py` at
<http://127.0.0.1:8757/>. It lets you search the repo's paper collection for
evidence and walk away with a context block ready to paste into your LLM.

> **About languages.** The interface chrome is in **Spanish** (`Buscar`,
> `Filtros`, `Copiar`…); this guide quotes every label and glosses it. Write your
> *queries* in **English** regardless, because the corpus and the embedding model
> are English. Measured on the same intent, `which VLAs run as native ROS 2
> nodes` scores **0.660** while its Spanish translation scores **0.482** and
> loses the relevant curated documents.

> General RAG context (installation, indexing, CLI): [`../README.md`](../README.md).
> Programmatic use by AI agents: [`../../AGENTS.md`](../../AGENTS.md).

---

## 1. Starting and stopping

```powershell
# From the repository root
rag\.venv\Scripts\python.exe rag\serve.py
```

It loads the index, prints a banner and **opens your default browser**. Stop it
with `Ctrl+C` in that console.

| Option | Effect |
|--------|--------|
| `--port 9000` | Listen on another port (8757 is taken if another instance is running) |
| `--no-browser` | Do not open the browser; navigate to the URL yourself |

```
========================================================================
  RAG local — interfaz web (solo lectura)
  URL        : http://127.0.0.1:8757/
  Colección  : embodied_ai  (3595 chunks)
  Índice     : rag/chroma_db
  Loopback únicamente: no hay acceso desde la LAN ni credenciales.
  Ctrl+C para parar.
========================================================================
```

(The banner is the server's own console output, in Spanish; it is not part of the
page.)

**Prerequisite:** the index must exist. If the `embodied_ai` collection has not
been built, the server prints `[error] ...` and exits with code 2 — the web never
comes up. Fix it with:

```powershell
rag\.venv\Scripts\python.exe rag\build_index.py
```

---

## 2. What you see when it opens

```
+-----------------------------------------------------------------------+
| RAG local · awesome-embodied-ai   3595 chunks · 69 docs (62 PDF, 7 MD) | <- header
| Recuperación semántica 100 % local · ChromaDB + all-MiniLM-L6-v2 ·     |
| sin credenciales                                                       |
+------------------------------------------------------------------------+
| [Pregunta algo: ¿qué VLAs corren como nodos nativos de ROS 2?]         | <- search box
| [Buscar] [Contexto LLM]                                                |
| > Filtros opcionales                                                   | <- collapsible
|                                                                        |
| 4 fragmentos de 2 documentos distintos · 147 ms                        | <- status
| +---+ RT-2: Vision-Language-Action Models Transfer Web Knowledge…      | <- card
| | 1 | ######################## arXiv:2307.15818              0.686     |
| +---+ [año: 2023] [pág.: pp.11-12] [cat.: VLA_Models]                  |
|       [carpeta: 01_VLA_Models] [ROS 2: No] [robot: Mobile manipulator] |
|       "retrieved chunk text…"                                          |
|       papers/01_VLA_Models/RT-2_Vision-Language-Action_Models….pdf     |
+------------------------------------------------------------------------+
```

(Real capture from the current index; your numbers depend on what you indexed.)

* **Header (right):** real index counts, fetched from `/api/stats` on load. It
  reads `cargando índice…` ("loading index…") until that call returns; if it ends
  up saying `índice no disponible` ("index unavailable"), the index is missing
  (section 11).
* **Search bar:** text box + **Buscar** (Search) + **Contexto LLM** (LLM context).
* **`Filtros opcionales`** (Optional filters): collapsed by default; click the
  title to expand.
* **Status line:** how many chunks and distinct documents came back, and how many
 milliseconds it took (measured in the browser). Amber when it is a warning or an
  error.
* **Cards:** one result per row, sorted by descending similarity.

---

## 3. Searching, step by step

1. Type the question in the box. **English performs better**: the corpus (PDFs
   and Markdown) is in English and the embedder is `all-MiniLM-L6-v2`.
2. Press **Enter** or click **Buscar** (Search).
3. If the results are noisy, expand **Filtros**, narrow them and search again:
   filters **are not applied until you press Search** (there is no automatic
   re-query).
4. With the evidence in front of you, click **Contexto LLM** and copy the block
   (section 6).

Tips that visibly change retrieval quality:

* Concrete technical phrases beat long questions: `tactile sim-to-real gap`
  outperforms `which papers talk about touch?`.
* Read the status line: `6 fragmentos de 1 documento distinto` ("6 chunks from 1
  distinct document") means all the evidence comes from a single paper, so open
  the filters or raise `Fragmentos`.
* **Similarity is cosine from a small model**: use it to *rank*, not as a truth
  threshold. 0.45 can be the right paper and 0.65 can be noise (the same
  criterion as in `AGENTS.md`).
* If nothing matches, the UI says so and suggests removing filters or rephrasing
  in English.

---

## 4. Filters

Each control maps 1:1 to a CLI flag (`query.py`) and to an HTTP parameter,
because the web and the CLI share `build_where()` from `query.py`: the same query
returns exactly the same in both.

| UI control | HTTP parameter | CLI flag | What it does | Default |
|------------|----------------|----------|--------------|---------|
| **Fragmentos (k)** (Chunks) | `k` | `-k` / `--k` | How many chunks to return (1–50) | `6` |
| **Origen** (Source) | `source` | `--source` | `todo` / `solo PDFs` / `solo Markdown` (HTTP values `all`/`pdf`/`markdown`) | `todo` |
| **Categoría** (Category) | `category` | `--category` | Category from `papers.csv` (`VLA_Models`, `Sim2Real_RL`, …) | all |
| **Carpeta** (Folder) | `folder` | `--folder` | `papers/` subfolder (`01_VLA_Models`, …) or `repo_docs` | all |
| **Año desde** (Year from) | `year_min` | `--year-min` | Minimum publication year | unbounded |
| **Año hasta** (Year to) | `year_max` | `--year-max` | Maximum publication year | unbounded |
| **Similitud mínima** (Min similarity) | `min_sim` | `--min-sim` | Cosine threshold (0–1, steps of 0.05) | `0` |
| **Debe contener** (Must contain) | `contains` | `--contains` | Literal text required in the chunk | empty |
| **incluir retirados** (include retired) | `include_retired=1` | `--include-retired` | Includes papers marked as retired | off |

Behaviour details:

* **Categoría** and **Carpeta** are populated on page load from `/api/facets`,
  and each option carries its count in parentheses, so you know in advance how
  many chunks live there. Real values from the current corpus: categories
  `VLA_Models (387)`, `Recent_2025_2026 (1390)`, `Sim2Real_RL (376)`,
  `ROS2_AI_LLMs (404)`, `Simulation_Environments (212)`,
  `Surveys_Case_Studies (455)`, `Robotics_Frameworks (49)` and `repo_docs (322)`;
  folders `01_VLA_Models (387)` … `07_Recent_2025_2026 (1390)`, plus `repo_docs`
  for the repository's own Markdown.
* The **Año desde / Año hasta** fields show the corpus' real minimum and maximum
  years as *placeholders* (also from `/api/facets`; currently `2017` and `2026`):
  that is a hint, not an active value. Leaving them empty means no filtering.
* **Similitud mínima** and **Debe contener** are only sent if you fill them in.
* If `/api/facets` fails, the dropdowns stay at `todas` ("all") but search keeps
  working.
* `Fragmentos` is additionally clamped server-side to 1–50, so you cannot ask for
  500 through the URL.

---

## 5. Anatomy of a result card

```
+---+ RT-2: Vision-Language-Action Models Transfer Web Knowledge to
| 1 | Robotic Control   arXiv:2307.15818                          0.686
+---+ #############################################
      [año: 2023] [pág.: pp.11-12] [cat.: VLA_Models] [carpeta: 01_VLA_Models]
      [ROS 2: No] [robot: Mobile manipulator] [hardware: Everyday Robots]
      "full text of the retrieved chunk, with line breaks collapsed..."
      papers/01_VLA_Models/RT-2_Vision-Language-Action_Models_Transfer_Web_Knowledge.pdf
```

(Real capture, query `vision-language-action model generalization` with
`Origen = solo PDFs`.)

| Part | What it is |
|------|------------|
| `1` | Ranking position: 1 is the most similar |
| Title | `metadata.title` of the paper. For the repo's own Markdown, its path is shown |
| `arXiv:2307.15818` | Link to `arxiv.org/abs/...` in a new tab. Shown only if the paper has an `arxiv_id` in `papers.csv` |
| `0.686` | Cosine similarity, 3 decimals |
| Bar | The same similarity as a percentage (width = `sim x 100 %`) |
| Chips | Paper metadata; hidden only when the field is empty or `-` (exact rule below) |
| Text | The full chunk, with line breaks collapsed into spaces |
| Final path | `doc_path`, relative to the repository root |

Possible chips and their source field:

| Chip | Field in `papers.csv` / index | Real example |
|------|-------------------------------|--------------|
| `año` (year) | `year` | `año: 2023` |
| `pág.` (pages) | `page_start` / `page_end` | `pág.: p.3` or `pág.: pp.11-12` |
| `cat.` (category) | `category` | `cat.: VLA_Models` |
| `carpeta` (folder) | `folder` | `carpeta: 01_VLA_Models` |
| `ROS 2` | `ros_integration` | `ROS 2: No`, `ROS 2: Partial` |
| `robot` | `robot_type` | `robot: Mobile manipulator` |
| `sim.` | `simulator` | `sim.: Habitat`, `sim.: Custom`, `sim.: N/A` |
| `hardware` | `hardware` | `hardware: Everyday Robots` |
| `sección` (section) | `heading_path` | `sección: Paper Library ... > 01 - Vision-Language-Action (VLA) Models` |

The exact painting rule: a chip is hidden **only** if its field is empty or is
`-`. Everything else is shown as-is, including the unhelpful values:

* `sim.: N/A` or `hardware: N/A` → the field is filled in `papers.csv` with
  `N/A`: the datum is missing and is worth completing.
* `año: 0` → it is one of the repo's own Markdown files (`cat.: repo_docs`),
  which has no publication year.
* A chip that does **not** appear (`sim.`, `robot`, ...) → that field is `-` or
  empty in the CSV. It is the fastest signal that `papers.csv` is incomplete.
* `sección` only makes sense for Markdown; for PDFs the provenance is `pág.`.

---

## 6. The "Contexto LLM" button

Generates the **context block** with the numbered chunks and their citations,
ready to paste into the LLM of your choice. It is the exact equivalent of
`query.py --prompt` (same function, `raglib.build_prompt`).

1. Write the question and adjust the filters.
2. Click **Contexto LLM** (you do not need to have pressed Search first: it uses
   the same *query string* the search would use).
3. The modal **"Contexto para pegar en tu LLM"** ("Context to paste into your
   LLM") opens with:
   * an info line: `N fragmentos · X caracteres · pégalo en el LLM que prefieras`
     ("N chunks · X characters · paste it into whichever LLM you prefer");
   * a **read-only** text area with the complete block;
   * the buttons **Copiar** (Copy) and **Cerrar** (Close).
4. **Copiar** copies to the clipboard and its label changes to `Copiado ✓`
   ("Copied") for a moment. If the browser denies clipboard access, select the
   text and press `Ctrl+C`.

The block is generated by `raglib.build_prompt`, so its wording is Spanish. This
is its exact shape:

```
Eres un asistente de investigación sobre Embodied AI, modelos VLA/VLM/LLM,
ROS 2 y Sim2Real. Responde usando ÚNICAMENTE el contexto siguiente. Cita las
fuentes con su número [n] y di explícitamente si el contexto no alcanza para
responder.

PREGUNTA: <your question>

CONTEXTO RECUPERADO:
=======================
[1] <source label: title, year, pages>
<chunk text>

---

[2] <source label>
<chunk text>
=======================

RESPUESTA:
```

Translation of the instruction line, for reference: "You are a research assistant
on Embodied AI, VLA/VLM/LLM models, ROS 2 and Sim2Real. Answer using ONLY the
following context. Cite sources with their number [n] and say explicitly if the
context is not enough to answer." Chunks are separated by `---` and each starts
with its `[n]` label, so your LLM has no excuse to invent references.

If the search box is empty you get `Escribe una pregunta antes de generar el
contexto.` ("Write a question before generating the context"), and
`Sin resultados con esos filtros.` ("No results with those filters") if the
filters leave nothing.

Recommended flow for a theoretical framework:

1. Search and generate the context for each subtopic.
2. Paste it into your LLM, asking it to cite **only the block's numbers**.
3. Verify every resulting citation with `/api/verify` before accepting it
   (section 9): that is the anti-hallucination guardrail.

---

## 7. Shortcuts and gestures

| Action | How |
|--------|-----|
| Search | `Enter` in the search box (it has focus when the page opens) |
| Show / hide filters | Click `Filtros opcionales` |
| Generate the context | The **Contexto LLM** button |
| Copy the context | The **Copiar** button inside the modal |
| Close the modal | `Esc`, the **Cerrar** button, or a click on the dark backdrop |
| Open the paper on arXiv | Click `arXiv:...` (new tab, `rel="noreferrer"`) |
| Refresh the data | `F5`: the server answers `Cache-Control: no-store`, so you always see the current index |

---

## 8. Recipes

| Goal | What you type | What you touch in Filters |
|------|---------------|---------------------------|
| State of the art of a topic | `vision-language-action models survey` | `Fragmentos` 12–15 |
| Only the recent work | `tactile sim-to-real gap` | `Año desde` = 2024 |
| Only papers (not the repo docs) | `failure detection manipulation` | `Origen` = `solo PDFs` |
| Only the repo's guides/protocols | `evaluation protocol embodied` | `Origen` = `solo Markdown` |
| One specific area | `policy learning generalization` | `Categoría` = `VLA_Models` |
| Force an exact term | `generalization` | `Debe contener` = `VLA` |
| Remove weak noise | `grasping deformable objects` | `Similitud mínima` = `0.45` |
| Include retracted work | `robot manipulation benchmark` | ✔ `incluir retirados` |

Every row has its exact CLI equivalent, useful to keep the query saved in a
script:

```powershell
# Equivalent to: q="tactile sim-to-real gap", Año desde=2024, Fragmentos=12
rag\.venv\Scripts\python.exe rag\query.py "tactile sim-to-real gap" -k 12 --year-min 2024

# Equivalent to: Origen=solo PDFs, Debe contener=VLA, Similitud mínima=0.45
rag\.venv\Scripts\python.exe rag\query.py "failure detection manipulation" --source pdf --contains VLA --min-sim 0.45
```

---

## 9. What the UI does **not** do (and where it gets done)

The interface covers searching and copying context. These four things are left
out on purpose:

**a) Theoretical framework and citation verification: API only.** There is no
button because their consumer is an AI agent, not a person. With the server
running:

```powershell
# Evidence shaped as a theoretical framework (state of the art, limitations,
# gaps, theoretical bases, quantitative comparison and BibTeX)
$m = Invoke-RestMethod "http://127.0.0.1:8757/api/marco?q=sim2real%20transfer%20safety&k=8&per_section=3"
$m.sections | Format-List

# Does this reference exist in the corpus? (anti-hallucination guardrail)
Invoke-RestMethod ("http://127.0.0.1:8757/api/verify?ref=" + [uri]::EscapeDataString("OpenVLA"))
# -> status: confirmed  -> citable without doubt

Invoke-RestMethod ("http://127.0.0.1:8757/api/verify?ref=" + [uri]::EscapeDataString("RT-2"))
# -> status: probable, 3 tied candidates -> add the year or the arxiv_id and repeat

# Batch of references separated by "|"
Invoke-RestMethod ("http://127.0.0.1:8757/api/verify?refs=" + [uri]::EscapeDataString("OpenVLA|RT-2"))
# -> total: 2, counts: {confirmed: 1, probable: 1, not_found: 0}, ok: false
```

`/api/marco` accepts `q`, `k` (≤ 50), `per_section` (1–10), `min_sim`,
`category`, `folder` and `include_retired`. **It does not apply
`year_min`/`year_max`**: if you need to trim by year, use `/api/search` or the
CLI with `--year-min`. `/api/verify` accepts a repeatable `ref` or `refs=a|b`,
plus `limit` (1–10) for the number of candidates; it does not split on commas,
because a legitimate reference contains them (`Kim et al., 2024`). Verdicts:
`confirmed`, `probable`, `not_found`.

CLI equivalent: `query.py --marco` and `query.py --verify`. The full protocol for
agents is in [`../../AGENTS.md`](../../AGENTS.md).

**b) It writes nothing.** It does not download PDFs, does not re-index, does not
modify `papers.csv`, does not generate files. After adding a paper or editing a
Markdown you have to rebuild the index and press `F5`:

```powershell
rag\.venv\Scripts\python.exe rag\build_index.py
```

**c) It does not remember your searches.** There is no history, no favourites and
no state in the URL: on reload you go back to the defaults and **you cannot share
a search by link**. If you want to keep a query, copy it as an API URL
(`/api/search?q=…&k=…`) or save it in a script.

**d) It runs no LLM.** It returns evidence and context; the generation is yours,
on whichever model you choose. By design there are no API keys in this folder (it
syncs to OneDrive).

---

## 10. Security and privacy

Everything is deliberate and lives in the code, not only in the documentation:

* **Loopback only.** The socket opens on `127.0.0.1`: your index is not reachable
  from the LAN or from the internet. There is no way to expose it.
* **`Host` header validation.** Only `127.0.0.1`, `localhost` and `[::1]` are
  accepted; anything else gets `403`. This blocks *DNS rebinding*: a malicious web
  page open in your browser cannot query your index.
* **It serves no arbitrary files.** Only `/` (which returns `web/index.html`) and
  the `/api/*` routes. Everything else returns a JSON `404`. There is no directory
  listing and no *path traversal*.
* **Read-only.** It does not write to disk, makes no outgoing requests and uses no
  credentials. The worst possible failure is a malformed response.
* **Self-contained page.** No CDN, no external fonts, no analytics: not one byte
  leaves your machine and it works with the wifi off.
* **Defensive headers.** `Cache-Control: no-store` and
  `X-Content-Type-Options: nosniff` on every response.
* **Minimal logging.** The server console prints one line per request (method,
  path with its *query string*, and status code) to `stderr`. Nothing is written
  to any file unless you redirect the output when starting it.
* **HTML escaping.** Everything that comes from the index is escaped before being
  painted (`esc()`), because the PDFs contain stray `<`, `>` and `&`.

---

## 11. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| The header says `índice no disponible` and the status shows an error | The `embodied_ai` collection does not exist | `rag\.venv\Scripts\python.exe rag\build_index.py`, then `F5` |
| The server prints `[error] …` and exits with code 2 | Same: the web never comes up | Same |
| `OSError: [WinError 10048]` on start | Another instance already holds port 8757 | `--port 9000`, or close the other console |
| `Sin resultados con esos filtros.` | Filters too narrow, or a query in Spanish | Remove filters, rephrase in English, raise `Fragmentos` |
| The first query takes several seconds | The ONNX model is loaded into memory at start-up | Normal: the following ones drop to tens–hundreds of ms (147 ms measured with `k=4`) |
| No chunks from a just-added paper | The index was not rebuilt | `build_index.py` and `F5` |
| `403 {"error": "Host no permitido: solo acceso local."}` | You entered through the LAN IP or another hostname | Use `http://127.0.0.1:8757/` or `http://localhost:8757/` |
| `404 {"error": "Ruta desconocida: /…"}` | You asked for something that is neither `/`, `/api/*` nor `/healthz` | Only the page, the six `/api/*` endpoints and `/healthz` exist |
| `503 {"error": "La colección … no está disponible"}` | The index was missing when the server started | Rebuild the index and restart the server |
| A result shows no arXiv link | That paper has no `arxiv_id` in `papers.csv` (or it is `-`) | Open the document through its `doc_path` |
| The PDFs are not on disk | They are not versioned, because of redistribution licences | `python scripts/download_papers.py` and re-index |
| The **Copiar** button does not respond | The browser blocks the clipboard | Select the text in the area and copy with `Ctrl+C` |
| `Error: HTTP 500` in the status | An exception inside the endpoint | Look at the server console: the summarised traceback is there |

(The quoted error strings are the server's own, in Spanish; they are reproduced
verbatim so you can recognise them.)

---

## 12. Modifying the UI

It is **one file**: `web/index.html` (HTML + CSS + JS inline, no build, no `npm`,
no dependencies). `serve.py` reads it from disk on **every** request to `/`, so
you can edit it and press `F5` without restarting the server.

Conventions to respect when touching it:

* **No CDN, external fonts or analytics.** It would break offline operation and
  the policy of this folder (synced with OneDrive).
* **No writing and no credentials.** The UI is read-only; if you need to re-index,
  that is done through the CLI.
* **Always escape with `esc()`** any value coming from the index before inserting
  it into the DOM: the PDFs bring stray `<`, `>` and `&`.
* **A new filter exists first in `query.py`.** Add it to `build_where()`, then map
  it in `args_from_params()` of `serve.py`, and finally paint it in the panel.
  That way the web and the CLI keep returning exactly the same.
* **`params()` is the only place** where the *query string* shared by
  `/api/search` and `/api/prompt` is built: a new filter is added there once and
  appears in both.
* The colours live in CSS variables under `:root` (`--bg`, `--panel`, `--acc`,
  `--warn`…); the theme is dark and there is no separate stylesheet.
* The favicon is an inline SVG in `<link rel="icon">`: it avoids the 404 of
  `/favicon.ico` without adding files or requests.

---

## 13. Appendix: which endpoint each action hits

| When | Endpoint | What the UI uses it for |
|------|----------|-------------------------|
| On page load | `GET /api/stats` | The header counts (`chunks · docs · collection`) |
| On page load | `GET /api/facets` | Fills `Categoría` and `Carpeta` with counts, and the year *placeholders* |
| **Buscar** button | `GET /api/search?q=…` | The result cards |
| **Contexto LLM** button | `GET /api/prompt?q=…` | The modal's text block |
| — (no button) | `GET /api/marco?q=…` | Framework sections + BibTeX, for agents |
| — (no button) | `GET /api/verify?ref=…` | Citation verification, for agents |
| — (no button) | `GET /healthz` | `{"ok": true}` so a script can check that the server is alive |

The last three have no interface on purpose: their consumer is an AI agent. The
full contract is in [`../../AGENTS.md`](../../AGENTS.md) and in the web-interface
section of [`../README.md`](../README.md).
