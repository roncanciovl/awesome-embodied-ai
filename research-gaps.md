# 🔍 Research Gaps — Embodied AI & Sim2Real

**Cutoff date:** 2026-08-30
**Based on:** 41 papers analyzed (see [`papers.csv`](papers.csv))
**Protocol:** [`research-protocol.md`](research-protocol.md)

---

## 📌 Executive Summary

The analysis of the collection reveals **four research sublines** with significant gaps. Each represents an opportunity for original contributions, especially in the context of integration with **ROS 2** as a production framework.

---

## 1️⃣ Multimodal Perception and Grounding

### Current state
- VLMs (Florence-2, GPT-4V, Gemini) achieve semantic understanding of scenes, but their integration as **native ROS 2 nodes** is incipient (only `ROS2_Wrapper_Florence-2_2026`).
- Spatial grounding (mapping "the red cup" → 3D coordinates) relies on fragmented pipelines: VLM + detector + pose estimator.
- Papers such as VoxPoser and SayCan use multimodal perception, but with proprietary architectures without a clear path to ROS 2.

### Identified gaps
| Gap | Evidence | Opportunity |
|-----|----------|-------------|
| **Lack of a ROS 2 standard for VLMs** | Only 1 paper (2604.01179) provides a ROS 2 wrapper | Create `ros2_vlm_msgs` with standard interfaces |
| **Real-time 3D grounding** | VoxPoser requires an external VLM; latency >500 ms | Quantized VLM + 3D projection in <100 ms |
| **Multimodal sensor fusion** | Papers treat camera/LiDAR/tactile separately | Early-fusion ROS 2 node VLM+depth+tactile |
| **Semantic calibration** | No papers on VLM-robot calibration | Metric-semantic grounding benchmark |

### Key reference papers
- `2604.01179` (ROS 2 Wrapper Florence-2)
- `2307.05973` (VoxPoser)
- `2204.01691` (SayCan)

---

## 2️⃣ Semantic Planning and Robotic Agents

### Current state
- LLMs as high-level planners (SayCan, Code as Policies, SayPlan, LLM+P) demonstrate task decomposition capability.
- Low-level execution remains classical (MoveIt 2, PID controllers) — the semantic→action bridge is the bottleneck.
- VLAs (OpenVLA, π0) promise to unify planning and control, but their latency (>50 ms) limits reactive use.

### Identified gaps
| Gap | Evidence | Opportunity |
|-----|----------|-------------|
| **Standardized LLM→ROS 2 bridge** | Code as Policies generates ad-hoc code | Framework of ROS 2 "skill primitives" callable by LLMs |
| **Failure recovery** | Only FLARE (2608.26645, not included) addresses failures | ROS 2 agent with self-diagnosis and re-planning |
| **Robotic episodic memory** | Inner Monologue uses manual feedback | Persistent ROS 2 memory graph across sessions |
| **Multi-robot semantic** | MA-VLA (2608.25864) is recent | LLM orchestration of heterogeneous ROS 2 fleets |

### Key reference papers
- `2209.07753` (Code as Policies)
- `2309.11489` (SayPlan)
- `2304.11477` (LLM+P)
- `2606.09416` (Harness Engineering)

---

## 3️⃣ Local Inference and Edge AI

### Current state
- Most VLAs require datacenter GPUs (A100, TPU) — incompatible with autonomous mobile robots.
- 2025-2026 papers (TurboVLA, LiteVLA-Edge, Quantized LLMs, ROS2SmolVLA) attack the problem, but as isolated solutions.
- There is no standard **latency/accuracy/power** benchmark for VLAs on embedded hardware (Jetson, Raspberry Pi, NPU).

### Identified gaps
| Gap | Evidence | Opportunity |
|-----|----------|-------------|
| **Edge-VLA benchmark** | Each paper uses its own hardware/metric | ROS 2 + Jetson Orin benchmark with unified metrics |
| **Lossless robotic quantization** | LiteVLA-Edge quantizes but loses accuracy | QAT (Quantization-Aware Training) techniques specific to actions |
| **Asynchronous ROS 2 inference** | FlashVLA (2608.27384) proposes streaming | ROS 2 node with async VLA pipeline + executor |
| **NPU/FPGA for VLA** | No papers on robotic NPU | Port SmolVLA to NPU (Hailo, Coral, Jetson) |

## 4️⃣ Sim2Real, Safety and Reproducible Evaluation

### Current state
- Domain Randomization (2017) is still the dominant technique; few methodological improvements in 8 years.
- Locomotion papers (RMA, ANYmal) have robust Sim2Real, but **contact-rich manipulation** still fails.
- There are no safety protocols for deploying VLA policies on collaborative robots (ISO/TS 15066).
- Evaluation is irreproducible: each paper uses its own setup, without shared benchmarks.

### Identified gaps
| Gap | Evidence | Opportunity |
|-----|----------|-------------|
| **Sim2Real for soft manipulation** | Only 1910.07113 (OpenAI) addresses dexterous | Sim2Real with tactile sensors + VLA |
| **Policy certification** | 2608.21572 (not included) proposes certificates | Pre-deployment verification framework for ROS 2 |
| **VLA safety in cobots** | No papers on ISO/TS 15066 + VLA | ROS 2 safety layer that validates VLA actions |
| **Reproducible benchmark** | RoboCasa is sim-only; no real | Dual sim+real benchmark with ROS 2 + AprilTags |
| **Standardized success metrics** | Each paper defines "success" differently | Metric taxonomy (task success, safety, latency, energy) |

### Key reference papers
- `1703.06907` (Domain Randomization)
- `2107.04034` (RMA)
- `1910.07113` (Dexterous Manipulation)
- `2406.02523` (RoboCasa)

---

## 🎯 Opportunity Matrix

| Sublines | Impact | Feasibility with ROS 2 | Priority |
|----------|--------|------------------------|----------|
| Multimodal perception | High | High (existing wrappers) | 🥇 |
| Semantic planning | High | Medium (requires skill design) | 🥈 |
| Edge AI / local inference | Very high | High (ROS2SmolVLA as base) | 🥇 |
| Sim2Real + safety | Critical | Medium (requires hardware) | 🥉 |

---

## 🔬 Experimental Proposal: `burger_delivery` as a Testbed

The [burger_delivery](https://github.com/roncanciovl/burger_delivery) project (ROS 2 Jazzy + Kinova Gen3 + AprilTags + gemini-robotics) is ideal to validate these gaps:

| Experiment | Architecture | Metric |
|------------|--------------|--------|
| **Classical baseline** | AprilTags + MoveIt 2 + FSM | Task success rate, latency |
| **Cloud VLM** | gemini-robotics API + MoveIt 2 | Latency, cost, robustness |
| **Quantized local VLA** | SmolVLA/Florence-2 ROS 2 + MoveIt 2 | Latency, accuracy, power |

**Hypothesis:** The quantized local alternative will reach ≥80% of the cloud solution's success rate with <50% of its latency.

---

## 📎 Cross references

- Full metadata: [`papers.csv`](papers.csv)
- Research protocol: [`research-protocol.md`](research-protocol.md)
- Narrative index: [`papers/PAPERS.md`](papers/PAPERS.md)

---

*Living document — update with every revision of the collection.*