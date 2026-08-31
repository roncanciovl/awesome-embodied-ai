# 📖 Glosario — Awesome Embodied AI & Sim2Real

Glosario de términos usados en esta colección y en la literatura de IA aplicada a robótica.

---

## 🧠 Modelos de Inteligencia Artificial

### LLM — Large Language Model (Modelo de Lenguaje a Gran Escala)
Red neuronal entrenada con masivos textos para comprender y generar lenguaje natural. Ejemplos: GPT-4, Claude, Llama 2, Gemini. En robótica se usan para **planificación de tareas** ("recoge la taza y ponla en el fregadero" → secuencia de pasos) y **generación de código** de control.

### VLM — Vision-Language Model (Modelo Visión-Lenguaje)
Modelo multimodal que combina visión (imágenes/cámara) y lenguaje. Entiende el contenido de una escena y responde preguntas sobre ella. Ejemplos: Florence-2, CLIP, GPT-4V, Gemini Vision. En robótica se usan para **percepción semántica**: "¿dónde está el objeto rojo?", "¿qué está haciendo el humano?".

### VLA — Vision-Language-Action (Modelo Visión-Lenguaje-Acción)
La evolución del VLM: además de percibir y entender, **genera acciones robóticas directamente** (coordenadas de movimiento, comandos de agarre). Es el paradigma central de esta colección. Ejemplos: OpenVLA, RT-2, π0, Octo, SmolVLA.
> 📌 **Diferencia clave:** VLM responde con texto; VLA responde con acciones físicas.

### RL — Reinforcement Learning (Aprendizaje por Refuerzo)
Paradigma donde un agente aprende mediante prueba y error, recibiendo recompensas o castigos. Base de los papers de locomoción (RMA, ANYmal) y control (Domain Randomization). Alternativa a la supervisión directa de VLAs.

### IL — Imitation Learning (Aprendizaje por Imitación)
El agente aprende imitando demostraciones humanas (teleoperación, kinesthetic teaching). Fuente principal de datos para entrenar VLAs (Open X-Embodiment: 800k+ trayectorias).

### PDDL — Planning Domain Definition Language
Lenguaje formal para planificadores clásicos de IA. LLM+P lo combina con LLMs: el LLM traduce lenguaje natural → PDDL, el planificador resuelve óptimamente.

---

## 🌉 Sim2Real (Simulación → Realidad)

### Sim2Real — Sim-to-Real Transfer (Transferencia Simulación-Realidad)
El proceso de entrenar un modelo en simulación y hacerlo funcionar en el mundo físico. El problema central: la simulación nunca es perfecta (el "reality gap").

### Reality Gap (Brecha de Realidad)
Diferencia entre la simulación y el mundo real: física simplificada, sensores ideales, sin ruido. Causa principal del fallo de políticas transferidas.

### Domain Randomization (Randomización de Dominio)
Técnica fundacional (Tobin et al., 2017): randomizar masivamente propiedades del simulador (texturas, iluminación, física) para que el modelo aprenda a ser robusto ante variaciones, en lugar de ajustarse a una simulación específica.

### Dynamics Randomization
Extensión: randomizar parámetros dinámicos (masa, fricción, rigidez de motores) además de los visuales.

### Teacher-Student (Profesor-Alumno)
Paradigma de destilación: el "Teacher" se entrena en simulación con información privilegiada (privileged info: posiciones exactas, fricción real); el "Student" aprende solo de observaciones disponibles en el robot real. Base de RMA.

### RMA — Rapid Motor Adaptation
Arquitectura (Kumar et al., 2021) con dos módulos: un estimador de entorno (adaptation module) que se ajusta online a cambios no vistos (carga, terreno), y una política que usa esa estimación.

---

## 🤖 Robótica y Frameworks

### ROS — Robot Operating System
Middleware de código abierto para robótica. No es un "sistema operativo" sino una capa de abstracción con nodos, mensajes, tópicos, servicios y acciones.

