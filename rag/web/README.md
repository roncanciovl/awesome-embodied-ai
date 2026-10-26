# Interfaz web del RAG local — guía de uso

La UI es **una sola página autocontenida** (`web/index.html`: HTML + CSS + JS en
un fichero, sin CDN, sin `npm`, sin build) que sirve `rag/serve.py` en
<http://127.0.0.1:8757/>. Sirve para buscar evidencia en la colección de papers
del repo y para llevarte un bloque de contexto listo para pegar en tu LLM.

> Contexto general del RAG (instalación, indexado, CLI): [`../README.md`](../README.md).
> Uso programático por agentes de IA: [`../../AGENTS.md`](../../AGENTS.md).

---

## 1. Arrancar y parar

```powershell
# Desde la raíz del repo
rag\.venv\Scripts\python.exe rag\serve.py
```

Carga el índice, imprime un banner y **abre el navegador por defecto**. Para
pararlo, `Ctrl+C` en esa consola.

| Opción | Efecto |
|--------|--------|
| `--port 9000` | Escucha en otro puerto (el 8757 está ocupado si ya hay otra instancia) |
| `--no-browser` | No abre el navegador; tú vas a la URL a mano |

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

**Requisito previo:** el índice debe existir. Si la colección `embodied_ai` no
está construida, el servidor imprime `[error] ...` y termina con código 2 (no
llega a levantar la web). Se arregla con:

```powershell
rag\.venv\Scripts\python.exe rag\build_index.py
```

---

## 2. Qué ves al abrirla

```
┌───────────────────────────────────────────────────────────────────────┐
│ RAG local · awesome-embodied-ai   3595 chunks · 69 docs (62 PDF, 7 MD) │ ← cabecera
│ Recuperación semántica 100 % local · ChromaDB + all-MiniLM-L6-v2       │
├────────────────────────────────────────────────────────────────────────┤
│ [Pregunta algo: ¿qué VLAs corren como nodos nativos de ROS 2?]         │ ← barra
│ [Buscar] [Contexto LLM]                                                │
│ ▸ Filtros opcionales                                                   │ ← plegable
│                                                                        │
│ 4 fragmentos de 2 documentos distintos · 147 ms                        │ ← estado
│ ┌───┐ RT-2: Vision-Language-Action Models Transfer Web Knowledge…      │ ← tarjeta
│ │ 1 │ ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬ arXiv:2307.15818           0.686     │
│ └───┘ [año: 2023] [pág.: pp.11-12] [cat.: VLA_Models]                  │
│       [carpeta: 01_VLA_Models] [ROS 2: No] [robot: Mobile manipulator] │
│       «fragmento de texto recuperado…»                                 │
│       papers/01_VLA_Models/RT-2_Vision-Language-Action_Models….pdf     │
└────────────────────────────────────────────────────────────────────────┘
```

(Ejemplo real capturado del índice actual; tus cifras dependerán de lo que hayas
indexado.)

* **Cabecera (derecha):** recuento real del índice, obtenido de `/api/stats` al
  cargar. Si dice `índice no disponible`, falta construirlo (apartado 11).
* **Barra de búsqueda:** caja de texto + botón **Buscar** + botón
  **Contexto LLM**.
* **`▸ Filtros opcionales`:** panel plegado por defecto; se despliega al hacer
  clic en el título.
* **Línea de estado:** cuántos fragmentos y documentos distintos han salido, y
  los milisegundos que ha tardado (medidos en el navegador). En ámbar cuando es
  un aviso o un error.
* **Tarjetas:** un resultado por fila, ordenadas por similitud descendente.

---

## 3. Buscar paso a paso

1. Escribe la pregunta en la caja. **En inglés rinde más**: el corpus (PDFs y
   Markdown) está en inglés y el embedder es `all-MiniLM-L6-v2`.
2. Pulsa **Enter** o el botón **Buscar**.
3. Si sale ruido, despliega **Filtros**, recorta y vuelve a buscar: los filtros
   **no se aplican hasta que pulsas Buscar** (no hay re-búsqueda automática).
