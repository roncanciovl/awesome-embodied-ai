#!/usr/bin/env python
"""
marco — evidencia con forma de marco teórico + verificación de citas.

Por qué existe
--------------
Un agente de IA que redacta un marco teórico no necesita "los k fragmentos más
parecidos": necesita fuentes citables con localización exacta, las limitaciones
documentadas de cada trabajo y los vacíos que el propio corpus reconoce. Todo
eso YA está en papers.csv (20 columnas) y en los Markdown del repo; este módulo
lo ensambla en vez de obligar al agente a reconstruirlo.

Dos decisiones de diseño:
  1. La recuperación semántica decide QUÉ papers importan; los metadatos
     estructurados de papers.csv aportan el análisis (limitaciones, vacíos,
     latencia, ROS 2). Lo primero es aproximado, lo segundo es exacto: mezclarlos
     al revés daría un marco teórico inventado.
  2. `verify_citation()` es el guardarrail anti-alucinación. El corpus es cerrado
     (62 papers), así que "¿existe esta referencia?" se responde de forma
     determinista. Un NOT_FOUND explícito vale más que un match dudoso: es lo que
     le dice al agente que busque fuera y lo marque como fuente externa.

Sin dependencias nuevas: solo stdlib + raglib.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from argparse import Namespace
from pathlib import Path
from typing import Any

import raglib as R

# query.py importa este módulo de forma tardía (dentro de main()) para no crear
# un ciclo; aquí sí podemos importar en cabeza de módulo.
from query import run_query  # noqa: E402  (reuso, no duplico los filtros)

# ── Secciones canónicas de un marco teórico ──────────────────────────────────
# `doc` fija un Markdown curado del repo; si no, la sección sale de papers/.
MARCO_SECTIONS: dict[str, dict[str, str]] = {
    "estado_del_arte": {
        "titulo": "Estado del arte (papers relevantes)",
        "origen": "recuperación semántica sobre papers/ (solo PDF)",
    },
    "bases_teoricas": {
        "titulo": "Bases teóricas y definiciones",
        "origen": "GLOSSARY.md (conocimiento curado)",
    },
    "vacios": {
        "titulo": "Vacíos de investigación",
        "origen": "columna gap_category de papers.csv + research-gaps.md",
    },
    "metodologia": {
        "titulo": "Protocolo metodológico del corpus",
        "origen": "research-protocol.md (conocimiento curado)",
    },
    "limitaciones": {
        "titulo": "Limitaciones documentadas de los trabajos previos",
        "origen": "columna limitations de papers.csv",
    },
    "comparativa": {
        "titulo": "Comparativa cuantitativa",
        "origen": "columnas latency_ms / compute_resources / sim2real / ros_integration",
    },
}

CURATED_DOCS = {
    "bases_teoricas": "GLOSSARY.md",
    "vacios": "research-gaps.md",
    "metodologia": "research-protocol.md",
}

# ── papers.csv ───────────────────────────────────────────────────────────────


def load_paper_records() -> list[dict[str, Any]]:
    """Las filas de papers.csv tal cual (20 columnas), sin transformar."""
    records: list[dict[str, Any]] = []
    if not R.PAPERS_CSV.exists():
        return records
    with R.PAPERS_CSV.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            clean = {k: v.strip() for k, v in (row or {}).items()
                     if k and isinstance(v, str)}
            if clean.get("file_path"):
                records.append(clean)
    return records


def records_by_path(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Índice por `file_path`, que es la clave que comparten CSV e índice."""
    return {str(r.get("file_path", "")): r for r in records if r.get("file_path")}


# ── BibTeX ───────────────────────────────────────────────────────────────────
# papers.csv guarda `authors_first` como "Apellido et al.", sin nombres de pila.
# BibTeX no puede inventarlos: se emite `Apellido and others` y el aviso de más
# abajo recuerda completarlos desde arXiv antes de enviar el paper.

_BIB_STOP = {"the", "a", "an", "of", "for", "and", "on", "in", "to", "with",
             "via", "using", "towards", "toward", "from"}


