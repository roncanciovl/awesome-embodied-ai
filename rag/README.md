# RAG local — awesome-embodied-ai

Recuperación aumentada (**RAG**) sobre la colección de papers del repo, 100 % local
y **sin credenciales**: ChromaDB persistido en disco + embeddings ONNX
`all-MiniLM-L6-v2` (384 dims) ejecutados con `onnxruntime` en CPU.

> Esta carpeta vive dentro de un repositorio sincronizado con OneDrive, así que
> por diseño **no hay llaves de API, tokens ni archivos `.env` aquí**. El script
> devuelve la evidencia citada y, con `--prompt`, el bloque de contexto listo
> para pegar en el LLM que tú elijas.

---

## Contenido

| Archivo | Función |
|---------|---------|
| `raglib.py` | Rutas, limpieza de texto, extracción de PDF, chunking, metadatos, cliente Chroma |
| `build_index.py` | Construye / actualiza el índice vectorial |
| `query.py` | Consulta el índice (CLI) |
| `marco.py` | Evidencia con forma de marco teórico + verificación de citas |
| `serve.py` | Interfaz web local (servidor `http.server`, solo lectura) |
| `web/index.html` | Front de esa interfaz (autocontenido, sin CDN) |
| `web/README.md` | Guía de uso de la interfaz web (controles, filtros, recetas, fallos) |
| `requirements.txt` | Dependencias (`chromadb`, `PyMuPDF`) |
| `ask.ps1` | Atajo de PowerShell con la consola en UTF‑8 |

Artefactos generados (**ignorados por git**, regenerables):

| Carpeta | Contenido |
|---------|-----------|
| `.venv/` | Entorno virtual de Python |
| `chroma_db/` | Índice vectorial persistido (colección `embodied_ai`) |
| `cache/` | Texto extraído de cada PDF (acelera re-indexados) |
| `models/` | Modelo ONNX `all-MiniLM-L6-v2` (se baja una sola vez, ~80 MB) |

---

## Instalación (una sola vez)

Desde la raíz del repo:

```powershell
py -3.14 -m venv awesome-embodied-ai\rag\.venv
awesome-embodied-ai\rag\.venv\Scripts\python.exe -m pip install -r awesome-embodied-ai\rag\requirements.txt
```

La primera ejecución de `build_index.py` descarga el modelo de embeddings a
`rag/models/` (nunca fuera del workspace).

---

## Construir / actualizar el índice

```powershell
# Desde la raíz del repo
rag\.venv\Scripts\python.exe rag\build_index.py              # upsert incremental
rag\.venv\Scripts\python.exe rag\build_index.py --rebuild    # desde cero
rag\.venv\Scripts\python.exe rag\build_index.py --stats      # estadísticas
rag\.venv\Scripts\python.exe rag\build_index.py --include-retired
rag\.venv\Scripts\python.exe rag\build_index.py --only *VLA* --limit 3
```

Los IDs de chunk son deterministas (`sha1(ruta)::índice`), por lo que
re-ejecutar el script **actualiza sin duplicar** y poda los chunks de documentos
que desaparecieron del disco.

### Qué se indexa

1. **Los 62 PDFs de `papers/`** (excluye `papers/_retirados/` salvo `--include-retired`),
   enriquecidos con las 20 columnas de [`papers.csv`](../papers.csv).
2. **Los Markdown curados del repo**: `README.md`, `GLOSSARY.md`, `CONTRIBUTING.md`,
   `research-protocol.md`, `research-gaps.md`, `tactile-sota.md`, `papers/PAPERS.md`.
   (`PLAN_PUBLICACIONES_HENRY.md` queda excluido a propósito.)

### Chunking

* Bloques de ~1400 caracteres con ~220 de solape, cortados en fronteras de párrafo.
* Se conserva el rango de páginas (`page_start` / `page_end`) para poder citar.
* En Markdown se conserva la ruta de encabezados (`heading_path`).
* Se descartan páginas sin prosa útil (portadas, páginas de solo números).

---

## Interfaz web local (la forma más cómoda)

```powershell
# Desde la raíz del repo
rag\.venv\Scripts\python.exe rag\serve.py
```

Arranca un servidor en <http://127.0.0.1:8757/> y abre el navegador. Parar con
`Ctrl+C`. Opciones: `--port 9000` (otro puerto) y `--no-browser` (no abrir el
navegador).