4. Con la evidencia delante, pulsa **Contexto LLM** y copia el bloque (apartado 6).

Consejos que se notan en la calidad de lo recuperado:

* Frases técnicas concretas > preguntas largas: `tactile sim-to-real gap` rinde
  mejor que `¿qué papers hablan de tactil?`.
* Lee la línea de estado: `6 fragmentos de 1 documento distinto` significa que
  toda la evidencia sale del mismo paper, así que conviene abrir filtros o subir
  `Fragmentos`.
* La **similitud es coseno de un modelo pequeño**: úsala para *ordenar*, no como
  umbral de verdad. Un 0.45 puede ser el paper correcto y un 0.65 puede ser
  ruido (mismo criterio que en `AGENTS.md`).
* Si no hay resultados, la UI lo dice y sugiere quitar filtros o reformular en
  inglés.

---

## 4. Filtros

Cada control equivale 1:1 a un flag del CLI (`query.py`) y a un parámetro HTTP,
porque la web y el CLI comparten `build_where()` de `query.py`: una misma
consulta devuelve exactamente lo mismo en ambos.

| Control en la UI | Parámetro HTTP | Flag del CLI | Qué hace | Por defecto |
|------------------|----------------|--------------|----------|-------------|
| **Fragmentos (k)** | `k` | `-k` / `--k` | Cuántos fragmentos devolver (1–50) | `6` |
| **Origen** | `source` | `--source` | `todo` / `solo PDFs` / `solo Markdown` (valores HTTP `all`/`pdf`/`markdown`) | `todo` |
| **Categoría** | `category` | `--category` | Categoría de `papers.csv` (`VLA_Models`, `Sim2Real_RL`, …) | todas |
| **Carpeta** | `folder` | `--folder` | Subcarpeta de `papers/` (`01_VLA_Models`, …) o `repo_docs` | todas |
| **Año desde** | `year_min` | `--year-min` | Año mínimo de publicación | sin límite |
| **Año hasta** | `year_max` | `--year-max` | Año máximo de publicación | sin límite |
| **Similitud mínima** | `min_sim` | `--min-sim` | Umbral coseno (0–1, pasos de 0.05) | `0` |
| **Debe contener** | `contains` | `--contains` | Texto literal obligatorio en el fragmento | vacío |
| **incluir retirados** | `include_retired=1` | `--include-retired` | Incluye papers marcados como retirados | desactivado |

Detalles de comportamiento:

* **Categoría** y **Carpeta** se rellenan solos al abrir la página con
  `/api/facets`, y cada opción lleva su recuento entre paréntesis, así que sabes
  de antemano cuántos chunks hay ahí. Valores reales del corpus actual:
  categorías `VLA_Models (387)`, `Recent_2025_2026 (1390)`, `Sim2Real_RL (376)`,
  `ROS2_AI_LLMs (404)`, `Simulation_Environments (212)`,
  `Surveys_Case_Studies (455)`, `Robotics_Frameworks (49)` y `repo_docs (322)`;
  carpetas `01_VLA_Models (387)` … `07_Recent_2025_2026 (1390)`, más
  `repo_docs` para los Markdown del propio repositorio.
* Los campos **Año desde / Año hasta** muestran como *placeholder* el año mínimo
  y máximo reales del corpus (también de `/api/facets`; ahora mismo `2017` y
  `2026`): es una pista, no un valor activo. Si los dejas vacíos no filtran.
* **Similitud mínima** y **Debe contener** solo se envían si los rellenas.
* Si `/api/facets` falla, los desplegables se quedan en `todas` pero la búsqueda
  sigue funcionando.
* `Fragmentos` se recorta además en el servidor al rango 1–50, así que no puedes
  pedir 500 por URL.

---

## 5. Anatomía de una tarjeta de resultado

```
┌───┐ RT-2: Vision-Language-Action Models Transfer Web Knowledge to
│ 1 │ Robotic Control   arXiv:2307.15818                          0.686
└───┘ ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
      [año: 2023] [pág.: pp.11-12] [cat.: VLA_Models] [carpeta: 01_VLA_Models]
      [ROS 2: No] [robot: Mobile manipulator] [hardware: Everyday Robots]
      «texto completo del fragmento recuperado, con los saltos colapsados…»
      papers/01_VLA_Models/RT-2_Vision-Language-Action_Models_Transfer_Web_Knowledge.pdf
```