def cite_key(rec: dict[str, Any]) -> str:
    """`kim2024openvla` — apellido + año + primera palabra significativa."""
    raw = str(rec.get("authors_first") or "")
    parts = raw.replace("et al.", " ").split()
    surname = re.sub(r"[^a-z]", "", parts[0].lower()) if parts else ""
    year = re.sub(r"\D", "", str(rec.get("year") or ""))
    words = [w for w in re.findall(r"[a-z]{3,}", str(rec.get("title") or "").lower())
             if w not in _BIB_STOP]
    return f"{surname or 'anon'}{year or 'nd'}{words[0] if words else 'untitled'}"


def to_bibtex(rec: dict[str, Any]) -> str:
    """Entrada BibTeX de un paper del corpus."""
    raw = str(rec.get("authors_first") or "").strip()
    parts = raw.replace("et al.", " ").split()
    surname = re.sub(r"[^A-Za-z]", "", parts[0]) if parts else ""
    author = f"{surname} and others" if surname and "et al" in raw.lower() else (surname or "unknown")
    year = re.sub(r"\D", "", str(rec.get("year") or "")) or "n.d."
    aid = str(rec.get("arxiv_id") or "").strip()
    lines = [
        f"@article{{{cite_key(rec)},",
        f"  title         = {{{str(rec.get('title') or '').strip()}}},",
        f"  author        = {{{author}}},",
        f"  year          = {{{year}}},",
    ]
    if aid and aid != "-":
        lines += [
            f"  eprint        = {{{aid}}},",
            "  archivePrefix = {arXiv},",
            f"  url           = {{https://arxiv.org/abs/{aid}}},",
        ]
    lines.append("}")
    return "\n".join(lines)


_CFF_KEYS = ("title", "version", "date-released", "doi")


def collection_bibtex() -> str:
    """
    Cita la colección completa leyendo CITATION.cff.

    Parseo mínimo con regex a propósito: PyYAML no está en uso en este repo y
    añadirlo solo para leer seis campos no compensa. Si el fichero falta o
    cambia de forma, se degrada a una entrada genérica en vez de reventar.
    """
    cff = R.REPO_DIR / "CITATION.cff"
    data: dict[str, str] = {}
    family = given = ""
    if cff.exists():
        for line in cff.read_text(encoding="utf-8").splitlines():
            top = re.match(r'^([a-z][a-z\-]*):\s*"?(.*?)"?\s*$', line)
            if top and top.group(1) in _CFF_KEYS:
                data[top.group(1)] = top.group(2)
            person = re.match(r'^\s+-?\s*(family-names|given-names):\s*"?(.*?)"?\s*$', line)
            if person:
                if person.group(1) == "family-names":
                    family = person.group(2)
                else:
                    given = person.group(2)
    year = (data.get("date-released") or "")[:4] or "n.d."
    author = f"{family}, {given}" if family and given else (family or "unknown")
    doi = data.get("doi") or ""
    key = f"{re.sub(r'[^a-z]', '', family.lower()) or 'anon'}{year}awesome"
    lines = [
        f"@misc{{{key},",
        f"  title        = {{{data.get('title') or 'Awesome Embodied AI & Sim2Real'}}},",
        f"  author       = {{{author}}},",
        f"  year         = {{{year}}},",
        f"  version      = {{{data.get('version') or ''}}},",
        "  howpublished = {https://github.com/roncanciovl/awesome-embodied-ai},",
    ]
    if doi:
        lines.append(f"  doi          = {{{doi}}},")
    lines.append("}")
    return "\n".join(lines)


# ── Verificación de citas (guardarrail anti-alucinación) ─────────────────────
# El corpus es cerrado, así que esto es determinista: o la referencia está entre
# los 62 papers o no está. El caso útil no es el acierto, es el fallo explícito.

CONFIRMED = 0.80
PROBABLE = 0.50
# Varias referencias empatadas casi igual = cita ambigua. Confirmar ahí sería
# elegir al azar, que es justo el fallo que este módulo existe para evitar.
AMBIGUITY_MARGIN = 0.05

