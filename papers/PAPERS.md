# 📄 Paper Library — Awesome Embodied AI & Sim2Real

Colección local de papers fundamentales descargados desde [arXiv](https://arxiv.org).
Para re-descargar o actualizar, ejecuta:

```bash
python scripts/download_papers.py
```

> **Nota:** Todos los PDFs provienen de arXiv. Verifica las licencias de cada paper antes de redistribuirlos.

---

## 📁 Estructura

```
papers/
├── 01_VLA_Models/              # Vision-Language-Action Models
├── 02_Simulation_Environments/ # Simuladores y entornos 3D
├── 03_Sim2Real_RL/             # Transferencia Sim2Real y RL
├── 04_Robotics_Frameworks/     # ROS 2 y frameworks de manipulación
└── 05_Surveys_Case_Studies/    # Surveys y agentes embodied
```

---

## 🤖 01 — Vision-Language-Action (VLA) Models

| Paper | arXiv | Año | Archivo |
|-------|-------|-----|---------|
| **OpenVLA: An Open-Source Vision-Language-Action Model** | [2406.09246](https://arxiv.org/abs/2406.09246) | 2024 | `OpenVLA_An_Open-Source_Vision-Language-Action_Model.pdf` |
| **RT-1: Robotics Transformer for Real-World Control at Scale** | [2212.06817](https://arxiv.org/abs/2212.06817) | 2022 | `RT-1_Robotics_Transformer_for_Real-World_Control_at_Scale.pdf` |
| **RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control** | [2307.15818](https://arxiv.org/abs/2307.15818) | 2023 | `RT-2_Vision-Language-Action_Models_Transfer_Web_Knowledge.pdf` |
| **Octo: An Open-Source Generalist Robot Policy** | [2405.12213](https://arxiv.org/abs/2405.12213) | 2024 | `Octo_An_Open-Source_Generalist_Robot_Policy.pdf` |
| **Open X-Embodiment: Robotic Learning Datasets and RT-X Models** | [2310.08864](https://arxiv.org/abs/2310.08864) | 2023 | `Open_X-Embodiment_Robotic_Learning_Datasets_and_RTX_Models.pdf` |
| **π0: A Vision-Language-Action Flow Model for General Robot Control** | [2410.24164](https://arxiv.org/abs/2410.24164) | 2024 | `pi0_Vision-Language-Action_Flow_Models.pdf` |

### Resumen rápido
- **RT-1** fue el primer Transformer de Google para control robótico real a escala (130k demostraciones, 700+ tareas).
- **RT-2** demostró que el conocimiento web (VLM) se transfiere directamente a acciones robóticas.
- **Open X-Embodiment / RT-X** unificó datasets de 22 robots distintos para entrenar políticas generalistas.
- **OpenVLA** es la alternativa open-source de 7B parámetros basada en Llama 2 + SigLIP.
- **Octo** ofrece una política generalista open-source entrenada en 800k trayectorias.
- **π0** (Physical Intelligence) introduce flow matching para acciones continuas de alta frecuencia.

---

## 🏙️ 02 — Simulation Environments & Digital Twins

| Paper | arXiv | Año | Archivo |
|-------|-------|-----|---------|
| **Habitat: A Platform for Embodied AI Research** | [1904.01201](https://arxiv.org/abs/1904.01201) | 2019 | `Habitat_A_Platform_for_Embodied_AI_Research.pdf` |
| **AI2-THOR: An Interactive 3D Environment for Visual AI** | [1712.05474](https://arxiv.org/abs/1712.05474) | 2017 | `AI2-THOR_An_Interactive_3D_Environment_for_Visual_AI.pdf` |
| **iGibson: A Simulation Environment for Interactive Tasks in Large Realistic Scenes** | [2008.11765](https://arxiv.org/abs/2008.11765) | 2020 | `iGibson_A_Simulation_Environment_for_Interactive_Tasks.pdf` |
| **Habitat-Matterport 3D Dataset (HM3D): 1000 Large-scale 3D Environments for Embodied AI** | [2109.08238](https://arxiv.org/abs/2109.08238) | 2021 | `Habitat-Matterport_3D_Dataset.pdf` |
| **RoboCasa: Large-Scale Simulation of Everyday Tasks for Generalist Robots** | [2406.02523](https://arxiv.org/abs/2406.02523) | 2024 | `RoboCasa_Large-Scale_Simulation_of_Everyday_Tasks.pdf` |
| **BEHAVIOR-1K: A Human-Centered, Embodied AI Benchmark with 1,000 Everyday Activities** | [2306.03310](https://arxiv.org/abs/2306.03310) | 2023 | `BEHAVIOR-1K_A_Human-Centered_Benchmark_for_Embodied_AI.pdf` |

### Resumen rápido
- **Habitat** (Meta) es el estándar para navegación embodied en escenas 3D escaneadas.
- **AI2-THOR** (Allen Institute) añade interactividad física (abrir puertas, mover objetos).
- **iGibson / BEHAVIOR-1K** (Stanford) se enfocan en tareas domésticas realistas con física compleja.
- **HM3D** provee 1000 escenas 3D reales escaneadas para entrenar agentes.
- **RoboCasa** (UT Austin/NVIDIA) genera 100+ cocinas proceduralmente para manipulación.

---

## 🌉 03 — Sim2Real Transfer & Reinforcement Learning

| Paper | arXiv | Año | Archivo |
|-------|-------|-----|---------|
| **Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World** | [1703.06907](https://arxiv.org/abs/1703.06907) | 2017 | `Domain_Randomization_for_Transferring_DNNs_from_Simulation.pdf` |
| **Sim-to-Real Transfer of Robotic Control with Dynamics Randomization** | [1710.06537](https://arxiv.org/abs/1710.06537) | 2017 | `Sim-to-Real_Transfer_of_Robotic_Control_with_Dynamics_Randomization.pdf` |
| **Learning Quadrupedal Locomotion over Challenging Terrain** | [1910.11100](https://arxiv.org/abs/1910.11100) | 2019 | `Learning_Quadrupedal_Locomotion_over_Challenging_Terrain.pdf` |
| **Sim-to-Real Transfer for Dexterous Manipulation** | [1910.07113](https://arxiv.org/abs/1910.07113) | 2019 | `Sim-to-Real_Transfer_for_Dexterous_Manipulation.pdf` |
| **Learning Agile and Dynamic Motor Skills for Legged Robots** | [1901.08652](https://arxiv.org/abs/1901.08652) | 2019 | `Learning_Agile_and_Dynamic_Motor_Skills_for_Legged_Robots.pdf` |
| **Rapid Motor Adaptation for Legged Robots (Teacher-Student)** | [2009.03317](https://arxiv.org/abs/2009.03317) | 2020 | `Teacher-Student_Framework_for_Sim-to-Real_Locomotion.pdf` |
| **RMA: Rapid Motor Adaptation for Legged Robots** | [2107.04034](https://arxiv.org/abs/2107.04034) | 2021 | `RMA_Rapid_Motor_Adaptation_for_Legged_Robots.pdf` |

### Resumen rápido
- **Domain Randomization** (Tobin et al., OpenAI) es la técnica fundacional: randomizar texturas/física en sim para que el modelo sea robusto en real.
- **Dynamics Randomization** (Peng et al.) extiende la idea al espacio de parámetros dinámicos.
- **ANYmal / ETH papers** establecieron el paradigma de locomoción cuadrúpeda aprendida.
- **Teacher-Student / RMA** introdujeron la adaptación online vía destilación de información privilegiada.

---

## ⚙️ 04 — Robotic Frameworks (ROS 2)

| Paper | arXiv | Año | Archivo |
|-------|-------|-----|---------|
| **ROS 2: Architecture and Performance** | [2202.01734](https://arxiv.org/abs/2202.01734) | 2022 | `ROS2_Architecture_and_Performance.pdf` |
| **MoveIt 2: Real-Time Motion Planning and Manipulation** | [2405.13268](https://arxiv.org/abs/2405.13268) | 2024 | `MoveIt2_and_Real-Time_Manipulation.pdf` |

### Resumen rápido
- Paper de arquitectura ROS 2: compara DDS vs. ROS 1, latencia y determinismo.
- MoveIt 2: planificación de movimiento en tiempo real para manipulación industrial.

---

## 📚 05 — Surveys & Case Studies

| Paper | arXiv | Año | Archivo |
|-------|-------|-----|---------|
| **A Survey of Embodied AI: From Sim-to-Real and Beyond** | [2407.01738](https://arxiv.org/abs/2407.01738) | 2024 | `A_Survey_of_Embodied_AI_From_Sim-to-Real.pdf` |
| **Vision-Language-Action Models for Robotics: A Survey** | [2411.13548](https://arxiv.org/abs/2411.13548) | 2024 | `Vision-Language-Action_Models_Survey.pdf` |
| **Embodied AI: Recent Advances and Future Directions** | [2311.11267](https://arxiv.org/abs/2311.11267) | 2023 | `Embodied_AI_Survey_Recent_Advances.pdf` |
| **SayPlan: Grounding Large Language Models using 3D Scene Graphs for Scalable Robot Task Planning** | [2309.11489](https://arxiv.org/abs/2309.11489) | 2023 | `SayPlan_Grounding_LLMs_using_3D_Graphs.pdf` |
| **Voyager: An Open-Ended Embodied Agent with Large Language Models** | [2305.16291](https://arxiv.org/abs/2305.16291) | 2023 | `Voyager_An_Open-Ended_Embodied_Agent.pdf` |

### Resumen rápido
- Los tres surveys cubren el estado del arte de Embodied AI y VLA (ideal como punto de entrada).
- **SayPlan** conecta LLMs con grafos de escena 3D para planificación multi-habitación.
- **Voyager** (NVIDIA) usa GPT-4 para aprendizaje abierto en Minecraft — referencia clave para agentes embodied con LLM.

---

## 🔗 Enlaces complementarios (sin PDF local)

- [MuJoCo (IROS 2012)](https://mujoco.org/) — Motor de física de DeepMind.
- [PyBullet](https://pybullet.org/) — Módulo Python para simulación Bullet.
- [NVIDIA Isaac Sim](https://developer.nvidia.com/isaac-sim) — Simulación sobre Omniverse.
- [Isaac Gym](https://developer.nvidia.com/isaac-gym) — RL paralelo en GPU.
- [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3) — Implementaciones de RL.
- [Gymnasium](https://github.com/Farama-Foundation/Gymnasium) — API estándar de RL.
- [ROS 2 Jazzy Docs](https://docs.ros.org/en/jazzy/index.html)
- [Nav2](https://nav2.ros.org/) — Navegación autónoma.
- [micro-ROS](https://micro.ros.org/) — ROS 2 para microcontroladores.
- [burger_delivery](https://github.com/roncanciovl/burger_delivery) — Caso de estudio ROS 2 + gemini-robotics.

---

*Generado automáticamente. Última actualización: 2026-08-30.*