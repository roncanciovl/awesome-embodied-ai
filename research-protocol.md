# 📋 Research Protocol — Awesome Embodied AI & Sim2Real

**Fecha de corte:** 2026-08-30
**Versión:** 1.0
**Investigador principal:** [Roncanciovl](https://github.com/roncanciovl)

---

## 🎯 Preguntas de investigación

### Pregunta principal
> ¿Cómo se está integrando la inteligencia artificial generativa (LLMs, VLMs, VLAs) con frameworks robóticos de producción (ROS 2) para cerrar la brecha entre simulación y realidad?

### Preguntas secundarias
1. **P1:** ¿Qué modelos VLA/VLM/LLM son más adecuados para despliegue en hardware robótico real con recursos limitados (Edge AI)?
2. **P2:** ¿Cuál es el estado del arte en transferencia Sim2Real para manipulación y navegación con políticas aprendidas?
3. **P3:** ¿Cómo actúa ROS 2 como capa de orquestación ("harness") entre modelos de IA y actuadores físicos?
4. **P4:** ¿Qué benchmarks y métricas existen para evaluar de forma reproducible sistemas embodied con IA?
5. **P5:** ¿Cuáles son las brechas abiertas en percepción multimodal, planificación semántica e inferencia local?

---

## 📚 Fuentes consultadas

| Fuente | Tipo | Uso |
|--------|------|-----|
| [arXiv](https://arxiv.org) (cs.RO, cs.AI, cs.CV, cs.CL) | Preprints | Fuente principal de papers |
| [arXiv API](https://info.arxiv.org/help/api/) | API de búsqueda | Consultas programáticas (`scripts/search_recent_papers.py`) |
| [GitHub](https://github.com) | Repositorios | Implementaciones open-source (OpenVLA, Octo, etc.) |
| [Papers with Code](https://paperswithcode.com) | Índice | Verificación de disponibilidad de código |
| [ROS 2 Documentation](https://docs.ros.org) | Docs oficiales | Contexto de integración ROS 2 |
| [IEEE Xplore / ACM DL](https://ieeexplore.ieee.org) | Publicaciones | Referencias de conferencias (ICRA, IROS, CoRL) |

---

## 🔍 Consultas realizadas (arXiv API)

```
# Consulta 1: VLA recientes
search_query=all:"vision-language-action" AND submittedDate:[202501 TO 202612]
sortBy=submittedDate&sortOrder=descending

# Consulta 2: Embodied AI
search_query=all:"embodied AI" AND submittedDate:[202501 TO 202612]

# Consulta 3: ROS 2 + LLM
search_query=all:"ROS 2" AND all:"language model"

# Consulta 4: Sim2Real
search_query=all:"sim-to-real" AND submittedDate:[202501 TO 202612]

# Consulta 5: LLM + manipulación
search_query=all:"large language model" AND all:"robot manipulation" AND submittedDate:[202501 TO 202612]

# Consulta 6: VLA + ROS
search_query=all:"vision-language-action" AND all:"ROS"
```

**Script de reproducción:** `scripts/search_recent_papers.py`

---

## 📅 Periodo de búsqueda

| Parámetro | Valor |
|-----------|-------|
| Periodo principal | 2017-01 → 2026-08 |
| Énfasis en frontera | 2025-01 → 2026-08 |
| Fecha de corte | 2026-08-30 |
| Última actualización | 2026-08-30 |

---

## ✅ Criterios de inclusión

Un paper se **incluye** si cumple al menos 3 de 5:

1. **Relevancia temática:** Trata sobre Embodied AI, VLA/VLM/LLM en robótica, Sim2Real o integración con ROS/ROS 2.
2. **Aplicabilidad física:** Propone o evalúa soluciones en robots físicos o simuladores con transferencia a real.
3. **Integración con framework:** Menciona o utiliza ROS, ROS 2, MoveIt, Nav2, Isaac Sim, o middleware robótico.
4. **Reproducibilidad:** Tiene código, datos o implementación disponible (o es un paper fundacional).
5. **Impacto:** Es citado ampliamente, proviene de grupo relevante (Google DeepMind, NVIDIA, Stanford, ETH, etc.) o es de 2025-2026.

## ❌ Criterios de exclusión

Un paper se **excluye** si cumple alguno:

1. **Sin robótica física:** Agentes puramente virtuales (ej. Minecraft, videojuegos) sin camino a despliegue real.
2. **Benchmark sin integración:** Datasets/benchmarks sin conexión a frameworks robóticos de producción.
3. **Redundancia:** Duplica metodología de otro paper ya incluido con menor aporte.
4. **Fuera de scope:** Generación de datos sintéticos como fin único, sin evaluación robótica.
5. **Sin acceso:** PDF no disponible públicamente en arXiv.

---

## 📊 Registro de decisiones

| Paper | Decisión | Justificación |
|-------|----------|---------------|
| Voyager (2305.16291) | ❌ Excluido | Agente en Minecraft, sin robótica física |
| BEHAVIOR-1K (2306.03310) | ❌ Excluido | Benchmark Stanford sin integración ROS 2 |
| RoboGen (2311.01455) | ❌ Excluido | Generación de datos sim, muy específico |
| GenSim (2310.01361) | ❌ Excluido | Redundante con RoboGen |
| ROS2SmolVLA (2608.23320) | ✅ Incluido | VLA nativo en ROS 2 industrial |
| ROS 2 Wrapper Florence-2 (2604.01179) | ✅ Incluido | VLM local como nodo ROS 2 |

---

## 🔁 Protocolo de actualización

1. Ejecutar `python scripts/search_recent_papers.py` mensualmente.
2. Evaluar nuevos papers contra criterios de inclusión/exclusión.
3. Actualizar `papers.csv` (metadatos) y `PAPERS.md` (índice narrativo).
4. Registrar decisiones en la tabla de este documento.
5. Commit con mensaje `Update paper collection: YYYY-MM`.

---

## 📎 Documentos relacionados

- [`papers/PAPERS.md`](papers/PAPERS.md) — Índice narrativo de papers
- [`papers.csv`](papers.csv) — Metadatos estructurados (machine-readable)
- [`research-gaps.md`](research-gaps.md) — Brechas identificadas
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — Guía de contribución
- [`CITATION.cff`](CITATION.cff) — Citación del repositorio

---

*Este protocolo sigue las mejores prácticas de revisión sistemática adaptadas a un repositorio awesome.*