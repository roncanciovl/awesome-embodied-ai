"""
raglib — utilidades compartidas del RAG de awesome-embodied-ai.

Todo es local y sin credenciales:
  * Extracción de texto de PDF con PyMuPDF.
  * Embeddings con el modelo ONNX all-MiniLM-L6-v2 que trae ChromaDB
    (se descarga una sola vez y se guarda DENTRO de esta carpeta, en rag/models/).
  * Índice vectorial persistido en rag/chroma_db/.

Ningún archivo de esta carpeta contiene tokens ni llaves.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable

# ── Rutas (siempre relativas al repo, nunca fuera del workspace) ─────────────
RAG_DIR = Path(__file__).resolve().parent
REPO_DIR = RAG_DIR.parent
PAPERS_DIR = REPO_DIR / "papers"
PAPERS_CSV = REPO_DIR / "papers.csv"

DB_DIR = RAG_DIR / "chroma_db"
CACHE_DIR = RAG_DIR / "cache"
MODEL_DIR = RAG_DIR / "models"

COLLECTION_NAME = "embodied_ai"

# Documentos del repo que también se indexan (conocimiento curado, no solo PDFs).
MARKDOWN_DOCS = [
    "README.md",
    "GLOSSARY.md",
    "CONTRIBUTING.md",
    "research-protocol.md",
    "research-gaps.md",
    "tactile-sota.md",
    "papers/PAPERS.md",
]

# Nunca indexar (plan privado, notas de trabajo, artefactos generados).
EXCLUDE_MARKDOWN = {"PLAN_PUBLICACIONES_HENRY.md"}
RETIRED_DIRNAME = "_retirados"

# ── Parámetros de chunking ───────────────────────────────────────────────────
CHUNK_CHARS = 1400      # ~300-350 tokens; all-MiniLM-L6-v2 acepta hasta 256 words
MIN_CHUNK_CHARS = 120
OVERLAP_CHARS = 220
EMBED_BATCH = 64


# ── Limpieza de texto ────────────────────────────────────────────────────────
_LIGATURES = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"}
_WS_RE = re.compile(r"[ \t\r\f\v]+")
_HYPHEN_RE = re.compile(r"(\w)-\n(\w)")
_MULTI_NL_RE = re.compile(r"\n{3,}")


def clean_text(raw: str) -> str:
    """Normaliza texto extraído de PDF: ligaduras, guiones de corte, espacios."""
    if not raw:
        return ""
    text = unicodedata.normalize("NFKC", raw)
    for lig, rep in _LIGATURES.items():
        text = text.replace(lig, rep)
    text = text.replace("\u00ad", "")          # soft hyphen
    text = _HYPHEN_RE.sub(r"\1\2", text)       # "manipu-\nlation" -> "manipulation"
    text = _WS_RE.sub(" ", text)
    text = _MULTI_NL_RE.sub("\n\n", text)
    return text.strip()


def is_noise_page(text: str) -> bool:
    """Filtra páginas sin prosa útil (portadas vacías, solo números de página)."""
    words = re.findall(r"[A-Za-z]{3,}", text)
    return len(words) < 12


# ── Metadatos desde papers.csv ───────────────────────────────────────────────
_SCALAR_TYPES = (str, int, float, bool)


def _scalar(value: Any) -> Any:
    """Chroma solo acepta str/int/float/bool en metadata."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    return str(value)


def load_papers_metadata() -> dict[str, dict[str, Any]]:
    """Devuelve {ruta_relativa_posix: metadatos} usando la columna file_path."""
    table: dict[str, dict[str, Any]] = {}
    if not PAPERS_CSV.exists():
        return table
    with PAPERS_CSV.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            file_path = (row.get("file_path") or "").strip()
            if not file_path:
                continue
            key = file_path.replace("\\", "/").removeprefix("papers/")
            meta = {k: _scalar(v) for k, v in row.items() if k != "file_path"}
            # year como entero para poder filtrar con $gte/$lte
            try:
                meta["year"] = int(str(meta.get("year", "")).strip())
            except (TypeError, ValueError):
                meta["year"] = 0
            table[key] = meta
    return table