(Captura real con la consulta `vision-language-action model generalization` y
`Origen = solo PDFs`.)

| Parte | Qué es |
|-------|--------|
| `1` | Puesto en el ranking: el 1 es el más similar |
| Título | `metadata.title` del paper. En los Markdown del repo se muestra su ruta |
| `arXiv:2307.15818` | Enlace a `arxiv.org/abs/…` en pestaña nueva. Solo sale si el paper tiene `arxiv_id` en `papers.csv` |
| `0.686` | Similitud coseno con 3 decimales |
| Barra | La misma similitud en porcentaje (ancho = `sim × 100 %`) |
| Chips | Metadatos del paper; se ocultan solo si el campo está vacío o vale `-` (regla exacta más abajo) |
| Texto | El fragmento (`chunk`) completo, con los saltos de línea colapsados a espacios |
| Ruta final | `doc_path`, relativo a la raíz del repo |

Chips posibles y su campo de origen:

| Chip | Campo de `papers.csv` / índice | Ejemplo real |
|------|-------------------------------|--------------|
| `año` | `year` | `año: 2023` |
| `pág.` | `page_start` / `page_end` | `pág.: p.3` o `pág.: pp.11-12` |
| `cat.` | `category` | `cat.: VLA_Models` |
| `carpeta` | `folder` | `carpeta: 01_VLA_Models` |
| `ROS 2` | `ros_integration` | `ROS 2: No`, `ROS 2: Partial` |
| `robot` | `robot_type` | `robot: Mobile manipulator` |
| `sim.` | `simulator` | `sim.: Habitat`, `sim.: Custom`, `sim.: N/A` |
| `hardware` | `hardware` | `hardware: Everyday Robots` |
| `sección` | `heading_path` | `sección: 📄 Paper Library … > 🤖 01 — Vision-Language-Action (VLA) Models` |

Regla exacta de qué se pinta: un chip se oculta **solo** si su campo está vacío o
vale `-`. Todo lo demás aparece tal cual, incluidos los valores poco útiles:

* `sim.: N/A` o `hardware: N/A` → el campo está rellenado en `papers.csv` con
  `N/A`: el dato falta y conviene completarlo.
* `año: 0` → es un Markdown del propio repo (`cat.: repo_docs`), que no tiene año
  de publicación.
* Que un chip **no** aparezca (`sim.`, `robot`, …) → ese campo vale `-` o está
  vacío en el CSV. Es la señal más rápida de que `papers.csv` está incompleto.
* `sección` solo tiene sentido en los Markdown; en los PDFs la procedencia la da
  `pág.`.

---

## 6. Botón «Contexto LLM»

Genera el **bloque de contexto** con los fragmentos numerados y sus citas, listo
para pegar en el LLM que prefieras. Es el equivalente exacto de
`query.py --prompt` (misma función `raglib.build_prompt`).

1. Escribe la pregunta y ajusta filtros.
2. Pulsa **Contexto LLM** (no hace falta haber pulsado Buscar antes: usa la misma
   *query string* que usaría la búsqueda).
3. Se abre el modal **«Contexto para pegar en tu LLM»** con:
   * una línea informativa: `N fragmentos · X caracteres · pégalo en el LLM que prefieras`;
   * un área de texto de **solo lectura** con el bloque completo;
   * los botones **Copiar** y **Cerrar**.
4. **Copiar** lo manda al portapapeles y el botón cambia a `Copiado ✓` durante
   1,6 s.

El bloque **ya lleva sus instrucciones dentro**: empieza pidiendo al modelo que
responda *únicamente* con ese contexto, que cite las fuentes con su número `[n]`
y que diga de forma explícita si el contexto no alcanza para responder. Después
va la pregunta y los fragmentos numerados. Ejemplo real de la línea informativa:
`4 fragmentos · 4736 caracteres · pégalo en el LLM que prefieras`.

