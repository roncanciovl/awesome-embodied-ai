# 🔍 Research Gaps — Embodied AI & Sim2Real

**Fecha de corte:** 2026-08-30
**Basado en:** 41 papers analizados (ver [`papers.csv`](papers.csv))
**Protocolo:** [`research-protocol.md`](research-protocol.md)

---

## 📌 Resumen ejecutivo

El análisis de la colección revela **cuatro sublíneas de investigación** con brechas significativas. Cada una representa una oportunidad para contribuciones originales, especialmente en el contexto de integración con **ROS 2** como framework de producción.

---

## 1️⃣ Percepción y Grounding Multimodal

### Estado actual
- Los VLMs (Florence-2, GPT-4V, Gemini) logran comprensión semántica de escenas, pero su integración como **nodos ROS 2 nativos** es incipiente (solo `ROS2_Wrapper_Florence-2_2026`).
- El grounding espacial (mapear "la taza roja" → coordenadas 3D) depende de pipelines fragmentados: VLM + detector + estimador de pose.
- Papers como VoxPoser y SayCan usan percepción multimodal, pero con arquitecturas propietarias sin camino claro a ROS 2.

### Brechas identificadas
| Brecha | Evidencia | Oportunidad |
|--------|-----------|-------------|
| **Falta de estándar ROS 2 para VLMs** | Solo 1 paper (2604.01179) provee wrapper ROS 2 | Crear `ros2_vlm_msgs` con interfaces estándar |
| **Grounding 3D en tiempo real** | VoxPoser requiere VLM externo; latencia >500ms | VLM cuantizado + proyección 3D en <100ms |
| **Fusión sensorial multimodal** | Papers tratan cámara/LiDAR/táctil por separado | Nodo ROS 2 de fusión temprana VLM+depth+tactile |
| **Calibración semántica** | No hay papers sobre calibración VLM-robot | Benchmark de grounding métrico-semántico |

### Papers clave de referencia
- `2604.01179` (ROS 2 Wrapper Florence-2)
- `2307.05973` (VoxPoser)
- `2204.01691` (SayCan)

---

## 2️⃣ Planificación Semántica y Agentes Robóticos

### Estado actual
- LLMs como planificadores de alto nivel (SayCan, Code as Policies, SayPlan, LLM+P) demuestran capacidad de descomposición de tareas.
- La ejecución de bajo nivel sigue siendo clásica (MoveIt 2, controladores PID) — el puente semántico→acción es el cuello de botella.
- Los VLAs (OpenVLA, π0) prometen unificar planificación y control, pero su latencia (>50ms) limita el uso reactivo.

### Brechas identificadas
| Brecha | Evidencia | Oportunidad |
|--------|-----------|-------------|
| **Puente LLM→ROS 2 estandarizado** | Code as Policies genera código ad-hoc | Framework de "skill primitives" ROS 2 accionables por LLM |
| **Recuperación ante fallos** | Solo FLARE (2608.26645, no incluido) aborda fallos | Agente ROS 2 con auto-diagnóstico y re-planificación |
| **Memoria episódica robótica** | Inner Monologue usa feedback manual | Grafo de memoria ROS 2 persistente entre sesiones |
| **Multi-robot semántico** | MA-VLA (2608.25864) es reciente | Orquestación LLM de flotas ROS 2 heterogéneas |

### Papers clave de referencia
- `2209.07753` (Code as Policies)
- `2309.11489` (SayPlan)
- `2304.11477` (LLM+P)
- `2606.09416` (Harness Engineering)

---

## 3️⃣ Inferencia Local y Edge AI

### Estado actual
- La mayoría de VLAs requieren GPUs de datacenter (A100, TPU) — incompatible con robots móviles autónomos.
- Papers 2025-2026 (TurboVLA, LiteVLA-Edge, Quantized LLMs, ROS2SmolVLA) atacan el problema, pero son soluciones aisladas.
- No existe un benchmark estándar de **latencia/precisión/consumo** para VLAs en hardware embebido (Jetson, Raspberry Pi, NPU).