# ── Detección de bibliografía ────────────────────────────────────────────────
# Las listas de referencias comparten vocabulario con el cuerpo del paper y por
# eso rankean alto en una búsqueda semántica, pero no aportan evidencia: son
# ruido. Hay dos estilos de entrada y se detectan por separado:
#
#   A) numerado     "[12] Apellido, Nombre, ..."  → arXiv/CoRL/RSS/ICRA
#   B) autor-año    "Apellido, N., ..., venue, 2019."  → NeurIPS/ICML/Nature
#   C) paréntesis   "35. V. Barasuol, ..., 916-926 (2018)."  → Science Robotics
#                   "12. Du, Y., ..., pp. 276-286 (2019)"     → Springer LNCS
#
# La clave es exigir VOLUMEN ABSOLUTO de entradas, no solo densidad: una página
# de referencias tiene decenas, mientras que la prosa tiene 0-3 citas y una tabla
# puede tener muchos años sueltos. Normalizar solo por longitud clasificaba mal
# páginas cortas y tablas (falsos positivos medidos sobre este corpus).
_REF_ENTRY_RE = re.compile(r"\[\d{1,3}\]\s+[A-Z][^\[\]\n]{0,40}?,")
# Año de publicación real: coma o punto + ESPACIO + año + punto.
#   - El espacio obligatorio excluye los años de un DOI ("10.1016/j.echo.2014.10.003").
#   - Excluir ";" y "," como cierre es lo que elimina las citas parentéticas en
#     prosa: "(Zhang & Chai, 2021; Pashevich et al., 2021; Silva et al., 2021)".
#     Una entrada bibliográfica de verdad cierra el año con punto.
_VENUE_YEAR_RE = re.compile(r"[.,]\s+(?:19|20)\d{2}\.")
# Estilo C: año entre paréntesis de APERTURA. Es discriminante porque en una
# cita dentro de prosa —"(Hwangbo et al., 2019)"— lo que precede al año es un
# espacio, no un paréntesis; el paréntesis de apertura solo aparece cuando el
# año cierra él mismo la entrada bibliográfica.
_PAREN_YEAR_RE = re.compile(r"\((?:19|20)\d{2}\)")
_ETAL_RE = re.compile(r"\bet\s+al\.")

MIN_NUMBERED_ENTRIES = 5      # estilo A: entradas "[n] Apellido,"
MIN_VENUE_YEARS = 5           # estilo B: años de publicación cerrados con punto
MIN_VENUE_YEAR_DENSITY = 2.5  # estilo B: por cada 1000 caracteres
MIN_PAREN_YEARS = 6           # estilo C: años "(2019)"
MIN_PAREN_YEAR_DENSITY = 3.0  # estilo C: por cada 1000 caracteres


def reference_signals(text: str) -> tuple[int, int, int, int]:
    """(entradas "[n]", 'venue, año.', '(año)', 'et al.') presentes en el bloque."""
    return (
        len(_REF_ENTRY_RE.findall(text)),
        len(_VENUE_YEAR_RE.findall(text)),
        len(_PAREN_YEAR_RE.findall(text)),
        len(_ETAL_RE.findall(text)),
    )


def reference_score(text: str) -> float:
    """Puntuación ponderada por 1000 caracteres. Informativa, para depurar."""
    if not text:
        return 0.0
    strong, venue, paren, etal = reference_signals(text)
    return (3 * strong + 2 * venue + 2 * paren + etal) * 1000.0 / len(text)


def is_reference_block(text: str) -> bool:
    """True si el bloque es predominantemente una lista de referencias."""
    if len(text) < 300:
        return False
    strong, venue, paren, _etal = reference_signals(text)
    if strong >= MIN_NUMBERED_ENTRIES:
        return True
    if (venue >= MIN_VENUE_YEARS
            and venue * 1000.0 / len(text) >= MIN_VENUE_YEAR_DENSITY):
        return True
    return (
        paren >= MIN_PAREN_YEARS
        and paren * 1000.0 / len(text) >= MIN_PAREN_YEAR_DENSITY
    )


# Encabezado "References" aislado en su propia línea. Sirve para el caso que la
# densidad no cubre: la bibliografía empieza a mitad de página, de modo que la
# página entera queda diluida por la prosa anterior y no supera el umbral.
_REFERENCES_HEADING_RE = re.compile(
    r"(?mi)^[ \t]*(?:references|bibliography|referencias)[ \t]*$"
)
MIN_TAIL_SIGNALS = 3   # entradas o años mínimos tras el encabezado para cortar


def strip_references_tail(text: str) -> str:
    """Corta el texto desde un encabezado 'References' hasta el final de página.

    Solo corta si lo que sigue parece de verdad una lista de referencias: así un
    'References' suelto en cabecera o pie de página no amputa una página útil.
    """
    match = _REFERENCES_HEADING_RE.search(text)
    if not match:
        return text
    strong, venue, paren, _etal = reference_signals(text[match.end():])
    if max(strong, venue, paren) >= MIN_TAIL_SIGNALS:
        return text[: match.start()].rstrip()
    return text


# ── Extracción de PDF (con caché) ────────────────────────────────────────────
# Versión del pipeline de extracción: forma parte de la clave de caché para que
# cambiar los filtros invalide automáticamente los JSON ya generados.
EXTRACT_VERSION = "v4"