Avisos posibles: `Escribe una pregunta antes de generar el contexto.` si la caja
está vacía, y `Sin resultados con esos filtros.` si los filtros no dejan nada.

Flujo recomendado para un marco teórico:

1. Busca y genera el contexto de cada subtema.
2. Pégalo en tu LLM pidiéndole que cite **solo los números del bloque**.
3. Verifica cada cita resultante con `/api/verify` antes de dárla por buena
   (apartado 9): es el guardarrail anti-alucinación.

---

## 7. Atajos y gestos

| Acción | Cómo |
|--------|------|
| Buscar | `Enter` en la caja de búsqueda (tiene el foco al abrir la página) |
| Ver / ocultar filtros | Clic en `▸ Filtros opcionales` |
| Generar el contexto | Botón **Contexto LLM** |
| Copiar el contexto | Botón **Copiar** dentro del modal |
| Cerrar el modal | `Esc`, botón **Cerrar**, o clic en el fondo oscuro |
| Abrir el paper en arXiv | Clic en `arXiv:…` (pestaña nueva, `rel="noreferrer"`) |
| Refrescar los datos | `F5`: el servidor responde `Cache-Control: no-store`, así que siempre ves el índice actual |

---

## 8. Recetas

| Objetivo | Qué escribes | Qué tocas en Filtros |
|----------|--------------|----------------------|
| Estado del arte de un tema | `vision-language-action models survey` | `Fragmentos` 12–15 |
| Solo lo reciente | `tactile sim-to-real gap` | `Año desde` = 2024 |
| Solo papers (no los docs del repo) | `failure detection manipulation` | `Origen` = `solo PDFs` |
| Solo guías/protocolos del repo | `evaluation protocol embodied` | `Origen` = `solo Markdown` |
| Un área concreta | `policy learning generalization` | `Categoría` = `VLA_Models` |
| Forzar un término exacto | `generalization` | `Debe contener` = `VLA` |
| Quitar ruido flojo | `grasping deformable objects` | `Similitud mínima` = `0.45` |
| Incluir trabajo retractado | `robot manipulation benchmark` | ✔ `incluir retirados` |

Cada fila tiene su equivalente exacto en el CLI, útil para dejar la consulta
guardada en un script:

```powershell
# Equivalente a: q="tactile sim-to-real gap", Año desde=2024, Fragmentos=12
rag\.venv\Scripts\python.exe rag\query.py "tactile sim-to-real gap" -k 12 --year-min 2024

# Equivalente a: Origen=solo PDFs, Debe contener=VLA, Similitud mínima=0.45
rag\.venv\Scripts\python.exe rag\query.py "failure detection manipulation" --source pdf --contains VLA --min-sim 0.45
```

---

## 9. Lo que la UI **no** hace (y dónde se hace)

La interfaz cubre buscar y copiar contexto. Estas cuatro cosas quedan fuera a
propósito:

**a) Marco teórico y verificación de citas: solo por API.** No hay botón porque
su consumidor es un agente de IA, no una persona. Con el servidor arrancado:

```powershell
# Evidencia con forma de marco teórico (estado del arte, limitaciones, vacíos,
# bases teóricas, comparativa cuantitativa y BibTeX)
$m = Invoke-RestMethod "http://127.0.0.1:8757/api/marco?q=sim2real%20transfer%20safety&k=8&per_section=3"
$m.sections | Format-List

# ¿Existe esta referencia en el corpus? (guardarrail anti-alucinación)
Invoke-RestMethod ("http://127.0.0.1:8757/api/verify?ref=" + [uri]::EscapeDataString("OpenVLA"))
# -> status: confirmed  -> citable sin duda

Invoke-RestMethod ("http://127.0.0.1:8757/api/verify?ref=" + [uri]::EscapeDataString("RT-2"))
# -> status: probable, 3 candidatos empatados -> añade el año o el arxiv_id y repite

# Lote de referencias separadas por "|"
Invoke-RestMethod ("http://127.0.0.1:8757/api/verify?refs=" + [uri]::EscapeDataString("OpenVLA|RT-2"))
# -> total: 2, counts: {confirmed: 1, probable: 1, not_found: 0}, ok: false
```

