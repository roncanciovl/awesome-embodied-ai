# 📖 Glossary — Awesome Embodied AI & Sim2Real

Glossary of terms used in this collection and in the literature of AI applied to robotics.

---

## 🧠 Artificial Intelligence Models

### LLM — Large Language Model
A neural network trained on massive text corpora to understand and generate natural language. Examples: GPT-4, Claude, Llama 2, Gemini. In robotics they are used for **task planning** ("pick up the cup and put it in the sink" → sequence of steps) and **control code generation**.

### VLM — Vision-Language Model
A multimodal model that combines vision (images/camera) and language. It understands the content of a scene and answers questions about it. Examples: Florence-2, CLIP, GPT-4V, Gemini Vision. In robotics they are used for **semantic perception**: "where is the red object?", "what is the human doing?".

### VLA — Vision-Language-Action Model
The evolution of the VLM: in addition to perceiving and understanding, it **directly generates robotic actions** (motion coordinates, grasp commands). It is the central paradigm of this collection. Examples: OpenVLA, RT-2, π0, Octo, SmolVLA.
> 📌 **Key difference:** a VLM responds with text; a VLA responds with physical actions.

### RL — Reinforcement Learning
A paradigm where an agent learns through trial and error, receiving rewards or penalties. Basis of the locomotion papers (RMA, ANYmal) and control (Domain Randomization). Alternative to direct VLA supervision.

### IL — Imitation Learning
The agent learns by imitating human demonstrations (teleoperation, kinesthetic teaching). Main data source for training VLAs (Open X-Embodiment: 800k+ trajectories).

### PDDL — Planning Domain Definition Language
Formal language for classical AI planners. LLM+P combines it with LLMs: the LLM translates natural language → PDDL, and the planner solves it optimally.

---

## 🌉 Sim2Real (Simulation → Reality)

### Sim2Real — Sim-to-Real Transfer
The process of training a model in simulation and making it work in the physical world. Core problem: simulation is never perfect (the "reality gap").

### Reality Gap
The difference between simulation and the real world: simplified physics, ideal sensors, no noise. Main cause of failure for transferred policies.

### Domain Randomization
Foundational technique (Tobin et al., 2017): massively randomize simulator properties (textures, lighting, physics) so the model learns to be robust to variations instead of overfitting to one specific simulation.

### Dynamics Randomization
Extension: randomize dynamic parameters (mass, friction, motor stiffness) in addition to visual ones.

### Teacher-Student
Distillation paradigm: the "Teacher" is trained in simulation with privileged information (exact positions, real friction); the "Student" learns only from observations available on the real robot. Basis of RMA.

### RMA — Rapid Motor Adaptation
Architecture (Kumar et al., 2021) with two modules: an environment estimator (adaptation module) that adjusts online to unseen changes (load, terrain), and a policy that uses that estimate.

---

## 🤖 Robotics and Frameworks

### ROS — Robot Operating System
Open-source middleware for robotics. Not an "operating system" but an abstraction layer with nodes, messages, topics, services and actions.

### ROS 2
Modern version of ROS (2020+). Changes the transport from TCPROS to **DDS**, with improvements in:
- **Real-time** performance and determinism
- Configurable **QoS** (Quality of Service)
- **Security** (SROS)
- Cross-platform support (Windows, macOS, RTOS)

### DDS — Data Distribution Service
OMG standard for publish-subscribe communication used by ROS 2. Provides automatic node discovery, per-topic QoS and efficient transport without a central broker.

### Node / Topic / Service / Action (ROS 2)
- **Node:** a process that runs a function (e.g., `camera_driver`, `vla_policy`)
- **Topic:** publish-subscribe channel (e.g., `/image_raw`)
- **Service:** request-response call (e.g., `/get_pose`)
- **Action:** long-lived goal with feedback (e.g., `/move_to` with progress)

### MoveIt 2
**Motion planning** framework for ROS 2: inverse kinematics (IK), trajectory planning (OMPL, Pilz), collision management. Used to manipulate arms such as the Kinova Gen3.

### Nav2
**Autonomous navigation** framework for ROS 2: SLAM, localization (AMCL), path planning, obstacle avoidance. For mobile robots.

### ros2_control
Real-time control framework for ROS 2: hardware interfaces (motors, sensors), controllers (PID, effort, velocity).

### micro-ROS
ROS 2 for **microcontrollers** (STM32, ESP32): lets embedded devices participate in the ROS 2 network (Edge AI).

### AprilTags
QR-like visual markers for **spatial localization**: the robot detects the tag with the camera and computes its absolute pose. Used in `burger_delivery`.

### Cobot — Collaborative Robot
A robot designed to work alongside humans without safety cages (e.g., Kinova Gen3, UR5). Regulated by ISO/TS 15066.

---

## 🎯 Embodied AI Concepts

### Grounding
Connecting language symbols with the physical world: "cup" → detect cup in image + estimate 3D position. The central problem of the language→action bridge.