### ROS 2
Versión moderna de ROS (2020+). Cambia el transporte de TCPROS a **DDS**, con mejoras de:
- **Tiempo real** y determinismo
- **QoS** (Quality of Service) configurable
- **Seguridad** (SROS)
- Multi-plataforma (Windows, macOS, RTOS)

### DDS — Data Distribution Service
Estándar OMG de comunicación publish-subscribe usado por ROS 2. Provee descubrimiento automático de nodos, QoS por tópico y transporte eficiente sin broker central.

### Nodo / Tópico / Servicio / Acción (ROS 2)
- **Nodo:** proceso que ejecuta una función (ej. `camera_driver`, `vla_policy`)
- **Tópico:** canal publish-subscribe (ej. `/image_raw`)
- **Servicio:** llamada request-response (ej. `/get_pose`)
- **Acción:** objetivo largo con feedback (ej. `/move_to` con progreso)

### MoveIt 2
Framework de **planificación de movimiento** para ROS 2: cinemática inversa (IK), planificación de trayectorias (OMPL, Pilz), gestión de colisiones. Usado para manipular brazos como el Kinova Gen3.

### Nav2
Framework de **navegación autónoma** para ROS 2: SLAM, localización (AMCL), planificación de rutas, evasión de obstáculos. Para robots móviles.

### ros2_control
Framework de control en tiempo real de ROS 2: interfaces de hardware (motores, sensores), controladores (PID, effort, velocity).

### micro-ROS
ROS 2 para **microcontroladores** (STM32, ESP32): permite que dispositivos embebidos participen en la red ROS 2 (Edge AI).

### AprilTags
Marcadores visuales tipo QR para **localización espacial**: el robot detecta el tag con la cámara y calcula su pose absoluta. Usados en `burger_delivery`.

### Cobot — Robot Colaborativo
Robot diseñado para trabajar junto a humanos sin jaulas de seguridad (ej. Kinova Gen3, UR5). Regulados por ISO/TS 15066.

---

## 🎯 Conceptos de IA Embodied

### Grounding (Anclaje)
Conectar símbolos del lenguaje con el mundo físico: "taza" → detectar taza en imagen + estimar posición 3D. El problema central del puente lenguaje→acción.

### Affordance (Aforanza)
Propiedad de un objeto que indica qué acciones permite: una taza "aforda" ser agarrada por el asa; una puerta "aforda" abrirse. SayCan usa funciones de valor de affordance para que los LLMs propongan acciones factibles.

### Embodied AI (IA Embodied / Encarnada)
IA que percibe, razona y **actúa en un entorno físico** (o simulado físicamente). Contraste con IA "de escritorio" (chatbots, generación de imágenes).

### Task Planning (Planificación de Tareas)
Descomponer un objetivo de alto nivel ("prepara un café") en acciones ejecutables ("agarrar jarra" → "llenar de agua" → "verter"...).

### Skill Primitive (Primitiva de Habilidad)
Acción robótica atómica y reutilizable ("pick", "place", "open"). Los LLMs planifican combinando primitivas; el controlador las ejecuta.

### HRI — Human-Robot Interaction
Interacción Humano-Robot: interfaces, seguridad, colaboración. `Conversational_Framework_HRI` (2026) es un ejemplo reciente.

### World Model (Modelo del Mundo)
Red neuronal que predice cómo cambia el entorno tras acciones (simulación interna aprendida). Base de GenSim, RoboGen y los enfoques de model-based RL.

---

## ⚡ Inferencia y Despliegue

### Edge AI
Ejecutar modelos de IA **en el dispositivo** (robot) en lugar de la nube. Ventajas: latencia baja, privacidad, funciona sin internet. Desafío: hardware limitado.

### Cuantización (Quantization)
Reducir la precisión numérica de un modelo (FP32 → INT8/INT4) para hacerlo más pequeño y rápido, con mínima pérdida de calidad. Clave para Edge AI. Ejemplos en la colección: LiteVLA-Edge, Quantized LLMs.

### QAT — Quantization-Aware Training
Entrenamiento considerando la cuantización desde el inicio (vs. cuantizar post-entrenamiento), preservando mejor la precisión.

