# Awesome Embodied AI & Sim2Real 🤖

A curated list of awesome resources, papers, frameworks, and projects dedicated to **Embodied Artificial Intelligence**, **Vision-Language-Action (VLA) models**, and the bridge between simulation and reality (**Sim2Real**).

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

---

## 📑 Contents
- [What is Embodied AI?](#-what-is-embodied-ai)
- [Paper Library (Local PDFs)](#-paper-library-local-pdfs)
- [Vision-Language-Action (VLA) Models](#-vision-language-action-vla-models)
- [Simulation Environments & Digital Twins](#-simulation-environments--digital-twins)
- [Sim2Real Transfer & Reinforcement Learning](#-sim2real-transfer--reinforcement-learning)
- [Robotic Frameworks (ROS 2)](#-robotic-frameworks-ros-2)
- [Featured Case Studies](#-featured-case-studies)

---

## 🧠 What is Embodied AI?
Embodied AI refers to artificial intelligence agents that interact with physical (or physically simulated) environments. Unlike pure software agents, Embodied AI must perceive its surroundings through sensors, reason about the physical world, and take physical actions to accomplish tasks.

## 📄 Paper Library (Local PDFs)

A curated collection of **45 foundational papers** (PDFs from arXiv) organized in [`papers/`](papers/PAPERS.md):

| Category | Papers | Highlights |
|----------|--------|------------|
| 🤖 VLA Models | 6 | OpenVLA, RT-1, RT-2, Octo, RT-X, π0 |
| 🏙️ Simulation Environments | 6 | Habitat, AI2-THOR, iGibson, HM3D, RoboCasa, BEHAVIOR-1K |
| 🌉 Sim2Real & RL | 7 | Domain Randomization, Teacher-Student, RMA, ANYmal |
| ⚙️ Robotics Frameworks | 2 | ROS 2 Architecture, MoveIt 2 |
| 📚 Surveys & Case Studies | 5 | Embodied AI Surveys, SayPlan, Voyager |
| 🧩 ROS 2 + IA/LLMs | 9 | SayCan, Code as Policies, ChatGPT for Robotics, VoxPoser, TidyBot |
| 🚀 Recent 2025-2026 | 10 | ROS2SmolVLA, Florence-2 ROS 2, TurboVLA, CoRAL, Edge AI LLMs |

👉 **Full index:** [papers/PAPERS.md](papers/PAPERS.md)
🔄 **Re-download/update:** `python scripts/download_papers.py`

## 🤖 Vision-Language-Action (VLA) Models
Foundation models that map visual and language inputs directly to robotic actions.

- [OpenVLA](https://github.com/openvla/openvla) - An open-source VLA model for robotic manipulation.
- [RT-X (Robotics Transformer)](https://robotics-transformer-x.github.io/) - General-purpose robotics models from Google DeepMind.
- [Octo Model](https://octo-models.github.io/) - A versatile, open-source robotics foundation model.

## 🏙️ Simulation Environments & Digital Twins
High-fidelity physical simulators required to train AI models safely before physical deployment.

- [NVIDIA Isaac Sim](https://developer.nvidia.com/isaac-sim) - A robotics simulation application built on the NVIDIA Omniverse platform.
- [MuJoCo](https://mujoco.org/) - A free and open-source physics engine developed by DeepMind, highly optimized for robotics.
- [PyBullet](https://pybullet.org/) - Easy-to-use Python module for physics simulation for robotics and machine learning.
- [Habitat (Meta)](https://aihabitat.org/) - A platform for embodied AI research in photorealistic 3D environments.

## 🌉 Sim2Real Transfer & Reinforcement Learning
Techniques to bridge the reality gap so models trained in simulation work in the real world.

- [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3) - Reliable implementations of reinforcement learning algorithms in PyTorch.
- [Isaac Gym](https://developer.nvidia.com/isaac-gym) - NVIDIA's high-performance RL environment.
- [Gymnasium](https://github.com/Farama-Foundation/Gymnasium) - The standard API for reinforcement learning, maintained by the Farama Foundation.

## ⚙️ Robotic Frameworks (ROS 2)
The standard middleware for building scalable robotic applications.

- [ROS 2 (Robot Operating System)](https://docs.ros.org/en/jazzy/index.html) - The standard for writing robot software (Jazzy Jalisco).
- [MoveIt 2](https://moveit.ros.org/) - The leading framework for robotic manipulation and motion planning.
- [Nav2](https://nav2.ros.org/) - The professional standard for autonomous mobile robot navigation.
- [micro-ROS](https://micro.ros.org/) - ROS 2 for microcontrollers and Edge AI.

## 📚 Featured Case Studies

- **[burger_delivery](https://github.com/roncanciovl/burger_delivery)**: An advanced collaborative robotics environment in ROS 2 Jazzy. Features spatial localization (AprilTags), MoveIt 2 integration for Kinova Gen3, and semantic scene processing using models like **gemini-robotics** and Edge-AI. An excellent reference for bridging classic ROS 2 architecture with modern AI semantics.

---

### Contributing
Contributions are very welcome! If you know of an awesome framework, paper, or project that belongs here, please read the [contribution guidelines](CONTRIBUTING.md) (coming soon) and open a Pull Request.

---
*Curated by [Roncanciovl](https://github.com/roncanciovl).*