`/api/marco` acepta `q`, `k` (≤ 50), `per_section` (1–10), `min_sim`,
`category`, `folder` e `include_retired`. **No aplica `year_min`/`year_max`**:
si necesitas recortar por año, usa `/api/search` o el CLI con `--year-min`.
`/api/verify` acepta `ref` repetible o `refs=a|b`, más `limit` (1–10) para el
número de candidatos; no parte por comas, porque una referencia legítima las
lleva (`Kim et al., 2024`). Veredictos: `confirmed`, `probable`, `not_found`.

Equivalente en CLI: `query.py --marco` y `query.py --verify`. El protocolo
completo para agentes está en [`../../AGENTS.md`](../../AGENTS.md).

**b) No escribe nada.** No descarga PDFs, no reindexa, no modifica `papers.csv`,
no genera ficheros. Tras añadir un paper o editar un Markdown hay que
reconstruir el índice y pulsar `F5`:

```powershell
rag\.venv\Scripts\python.exe rag\build_index.py
```

**c) No recuerda tus búsquedas.** No hay histórico, ni favoritos, ni estado en la
URL: al recargar vuelves a los valores por defecto y **no puedes compartir una
búsqueda por enlace**. Si quieres conservar una consulta, cópiala como URL de la
API (`/api/search?q=…&k=…`) o guárdala en un script.

**d) No ejecuta ningún LLM.** Devuelve evidencia y contexto; la generación la
haces tú en el modelo que elijas. Por diseño no hay llaves de API en esta
carpeta (se sincroniza con OneDrive).

---

## 10. Seguridad y privacidad

Todo es deliberado y está en el código, no solo en la documentación:

* **Solo loopback.** El socket se abre en `127.0.0.1`: tu índice no es accesible
  desde la LAN ni desde internet. No hay modo de exponerlo.
* **Validación del header `Host`.** Solo se aceptan `127.0.0.1`, `localhost` y
  `[::1]`; cualquier otra cosa recibe `403`. Esto bloquea *DNS rebinding*: una
  página web maliciosa abierta en tu navegador no puede consultar tu índice.
* **No sirve ficheros arbitrarios.** Solo `/` (que devuelve `web/index.html`) y
  las rutas `/api/*`. El resto da `404` en JSON. No hay listado de directorios ni
  posibilidad de *path traversal*.
* **Solo lectura.** No escribe en disco, no hace peticiones salientes y no usa
  credenciales. El peor fallo posible es una respuesta mal formada.
* **Página autocontenida.** Sin CDN, sin fuentes externas, sin analítica: no sale
  ni un byte de tu máquina y funciona con el wifi apagado.
* **Cabeceras defensivas.** `Cache-Control: no-store` y
  `X-Content-Type-Options: nosniff` en cada respuesta.
* **Registro mínimo.** La consola del servidor imprime la línea de cada petición
  (método, ruta con su *query string* y código) en `stderr`. No se escribe en
  ningún fichero, salvo que tú redirijas la salida al arrancarlo.
* **Escapado de HTML.** Todo lo que viene del índice se escapa antes de pintarse
  (`esc()`), porque los PDFs contienen `<`, `>` y `&` sueltos.

---

## 11. Solución de problemas