_STOP = {"the", "a", "an", "of", "for", "and", "on", "in", "to", "with", "et",
         "al", "via", "using", "towards", "toward", "from", "by", "is", "are",
         "at", "as", "or", "pp", "p"}

_INSTRUCTIONS = {
    "confirmed": (
        "Referencia VERIFICADA en el corpus. Puedes citarla. El BibTeX adjunto es "
        "la entrada correcta, pero completa los nombres de pila desde arXiv: "
        "papers.csv solo guarda 'Apellido et al.'."
    ),
    "probable": (
        "Coincidencia PARCIAL. No cites todavía: desambigua cuál de estos papers "
        "es (compara título, año y arXiv) y vuelve a verificar la referencia "
        "corregida."
    ),
    "not_found": (
        "ESTA REFERENCIA NO ESTÁ EN EL CORPUS (62 papers). No la atribuyas a esta "
        "colección: márcala como fuente externa y verifícala tú en arXiv/DOI. Las "
        "coincidencias cercanas se listan por si la cita estaba mal escrita."
    ),
}

_AMBIGUOUS = (
    "CITA AMBIGUA: varios papers del corpus encajan casi igual de bien. No "
    "elijas uno al azar — añadir el año o el arXiv_id a la referencia y volver "
    "a verificar resuelve el empate."
)


def _normalize(text: Any) -> str:
    """Minúsculas y sin acentos, para comparar títulos en cualquier idioma."""
    flat = unicodedata.normalize("NFKD", str(text or ""))
    return "".join(c for c in flat if not unicodedata.combining(c)).lower()


def _tokens(text: Any) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", _normalize(text))
            if len(w) > 1 and w not in _STOP]


def _surname(rec: dict[str, Any]) -> str:
    raw = str(rec.get("authors_first") or "")
    parts = raw.replace("et al.", " ").split()
    return re.sub(r"[^a-z]", "", _normalize(parts[0])) if parts else ""


def _match(text: str, rec: dict[str, Any]) -> tuple[float, list[str]]:
    """
    Cuánto explica `rec` a la cita `text` -> (score 0..1, razones).

    La señal principal es la COBERTURA: qué fracción de los tokens de la cita
    aparece en el título. Jaccard castigaría injustamente una cita corta
    ("OpenVLA") contra un título largo, y eso es justo lo que escribe un agente.
    """
    norm = _normalize(text)
    reasons: list[str] = []

    aid = str(rec.get("arxiv_id") or "").strip().lower()
    if aid and aid != "-" and aid in norm:
        return 1.0, [f"arXiv:{aid} aparece literalmente en la cita"]

    quoted = set(_tokens(text))
    titled = set(_tokens(rec.get("title")))
    if not quoted or not titled:
        return 0.0, []

    overlap = quoted & titled
    # 0.90 y no 0.75: un título que explica TODA la cita debe poder confirmarse
    # por sí solo, sin exigir que el agente añada además año o autor.
    score = 0.90 * (len(overlap) / len(quoted))
    if overlap:
        sample = ", ".join(sorted(overlap)[:5])
        reasons.append(f"{len(overlap)} término(s) del título: {sample}")

    year = re.sub(r"\D", "", str(rec.get("year") or ""))
    year_ok = bool(year) and re.search(rf"\b{re.escape(year)}\b", norm) is not None
    if year_ok:
        score += 0.15
        reasons.append(f"año {year}")

    surname = _surname(rec)
    author_ok = len(surname) > 2 and re.search(rf"\b{re.escape(surname)}\b", norm) is not None
    if author_ok:
        score += 0.20
        reasons.append(f"autor {surname}")

    # Cita sin título ("Kim et al. 2024"): autor+año es evidencia débil pero
    # localizable. Se deja en "probable" para forzar la desambiguación.
    if not overlap and author_ok and year_ok:
        score = max(score, PROBABLE + 0.05)
        reasons.append("solo autor+año, sin título: desambiguar")

    return min(score, 1.0), reasons


