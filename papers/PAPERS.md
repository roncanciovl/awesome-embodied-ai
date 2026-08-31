# 📄 Paper Library — Awesome Embodied AI & Sim2Real

Local collection of foundational papers from [arXiv](https://arxiv.org).
To re-download or update, run:

```bash
python scripts/download_papers.py
```

> **Note:** All PDFs come from arXiv. Check each paper's license before redistributing. PDFs are intentionally **not versioned in git** (see `.gitignore`); `papers.csv` and this index are the canonical metadata and link sources.

---

## 📁 Structure

```
papers/
├── 01_VLA_Models/              # Vision-Language-Action Models
├── 02_Simulation_Environments/ # Simulators and 3D environments
├── 03_Sim2Real_RL/             # Sim2Real transfer and RL
├── 04_Robotics_Frameworks/     # ROS 2 and manipulation frameworks
├── 05_Surveys_Case_Studies/    # Surveys and embodied agents
├── 06_ROS2_AI_LLMs/            # ROS 2 + AI/LLMs for robotics
└── 07_Recent_2025_2026/        # Recent ROS 2 + LLM papers (2025-2026)
```

---

## 🤖 01 — Vision-Language-Action (VLA) Models

| Paper | arXiv | Year | File |
|-------|-------|------|------|
| **OpenVLA: An Open-Source Vision-Language-Action Model** | [2406.09246](https://arxiv.org/abs/2406.09246) | 2024 | `OpenVLA_An_Open-Source_Vision-Language-Action_Model.pdf` |
| **RT-1: Robotics Transformer for Real-World Control at Scale** | [2212.06817](https://arxiv.org/abs/2212.06817) | 2022 | `RT-1_Robotics_Transformer_for_Real-World_Control_at_Scale.pdf` |
| **RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control** | [2307.15818](https://arxiv.org/abs/2307.15818) | 2023 | `RT-2_Vision-Language-Action_Models_Transfer_Web_Knowledge.pdf` |
| **Octo: An Open-Source Generalist Robot Policy** | [2405.12213](https://arxiv.org/abs/2405.12213) | 2024 | `Octo_An_Open-Source_Generalist_Robot_Policy.pdf` |
| **Open X-Embodiment: Robotic Learning Datasets and RT-X Models** | [2310.08864](https://arxiv.org/abs/2310.08864) | 2023 | `Open_X-Embodiment_Robotic_Learning_Datasets_and_RTX_Models.pdf` |
| **π0: A Vision-Language-Action Flow Model for General Robot Control** | [2410.24164](https://arxiv.org/abs/2410.24164) | 2024 | `pi0_Vision-Language-Action_Flow_Models.pdf` |

### Quick summary
- **RT-1** was Google's first Transformer for real-world robotic control at scale (130k demonstrations, 700+ tasks).
- **RT-2** showed that web knowledge (VLMs) transfers directly to robotic actions.
- **Open X-Embodiment / RT-X** unified datasets from 22 different robots to train generalist policies.
- **OpenVLA** is the open-source 7B-parameter alternative built on Llama 2 + SigLIP.
- **Octo** offers an open-source generalist policy trained on 800k trajectories.
- **π0** (Physical Intelligence) introduces flow matching for high-frequency continuous actions.

---

## 🏙️ 02 — Simulation Environments & Digital Twins

| Paper | arXiv | Year | File |
|-------|-------|------|------|
| **Habitat: A Platform for Embodied AI Research** | [1904.01201](https://arxiv.org/abs/1904.01201) | 2019 | `Habitat_A_Platform_for_Embodied_AI_Research.pdf` |
| **AI2-THOR: An Interactive 3D Environment for Visual AI** | [1712.05474](https://arxiv.org/abs/1712.05474) | 2017 | `AI2-THOR_An_Interactive_3D_Environment_for_Visual_AI.pdf` |
| **iGibson: A Simulation Environment for Interactive Tasks in Large Realistic Scenes** | [2008.11765](https://arxiv.org/abs/2008.11765) | 2020 | `iGibson_A_Simulation_Environment_for_Interactive_Tasks.pdf` |
| **Habitat-Matterport 3D Dataset (HM3D): 1,000 Large-scale 3D Environments for Embodied AI** | [2109.08238](https://arxiv.org/abs/2109.08238) | 2021 | `Habitat-Matterport_3D_Dataset.pdf` |
| **RoboCasa: Large-Scale Simulation of Everyday Tasks for Generalist Robots** | [2406.02523](https://arxiv.org/abs/2406.02523) | 2024 | `RoboCasa_Large-Scale_Simulation_of_Everyday_Tasks.pdf` |

### Quick summary
- **Habitat** (Meta) is the standard for embodied navigation in scanned 3D scenes.
- **AI2-THOR** (Allen Institute) adds physical interactivity (opening doors, moving objects).
- **iGibson** (Stanford) focuses on realistic household tasks with complex physics.
- **HM3D** provides 1,000 real scanned 3D scenes for training agents.
- **RoboCasa** (UT Austin/NVIDIA) procedurally generates 100+ kitchens for manipulation.

---

| Paper | arXiv | Year | File |
|-------|-------|------|------|
| **Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World** | [1703.06907](https://arxiv.org/abs/1703.06907) | 2017 | `Domain_Randomization_for_Transferring_DNNs_from_Simulation.pdf` |
| **Sim-to-Real Transfer of Robotic Control with Dynamics Randomization** | [1710.06537](https://arxiv.org/abs/1710.06537) | 2017 | `Sim-to-Real_Transfer_of_Robotic_Control_with_Dynamics_Randomization.pdf` |
| **Learning Quadrupedal Locomotion over Challenging Terrain** | [1910.11100](https://arxiv.org/abs/1910.11100) | 2019 | `Learning_Quadrupedal_Locomotion_over_Challenging_Terrain.pdf` |
| **Sim-to-Real Transfer for Dexterous Manipulation** | [1910.07113](https://arxiv.org/abs/1910.07113) | 2019 | `Sim-to-Real_Transfer_for_Dexterous_Manipulation.pdf` |
| **Learning Agile and Dynamic Motor Skills for Legged Robots** | [1901.08652](https://arxiv.org/abs/1901.08652) | 2019 | `Learning_Agile_and_Dynamic_Motor_Skills_for_Legged_Robots.pdf` |
| **Rapid Motor Adaptation for Legged Robots (Teacher-Student)** | [2009.03317](https://arxiv.org/abs/2009.03317) | 2020 | `Teacher-Student_Framework_for_Sim-to-Real_Locomotion.pdf` |
| **RMA: Rapid Motor Adaptation for Legged Robots** | [2107.04034](https://arxiv.org/abs/2107.04034) | 2021 | `RMA_Rapid_Motor_Adaptation_for_Legged_Robots.pdf` |

### Quick summary
- **Domain Randomization** (Tobin et al., OpenAI) is the foundational technique: randomize textures/physics in simulation so the model becomes robust in the real world.
- **Dynamics Randomization** (Peng et al.) extends the idea to the space of dynamic parameters.
- **ANYmal / ETH papers** established the learned quadruped locomotion paradigm.
- **Teacher-Student / RMA** introduced online adaptation via privileged-information distillation.

---

## ⚙️ 04 — Robotic Frameworks (ROS 2)

| Paper | arXiv | Year | File |
|-------|-------|------|------|
| **ROS 2: Architecture and Performance** | [2202.01734](https://arxiv.org/abs/2202.01734) | 2022 | `ROS2_Architecture_and_Performance.pdf` |
| **MoveIt 2: Real-Time Motion Planning and Manipulation** | [2405.13268](https://arxiv.org/abs/2405.13268) | 2024 | `MoveIt2_and_Real-Time_Manipulation.pdf` |

## 📚 05 — Surveys & Case Studies

| Paper | arXiv | Year | File |
|-------|-------|------|------|
| **A Survey of Embodied AI: From Sim-to-Real and Beyond** | [2407.01738](https://arxiv.org/abs/2407.01738) | 2024 | `A_Survey_of_Embodied_AI_From_Sim-to-Real.pdf` |
| **Vision-Language-Action Models for Robotics: A Survey** | [2411.13548](https://arxiv.org/abs/2411.13548) | 2024 | `Vision-Language-Action_Models_Survey.pdf` |
| **Embodied AI: Recent Advances and Future Directions** | [2311.11267](https://arxiv.org/abs/2311.11267) | 2023 | `Embodied_AI_Survey_Recent_Advances.pdf` |
| **SayPlan: Grounding Large Language Models using 3D Scene Graphs for Scalable Robot Task Planning** | [2309.11489](https://arxiv.org/abs/2309.11489) | 2023 | `SayPlan_Grounding_LLMs_using_3D_Graphs.pdf` |

### Quick summary
- The three surveys cover the state of the art in Embodied AI and VLA (ideal entry point).
- **SayPlan** connects LLMs with 3D scene graphs for multi-room planning.

---

## 🧩 06 — ROS 2 + AI/LLMs for Robotics

| Paper | arXiv | Year | File |
|-------|-------|------|------|
| **SayCan: Do As I Can, Not As I Say: Grounding Language in Robotic Affordances** | [2204.01691](https://arxiv.org/abs/2204.01691) | 2022 | `SayCan_Grounding_Language_in_Robotic_Affordances.pdf` |
| **Code as Policies: Language Model Programs for Robots** | [2209.07753](https://arxiv.org/abs/2209.07753) | 2022 | `Code_as_Policies_Language_Model_Programs_for_Robots.pdf` |
| **Inner Monologue: Embodied Reasoning through Planning with Language Models** | [2207.05608](https://arxiv.org/abs/2207.05608) | 2022 | `Inner_Monologue_Embodied_Reasoning_with_Language_Models.pdf` |
| **VoxPoser: Composable 3D Value Maps for Robotic Manipulation with Language Models** | [2307.05973](https://arxiv.org/abs/2307.05973) | 2023 | `VoxPoser_Composable_3D_Value_Maps_with_Language_Models.pdf` |
| **ChatGPT for Robotics: Design Principles and Model Abilities** | [2306.17582](https://arxiv.org/abs/2306.17582) | 2023 | `ChatGPT_for_Robotics_Design_Principles_and_Model_Abilities.pdf` |
| **TidyBot: Personalized Robot Assistance with Large Language Models** | [2305.05706](https://arxiv.org/abs/2305.05706) | 2023 | `TidyBot_Personalized_Robot_Assistance_with_LLMs.pdf` |
| **LLM+P: Empowering Large Language Models with Optimal Planning Proficiency** | [2304.11477](https://arxiv.org/abs/2304.11477) | 2023 | `LLM+P_Empowering_LLMs_with_Optimal_Planning.pdf` |

### Quick summary
- **SayCan** (Google) was the pioneer: combines LLMs with affordance value functions for real robot task planning.
- **Code as Policies** shows that LLMs can directly generate robot policy code (including examples with ROS APIs).
- **ChatGPT for Robotics** (Microsoft) provides design principles for integrating LLMs into robotic systems, with practical ROS examples.
- **Inner Monologue** adds success/failure feedback from the environment to LLM reasoning.
- **VoxPoser** uses LLMs + VLMs to compose 3D value maps for manipulation without additional training.
- **TidyBot** shows a real use case: personalized service robots with LLMs.
- **LLM+P** combines LLMs with classical planners (PDDL) for optimal planning.

### ROS 2 connection
These papers represent the emerging paradigm where **ROS 2 acts as the execution layer** while LLMs handle high-level reasoning:
- LLMs generate ROS 2 code (nodes, services, actions) or call high-level APIs.
- ROS 2 provides the communication infrastructure (DDS), perception (sensors) and actuation (controllers).
---

## 🚀 07 — Recent ROS 2 + LLM Papers (2025-2026)

| Paper | arXiv | Year | File |
|-------|-------|------|------|
| **ROS2SmolVLA: Enabling Small Vision-Language-Action Models for Integration into Industrial-Grade Lightweight ROS 2 Systems** | [2608.23320](https://arxiv.org/abs/2608.23320) | 2026 | `ROS2SmolVLA_Small_VLA_for_ROS2_Industrial_2026.pdf` |
| **A ROS 2 Wrapper for Florence-2: Multi-Mode Local Vision-Language Inference for Robotic Systems** | [2604.01179](https://arxiv.org/abs/2604.01179) | 2026 | `ROS2_Wrapper_Florence-2_Local_VLM_2026.pdf` |
| **A Conversational Framework for Human-Robot Collaborative Manipulation with Distributed Generative AI** | [2606.06061](https://arxiv.org/abs/2606.06061) | 2026 | `Conversational_Framework_HRI_Manipulation_GenAI_2026.pdf` |
| **Integrating Quantized LLMs into Robotics Systems as Edge AI** | [2506.09581](https://arxiv.org/abs/2506.09581) | 2025 | `Quantized_LLMs_Edge_AI_Robotics_2025.pdf` |
| **Harness Engineering for Physical AI: Robot Middleware Is the Harness Layer** | [2606.09416](https://arxiv.org/abs/2606.09416) | 2026 | `Harness_Engineering_Physical_AI_Middleware_2026.pdf` |
| **TurboVLA: Real-Time Vision-Language-Action Model at 32 Hz on an RTX 4090 with <1 GB VRAM** | [2607.27205](https://arxiv.org/abs/2607.27205) | 2026 | `TurboVLA_Real-Time_VLA_32Hz_2026.pdf` |
| **CoRAL: Contact-Rich Adaptive LLM-based Control for Robotic Manipulation** | [2605.02600](https://arxiv.org/abs/2605.02600) | 2026 | `CoRAL_Contact-Rich_LLM_Control_Manipulation_2026.pdf` |
| **A Semantic Autonomy Framework for VLM-Integrated Indoor Mobile Robots** | [2605.02525](https://arxiv.org/abs/2605.02525) | 2026 | `Semantic_Autonomy_VLM_Indoor_Mobile_Robots_2026.pdf` |
| **Towards Embodied Agentic AI: Review and Classification of LLM- and VLM-Driven Robot Autonomy** | [2508.05294](https://arxiv.org/abs/2508.05294) | 2025 | `Embodied_Agentic_AI_Survey_LLM_VLM_Robot_2025.pdf` |
| **LiteVLA-Edge: Quantized On-Device Multimodal Control for Embedded Robotics** | [2603.03380](https://arxiv.org/abs/2603.03380) | 2026 | `LiteVLA-Edge_Quantized_On-Device_Control_2026.pdf` |

### Quick summary
- **ROS2SmolVLA** ⭐ is the first paper to integrate a small VLA directly into industrial ROS 2 systems — a direct reference for the framework.
- **ROS 2 Wrapper Florence-2** ⭐ provides local VLM inference via ROS 2 nodes, without cloud dependency.
- **Quantized LLMs Edge AI** shows how to run quantized LLMs on embedded robotic hardware.
- **TurboVLA / LiteVLA-Edge** tackle efficiency: real-time VLA with limited resources.
- **CoRAL** combines LLMs with adaptive control for contact-rich manipulation.
- **Harness Engineering** positions robotic middleware (ROS 2) as the "harness" layer of physical AI.
- **Embodied Agentic AI Survey** (2025) classifies the state of the art of LLM/VLM in robot autonomy.

### Framework relevance
These papers represent the **2025-2026 frontier** of ROS 2 + AI integration:
- VLAs/VLMs running as native ROS 2 nodes.
- Edge AI and quantization for deployment on real hardware.
- Robotic middleware as the orchestration layer for AI agents.

---

## 🔗 Supplementary links (no local PDF)

- [MuJoCo (IROS 2012)](https://mujoco.org/) — DeepMind physics engine.
- [PyBullet](https://pybullet.org/) — Python module for Bullet simulation.
- [NVIDIA Isaac Sim](https://developer.nvidia.com/isaac-sim) — Simulation on Omniverse.
- [Isaac Gym](https://developer.nvidia.com/isaac-gym) — Parallel RL on GPU.
- [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3) — RL implementations.
- [Gymnasium](https://github.com/Farama-Foundation/Gymnasium) — Standard RL API.
- [ROS 2 Jazzy Docs](https://docs.ros.org/en/jazzy/index.html)
- [Nav2](https://nav2.ros.org/) — Autonomous navigation.
- [micro-ROS](https://micro.ros.org/) — ROS 2 for microcontrollers.
- [burger_delivery](https://github.com/roncanciovl/burger_delivery) — ROS 2 + gemini-robotics case study.

---

*Auto-generated. Last updated: 2026-08-30.*