### Brechas identificadas
| Brecha | Evidencia | Oportunidad |
|--------|-----------|-------------|
| **Benchmark Edge-VLA** | Cada paper usa su propio hardware/métrica | Benchmark ROS 2 + Jetson Orin con métricas unificadas |
| **Cuantización sin pérdida robótica** | LiteVLA-Edge cuantiza pero pierde precisión | Técnicas QAT (Quantization-Aware Training) específicas para acciones |
| **Inferencia asíncrona ROS 2** | FlashVLA (2608.27384) propone streaming | Nodo ROS 2 con pipeline asíncrono VLA + executor |
| **NPU/FPGA para VLA** | Sin papers sobre NPU robótica | Portar SmolVLA a NPU (Hailo, Coral, Jetson) |

### Papers clave de referencia
- `2608.23320` (ROS2SmolVLA)
- `2607.27205` (TurboVLA)
- `2603.03380` (LiteVLA-Edge)
- `2506.09581` (Quantized LLMs Edge AI)

---

## 4️⃣ Sim2Real, Seguridad y Evaluación Reproducible

### Estado actual
- Domain Randomization (2017) sigue siendo la técnica dominante; pocas mejoras metodológicas en 8 años.
- Los papers de locomoción (RMA, ANYmal) tienen Sim2Real robusto, pero **manipulación contact-rich** sigue fallando.
- No hay protocolos de seguridad para desplegar políticas VLA en robots colaborativos (ISO/TS 15066).
- La evaluación es irreproducible: cada paper usa su propio setup, sin benchmarks compartidos.

### Brechas identificadas
| Brecha | Evidencia | Oportunidad |
|--------|-----------|-------------|
| **Sim2Real para manipulación blanda** | Solo 1910.07113 (OpenAI) aborda diestra | Sim2Real con sensores táctiles + VLA |
| **Certificación de políticas** | 2608.21572 (no incluido) propone certificados | Framework de verificación pre-despliegue ROS 2 |
| **Seguridad VLA en cobots** | Sin papers sobre ISO/TS 15066 + VLA | Capa de seguridad ROS 2 que valide acciones VLA |
| **Benchmark reproducible** | RoboCasa es sim-only; sin real | Benchmark dual sim+real con ROS 2 + AprilTags |
| **Métricas de éxito estandarizadas** | Cada paper define "éxito" distinto | Taxonomía de métricas (task success, safety, latency, energy) |

### Papers clave de referencia
- `1703.06907` (Domain Randomization)
- `2107.04034` (RMA)
- `1910.07113` (Dexterous Manipulation)
- `2406.02523` (RoboCasa)

---

## 🎯 Matriz de oportunidades

| Sublínea | Impacto | Factibilidad con ROS 2 | Prioridad |
|----------|---------|------------------------|-----------|
| Percepción multimodal | Alto | Alta (wrappers existentes) | 🥇 |
| Planificación semántica | Alto | Media (requiere diseño de skills) | 🥈 |
| Edge AI / inferencia local | Muy alto | Alta (ROS2SmolVLA como base) | 🥇 |
| Sim2Real + seguridad | Crítico | Media (requiere hardware) | 🥉 |

---

## 🔬 Propuesta experimental: `burger_delivery` como banco de pruebas

El proyecto [burger_delivery](https://github.com/roncanciovl/burger_delivery) (ROS 2 Jazzy + Kinova Gen3 + AprilTags + gemini-robotics) es ideal para validar estas brechas:

| Experimento | Arquitectura | Métrica |
|-------------|--------------|---------|
| **Baseline clásico** | AprilTags + MoveIt 2 + FSM | Task success rate, latency |
| **VLM en la nube** | gemini-robotics API + MoveIt 2 | Latencia, costo, robustez |
| **VLA local cuantizado** | SmolVLA/Florence-2 ROS 2 + MoveIt 2 | Latencia, precisión, consumo |

**Hipótesis:** La alternativa local cuantizada alcanzará ≥80% del success rate de la solución en nube con <50% de latencia.

---

## 📎 Referencias cruzadas

- Metadatos completos: [`papers.csv`](papers.csv)
- Protocolo de investigación: [`research-protocol.md`](research-protocol.md)
- Índice narrativo: [`papers/PAPERS.md`](papers/PAPERS.md)

---

*Documento vivo — actualizar con cada revisión de la colección.*