def verify_citation(text: Any, records: list[dict[str, Any]] | None = None,
                    limit: int = 3) -> dict[str, Any]:
    """
    ¿Existe esta referencia en el corpus?

    Devuelve siempre `candidates`, también cuando falla: ver las coincidencias
    cercanas es lo que permite al agente autocorregir una cita mal escrita en
    lugar de insistir en una referencia inventada.
    """
    text = str(text or "").strip()
    if records is None:
        records = load_paper_records()
    if not text:
        return {"query": "", "status": "not_found", "in_corpus": False,
                "best_score": 0.0, "candidates": [],
                "instruction": "Cita vacía: no hay nada que verificar."}

    scored = []
    for rec in records:
        score, reasons = _match(text, rec)
        if score > 0:
            scored.append((score, reasons, rec))
    scored.sort(key=lambda item: -item[0])

    best = scored[0][0] if scored else 0.0
    status = ("confirmed" if best >= CONFIRMED
              else "probable" if best >= PROBABLE else "not_found")

    ambiguous = (status == "confirmed" and len(scored) > 1
                 and best - scored[1][0] < AMBIGUITY_MARGIN)
    if ambiguous:
        status = "probable"

    candidates = []
    for score, reasons, rec in scored[:max(1, int(limit))]:
        candidates.append({
            "score": round(score, 3),
            "reasons": reasons,
            "title": str(rec.get("title") or ""),
            "authors_first": str(rec.get("authors_first") or ""),
            "year": str(rec.get("year") or ""),
            "arxiv_id": str(rec.get("arxiv_id") or ""),
            "url": R.arxiv_url(rec.get("arxiv_id")),
            "category": str(rec.get("category") or ""),
            "file_path": str(rec.get("file_path") or ""),
            "bibtex": to_bibtex(rec),
        })

    return {
        "query": text,
        "status": status,
        # Solo `confirmed` cuenta como "está en el corpus": un probable es una
        # hipótesis, y tratarla como hecho es exactamente lo que hay que evitar.
        "in_corpus": status == "confirmed",
        "ambiguous": ambiguous,
        "best_score": round(best, 3),
        "corpus_size": len(records),
        "candidates": candidates,
        "instruction": _AMBIGUOUS if ambiguous else _INSTRUCTIONS[status],
    }


def verify_many(texts: Any, records: list[dict[str, Any]] | None = None,
                limit: int = 3) -> dict[str, Any]:
    """
    Verifica una bibliografía entera de una vez.

    Útil al final: el agente vuelca todas sus referencias y obtiene el veredicto
    global. Se cargan los registros una sola vez para las N comparaciones.
    """
    if isinstance(texts, str):
        texts = [part.strip() for part in re.split(r"[;\n]+", texts)]
    items = [str(t).strip() for t in (texts or []) if str(t).strip()]
    if records is None:
        records = load_paper_records()
    results = [verify_citation(item, records, limit) for item in items]
    counts = {"confirmed": 0, "probable": 0, "not_found": 0}
    for res in results:
        counts[res["status"]] = counts.get(res["status"], 0) + 1
    return {
        "total": len(results),
        "counts": counts,
        "ok": counts["confirmed"] == len(results) and len(results) > 0,
        "results": results,
    }


# ── Ensamblado del marco teórico ─────────────────────────────────────────────
def _retrieve(collection, query: str, **over: Any) -> list[dict[str, Any]]:
    """`run_query` con los defaults exactos que espera `build_where`."""
    args = Namespace(
        category=over.get("category"),
        folder=over.get("folder"),
        source=over.get("source", "all"),
        year_min=int(over.get("year_min", 0)),
        year_max=int(over.get("year_max", 0)),
        contains=over.get("contains"),
        min_sim=float(over.get("min_sim", 0.0)),
        include_retired=bool(over.get("include_retired", False)),
        k=int(over.get("k", 6)),
    )
    return run_query(collection, query, args)


def _pages(meta: dict[str, Any]) -> str:
    start, end = meta.get("page_start", 0), meta.get("page_end", 0)
    if start and end and start != end:
        return f"pp.{start}-{end}"
    return f"p.{start}" if start else ""


