#!/usr/bin/env python
"""
query — consulta el índice RAG de awesome-embodied-ai.

Recuperación semántica 100% local (ChromaDB + all-MiniLM-L6-v2 ONNX). No hay
llaves de API en esta carpeta: el script devuelve la evidencia con su cita y,
con --prompt, el bloque de contexto listo para pegar en el LLM que prefieras.

Ejemplos:
    rag\\.venv\\Scripts\\python.exe rag\\query.py "¿Qué VLAs corren como nodos ROS 2?"
    rag\\.venv\\Scripts\\python.exe rag\\query.py "sim2real gap locomotion" -k 8 --year-min 2024
    rag\\.venv\\Scripts\\python.exe rag\\query.py "tactile sensing dexterity" --category VLA_Models
    rag\\.venv\\Scripts\\python.exe rag\\query.py "failure detection VLA" --prompt --export ctx.md
    rag\\.venv\\Scripts\\python.exe rag\\query.py "quantization edge" --json

Modo marco teórico (evidencia por secciones + BibTeX, para redactar un paper):
    rag\\.venv\\Scripts\\python.exe rag\\query.py "VLA models for ROS 2 manipulation" --marco
    rag\\.venv\\Scripts\\python.exe rag\\query.py "sim2real safety" --marco --json --export marco.json

Modo verificación de citas (guardarrail anti-alucinación; NO carga Chroma):
    rag\\.venv\\Scripts\\python.exe rag\\query.py "OpenVLA: An Open-Source VLA Model" --verify
    rag\\.venv\\Scripts\\python.exe rag\\query.py "Kim et al. 2024" --verify
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import raglib as R  # noqa: E402


def build_where(args: argparse.Namespace) -> dict[str, Any] | None:
    clauses: list[dict[str, Any]] = []
    if args.category:
        clauses.append({"category": {"$in": list(args.category)}})
    if args.source == "pdf":
        clauses.append({"source_type": "pdf"})
    elif args.source == "markdown":
        clauses.append({"source_type": "markdown"})
    if not args.include_retired:
        clauses.append({"retired": False})
    if args.year_min:
        clauses.append({"year": {"$gte": int(args.year_min)}})
    if args.year_max:
        clauses.append({"year": {"$lte": int(args.year_max)}})
    if args.folder:
        clauses.append({"folder": {"$in": list(args.folder)}})

    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def run_query(collection, query: str, args: argparse.Namespace) -> list[dict[str, Any]]:
    where = build_where(args)
    kwargs: dict[str, Any] = {
        "query_texts": [query],
        "n_results": min(int(args.k), max(collection.count(), 1)),
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        kwargs["where"] = where
    if args.contains:
        kwargs["where_document"] = {"$contains": args.contains}

    raw = collection.query(**kwargs)
    documents = (raw.get("documents") or [[]])[0]
    metadatas = (raw.get("metadatas") or [[]])[0]
    distances = (raw.get("distances") or [[]])[0]

    hits: list[dict[str, Any]] = []
    for document, meta, distance in zip(documents, metadatas, distances):
        meta = meta or {}
        similarity = 1.0 - float(distance)
        if args.min_sim and similarity < float(args.min_sim):
            continue
        hits.append(
            {
                "document": document,
                "metadata": meta,
                "distance": float(distance),
                "similarity": similarity,
            }
        )
    return hits


def emit(output: str, export: str | None) -> None:
    """Imprime o guarda: el mismo camino de salida para todos los modos."""
    if export:
        target = Path(export)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output, encoding="utf-8")
        print(f"Escrito en {target} ({len(output)} chars)")
    else:
        print(output)


def main(argv: list[str] | None = None) -> int:
    R.force_utf8_stdout()
    parser = argparse.ArgumentParser(description="Consulta RAG sobre awesome-embodied-ai")
    parser.add_argument("query", help="pregunta en lenguaje natural")
    parser.add_argument("-k", "--k", type=int, default=6, help="nº de fragmentos (default 6)")
    parser.add_argument("--category", nargs="*", default=None,
                        help="filtra por categoría de papers.csv (VLA_Models, Sim2Real_RL, ...)")
    parser.add_argument("--folder", nargs="*", default=None,
                        help="filtra por carpeta (01_VLA_Models, 07_Recent_2025_2026, repo_docs)")
    parser.add_argument("--source", choices=["all", "pdf", "markdown"], default="all")
    parser.add_argument("--year-min", type=int, default=0)
    parser.add_argument("--year-max", type=int, default=0)
    parser.add_argument("--contains", default=None,
                        help="además exige que el fragmento contenga este texto")
    parser.add_argument("--min-sim", type=float, default=0.0,
                        help="umbral mínimo de similitud coseno (0..1)")
    parser.add_argument("--include-retired", action="store_true",
                        help="incluye papers/_retirados/ en la búsqueda")
    parser.add_argument("--json", action="store_true", help="salida JSON")
    parser.add_argument("--prompt", action="store_true",
                        help="emite el bloque de contexto listo para pegar en un LLM")
    parser.add_argument("--marco", action="store_true",
                        help="ensambla la evidencia como secciones de marco teórico "
                             "(estado del arte, limitaciones, vacíos, BibTeX)")
    parser.add_argument("--per-section", type=int, default=3,
                        help="fragmentos curados por sección con --marco (default 3)")
    parser.add_argument("--verify", action="store_true",
                        help="trata el argumento como referencia bibliográfica y "
                             "comprueba si existe en el corpus (anti-alucinación)")
    parser.add_argument("--export", default=None, help="guarda la salida en un archivo")
    args = parser.parse_args(argv)

    # La verificación solo necesita papers.csv: se resuelve SIN cargar Chroma,
    # así que responde en milisegundos en vez de los 15-25 s del arranque.
    if args.verify:
        import marco as M  # import tardío: marco importa query en cabeza de módulo

        result = M.verify_citation(args.query, limit=max(3, int(args.k)))
        output = (json.dumps(result, ensure_ascii=False, indent=2) if args.json
                  else M.render_verify(result))
        emit(output, args.export)
        return 0 if result["in_corpus"] else 1

    client = R.get_client()
    try:
        collection = R.get_collection(client, create=False)
    except Exception as exc:  # noqa: BLE001
        print(f"[error] La colección '{R.COLLECTION_NAME}' no existe todavía: {exc}")
        print("Constrúyela con: rag\\.venv\\Scripts\\python.exe rag\\build_index.py")
        return 2

    # --marco va antes que la búsqueda simple: organiza la evidencia por
    # secciones y hace su propia recuperación (PDFs + docs curados).
    if args.marco:
        import marco as M  # import tardío: marco importa query en cabeza de módulo

        data = M.build_marco(
            collection, args.query, k=args.k, min_sim=args.min_sim,
            per_section=args.per_section, include_retired=args.include_retired,
            category=args.category, folder=args.folder,
        )
        output = (json.dumps(data, ensure_ascii=False, indent=2) if args.json
                  else M.render_marco(data))
        emit(output, args.export)
        return 0

    hits = run_query(collection, args.query, args)
    if not hits:
        print("Sin resultados con esos filtros.")
        return 1

    if args.json:
        payload = {"query": args.query, "k": args.k, "hits": hits}
        output = json.dumps(payload, ensure_ascii=False, indent=2)
    elif args.prompt:
        output = R.build_prompt(args.query, hits)
    else:
        header = (f"Consulta: {args.query}\n"
                  f"{len(hits)} fragmentos de {len({h['metadata'].get('doc_id') for h in hits})} "
                  f"documentos distintos\n" + "=" * 78)
        body = "\n\n".join(
            R.format_hit(i, h["metadata"], h["document"], h["distance"])
            for i, h in enumerate(hits, start=1)
        )
        output = f"{header}\n\n{body}\n"

    emit(output, args.export)
    return 0


if __name__ == "__main__":
    sys.exit(main())