### Affordance
A property of an object that indicates what actions it permits: a cup "affords" being grabbed by its handle; a door "affords" opening. SayCan uses affordance value functions so LLMs propose feasible actions.

### Embodied AI
AI that perceives, reasons and **acts in a physical environment** (or physically simulated). Contrast with "desktop" AI (chatbots, image generation).

### Task Planning
Decomposing a high-level goal ("make a coffee") into executable actions ("grab jug" → "fill with water" → "pour"...).

### Skill Primitive
An atomic, reusable robot action ("pick", "place", "open"). LLMs plan by combining primitives; the controller executes them.

### HRI — Human-Robot Interaction
Interaction between humans and robots: interfaces, safety, collaboration. `Conversational_Framework_HRI` (2026) is a recent example.

### World Model
A neural network that predicts how the environment changes after actions (learned internal simulation). Basis of GenSim, RoboGen and model-based RL approaches.

---

## ⚡ Inference and Deployment

### Edge AI
Running AI models **on the device** (robot) instead of the cloud. Advantages: low latency, privacy, works offline. Challenge: limited hardware.

### Quantization
Reducing the numerical precision of a model (FP32 → INT8/INT4) to make it smaller and faster with minimal quality loss. Key for Edge AI. Examples in the collection: LiteVLA-Edge, Quantized LLMs.

### QAT — Quantization-Aware Training
Training that considers quantization from the start (vs. post-training quantization), preserving accuracy better.

### Latency
Model response time (perception → action). Critical in robotics:
- <10 ms: high-level reactive control
- 10-50 ms: standard control
- 50-200 ms: acceptable planning
- >200 ms: only non-urgent decisions

### FPS / Hz in VLA
Decision frequency of a policy. TurboVLA achieves 32 Hz (31 ms) — enough for dynamic manipulation. Most classical VLAs run at 1-10 Hz.

### VRAM
GPU memory. TurboVLA runs with <1 GB VRAM; OpenVLA (7B parameters) requires ~14 GB in FP16.

---

## 📊 Datasets and Benchmarks

### Open X-Embodiment
Collaborative dataset (2023) with data from **22 different robots** (Google, Stanford, ETH, etc.). Basis for training cross-embodiment generalist policies (RT-X).

### Benchmark
Standardized task suite to compare methods reproducibly. Examples: RoboCasa (sim), GuardianBench (safety), Arena 4.0 (ROS 2 navigation).

### Success Rate
Main metric: % of episodes where the robot completes the task. Complemented by: time to success, collisions, failed grasps.

---

## 🏢 Specific Systems

### Gemini Robotics (Google DeepMind)
**Model family with different classifications** — important not to confuse them:

| Variant | Type | Generates actions? | Use |
|----------|------|-------------------|-----|
| **Gemini Robotics** (base, 1.5) | ✅ **VLA** | Yes — controls arms (ALOHA 2) and humanoids (Apollo) | Direct robot control |
| **Gemini Robotics-ER** (*Embodied Reasoning*) | ⚠️ **VLM** with spatial reasoning | ❌ No — only perceives and reasons | Semantic perception, integration with existing controllers |
| **Gemini Robotics On-Device** (1.5) | ✅ **Quantized VLA** | Yes — locally on the robot (Jetson), no cloud | Edge AI, robots without connectivity |

> 📌 **In `burger_delivery`:** `gemini-robotics` is used for *semantic scene processing* → this is the **ER (VLM)** mode: the scene is interpreted semantically and actions are executed by MoveIt 2. It is NOT end-to-end VLA control.
>
> 📌 **Gemini Robotics On-Device** is especially relevant to the *Edge AI* subline of [`research-gaps.md`](research-gaps.md): it is the commercial analog of what ROS2SmolVLA / LiteVLA-Edge propose in research.

---

## 🏢 Mentioned Groups and Systems

| Name | What it is |
|--------|--------|
| **Google DeepMind** | Creator of RT-1, RT-2, RT-X, SayCan, MuJoCo, Gemini Robotics |
| **Physical Intelligence** | Startup creator of π0 |
| **Stanford iGibson/BEHAVIOR** | Li Fei-Fei's lab, household simulators |
| **ETH Zurich (ANYmal)** | Hutter's quadrupedal locomotion lab |
| **Kinova Gen3** | 7-DOF collaborative robotic arm |
| **NVIDIA Isaac Sim** | Omniverse-based simulator with photorealism |
| **Gazebo** | Classic ROS simulator (now gz-sim) |
| **MuJoCo** | Contact physics engine (DeepMind, open-source) |

---

## 🔗 Cross references

- Metadata: [`papers.csv`](papers.csv)
- Paper index: [`papers/PAPERS.md`](papers/PAPERS.md)
- Protocol: [`research-protocol.md`](research-protocol.md)
- Gaps: [`research-gaps.md`](research-gaps.md)

---

*Last updated: 2026-08-30. Term suggestions: open an issue with label `glossary`.*