def _snippet(text: Any, limit: int = 700) -> str:
    flat = " ".join(str(text).split())
    if len(flat) <= limit:
        return flat
    return flat[:limit].rsplit(" ", 1)[0] + "…"


def build_marco(collection, query: str, *, k: int = 8, min_sim: float = 0.0,
                per_section: int = 3, include_retired: bool = False,
                category: list[str] | None = None, folder: list[str] | None = None,
                records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """
    Devuelve la evidencia organizada por secciones de marco teórico.

    Flujo: (1) la búsqueda semántica sobre PDFs decide qué papers son
    relevantes; (2) con esos papers se consulta papers.csv y se extraen
    limitaciones, vacíos y cifras — datos exactos, no aproximados; (3) una única
    consulta sobre repo_docs alimenta bases teóricas, vacíos curados y
    protocolo, que luego se reparten por documento.
    """
    if records is None:
        records = load_paper_records()
    by_path = records_by_path(records)

    # ── 1. Estado del arte: solo PDF, que es lo citable ────────────────────
    art = _retrieve(collection, query, source="pdf", k=k, min_sim=min_sim,
                    include_retired=include_retired, category=category,
                    folder=folder)
    papers: list[dict[str, Any]] = []
    seen: set[str] = set()
    for hit in art:
        path = str(hit["metadata"].get("doc_path", ""))
        if path and path not in seen:      # un paper = una entrada, no k fragmentos
            seen.add(path)
            papers.append(hit)

    estado: list[dict[str, Any]] = []
    for n, hit in enumerate(papers, start=1):
        meta = hit["metadata"]
        path = str(meta.get("doc_path", ""))
        rec = by_path.get(path) or {}
        estado.append({
            "n": n,
            "similarity": round(hit["similarity"], 3),
            "title": str(meta.get("title") or R.title_from_filename(Path(path))),
            "authors_first": str(rec.get("authors_first") or ""),
            "year": str(meta.get("year") or rec.get("year") or ""),
            "arxiv_id": str(meta.get("arxiv_id") or ""),
            "url": R.arxiv_url(meta.get("arxiv_id")),
            "pages": _pages(meta),
            "category": str(meta.get("category") or ""),
            "folder": str(meta.get("folder") or ""),
            "doc_path": path,
            "snippet": _snippet(hit["document"]),
            "bibtex": to_bibtex(rec) if rec else "",
        })

    # ── 2. Análisis estructurado de ESOS papers (desde papers.csv) ─────────
    limitaciones: list[dict[str, Any]] = []
    comparativa: list[dict[str, Any]] = []
    vacios_cat: dict[str, list[dict[str, Any]]] = {}
    for item in estado:
        rec = by_path.get(item["doc_path"]) or {}
        ref = f"{item['title']} ({item['year']})" if item["year"] else item["title"]
        base = {"paper": ref, "arxiv_id": item["arxiv_id"], "url": item["url"]}

        lim = str(rec.get("limitations") or "").strip()
        if lim and lim != "-":
            limitaciones.append({**base, "limitations": lim})

        gap = str(rec.get("gap_category") or "").strip()
        if gap and gap != "-":
            vacios_cat.setdefault(gap, []).append(dict(base))

        comparativa.append({
            **base, "year": item["year"],
            "robot_type": str(rec.get("robot_type") or ""),
            "task": str(rec.get("task") or ""),
            "model_type": str(rec.get("model_type") or ""),
            "simulator": str(rec.get("simulator") or ""),
            "ros_integration": str(rec.get("ros_integration") or ""),
            "sim2real": str(rec.get("sim2real") or ""),
            "latency_ms": str(rec.get("latency_ms") or ""),
            "compute_resources": str(rec.get("compute_resources") or ""),
            "code_available": str(rec.get("code_available") or ""),
            "data_available": str(rec.get("data_available") or ""),
        })

    # ── 3. Docs curados: UNA consulta, repartida por documento ─────────────
    docs = _retrieve(collection, query, folder=["repo_docs"], source="markdown",
                     k=max(12, per_section * 4), min_sim=min_sim,
                     include_retired=include_retired)
    buckets: dict[str, list[dict[str, Any]]] = {}
    for hit in docs:
        buckets.setdefault(str(hit["metadata"].get("doc_path", "")), []).append(hit)

    def curated(name: str) -> list[dict[str, Any]]:
        out = []
        for hit in buckets.get(name, [])[:per_section]:
            meta = hit["metadata"]
            out.append({
                "doc_path": str(meta.get("doc_path", "")),
                "heading_path": str(meta.get("heading_path", "")),
                "similarity": round(hit["similarity"], 3),
                "snippet": _snippet(hit["document"]),
            })
        return out

    bases = curated(CURATED_DOCS["bases_teoricas"])
    vacios_doc = curated(CURATED_DOCS["vacios"])
    metodo = curated(CURATED_DOCS["metodologia"])

    # ── 4. Avisos: lo que el agente debe saber ANTES de escribir ───────────
    warnings = [
        "papers.csv guarda authors_first como 'Apellido et al.': completa los "
        "nombres de pila desde arXiv antes de dar el BibTeX por bueno.",
    ]
    if len(papers) < 3:
        warnings.append(
            f"COBERTURA BAJA: solo {len(papers)} paper(s) relevante(s). El corpus "
            f"tiene {len(records)} papers y puede no cubrir este tema; busca "
            "fuentes externas y márcalas como tales en el texto.")
    if estado:
        recent = sum(1 for e in estado
                     if str(e["year"]).isdigit() and int(str(e["year"])) >= 2025)
        if recent / len(estado) > 0.6:
            warnings.append(
                f"{recent}/{len(estado)} papers son de 2025-2026: la carpeta "
                "07_Recent_2025_2026 pesa mucho en el índice. Revisa si estás "
                "sobreponderando trabajo reciente frente a los fundacionales.")
    faltan = [nombre for nombre, items in (("bases_teoricas", bases),
                                           ("vacios", vacios_doc),
                                           ("metodologia", metodo)) if not items]
    if faltan:
        warnings.append("Sin evidencia curada para: " + ", ".join(faltan) + ".")

    return {
        "query": query,
        "corpus": {"papers_total": len(records), "papers_matched": len(papers),
                   "fragmentos_evaluados": len(art)},
        "sections": {
            "estado_del_arte": {**MARCO_SECTIONS["estado_del_arte"], "items": estado},
            "limitaciones": {**MARCO_SECTIONS["limitaciones"], "items": limitaciones},
            "vacios": {**MARCO_SECTIONS["vacios"], "por_categoria": vacios_cat,
                       "items": vacios_doc},
            "bases_teoricas": {**MARCO_SECTIONS["bases_teoricas"], "items": bases},
            "metodologia": {**MARCO_SECTIONS["metodologia"], "items": metodo},
            "comparativa": {**MARCO_SECTIONS["comparativa"], "items": comparativa},
        },
        "bibtex": "\n\n".join(e["bibtex"] for e in estado if e["bibtex"]),
        "collection_bibtex": collection_bibtex(),
        "warnings": warnings,
    }


# ── Presentación ─────────────────────────────────────────────────────────────
def render_marco(data: dict[str, Any]) -> str:
    """Versión legible del dict: para el CLI y para pegar en un LLM."""
    sec = data["sections"]
    corpus = data["corpus"]
    bar = "=" * 78
    out = [
        bar,
        "  EVIDENCIA PARA MARCO TEÓRICO — awesome-embodied-ai",
        f"  Consulta : {data['query']}",
        f"  Cobertura: {corpus['papers_matched']} papers relevantes "
        f"de {corpus['papers_total']} en el corpus",
        bar,
    ]

    def curated_block(items: list[dict[str, Any]], vacio: str) -> list[str]:
        if not items:
            return [f"  ({vacio})", ""]
        block: list[str] = []
        for it in items:
            heading = it["heading_path"] or "sin sección"
            block.append(f"  [{it['doc_path']} › {heading} · sim {it['similarity']:.3f}]")
            block.append(f"  {it['snippet']}")
            block.append("")
        return block

    out += ["", "## 1. ESTADO DEL ARTE", f"    ({sec['estado_del_arte']['origen']})", ""]
    for it in sec["estado_del_arte"]["items"]:
        bits = [b for b in (it["authors_first"], it["year"],
                            f"arXiv:{it['arxiv_id']}" if it["arxiv_id"] else "",
                            it["pages"], it["category"],
                            f"sim {it['similarity']:.3f}") if b]
        out.append(f"[{it['n']}] {it['title']}")
        out.append(f"    {' · '.join(bits)}")
        out.append(f"    archivo: {it['doc_path']}")
        if it["url"]:
            out.append(f"    enlace : {it['url']}")
        out.append("")
        out.append(f"    {it['snippet']}")
        out.append("")

    out += ["## 2. LIMITACIONES DOCUMENTADAS", f"    ({sec['limitaciones']['origen']})", ""]
    lims = sec["limitaciones"]["items"]
    out += ([f"  • {it['paper']}: {it['limitations']}" for it in lims]
            if lims else ["  (papers.csv no registra limitaciones para estos papers)"])

    out += ["", "## 3. VACÍOS DE INVESTIGACIÓN", f"    ({sec['vacios']['origen']})", ""]
    if sec["vacios"]["por_categoria"]:
        for gap, papers in sec["vacios"]["por_categoria"].items():
            out.append(f"  ◆ {gap}")
            out += [f"      - {p['paper']}" for p in papers]
    else:
        out.append("  (sin gap_category para estos papers)")
    out.append("")
    out += curated_block(sec["vacios"]["items"], "research-gaps.md sin coincidencias")

    out += ["## 4. BASES TEÓRICAS", f"    ({sec['bases_teoricas']['origen']})", ""]
    out += curated_block(sec["bases_teoricas"]["items"], "GLOSSARY.md sin coincidencias")

    out += ["## 5. PROTOCOLO METODOLÓGICO", f"    ({sec['metodologia']['origen']})", ""]
    out += curated_block(sec["metodologia"]["items"],
                         "research-protocol.md sin coincidencias")

    out += ["## 6. COMPARATIVA CUANTITATIVA", f"    ({sec['comparativa']['origen']})", ""]
    rows = sec["comparativa"]["items"]
    if rows:
        out.append(f"  {'PAPER':<46}{'AÑO':<6}{'LATENCIA':<11}{'ROS 2':<15}{'SIM2REAL':<9}")
        out.append("  " + "-" * 85)
        for it in rows:
            out.append(f"  {it['paper'][:44]:<46}{str(it['year']):<6}"
                       f"{str(it['latency_ms'])[:9]:<11}"
                       f"{str(it['ros_integration'])[:13]:<15}"
                       f"{str(it['sim2real'])[:7]:<9}")
    else:
        out.append("  (sin datos)")

    out += ["", "## BIBTEX DE LOS PAPERS RECUPERADOS", ""]
    out.append(data["bibtex"] or "(sin entradas)")
    out += ["", "% Si apoyas el texto en el corpus, cítalo también:",
            data["collection_bibtex"]]

    out += ["", "## AVISOS PARA QUIEN REDACTA", ""]
    out += [f"  ! {w}" for w in data["warnings"]]
    return "\n".join(out) + "\n"


def render_verify(result: dict[str, Any]) -> str:
    """Veredicto legible de una verificación de cita."""
    icon = {"confirmed": "[OK]", "probable": "[??]", "not_found": "[NO]"}
    out = [f"{icon.get(result['status'], '[??]')} {result['status'].upper()} "
           f"(score {result['best_score']:.3f}) — {result['query']}"]
    for cand in result.get("candidates", []):
        out.append(f"    {cand['score']:.3f}  {cand['title']}")
        out.append(f"           {cand['authors_first']} · {cand['year']} · "
                   f"arXiv:{cand['arxiv_id'] or '-'} · {cand['category']}")
        out.append(f"           por qué: {'; '.join(cand['reasons'])}")
    out.append("")
    out.append(f"    >> {result['instruction']}")
    return "\n".join(out)






