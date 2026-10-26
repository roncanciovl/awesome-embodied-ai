#!/usr/bin/env python
"""
build_index — construye/actualiza el índice vectorial de awesome-embodied-ai.

Indexa:
  * Los 62 PDFs de papers/ (con metadatos enriquecidos desde papers.csv).
  * Los documentos Markdown curados del repo (README, GLOSSARY, research-*, PAPERS.md).

Los IDs de chunk son deterministas (sha1(ruta) + índice), así que re-ejecutar el
script hace upsert idempotente: actualiza lo que cambió y no duplica nada.

Uso (desde la raíz del repo o desde rag/):
    rag\\.venv\\Scripts\\python.exe rag\\build_index.py
    rag\\.venv\\Scripts\\python.exe rag\\build_index.py --rebuild
    rag\\.venv\\Scripts\\python.exe rag\\build_index.py --stats
    rag\\.venv\\Scripts\\python.exe rag\\build_index.py --include-retired
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import raglib as R  # noqa: E402

# Lotes de lectura de metadatos ya indexados (para detectar chunks sin cambios).
GET_BATCH = 500


def build_pdf_records(path: Path, csv_meta: dict[str, dict[str, Any]],
                      use_cache: bool) -> list[dict[str, Any]]:
    rel = R.rel_to_repo(path)                       # papers/01_.../X.pdf
    key = rel.removeprefix("papers/")               # 01_.../X.pdf
    meta_row = csv_meta.get(key, {})

    pages = R.extract_pdf_pages(path, use_cache=use_cache)
    if not pages:
        print(f"  [WARN] sin texto extraíble: {rel}")
        return []

    chunks = R.chunk_pdf(pages)
    doc_id = R.doc_id_for(rel)
    category = key.split("/")[0] if "/" in key else ""

    records: list[dict[str, Any]] = []
    for index, chunk in enumerate(chunks):
        base = {
            "doc_id": doc_id,
            "doc_path": rel,
            "source_type": "pdf",
            "title": meta_row.get("title") or R.title_from_filename(path),
            "category": meta_row.get("category") or category,
            "folder": category,
            "year": int(meta_row.get("year") or 0),
            "arxiv_id": str(meta_row.get("arxiv_id") or ""),
            "authors_first": str(meta_row.get("authors_first") or ""),
            "model_type": str(meta_row.get("model_type") or ""),
            "task": str(meta_row.get("task") or ""),
            "robot_type": str(meta_row.get("robot_type") or ""),
            "ros_integration": str(meta_row.get("ros_integration") or ""),
            "simulator": str(meta_row.get("simulator") or ""),
            "hardware": str(meta_row.get("hardware") or ""),
            "sim2real": str(meta_row.get("sim2real") or ""),
            "code_available": str(meta_row.get("code_available") or ""),
            "gap_category": str(meta_row.get("gap_category") or ""),
            "retired": False,
            "page_start": int(chunk["page_start"] or 0),
            "page_end": int(chunk["page_end"] or 0),
            "chunk_index": index,
            "heading_path": "",
        }
        records.append(
            {"id": f"{doc_id}::{index:05d}", "document": chunk["text"], "metadata": base}
        )
    return records


def build_markdown_records(path: Path) -> list[dict[str, Any]]:
    rel = R.rel_to_repo(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    chunks = R.chunk_markdown(text)
    doc_id = R.doc_id_for(rel)

    records: list[dict[str, Any]] = []
    for index, chunk in enumerate(chunks):
        base = {
            "doc_id": doc_id,
            "doc_path": rel,
            "source_type": "markdown",
            "title": path.stem,
            "category": "repo_docs",
            "folder": "repo_docs",
            "year": 0,
            "arxiv_id": "",
            "authors_first": "",
            "model_type": "",
            "task": "",
            "robot_type": "",
            "ros_integration": "",
            "simulator": "",
            "hardware": "",
            "sim2real": "",
            "code_available": "",
            "gap_category": "",
            "retired": False,
            "page_start": 0,
            "page_end": 0,
            "chunk_index": index,
            "heading_path": str(chunk.get("heading_path", "")),
        }
        records.append(
            {"id": f"{doc_id}::{index:05d}", "document": chunk["text"], "metadata": base}
        )
    return records


def matches_only(rel: str, patterns: list[str] | None) -> bool:
    if not patterns:
        return True
    name = rel.rsplit("/", 1)[-1]
    return any(
        fnmatch.fnmatch(name.lower(), p.lower()) or fnmatch.fnmatch(rel.lower(), p.lower())
        for p in patterns
    )


def prune_stale(collection, valid_ids: set[str]) -> int:
    """Borra chunks obsoletos del índice.

    Cubre dos casos:
      * documentos que ya no existen en disco;
      * **colas de documentos que se encogieron**. Los IDs son
        ``doc_id::índice``, así que si un PDF pasa de 60 a 52 chunks (por
        ejemplo al filtrar sus páginas de bibliografía), los chunks 52..59
        quedan huérfanos aunque el doc_id siga siendo válido. Podar por
        doc_id dejaría viva justo la bibliografía que se quería eliminar.
    """
    existing = collection.get(include=["metadatas"])
    ids = existing.get("ids") or []
    stale = [cid for cid in ids if cid not in valid_ids]
    for start in range(0, len(stale), 500):
        collection.delete(ids=stale[start:start + 500])
    return len(stale)


def text_hash(text: str) -> str:
    """Huella del contenido de un chunk."""
    return hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()[:20]


def upsert_all(collection, records: list[dict[str, Any]],
               force: bool = False) -> int:
    """Sube los chunks re-embedeando **solo** los que cambiaron.

    Chroma calcula el embedding dentro de ``upsert()``, así que re-subir un
    chunk idéntico cuesta exactamente lo mismo que uno nuevo (~5 min para los
    ~4.300 chunks). Comparar una huella de contenido contra lo ya indexado
    convierte una ejecución incremental en cuestión de segundos.

    Devuelve el número de chunks realmente re-embedeados.
    """
    for rec in records:
        rec["metadata"]["text_hash"] = text_hash(rec["document"])

    ids = [r["id"] for r in records]
    pending = list(range(len(records)))

    if not force:
        stored: dict[str, str | None] = {}
        for start in range(0, len(ids), GET_BATCH):
            got = collection.get(ids=ids[start:start + GET_BATCH],
                                 include=["metadatas"])
            for cid, meta in zip(got.get("ids") or [], got.get("metadatas") or []):
                stored[cid] = (meta or {}).get("text_hash")
        pending = [
            i for i in range(len(records))
            if stored.get(ids[i]) != records[i]["metadata"]["text_hash"]
        ]
        unchanged = len(records) - len(pending)
        if unchanged:
            print(f"  {unchanged} chunks sin cambios (embeddings reutilizados).")

    if not pending:
        print("  Nada que re-embedear: el índice ya está al día.")
        return 0

    print(f"  {len(pending)} chunks por embedear y subir.")
    for start in range(0, len(pending), R.EMBED_BATCH):
        batch = [records[i] for i in pending[start:start + R.EMBED_BATCH]]
        collection.upsert(
            ids=[r["id"] for r in batch],
            documents=[r["document"] for r in batch],
            metadatas=[r["metadata"] for r in batch],
        )
        done = min(start + R.EMBED_BATCH, len(pending))
        print(f"    upsert {done}/{len(pending)}", end="\r", flush=True)
    print(" " * 40, end="\r")
    return len(pending)


def print_stats(client) -> None:
    import chromadb

    print(f"chromadb {chromadb.__version__}")
    print(f"DB dir   : {R.rel_to_repo(R.DB_DIR)}")
    try:
        collection = R.get_collection(client, create=False)
    except Exception as exc:  # noqa: BLE001
        print(f"Coleccion '{R.COLLECTION_NAME}' aun no existe: {exc}")
        return
    print(f"Coleccion: {R.COLLECTION_NAME}  ({collection.count()} chunks)")

    metas = (collection.get(include=["metadatas"]).get("metadatas")) or []
    docs: dict[str, dict[str, Any]] = {}
    for meta in metas:
        meta = meta or {}
        entry = docs.setdefault(
            str(meta.get("doc_id", "")),
            {"path": meta.get("doc_path", ""), "type": meta.get("source_type", ""), "n": 0},
        )
        entry["n"] += 1
    pdfs = [d for d in docs.values() if d["type"] == "pdf"]
    mds = [d for d in docs.values() if d["type"] == "markdown"]
    print(f"Documentos: {len(docs)}  ({len(pdfs)} PDF, {len(mds)} Markdown)")

    by_folder: dict[str, int] = {}
    for meta in metas:
        folder = str((meta or {}).get("folder", "?"))
        by_folder[folder] = by_folder.get(folder, 0) + 1
    for folder in sorted(by_folder):
        print(f"  {folder:<32} {by_folder[folder]:>6} chunks")


def main(argv: list[str] | None = None) -> int:
    R.force_utf8_stdout()
    parser = argparse.ArgumentParser(description="Indice RAG de awesome-embodied-ai")
    parser.add_argument("--rebuild", action="store_true",
                        help="borra la coleccion y reindexa desde cero")
    parser.add_argument("--force", action="store_true",
                        help="re-embedea todos los chunks aunque no hayan cambiado")
    parser.add_argument("--stats", action="store_true", help="solo muestra estadisticas")
    parser.add_argument("--include-retired", action="store_true",
                        help="indexa tambien papers/_retirados/")
    parser.add_argument("--no-markdown", action="store_true", help="indexa solo PDFs")
    parser.add_argument("--no-cache", action="store_true",
                        help="re-extrae el texto de los PDFs (ignora rag/cache/)")
    parser.add_argument("--only", nargs="*", default=None,
                        help="filtra por nombre/ruta (glob), ej: --only *VLA*")
    parser.add_argument("--limit", type=int, default=0,
                        help="procesa solo N documentos (smoke test)")
    args = parser.parse_args(argv)

    client = R.get_client()

    if args.stats:
        print_stats(client)
        return 0

    if args.rebuild:
        print(f"[rebuild] eliminando coleccion '{R.COLLECTION_NAME}'...")
        try:
            client.delete_collection(R.COLLECTION_NAME)
        except Exception:  # noqa: BLE001
            pass

    started = time.time()
    embedding_function = R.build_embedding_function()
    collection = R.get_collection(client, embedding_function)

    csv_meta = R.load_papers_metadata()
    print(f"papers.csv: {len(csv_meta)} filas de metadatos")

    pdf_paths = [p for p in R.iter_pdf_paths(args.include_retired)
                 if matches_only(R.rel_to_repo(p), args.only)]
    md_paths = [] if args.no_markdown else [
        p for p in R.iter_markdown_paths() if matches_only(R.rel_to_repo(p), args.only)
    ]
    if args.limit:
        pdf_paths = pdf_paths[:args.limit]

    print(f"PDFs a indexar: {len(pdf_paths)}   Markdown: {len(md_paths)}")

    records: list[dict[str, Any]] = []
    valid_doc_ids: set[str] = set()
    failures: list[str] = []

    for number, path in enumerate(pdf_paths, start=1):
        rel = R.rel_to_repo(path)
        print(f"[{number}/{len(pdf_paths)}] {rel}")
        try:
            batch = build_pdf_records(path, csv_meta, use_cache=not args.no_cache)
        except Exception as exc:  # noqa: BLE001
            print(f"  [FAIL] {exc}")
            failures.append(rel)
            continue
        if not batch:
            continue
        if R.RETIRED_DIRNAME in path.parts:
            for record in batch:
                record["metadata"]["retired"] = True
        records.extend(batch)
        valid_doc_ids.add(batch[0]["metadata"]["doc_id"])
        print(f"  -> {len(batch)} chunks")

    for path in md_paths:
        rel = R.rel_to_repo(path)
        print(f"[md] {rel}")
        try:
            batch = build_markdown_records(path)
        except Exception as exc:  # noqa: BLE001
            print(f"  [FAIL] {exc}")
            failures.append(rel)
            continue
        records.extend(batch)
        if batch:
            valid_doc_ids.add(batch[0]["metadata"]["doc_id"])
            print(f"  -> {len(batch)} chunks")

    if not records:
        print("No hay nada que indexar.")
        return 1

    print(f"\nTotal: {len(records)} chunks en {len(valid_doc_ids)} documentos.")
    print("Embedding + upsert en Chroma...")
    upsert_all(collection, records, force=args.force or args.rebuild)

    if not args.only and not args.limit:
        removed = prune_stale(collection, {r["id"] for r in records})
        if removed:
            print(f"Poda: {removed} chunks obsoletos eliminados.")

    elapsed = time.time() - started
    print(f"\nListo en {elapsed:.1f}s - coleccion '{R.COLLECTION_NAME}' "
          f"con {collection.count()} chunks.")
    if failures:
        print(f"\nFallos ({len(failures)}):")
        for rel in failures:
            print(f"  - {rel}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