| Síntoma | Causa | Solución |
|---------|-------|----------|
| La cabecera dice `índice no disponible` y el estado muestra un error | La colección `embodied_ai` no existe | `rag\.venv\Scripts\python.exe rag\build_index.py` y luego `F5` |
| El servidor imprime `[error] …` y termina con código 2 | Ídem: no llega a levantar la web | Ídem |
| `OSError: [WinError 10048]` al arrancar | Ya hay otra instancia en el puerto 8757 | `--port 9000`, o cierra la otra consola |
| `Sin resultados con esos filtros.` | Filtros demasiado estrechos o consulta en español | Quita filtros, reformula en inglés, sube `Fragmentos` |
| La primera consulta tarda varios segundos | El modelo ONNX se carga en memoria al arrancar | Normal: las siguientes bajan a decenas–cientos de ms (147 ms medidos con `k=4`) |
| No aparecen fragmentos de un paper recién añadido | El índice no se ha reconstruido | `build_index.py` y `F5` |
| `403 {"error": "Host no permitido: solo acceso local."}` | Entraste por la IP de LAN u otro nombre de host | Usa `http://127.0.0.1:8757/` o `http://localhost:8757/` |
| `404 {"error": "Ruta desconocida: /…"}` | Pediste algo que no es `/` ni `/api/*` | Solo existen la página y los seis endpoints |
| `503 {"error": "La colección … no está disponible"}` | El índice no estaba al arrancar el servidor | Reconstruye el índice y reinicia el servidor |
| Un resultado no muestra enlace arXiv | Ese paper no tiene `arxiv_id` en `papers.csv` (o vale `-`) | Abre el documento por su `doc_path` |
| Los PDFs no están en disco | No se versionan por licencias de redistribución | `python scripts/download_papers.py` y reindexa |
| El botón **Copiar** no responde | El navegador bloquea el portapapeles | Selecciona el texto del área y copia con `Ctrl+C` |
| `Error: HTTP 500` en el estado | Excepción dentro del endpoint | Mira la consola del servidor: ahí está el traceback resumido |

---

## 12. Modificar la UI

Es **un fichero**: `web/index.html` (HTML + CSS + JS en línea, sin build, sin
`npm`, sin dependencias). `serve.py` lo lee del disco en **cada** petición a `/`,
así que puedes editarlo y pulsar `F5` sin reiniciar el servidor.

Convenciones que hay que respetar al tocarlo:

* **Nada de CDN, fuentes externas ni analítica.** Rompería el funcionamiento
  offline y la política de esta carpeta (sincronizada con OneDrive).
* **Nada de escritura ni credenciales.** La UI es de solo lectura; si necesitas
  reindexar, se hace por CLI.
* **Escapa siempre con `esc()`** cualquier valor que venga del índice antes de
  insertarlo en el DOM: los PDFs traen `<`, `>` y `&` sueltos.
* **Un filtro nuevo existe primero en `query.py`.** Se añade a `build_where()`,
  luego se mapea en `args_from_params()` de `serve.py` y por último se pinta en
  el panel. Así la web y el CLI siguen devolviendo exactamente lo mismo.
* **`params()` es el único sitio** donde se construye la *query string* que
  comparten `/api/search` y `/api/prompt`: un filtro nuevo se añade ahí una sola
  vez y aparece en ambos.
* Los colores están en variables CSS bajo `:root` (`--bg`, `--panel`, `--acc`,
  `--warn`…); el tema es oscuro y no hay hoja de estilos separada.
* El favicon es un SVG en línea en `<link rel="icon">`: evita el 404 de
  `/favicon.ico` sin añadir ficheros ni peticiones.

---

## 13. Anexo: qué endpoint toca cada acción

| Cuándo | Endpoint | Para qué lo usa la UI |
|--------|----------|------------------------|
| Al cargar la página | `GET /api/stats` | El recuento de la cabecera (`chunks · docs · colección`) |
| Al cargar la página | `GET /api/facets` | Rellena `Categoría` y `Carpeta` con recuentos, y los años de los *placeholders* |
| Botón **Buscar** | `GET /api/search?q=…` | Las tarjetas de resultados |
| Botón **Contexto LLM** | `GET /api/prompt?q=…` | El bloque de texto del modal |
| — (sin botón) | `GET /api/marco?q=…` | Marco teórico por secciones + BibTeX, para agentes |
| — (sin botón) | `GET /api/verify?ref=…` | Verificación de citas, para agentes |
| — (sin botón) | `GET /healthz` | `{"ok": true}` para que un script compruebe que el servidor vive |

Los tres últimos no tienen interfaz a propósito: su consumidor es un agente de
IA. El contrato completo está en [`../../AGENTS.md`](../../AGENTS.md) y en el
apartado de la interfaz web de [`../README.md`](../README.md).