Qué permite:

* Buscar en lenguaje natural y ver los fragmentos con su **similitud**, página,
  categoría, carpeta, robot, simulador e integración con ROS 2.
* Filtrar por categoría, carpeta, origen (PDF/Markdown), rango de años,
  similitud mínima y texto obligatorio — los mismos filtros que el CLI.
* Enlace directo a arXiv en cada resultado.
* Botón **«Contexto LLM»**: genera el bloque con las citas numeradas y un botón
  para copiarlo (equivalente a `query.py --prompt`).

> Guía paso a paso de la interfaz —qué hace cada control, recetas, seguridad y
> solución de problemas— en [`web/README.md`](web/README.md).

Es **solo lectura** y **solo loopback**: no escribe en disco, no hace peticiones
salientes y no usa credenciales. Está construido únicamente con la stdlib
(`http.server`), así que no añade ninguna dependencia al venv. Además valida el
header `Host`, de modo que una página web maliciosa no pueda consultar tu índice
desde el navegador (DNS rebinding).

Los seis endpoints, por si quieres integrarlos con otro código:

| Endpoint | Devuelve |
|----------|----------|
| `GET /api/search?q=...` | JSON con los fragmentos, metadatos y similitud |
| `GET /api/prompt?q=...` | El bloque de contexto listo para un LLM |
| `GET /api/marco?q=...` | Evidencia por secciones de marco teórico + BibTeX |
| `GET /api/verify?ref=...` | Si una referencia existe en el corpus (anti-alucinación) |
| `GET /api/facets` | Categorías, carpetas y rango de años presentes |
| `GET /api/stats` | Chunks, documentos y reparto por carpeta |

Ejemplo con los mismos parámetros del CLI:

```powershell
Invoke-RestMethod "http://127.0.0.1:8757/api/search?q=sim2real&k=5&year_min=2024"
```

> La web y el CLI comparten `build_where()` y `run_query()` de `query.py`, así
> que una misma consulta devuelve exactamente lo mismo en ambos.

---

## Consultar

```powershell
rag\.venv\Scripts\python.exe rag\query.py "¿Qué VLAs corren como nodos nativos de ROS 2?"
```

```powershell
# Más fragmentos y filtro temporal
rag\.venv\Scripts\python.exe rag\query.py "sim2real gap in legged locomotion" -k 8 --year-min 2023

# Restringir a una categoría de papers.csv
rag\.venv\Scripts\python.exe rag\query.py "tactile sensing dexterity" --category VLA_Models

# Restringir a una carpeta (o a los docs del repo)
rag\.venv\Scripts\python.exe rag\query.py "harness assembly" --folder 07_Recent_2025_2026

# Solo PDFs / solo Markdown
rag\.venv\Scripts\python.exe rag\query.py "domain randomization" --source pdf

# Umbral de similitud + texto obligatorio
rag\.venv\Scripts\python.exe rag\query.py "failure detection" --min-sim 0.45 --contains VLA

# Salida JSON (para integrar con otro código)
rag\.venv\Scripts\python.exe rag\query.py "quantization edge deployment" --json

# Bloque de contexto listo para pegar en un LLM
rag\.venv\Scripts\python.exe rag\query.py "wire harness assembly automation" --prompt
rag\.venv\Scripts\python.exe rag\query.py "..." --prompt --export rag\out\contexto.md
```

Atajo con la consola en UTF‑8 (evita tildes rotas en PowerShell):

```powershell
.\rag\ask.ps1 "¿Qué dice la colección sobre detección de fallos silenciosos?" -k 5
```

### Metadatos disponibles para filtrar

`doc_id`, `doc_path`, `source_type` (`pdf`|`markdown`), `title`, `category`,
`folder`, `year`, `arxiv_id`, `authors_first`, `model_type`, `task`, `robot_type`,
`ros_integration`, `simulator`, `hardware`, `sim2real`, `code_available`,
`gap_category`, `retired`, `page_start`, `page_end`, `chunk_index`, `heading_path`.

---

## Marco teórico y verificación de citas

Pensado para quien redacta un paper —o para un **agente de IA** que lo redacta.
El contrato completo para agentes vive en [`../AGENTS.md`](../AGENTS.md).

### `--marco`: evidencia por secciones