### Latencia (Latency)
Tiempo de respuesta del modelo (percepción → acción). Crítico en robótica:
- <10 ms: control reactivo de alto nivel
- 10-50 ms: control estándar
- 50-200 ms: planificación aceptable
- >200 ms: solo decisiones no urgentes

### FPS / Hz en VLA
Frecuencia de decisión de una política. TurboVLA logra 32 Hz (31 ms) — suficiente para manipulación dinámica. La mayoría de VLAs clásicos operan a 1-10 Hz.

### VRAM
Memoria de la GPU. TurboVLA opera con <1 GB VRAM; OpenVLA (7B parámetros) requiere ~14 GB en FP16.

---

## 📊 Datasets y Benchmarks

### Open X-Embodiment
Dataset colaborativo (2023) con datos de **22 robots distintos** (Google, Stanford, ETH, etc.). Base para entrenar políticas generalistas cross-embodiment (RT-X).

### Benchmark
Suite estandarizada de tareas para comparar métodos de forma reproducible. Ejemplos: RoboCasa (sim), GuardianBench (seguridad), Arena 4.0 (ROS 2 navegación).

### Success Rate (Tasa de Éxito)
Métrica principal: % de episodios donde el robot completa la tarea. Complementada por: tiempo al éxito, colisiones, sujeciones fallidas.

---

## 🏢 Sistemas específicos

### Gemini Robotics (Google DeepMind)
**Familia de modelos con clasificaciones distintas** — importante no confundirlos:

| Variante | Tipo | ¿Genera acciones? | Uso |
|----------|------|-------------------|-----|
| **Gemini Robotics** (base, 1.5) | ✅ **VLA** | Sí — controla brazos (ALOHA 2) y humanoides (Apollo) | Control directo de robots |
| **Gemini Robotics-ER** (*Embodied Reasoning*) | ⚠️ **VLM** con razonamiento espacial | ❌ No — solo percibe y razona | Percepción semántica, integración con controladores existentes |
| **Gemini Robotics On-Device** (1.5) | ✅ **VLA cuantizado** | Sí — localmente en el robot (Jetson), sin nube | Edge AI, robots sin conectividad |

> 📌 **En `burger_delivery`:** se usa `gemini-robotics` para *semantic scene processing* → corresponde al modo **ER (VLM)**: la escena se interpreta semánticamente y las acciones las ejecuta MoveIt 2. No es control VLA end-to-end.
>
> 📌 **Gemini Robotics On-Device** es especialmente relevante para la sublínea *Edge AI* de [`research-gaps.md`](research-gaps.md): es el análogo comercial de lo que ROS2SmolVLA / LiteVLA-Edge proponen en investigación.

---

## 🏢 Grupos y Sistemas mencionados

| Nombre | Qué es |
|--------|--------|
| **Google DeepMind** | Creador de RT-1, RT-2, RT-X, SayCan, MuJoCo, Gemini Robotics |
| **Physical Intelligence** | Startup creadora de π0 |
| **Stanford iGibson/BEHAVIOR** | Lab de Li Fei-Fei, simuladores domésticos |
| **ETH Zurich (ANYmal)** | Lab de locomoción cuadrúpeda de Hutter |
| **Kinova Gen3** | Brazo robótico colaborativo de 7 DOF |
| **NVIDIA Isaac Sim** | Simulador basado en Omniverse con fotorrealismo |
| **Gazebo** | Simulador clásico de ROS (ahora gz-sim) |
| **MuJoCo** | Motor de física de contactos (DeepMind, open-source) |

---

## 🔗 Referencias cruzadas

- Metadatos: [`papers.csv`](papers.csv)
- Índice de papers: [`papers/PAPERS.md`](papers/PAPERS.md)
- Protocolo: [`research-protocol.md`](research-protocol.md)
- Brechas: [`research-gaps.md`](research-gaps.md)

---

*Última actualización: 2026-08-30. Sugerencias de términos: abrir issue con label `glossary`.*