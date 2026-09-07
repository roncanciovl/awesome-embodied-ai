# 🔍 Research Gaps — Embodied AI & Sim2Real

**Cutoff date:** 2026-08-30
**Based on:** 54 papers analyzed (see [`papers.csv`](papers.csv))
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
| **Failure recovery** | Detection now covered on both origins — reasoning (SAFE 2506.09937, UQ-VLA 2606.18043) and captured data (ELLIPSE 2603.04585, SAGE 2608.29772); recovery only FLARE (2608.26645, not included) | ROS 2 agent with self-diagnosis and re-planning on top of the new detectors |
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
- Human-hand dexterity remains unsolved in the collection: only one paper (1910.07113, OpenAI, 2019) transfers dexterous hands to reality; no papers cover in-hand manipulation, tactile skins, or deformable objects.
- Commercial triaxial tactile hardware now exists (e.g., PaXini PX-6AX GEN3/GEN4: 1 kHz output, 0.005 N resolution, up to 30 taxels/cm²) with community ROS 2 drivers, but there is no peer-reviewed, standardized tactile-VLA integration.
- There are no safety protocols for deploying VLA policies on collaborative robots (ISO/TS 15066), and no paper assigns liability or accountability when a deployed policy fails.
- Evaluation is irreproducible: each paper uses its own setup, without shared benchmarks.

### Identified gaps
| Gap | Evidence | Opportunity |
|-----|----------|-------------|
| **Sim2Real for soft manipulation** | Only 1910.07113 (OpenAI) addresses dexterous | Sim2Real with tactile sensors + VLA |
| **Dexterous in-hand manipulation** | Only 1910.07113 (2019); CoRAL (2605.02600) admits contact-rich "remains challenging"; zero papers on in-hand manipulation, deformable objects or tool use | Multi-finger VLA policies driven by distributed fingertip tactile arrays |
| **Tactile-VLA on a standard framework** | Hardware SOTA is commercial, not academic (PaXini PX-6AX GEN3/GEN4 triaxial arrays) and community ROS 2 drivers exist (e.g., `THU-DA-Robotics/paxini_ros2`), but no standardized ROS 2 tactile interface for VLAs | `ros2_tactile_msgs` standard + tactile-VLA node validated on the Kinova Gen3 gripper |
| **Policy certification** | 2608.21572 (not included) proposes certificates | Pre-deployment verification framework for ROS 2 |
| **Liability & accountability for failures** | 0 papers address who is responsible when a deployed VLA fails (dropped/broken objects, injury); certification (2608.21572) is pre-deployment only and FLARE (2608.26645) only recovery | ROS 2 audit trail ("black box" logger) + safety layer mapped to ISO 10218 / ISO/TS 15066 / EU AI Act feeding the certification loop |
| **VLA safety in cobots** | No papers on ISO/TS 15066 + VLA | ROS 2 safety layer that validates VLA actions |
| **Reproducible benchmark** | RoboCasa is sim-only; no real | Dual sim+real benchmark with ROS 2 + AprilTags |
| **Standardized success metrics** | Each paper defines "success" differently | Metric taxonomy (task success, safety, latency, energy) |

### Key reference papers
- `1703.06907` (Domain Randomization)
- `2107.04034` (RMA)
- `1910.07113` (Dexterous Manipulation)
- `2406.02523` (RoboCasa)

---

## 5️⃣ Industrial Deployment and Wire-Harness Assembly

### Current state
- Wire-harness and connector assembly remain manual in automotive, aerospace and electrical-cabinet production. The arXiv literature is recent and fragmented (cluster added 2026-09-07).
- Best reported results: connector insertion **>90%** with F/T + vision across five geometries (`2602.22100`); cable routing **78%** multimodal vs **36%** monocular on an industrial board (`2607.14021`, 48 trials per configuration).
- A systematic review from industrial engineering (`2309.13744`, *Advanced Engineering Informatics*) finds most solutions are proposed **"under simplified industrial configurations"** — demos, not lines.
- Edge deployment is validated on plant-class hardware (`2601.20262` on Jetson Orin/Thor; `2607.07403` onboard multi-agent VLMs), but always in demos or hardware-in-the-loop simulation.
- Certified safety for deformables exists only in simulation (`2505.13889`, wire-harness task with polynomial zonotopes, zero safety violations).

### Identified gaps
| Gap | Evidence | Opportunity |
|-----|----------|-------------|
| **No plant-grade benchmark** | IDB (`2607.14021`) uses purpose-built boards; no production-line integration | Benchmark on a real cell with cycle time, OEE and scrap rate as metrics |
| **Deformable Sim2Real** | Only `2203.15004` (online residual GNN) and `2505.13889` (sim-only) | Cable Sim2Real with tactile feedback + certified safety on real hardware |
| **Force-limited insertion as a standard skill** | `2602.22100` tunes force limits per connector geometry | ROS 2 compliant-insertion skill with force-envelope monitoring |
| **Certification for deformable tasks** | `2505.13889` certifies in simulation only | Pre-deployment certificates for DLO tasks wired into ROS 2 |
| **Shift-robust deployment** | SLR (`2309.13744`): simplified configurations | Domain-shift monitoring connected to ELLIPSE/SAGE-style detectors |

### Key reference papers
- `2607.14021` (Industrial Dexterity Benchmark)
- `2602.22100` (Connector Assembly)
- `2309.13744` (Wire-Harness Vision SLR)
- `2505.13889` (Certifiably Safe DLO)
- `2601.20262` (Shallow-π)
- `2203.15004` (GNN Cable Deformation)

---

## 🎯 Opportunity Matrix

| Sublines | Impact | Feasibility with ROS 2 | Priority |
|----------|--------|------------------------|----------|
| Multimodal perception | High | High (existing wrappers) | 🥇 |
| Semantic planning | High | Medium (requires skill design) | 🥈 |
| Edge AI / local inference | Very high | High (ROS2SmolVLA as base) | 🥇 |
| Sim2Real + safety | Critical | Medium (requires hardware) | 🥉 |
| Industrial deployment (wire harness) | Very high | Medium (requires a real cell) | 🥇 |

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
- Tactile & dexterity SOTA: [`tactile-sota.md`](tactile-sota.md)

---

*Living document — update with every revision of the collection.*

> **Addendum 2026-09-05:** Added gaps on human-hand dexterity, tactile-VLA integration, and liability & accountability after a state-of-the-art review of commercial tactile sensing: PaXini PX-6AX GEN3 (1 MHz sampling / 1 kHz output, 0.01 N min force, up to 717 triaxial signals, 0.1 mm spatial resolution) and GEN4 "FUSE" 6D chip (0.005 N, 30 taxels/cm², 2 mm thin, electronic-skin tiles), plus its ecosystem (DexH13 dexterous hand, TORA-ONE humanoid, OmniSharing DB). Sources: paxini.com/us/ax/gen3, paxini.com/us/ax/gen4, and GitHub `paxini` search (24 community repos incl. ROS 2 drivers, Python SDK, V-T-L-A stacks), consulted 2026-09-05. Vendor specs are lab-claimed, not independently peer-reviewed.