Un marco teórico no necesita "los k fragmentos más parecidos": necesita fuentes
citables con localización exacta, las limitaciones de cada trabajo y los vacíos
que el propio corpus reconoce. `--marco` ensambla eso:

```powershell
rag\.venv\Scripts\python.exe rag\query.py "VLA models for manipulation with ROS 2" --marco
rag\.venv\Scripts\python.exe rag\query.py "sim2real safety" --marco --json --export marco.json
rag\.venv\Scripts\python.exe rag\query.py "..." --marco --per-section 5 --category VLA_Models
```

| Sección | Origen |
|---------|--------|
| Estado del arte | búsqueda semántica sobre `papers/` (solo PDF, un paper = una entrada) |
| Limitaciones documentadas | columna `limitations` de `papers.csv` |
| Vacíos de investigación | columna `gap_category` + `research-gaps.md` |
| Bases teóricas | `GLOSSARY.md` |
| Protocolo metodológico | `research-protocol.md` |
| Comparativa cuantitativa | `latency_ms`, `compute_resources`, `sim2real`, `ros_integration` |
| BibTeX | una entrada por paper recuperado + la cita de la colección |

La clave del diseño: la búsqueda semántica decide **qué** papers importan y
`papers.csv` aporta el análisis de esos papers. Lo primero es aproximado, lo
segundo es exacto; mezclarlo al revés es como se acaba citando de oídas.

`--marco` también emite **avisos** para quien redacta: cobertura baja (<3
papers), sesgo hacia 2025-2026 y el recordatorio de que `authors_first` solo
trae "Apellido et al." (el BibTeX sale como `Apellido and others`).

### `--verify`: guardarrail anti-alucinación

El corpus es cerrado (62 papers), así que "¿existe esta referencia?" tiene
respuesta determinista. Es el riesgo nº1 de un marco teórico escrito por IA:

```powershell
rag\.venv\Scripts\python.exe rag\query.py "OpenVLA: An Open-Source Vision-Language-Action Model" --verify
rag\.venv\Scripts\python.exe rag\query.py "arXiv:2212.06817" --verify
rag\.venv\Scripts\python.exe rag\query.py "Kim et al. 2024" --verify
```

| Veredicto | Qué significa |
|-----------|---------------|
| `confirmed` | Está en el corpus. Citable; el BibTeX adjunto es la entrada correcta. |
| `probable` | Ambigua: varios papers encajan casi igual. Añade año o `arxiv_id` y repite. |
| `not_found` | **No está en el corpus.** Márcala como fuente externa y verifícala tú. |

Devuelve siempre candidatos cercanos, también al fallar: es lo que permite
autocorregir una cita mal escrita en vez de insistir en una referencia inventada.
Código de salida `0` si `confirmed` y `1` en cualquier otro caso (útil en
scripts).

> `--verify` **no carga Chroma**: solo lee `papers.csv`, así que responde en
> milisegundos en lugar de los 15-25 s que cuesta arrancar el índice.

Desde HTTP, `/api/verify` acepta `ref` repetido o `refs=a|b|c` para verificar una
bibliografía entera de una vez. Las comas **no** se usan como separador, porque
una referencia legítima las lleva ("Kim et al., 2024").

---

## Uso desde Python

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

## Notas y limitaciones

* **Solo recuperación.** No hay generación automática: `--prompt` entrega el
  contexto con sus citas para que lo pegues en tu LLM. Es una decisión deliberada
  (regla de no guardar secretos en una carpeta sincronizada con OneDrive).
* `all-MiniLM-L6-v2` es un modelo general en inglés de 384 dims y 256 tokens de
  ventana: los chunks se recortan a ~1400 caracteres para no perder la cola.
  Para consultas en español funciona, pero el corpus está en inglés.
* La extracción es de **texto**, no de figuras ni tablas: las tablas de resultados
  se recuperan como texto plano y pueden llegar desordenadas.
* `papers/_retirados/` queda fuera por defecto; esos 7 PDFs no están en `PAPERS.md`
  ni en `papers.csv`, así que se indexan sin metadatos enriquecidos.
* `rag/chroma_db/`, `rag/cache/`, `rag/models/` y `rag/.venv/` están en
  `.gitignore`. Aun así OneDrive los sincroniza: si no quieres subirlos, marca la
  carpeta `rag/` como excluida en OneDrive o muévela fuera y ajusta `raglib.py`.