def _cache_key(path: Path) -> str:
    stat = path.stat()
    raw = f"{EXTRACT_VERSION}|{path.as_posix()}|{stat.st_size}|{int(stat.st_mtime)}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def extract_pdf_pages(path: Path, use_cache: bool = True) -> list[dict[str, Any]]:
    """Extrae el texto página a página. Devuelve [{'page': n, 'text': str}, ...]."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{_cache_key(path)}.json"

    if use_cache and cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    try:                       # PyMuPDF >= 1.24 renombra fitz -> pymupdf
        import pymupdf as mupdf
    except ImportError:        # pragma: no cover - PyMuPDF antiguo
        import fitz as mupdf

    pages: list[dict[str, Any]] = []
    with mupdf.open(path) as doc:
        for index, page in enumerate(doc, start=1):
            text = strip_references_tail(clean_text(page.get_text("text")))
            if not text or is_noise_page(text) or is_reference_block(text):
                continue
            pages.append({"page": index, "text": text})

    if use_cache:
        try:
            cache_file.write_text(
                json.dumps(pages, ensure_ascii=False), encoding="utf-8"
            )
        except OSError:
            pass
    return pages


# ── Chunking ─────────────────────────────────────────────────────────────────
def _split_paragraphs(text: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"\n\s*\n", text)]
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        if len(part) <= CHUNK_CHARS:
            out.append(part)
        else:  # párrafo gigante (típico en PDFs de 2 columnas): corte por oraciones
            buf = ""
            for sentence in re.split(r"(?<=[.!?])\s+", part):
                if len(buf) + len(sentence) + 1 > CHUNK_CHARS and buf:
                    out.append(buf.strip())
                    buf = sentence
                else:
                    buf = f"{buf} {sentence}".strip()
            if buf:
                out.append(buf.strip())
    return out



def chunk_pdf(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Agrupa párrafos en chunks con solape conservando el rango de páginas."""
    chunks: list[dict[str, Any]] = []
    buf = ""
    start_page = 0
    last_text = ""          # cola del último chunk ACEPTADO (para el solape)

    def flush(end_page: int) -> None:
        nonlocal buf, start_page, last_text
        candidate = buf.strip()
        buf = ""
        # Un bloque de referencias se descarta y además corta el solape: no
        # queremos arrastrar bibliografía al chunk siguiente.
        if len(candidate) < MIN_CHUNK_CHARS or is_reference_block(candidate):
            last_text = ""
            return
        chunks.append(
            {
                "text": candidate,
                "page_start": start_page or end_page,
                "page_end": end_page,
            }
        )
        last_text = candidate

    for entry in pages:
        page = int(entry["page"])
        if not buf:
            start_page = page
        for paragraph in _split_paragraphs(entry["text"]):
            if buf and len(buf) + len(paragraph) + 2 > CHUNK_CHARS:
                flush(page)
                start_page = page
                # solape: arrastrar la cola del chunk anterior aceptado
                buf = last_text[-OVERLAP_CHARS:] if last_text else ""
            buf = f"{buf}\n\n{paragraph}".strip() if buf else paragraph
        if not buf:
            start_page = page + 1
    if buf:
        flush(pages[-1]["page"] if pages else 0)
    return chunks


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def chunk_markdown(text: str) -> list[dict[str, Any]]:
    """Chunking de Markdown conservando la ruta de encabezados (heading_path)."""
    text = clean_text(text)
    blocks: list[dict[str, Any]] = []
    headings: list[str] = []

    current: list[str] = []

    def push(section: str) -> None:
        body = "\n\n".join(current).strip()
        current.clear()
        if len(body) < MIN_CHUNK_CHARS:
            return
        for chunk in _split_paragraphs(body):
            blocks.append(
                {
                    "text": chunk,
                    "heading_path": " > ".join(headings),
                    "page_start": 0,
                    "page_end": 0,
                }
            )

    for block in re.split(r"\n\s*\n", text):
        match = _HEADING_RE.match(block.strip())
        if match:
            push(block)
            level = len(match.group(1))
            title = match.group(2).strip()
            del headings[level - 1:]
            headings.append(title)
            current.append(f"{'#' * level} {title}")
        else:
            current.append(block.strip())
    push("")
    return blocks



# ── Descubrimiento de documentos ─────────────────────────────────────────────
def doc_id_for(rel_posix: str) -> str:
    """ID estable por documento -> permite upsert idempotente (actualizar sin duplicar)."""
    return hashlib.sha1(rel_posix.encode("utf-8")).hexdigest()[:12]


def rel_to_repo(path: Path) -> str:
    return path.resolve().relative_to(REPO_DIR).as_posix()


def iter_pdf_paths(include_retired: bool = False) -> list[Path]:
    paths = sorted(PAPERS_DIR.rglob("*.pdf"))
    if not include_retired:
        paths = [p for p in paths if RETIRED_DIRNAME not in p.parts]
    return paths


