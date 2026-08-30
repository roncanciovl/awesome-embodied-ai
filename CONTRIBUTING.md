# 🤝 Contributing to Awesome Embodied AI & Sim2Real

¡Gracias por tu interés en contribuir! Este repositorio es una colección curada de papers y recursos sobre Embodied AI, VLA, Sim2Real y ROS 2 + IA.

---

## 📋 Antes de contribuir

1. Lee el [`research-protocol.md`](research-protocol.md) para entender los criterios de inclusión/exclusión.
2. Verifica que el paper no esté ya en [`papers.csv`](papers.csv).
3. Asegúrate de que el paper cumpla **al menos 3 de 5** criterios de inclusión.

---

## ➕ Cómo agregar un paper

### Paso 1: Verificar elegibilidad
El paper debe cumplir al menos 3 de estos criterios:
- [ ] Trata sobre Embodied AI, VLA/VLM/LLM en robótica, Sim2Real o ROS 2
- [ ] Propone o evalúa soluciones en robots físicos o simuladores con transferencia a real
- [ ] Menciona o utiliza ROS, ROS 2, MoveIt, Nav2, Isaac Sim u otro middleware robótico
- [ ] Tiene código, datos o implementación disponible (o es fundacional)
- [ ] Es de alto impacto o de 2025-2026

### Paso 2: Verificar licencia del paper
**IMPORTANTE:** Los PDFs NO se versionan en git por razones de licencia. Cada paper en arXiv tiene su propia licencia:

| Licencia arXiv | ¿Redistribución permitida? |
|----------------|---------------------------|
| CC BY 4.0 | ✅ Sí, con atribución |
| CC BY-SA 4.0 | ✅ Sí, con atribución + share-alike |
| CC0 | ✅ Sí (dominio público) |
| CC BY-NC-ND | ❌ No (no comercial, sin derivados) |
| arXiv non-exclusive license | ❌ No (solo arXiv distribuye) |
| Copyright del autor/editor | ❌ No |

**Verificar licencia:** Ir a la página del paper en arXiv → sección "License" (esquina inferior derecha).

El PDF se descarga localmente con:
```bash
# Agregar la entrada en scripts/download_papers.py y ejecutar:
python scripts/download_papers.py
```

### Paso 3: Actualizar metadatos
Agregar una fila en [`papers.csv`](papers.csv) con todos los campos:

```csv
arxiv_id,title,year,authors_first,robot_type,task,model_type,ros_integration,simulator,dataset,hardware,sim2real,latency_ms,compute_resources,code_available,data_available,limitations,gap_category,category,license,arxiv_url
```

> **Nota:** El campo `file_path` fue reemplazado por `arxiv_url` ya que los PDFs no se versionan.

### Paso 4: Actualizar índice narrativo
Agregar el paper en la sección correspondiente de [`papers/PAPERS.md`](papers/PAPERS.md).

### Paso 5: Registrar decisión
Agregar una fila en la tabla de decisiones de [`research-protocol.md`](research-protocol.md).

### Paso 6: Pull Request
- Título: `Add paper: [Título corto]`
- Descripción: Justificación de inclusión según criterios
- Labels: `paper`, `category-XX`

---

## 🧹 Cómo proponer la eliminación de un paper

Un paper puede eliminarse si:
- No cumple criterios de inclusión (ver `research-protocol.md`)
- Está duplicado o es redundante
- No tiene PDF accesible

Proceso:
1. Abrir issue con label `removal`
2. Justificar según criterios de exclusión
3. Esperar aprobación del maintainer

---

## 🔍 Control de calidad de metadatos

Cada PR que modifique `papers.csv` debe pasar estas verificaciones:

| Campo | Regla |
|-------|-------|
| `arxiv_id` | Formato `YYMM.NNNNN` válido |
| `year` | 2017-2026 |
| `title` | Coincide con el PDF |
| `file_path` | Existe en el repositorio |
| `category` | Una de las 7 categorías válidas |
| `limitations` | No vacío (mínimo 10 caracteres) |

Script de validación (TODO): `scripts/validate_metadata.py`

---

## 📁 Estructura del repositorio

```
awesome-embodied-ai/
├── README.md                 # Índice principal
├── research-protocol.md      # Protocolo de investigación
├── research-gaps.md          # Brechas identificadas
├── papers.csv                # Metadatos estructurados
├── CITATION.cff              # Citación del repositorio
├── LICENSE                   # Licencia CC BY-SA 4.0
├── CONTRIBUTING.md           # Este archivo
├── papers/                   # PDFs organizados por categoría
│   ├── PAPERS.md             # Índice narrativo
│   ├── 01_VLA_Models/
│   ├── 02_Simulation_Environments/
│   ├── 03_Sim2Real_RL/
│   ├── 04_Robotics_Frameworks/
│   ├── 05_Surveys_Case_Studies/
│   ├── 06_ROS2_AI_LLMs/
│   └── 07_Recent_2025_2026/
└── scripts/
    ├── download_papers.py    # Descarga con reintentos
    └── search_recent_papers.py  # Búsqueda en arXiv API
```

---

## 🏷️ Categorías válidas

| Categoría | Scope |
|-----------|-------|
| `VLA_Models` | Modelos Vision-Language-Action |
| `Simulation_Environments` | Simuladores y datasets 3D |
| `Sim2Real_RL` | Transferencia sim2real y RL |
| `Robotics_Frameworks` | ROS 2, MoveIt, Nav2, middleware |
| `Surveys_Case_Studies` | Surveys y casos de estudio |
| `ROS2_AI_LLMs` | Integración ROS 2 + LLM/VLM |
| `Recent_2025_2026` | Papers de frontera (2025-2026) |

---

## ⚖️ Licencia

Al contribuir, aceptas que tu contribución se licencie bajo [CC BY-SA 4.0](LICENSE).
Los PDFs de papers pertenecen a sus autores originales (ver licencias de arXiv).

---

## 📧 Contacto

- Maintainer: [Roncanciovl](https://github.com/roncanciovl)
- Issues: [GitHub Issues](https://github.com/roncanciovl/awesome-embodied-ai/issues)

---

*Última actualización: 2026-08-30*