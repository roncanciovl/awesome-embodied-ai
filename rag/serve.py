#!/usr/bin/env python
"""
serve — interfaz web local del RAG de awesome-embodied-ai.

Servidor HTTP de solo lectura sobre 127.0.0.1 construido ÚNICAMENTE con la
stdlib (`http.server`): sin dependencias nuevas y sin credenciales. Reutiliza
`raglib` y las funciones de `query.py`, así que la web y el CLI aplican
exactamente los mismos filtros.

Arranque (desde la raíz del repo):
    rag\\.venv\\Scripts\\python.exe rag\\serve.py
    rag\\.venv\\Scripts\\python.exe rag\\serve.py --port 8757 --no-browser

Por qué stdlib y no Flask/FastAPI:
    Esta carpeta se sincroniza con OneDrive. Un framework web sumaría
    dependencias pesadas al venv y superficie de actualización sin aportar nada:
    la UI y los agentes necesitan seis endpoints de lectura. `http.server` ya
    está instalado.

Seguridad (deliberada):
    * Escucha SOLO en 127.0.0.1: el índice no es accesible desde la LAN.
    * Valida el header `Host` para evitar DNS rebinding.
    * No sirve ficheros arbitrarios: solo `web/index.html` y las rutas `/api/*`.
    * No escribe en disco, no hace red saliente y no usa credenciales.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import webbrowser
from argparse import Namespace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import marco as M  # noqa: E402  (marco teórico + verificación de citas)
import raglib as R  # noqa: E402
from query import build_where, run_query  # noqa: E402  (reuso, no duplico)

WEB_DIR = Path(__file__).resolve().parent / "web"
INDEX_HTML = WEB_DIR / "index.html"

DEFAULT_PORT = 8757
HOST = "127.0.0.1"
ALLOWED_HOSTS = {"127.0.0.1", "localhost", "[::1]"}
MAX_K = 50

# Chroma persiste en SQLite; el candado serializa el acceso cuando hay varias
# pestañas abiertas. Las consultas rondan los 50 ms, no se nota.
LOCK = threading.Lock()

STATE: dict[str, Any] = {"collection": None, "error": ""}


# ── Query string -> Namespace (el contrato que espera query.py) ──────────────
def first(params: dict[str, list[str]], key: str, default: str = "") -> str:
    values = params.get(key) or []
    return values[0].strip() if values else default


def many(params: dict[str, list[str]], key: str) -> list[str] | None:
    """Acepta `category=a&category=b` y también `category=a,b`."""
    flat: list[str] = []
    for value in params.get(key) or []:
        flat.extend(part.strip() for part in str(value).split(",") if part.strip())
    return flat or None


def to_number(value: str, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def args_from_params(params: dict[str, list[str]]) -> Namespace:
    """
    Traduce la query string al `Namespace` que consumen `build_where`/`run_query`.

    Reusar `query.py` en lugar de reimplementar los filtros garantiza que una
    consulta devuelva lo mismo en la web, en el CLI y en `ask.ps1`.
    """
    source = first(params, "source", "all")
    k = int(to_number(first(params, "k"), 6))
    return Namespace(
        category=many(params, "category"),
        folder=many(params, "folder"),
        source=source if source in ("all", "pdf", "markdown") else "all",
        year_min=int(to_number(first(params, "year_min"), 0)),
        year_max=int(to_number(first(params, "year_max"), 0)),
        contains=first(params, "contains") or None,
        min_sim=to_number(first(params, "min_sim"), 0.0),
        k=max(1, min(k, MAX_K)),
        include_retired=first(params, "include_retired").lower() in ("1", "true", "yes"),
    )


# ── Endpoints ────────────────────────────────────────────────────────────────
def api_search(params: dict[str, list[str]]) -> dict[str, Any]:
    query = first(params, "q")
    if not query:
        return {"error": "Falta el parámetro 'q'."}
    args = args_from_params(params)
    with LOCK:
        hits = run_query(STATE["collection"], query, args)
    return {
        "query": query,
        "k": args.k,
        "count": len(hits),
        "documents": len({h["metadata"].get("doc_id") for h in hits}),
        "hits": hits,
    }


def api_prompt(params: dict[str, list[str]]) -> dict[str, Any]:
    """El bloque de contexto de `raglib.build_prompt`, listo para pegar en un LLM."""
    query = first(params, "q")
    if not query:
        return {"error": "Falta el parámetro 'q'."}
    args = args_from_params(params)
    with LOCK:
        hits = run_query(STATE["collection"], query, args)
    if not hits:
        return {"error": "Sin resultados con esos filtros.", "prompt": "", "count": 0}
    return {"query": query, "count": len(hits), "prompt": R.build_prompt(query, hits)}


def api_facets() -> dict[str, Any]:
    """Valores presentes en el índice, para poblar los desplegables de filtros."""
    with LOCK:
        metas = STATE["collection"].get(include=["metadatas"]).get("metadatas") or []
    categories: dict[str, int] = {}
    folders: dict[str, int] = {}
    years: set[int] = set()
    for meta in metas:
        meta = meta or {}
        cat = str(meta.get("category") or "")
        fol = str(meta.get("folder") or "")
        if cat:
            categories[cat] = categories.get(cat, 0) + 1
        if fol:
            folders[fol] = folders.get(fol, 0) + 1
        try:
            if meta.get("year"):
                years.add(int(meta["year"]))
        except (TypeError, ValueError):
            pass
    return {
        "categories": sorted(categories.items()),
        "folders": sorted(folders.items()),
        "year_min": min(years) if years else 0,
        "year_max": max(years) if years else 0,
    }


def api_stats() -> dict[str, Any]:
    """Equivalente en JSON de `build_index.py --stats`."""
    import chromadb

    with LOCK:
        total = STATE["collection"].count()
        metas = STATE["collection"].get(include=["metadatas"]).get("metadatas") or []

    docs: dict[str, dict[str, Any]] = {}
    by_folder: dict[str, int] = {}
    for meta in metas:
        meta = meta or {}
        entry = docs.setdefault(
            str(meta.get("doc_id", "")),
            {"type": str(meta.get("source_type", "")), "n": 0},
        )
        entry["n"] += 1
        folder = str(meta.get("folder") or "?")
        by_folder[folder] = by_folder.get(folder, 0) + 1

    return {
        "chromadb": chromadb.__version__,
        "collection": R.COLLECTION_NAME,
        "chunks": total,
        "documents": len(docs),
        "pdfs": sum(1 for d in docs.values() if d["type"] == "pdf"),
        "markdowns": sum(1 for d in docs.values() if d["type"] == "markdown"),
        "by_folder": sorted(by_folder.items()),
        "db_dir": R.rel_to_repo(R.DB_DIR),
    }


# ── Handler HTTP ─────────────────────────────────────────────────────────────
def api_marco(params: dict[str, list[str]]) -> dict[str, Any]:
    """
    Evidencia organizada por secciones de marco teórico.

    Pensado para agentes de IA que redactan un paper: en vez de un ranking plano
    de fragmentos devuelve estado del arte, limitaciones documentadas, vacíos,
    bases teóricas, comparativa cuantitativa y BibTeX.
    """
    query = first(params, "q")
    if not query:
        return {"error": "Falta el parámetro q."}
    args = args_from_params(params)
    per_section = int(to_number(first(params, "per_section"), 3))
    return M.build_marco(
        STATE["collection"], query,
        k=min(args.k, MAX_K),
        min_sim=args.min_sim,
        per_section=min(max(per_section, 1), 10),
        include_retired=args.include_retired,
        category=args.category,
        folder=args.folder,
    )


def api_verify(params: dict[str, list[str]]) -> dict[str, Any]:
    """
    ¿Existe esta referencia en el corpus? Guardarrail anti-alucinación.

    Acepta `ref` (repetible) o `refs` (varias separadas por `|`). A diferencia de
    `many()`, aquí NO se parte por comas: una referencia legítima las lleva
    ("Kim et al., 2024"). Solo lee papers.csv, no toca Chroma.
    """
    refs = [str(v).strip() for v in (params.get("ref") or []) if str(v).strip()]
    bulk = first(params, "refs")
    if bulk:
        refs.extend(p.strip() for p in bulk.split("|") if p.strip())
    if not refs:
        return {"error": "Falta el parámetro ref (repetible) o refs (separadas por |)."}
    limit = min(max(int(to_number(first(params, "limit"), 3)), 1), 10)
    records = M.load_paper_records()
    if len(refs) == 1:
        return M.verify_citation(refs[0], records, limit)
    return M.verify_many(refs, records, limit)



class Handler(BaseHTTPRequestHandler):
    server_version = "awesome-embodied-rag/1.0"
    protocol_version = "HTTP/1.1"  # exige Content-Length exacto (se envía siempre)

    def log_message(self, fmt: str, *fmt_args: Any) -> None:
        sys.stderr.write(f"  {fmt % fmt_args}\n")

    def _host_allowed(self) -> bool:
        raw = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip().lower()
        # Con IPv6 el Host llega como [::1]:puerto; rsplit sobre ':' deja "[::1]".
        return raw in ALLOWED_HOSTS or raw.strip("[]") in ALLOWED_HOSTS

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        # Sin caché: el índice puede reconstruirse con la pestaña abierta.
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:
        if not self._host_allowed():
            self._send_json(403, {"error": "Host no permitido: solo acceso local."})
            return

        parsed = urlparse(self.path)
        route = parsed.path.rstrip("/") or "/"
        params = parse_qs(parsed.query)

        if route == "/":
            if not INDEX_HTML.exists():
                self._send_json(500, {"error": f"Falta {R.rel_to_repo(INDEX_HTML)}"})
                return
            self._send(200, INDEX_HTML.read_bytes(), "text/html; charset=utf-8")
            return

        if route == "/healthz":
            self._send_json(200, {"ok": STATE["collection"] is not None})
            return

        if STATE["collection"] is None:
            self._send_json(503, {"error": STATE["error"] or "Índice no disponible."})
            return

        try:
            routes = {"/api/search": lambda: api_search(params),
                      "/api/prompt": lambda: api_prompt(params),
                      "/api/marco": lambda: api_marco(params),
                      "/api/verify": lambda: api_verify(params),
                      "/api/facets": api_facets,
                      "/api/stats": api_stats}
            handler = routes.get(route)
            if handler is None:
                self._send_json(404, {"error": f"Ruta desconocida: {route}"})
            else:
                self._send_json(200, handler())
        except Exception as exc:  # noqa: BLE001
            self._send_json(500, {"error": f"{type(exc).__name__}: {exc}"})

    def do_HEAD(self) -> None:
        self.do_GET()


# ── Arranque ─────────────────────────────────────────────────────────────────
def load_collection() -> None:
    """Abre el índice una sola vez: el modelo ONNX queda cargado en memoria."""
    try:
        client = R.get_client()
        STATE["collection"] = R.get_collection(client, create=False)
        STATE["error"] = ""
    except Exception as exc:  # noqa: BLE001
        STATE["collection"] = None
        STATE["error"] = (
            f"La colección '{R.COLLECTION_NAME}' no está disponible: {exc}. "
            "Constrúyela con: rag\\.venv\\Scripts\\python.exe rag\\build_index.py"
        )


def main(argv: list[str] | None = None) -> int:
    R.force_utf8_stdout()
    # Con la salida redirigida a un fichero Python usa búfer de bloque: sin esto
    # el banner no aparecería hasta cerrar el proceso (p.ej. al lanzarlo en segundo
    # plano con Start-Process -RedirectStandardOutput).
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):  # pragma: no cover
        pass
    parser = argparse.ArgumentParser(description="Interfaz web local del RAG")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"puerto en 127.0.0.1 (default {DEFAULT_PORT})")
    parser.add_argument("--no-browser", action="store_true",
                        help="no abre el navegador automáticamente")
    args = parser.parse_args(argv)

    load_collection()
    if STATE["collection"] is None:
        print(f"[error] {STATE['error']}")
        return 2

    server = ThreadingHTTPServer((HOST, args.port), Handler)
    url = f"http://{HOST}:{args.port}/"
    print("=" * 72)
    print("  RAG local — interfaz web (solo lectura)")
    print(f"  URL        : {url}")
    print(f"  Colección  : {R.COLLECTION_NAME}  ({STATE['collection'].count()} chunks)")
    print(f"  Índice     : {R.rel_to_repo(R.DB_DIR)}")
    print("  Loopback únicamente: no hay acceso desde la LAN ni credenciales.")
    print("  Ctrl+C para parar.")
    print("=" * 72)

    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[stop] cerrando el servidor...")
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