def iter_markdown_paths() -> list[Path]:
    paths: list[Path] = []
    for rel in MARKDOWN_DOCS:
        candidate = REPO_DIR / rel
        if candidate.exists() and candidate.name not in EXCLUDE_MARKDOWN:
            paths.append(candidate)
    return paths


def title_from_filename(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").strip()


# ── Embeddings y cliente de Chroma ───────────────────────────────────────────
def build_embedding_function():
    """
    all-MiniLM-L6-v2 en ONNX (384 dims), 100% local y sin credenciales.

    El modelo se descarga una sola vez y se guarda en rag/models/ para que
    nada se escriba fuera del workspace.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

    # Redirigir la caché del modelo ONNX dentro del workspace (si la versión
    # de chromadb lo expone como atributo de clase).
    for attr in ("DOWNLOAD_PATH", "EXTRACT_DIR"):
        if attr == "DOWNLOAD_PATH" and hasattr(ONNXMiniLM_L6_V2, attr):
            try:
                setattr(ONNXMiniLM_L6_V2, attr, MODEL_DIR)
            except (AttributeError, TypeError):
                pass
    return ONNXMiniLM_L6_V2()


def get_client():
    import chromadb
    from chromadb.config import Settings

    DB_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(DB_DIR),
        settings=Settings(anonymized_telemetry=False, allow_reset=True),
    )


def get_collection(client, embedding_function=None, create: bool = True):
    if embedding_function is None:
        embedding_function = build_embedding_function()
    if create:
        return client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
            embedding_function=embedding_function,
        )
    # get_collection() no admite `metadata`; la colección ya existe.
    return client.get_collection(
        name=COLLECTION_NAME, embedding_function=embedding_function
    )


def force_utf8_stdout() -> None:
    """Evita que la consola de Windows (cp1252/cp850) rompa tildes y símbolos."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover
            pass



# ── Presentación de resultados ───────────────────────────────────────────────
def arxiv_url(arxiv_id: Any) -> str:
    aid = str(arxiv_id or "").strip()
    return f"https://arxiv.org/abs/{aid}" if aid and aid != "-" else ""


def source_label(meta: dict[str, Any]) -> str:
    if meta.get("source_type") == "markdown":
        return str(meta.get("doc_path", ""))
    label = str(meta.get("title") or title_from_filename(Path(str(meta.get("doc_path", "")))))
    pages = ""
    start, end = meta.get("page_start", 0), meta.get("page_end", 0)
    if start and end:
        pages = f"p.{start}" if start == end else f"pp.{start}-{end}"
    elif start:
        pages = f"p.{start}"
    aid = str(meta.get("arxiv_id") or "").strip()
    bits = [label]
    if aid and aid != "-":
        bits.append(f"arXiv:{aid}")
    if meta.get("year"):
        bits.append(str(meta["year"]))
    if pages:
        bits.append(pages)
    return " · ".join(bits)


def format_hit(rank: int, meta: dict[str, Any], text: str, distance: float) -> str:
    score = max(0.0, 1.0 - float(distance))  # cosine distance -> similitud
    lines = [
        f"[{rank}] {source_label(meta)}   (similitud {score:.3f})",
        f"    archivo: {meta.get('doc_path', '')}",
    ]
    if meta.get("heading_path"):
        lines.append(f"    sección: {meta['heading_path']}")
    if meta.get("category"):
        lines.append(f"    categoría: {meta['category']}")
    url = arxiv_url(meta.get("arxiv_id"))
    if url:
        lines.append(f"    enlace: {url}")
    snippet = " ".join(str(text).split())
    lines.append("")
    lines.append(f"    {snippet}")
    return "\n".join(lines)


def build_prompt(query: str, hits: list[dict[str, Any]]) -> str:
    """
    Bloque de contexto listo para pegar en cualquier LLM.

    Este RAG es deliberadamente solo-recuperación: no hay llaves de API en esta
    carpeta (está sincronizada con OneDrive). El LLM lo pones tú.
    """
    context_parts = []
    for i, hit in enumerate(hits, start=1):
        meta = hit["metadata"]
        context_parts.append(
            f"[{i}] {source_label(meta)}\n{hit['document']}"
        )
    context = "\n\n---\n\n".join(context_parts)
    return (
        "Eres un asistente de investigación sobre Embodied AI, modelos VLA/VLM/LLM, "
        "ROS 2 y Sim2Real. Responde usando ÚNICAMENTE el contexto siguiente. "
        "Cita las fuentes con su número [n] y di explícitamente si el contexto no "
        "alcanza para responder.\n\n"
        f"PREGUNTA: {query}\n\n"
        "CONTEXTO RECUPERADO:\n"
        "=======================\n"
        f"{context}\n"
        "=======================\n\n"
        "RESPUESTA:"
    )

