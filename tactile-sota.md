# 🖐️ Tactile Sensing & Manual Dexterity — State of the Art

**Created:** 2026-09-05
**Scope:** What tactile sensing adds to the state of the art of human-hand-like (manual) dexterity in robots
**Method:** arXiv API queries + vendor documentation (PaXini) + GitHub ecosystem scan (see [Methodology](#-methodology--queries))
**Related gaps:** [`research-gaps.md`](research-gaps.md) → *Dexterous in-hand manipulation*, *Tactile-VLA on a standard framework*, *Liability & accountability for failures*

---

## 📌 Executive Summary

The paper collection (41 papers, cutoff 2026-08-30) contains **zero papers** integrating tactile sensing with VLA policies, and only one (OpenAI 2019) that transferred dexterous-hand skills to reality. Meanwhile, the 2025–2026 arXiv frontier shows a consolidating paradigm — **tactile-integrated world models and V-T-L-A policies** — and commercial triaxial tactile hardware (PaXini PX-6AX GEN3/GEN4) with community ROS 2 drivers is already shipping.

**Key claim:** touch is the only modality that observes the **hidden contact states** — force, incipient slip, contact stability — that vision and language cannot provide, and that human manual dexterity exploits by default (*"Vision and language … cannot reliably reveal hidden contact states such as force, slip, and contact stability"* — TouchWorld, `2607.07287`).

---

## 1️⃣ Why Touch Is the Missing Modality for Manual Dexterity

1. **Occlusion:** during grasping and in-hand manipulation, the fingers hide the contact zone from any camera. Tactile is the only sensor that observes the contact patch directly.
2. **The physics of dexterity is tactile:** grip-force regulation, friction-cone estimation, slip onset, deformation of soft objects — all are contact quantities.
3. **Bandwidth:** contact events (slip, impact) evolve in milliseconds; vision runs at ~30 Hz while tactile arrays output at up to 1 kHz — the right sensor for the fast loop.

The human mechanism is documented in robotics terms: humans detect *incipient slip* through tactile receptors and automatically regulate grip force ("grip no harder than necessary") — replicated artificially only with triaxial tactile sensing (`2503.15447`).

---

## 2️⃣ What Tactile Adds to the State of the Art (7 Contributions)

| # | Contribution | Evidence (2025–2026) | Key result |
|---|---|---|---|
| 1 | **VLA → V-T-L-A** (tactile as a first-class policy modality) | TouchWorld `2607.07287`; Motus2 `2608.30237`; TacForcing `2608.25798` | 65.0% success on 6 contact-rich dexterous tasks, +15.7 pp over best baseline (TouchWorld) |
| 2 | **Grip-force regulation via slip detection** (the core human mechanism) | PP-Tac `2504.16649` | Real-time slip detection + online friction control on a dexterous hand |
| 3 | **Hierarchical control: slow semantics + fast contact loop** | TouchWorld `2607.07287`; TacForcing `2608.25798` | Tactile world-model + high-frequency residual refinement attacks the VLA latency bottleneck (>50 ms) |
| 4 | **Deformable & fragile objects** (infeasible without touch) | PP-Tac `2504.16649` | First grasping of paper-like deformables with a tactile dexterous hand: **87.5%** success |
| 5 | **Full-hand tactile representations & data scaling** | HT-Bench/HandTouch `2606.19161` | 10M RGB + 7.8M tactile frames, 226 tasks; vision→tactile synthesis |
| 6 | **Sim2Real of contact** (closes the 2019 OpenAI gap) | Tactile Genesis `2606.22332`; TouchWorld `2607.07287` | 20,000 parallel tactile sims on one GPU; real transfer to a multi-finger hand (XHand) |
| 7 | **Safety, liability & security of the contact channel** | GhostTac `2608.20817` (ACM CCS 2026) | Tactile = audit evidence for ISO/TS 15066, but also a new attack surface |

### Design guidance from `2606.22332` (Tactile Genesis ablations)

- **Sensor placement dominates sensor type:** whole-hand coverage (palm + proximal phalanges) beats fingertip-only by a wide margin.
- **Resolution matters less than coverage:** ~200 taxels across the whole hand suffice across tasks.
- **Force/torque per taxel is the most useful sensor type** — exactly the design philosophy of commercial triaxial arrays (§3).

## 3️⃣ Hardware State of the Art: PaXini PX-6AX GEN3/GEN4

> Vendor specs ("Data from PaXini Lab"), consulted 2026-09-05 — **not independently peer-reviewed**. No pricing is published on the product pages.

| Parameter | PX-6AX GEN3 ([product page](https://www.paxini.com/us/ax/gen3)) | PX-6AX GEN4 ([product page](https://www.paxini.com/us/ax/gen4)) |
|---|---|---|
| Output | Triaxial force array (**up to 717 signals**) + 3D resultant force + 3D torque at any point | 6D native tactile sensing chip ("GEN4 FUSE") |
| Sampling / output | 1 MHz / up to **1 kHz** | 1 MHz / 1 kHz (microsecond-level acquisition) |
| Min. detectable force | 0.01 N | **0.005 N** |
| Force range | 0–25 N normal, ±10 N tangential | Same; customizable to 300 N+ |
| Spatial resolution | 0.1 mm | **30 taxels/cm²**; modules as thin as 2 mm |
| Repeatability | <0.5% FS | <0.5% FS |
| Robustness | IP68, >10M cycles, 200%/300% overload, chip-level stray-field immunity | Same + "Magnetic Armour™" |
| Form factors | 12 models: fingertip, finger pad, palm (Elite/Core/Omega series) | + electronic-skin tiles (10×10×3 mm), **gripper sensors (28×24×6 mm)**, U-shaped fingertip-pad |
| Integration | 3–5 V, external compute | Sensing + compute + communication integrated (no external compute); GEN3-compatible |

**Ecosystem:** DexH13 tactile dexterous hand · TORA-ONE / TORA-DOUBLE ONE humanoids · OmniSharing DB (omnimodal embodied-AI dataset) · PXCap III / PXDex III / PXCap Pro (teleoperation capture — the industrial path to full-hand tactile demonstrations).

### Context: sensor families

Vision-based sensors (GelSight, DIGIT — high-resolution contact images) and triaxial-array sensors (per-taxel F/T — PaXini, IIT uSkin) trade spatial detail against calibrated force vectors. The 2026 evidence (`2606.22332`) favors **per-taxel F/T with whole-hand coverage** for policy learning.

---

## 4️⃣ Software Ecosystem (GitHub Scan, 2026-09-05)

Query: `api.github.com/search/repositories?q=paxini` → **24 repos**; official org `px-DataCollection` → **1 repo**. Fragmented and community-driven; no standard interface.

| Layer | Repos |
|---|---|
| Official | `px-DataCollection/px_omnisharing_dataprocess_kit` ("Paxini's first open source project", Shell, 30 ⭐) |
| ROS 2 drivers | `THU-DA-Robotics/paxini_ros2` · `adnan-saood/paxini_ros2` (GEN3 array) · `junwenguiqi/ros2-paxini-tashan-tactile` (real-time tactile frames) · `CRAZY0921/AmazingHand_ROS2` (hand control + Paxini tactile) |
| SDKs | `Jingyi-Z/paxini-sdk` (cross-platform Python, MIT, PX-6AX GEN3) + ~8 community drivers |
| VLA / V-T-L-A stacks | `jhyeong687/VTLA` (Vision–Tactile–Language–Action, SO-101 + π0.5) · `ldh-at/paxini_vla` |
| Data collection | `Mr-Chen2003/bimanual_vr_tactile_data_collection` (PICO 4 Pro bimanual VR + CP-M3025 sensors) · `liesliy/tlabel` (sensor-agnostic tactile annotation toolkit) |

**Takeaway:** the hardware SOTA is commercial; the software SOTA is grassroots. No peer-reviewed, standardized ROS 2 tactile interface for VLAs exists — see gap *Tactile-VLA on a standard framework* in [`research-gaps.md`](research-gaps.md).

## 5️⃣ Spec → Capability Mapping

| PaXini spec | Dexterity capability enabled | Evidence |
|---|---|---|
| Triaxial array, ±10 N tangential | Incipient-slip detection → grip-force regulation | `2503.15447`, `2504.16649` |
| 1 kHz output | Fast reactive loop + residual refinement on top of a slow VLA | `2607.07287`, `2608.25798` |
| 0.005–0.01 N min. force | Fragile/deformable objects (paper, food) | `2504.16649` |
| 3D torque at any point | In-hand reorientation; extrinsic contact estimation | `2606.22251` |
| Fingertip→pad→palm coverage + skin tiles | Whole-hand tactile representations (placement > resolution) | `2606.19161`, `2606.22332` |
| Chip-level magnetic immunity | Mitigation of GhostTac-class EMI attacks | `2608.20817` |
| F/T per taxel (triaxial design) | The most policy-useful tactile abstraction (ablation result) | `2606.22332` |

---

## 6️⃣ Open Problems (→ [`research-gaps.md`](research-gaps.md))

1. **No standardized ROS 2 tactile interface** — 24 fragmented repos, zero standard messages → opportunity: `ros2_tactile_msgs`.
2. **Tactile sim-to-real fidelity** — GPU-parallel tactile simulation exists (`2606.22332`) but triaxial-array noise/drift realism is still young.
3. **No peer-reviewed commercial-array × VLA integration** — the 41-paper collection contains zero such papers.
4. **Reproducibility** — every paper uses a different sensor; a metric taxonomy is needed (task success, slip rate, grip-force margin, safety).
5. **Security of the tactile channel** — contactless EMI spoofing can induce excessive force (`2608.20817`) → audit trail + certification.
6. **Full-hand demonstration data** — HT-Bench direction; teleoperation capture rigs (PXCap, VR bimanual) are the scaling path.

---

## 7️⃣ Implications for the `burger_delivery` Testbed

The testbed (ROS 2 Jazzy + Kinova Gen3 + AprilTags + gemini-robotics) uses a parallel gripper — the GEN4 gripper sensors (28×24×6 mm) mount directly on such jaws:

| Experiment | Architecture | Metric |
|---|---|---|
| Tactile-gated grasp (classical) | AprilTags + MoveIt 2 + FSM + GEN4-GR slip detection | Failed-grasp rate ↓ |
| Tactile-conditioned VLA | GEN4-GR → `ros2_tactile_msgs` → SmolVLA/π0-style policy | Task success under occlusion |
| Safety validation | Force-limited grasping vs. ISO/TS 15066 thresholds | Max contact force distribution |

**Hypothesis:** a 1 kHz tactile residual loop raises the success rate of the quantized local VLA under object occlusion and reduces failed grasps, without changing the semantic policy.

---

## 8️⃣ Safety & Liability

- **Tactile as evidence:** per-taxel force logs are the "black box" of physical interaction — quantifiable ISO/TS 15066 compliance (0.005 N resolution) and an audit trail for post-failure attribution.
- **Tactile as attack surface:** GhostTac `2608.20817` spoofs tactile readings via electromagnetic interference (no physical contact needed), inducing excessive force; demonstrated on 15 sensors and 2 dexterous hands. Chip-level magnetic immunity (GEN4) and plausibility filters in the ROS 2 safety layer are candidate mitigations.
- Both feed the *Liability & accountability for failures* gap row: certification (pre-deployment) + audit trail (runtime) + spoofing resistance (integrity).

## 9️⃣ Methodology & Queries

- **arXiv API** (consulted 2026-09-05):
  - `all:"tactile" AND all:"vision-language-action"` → 39 results (10 newest reviewed)
  - `all:"tactile sensing" AND all:"dexterous manipulation"` → 64 results
  - `all:"slip detection" AND all:"grasping"` → 29 results
  - ID verification: `all:"PP-Tac"` → `2504.16649`; `all:"tactile genesis"` → `2606.22332`
- **Vendor documentation:** paxini.com/us/ax/gen3 and paxini.com/us/ax/gen4 (specs as published; DexH13 / TORA-ONE / SPiRAL Labs pages were not publicly detailed at the consultation date).
- **GitHub:** `api.github.com/search/repositories?q=paxini` (24 repos) and `api.github.com/orgs/px-DataCollection/repos` (1 repo).
- **Limitations:** hardware specs are vendor-claimed and not independently peer-reviewed; community repositories were catalogued but not quality-audited; all arXiv IDs cited here were verified against the arXiv API.

---

## 📚 References (all verified on arXiv, 2026-09-05)

1. **TouchWorld: A Predictive and Reactive Tactile Foundation Model for Dexterous Manipulation** — [2607.07287](https://arxiv.org/abs/2607.07287) (2026)
2. **TacForcing: Streaming Action Generation with Execution-Time Tactile Feedback** — [2608.25798](https://arxiv.org/abs/2608.25798) (2026)
3. **Sensing Which Modality Matters: Evidence-Gated Regularization for Robust VLA Policies** — [2609.03142](https://arxiv.org/abs/2609.03142) (2026)
4. **Motus2: A Self-Evolving General World Model for Dexterous Manipulation** — [2608.30237](https://arxiv.org/abs/2608.30237) (2026)
5. **HT-Bench: Benchmarking and Learning Dexterous Full-Hand Tactile Representations with Egocentric Vision** — [2606.19161](https://arxiv.org/abs/2606.19161) (2026)
6. **Tactile Genesis: Exploring Tactile Sensors at Scale for Learning Dexterous Tasks** — [2606.22332](https://arxiv.org/abs/2606.22332) (2026) · [project page](https://neuroagents-lab.github.io/tactile-genesis/)
7. **PP-Tac: Paper Picking Using Tactile Feedback in Dexterous Robotic Hands** — [2504.16649](https://arxiv.org/abs/2504.16649) (RSS 2025) · [project page](https://peilin-666.github.io/projects/PP-Tac/)
8. **GhostTac: Manipulating Tactile Sensors without Physical Contact** — [2608.20817](https://arxiv.org/abs/2608.20817) (ACM CCS 2026)
9. **Geometric Reconstruction of Extrinsic Contact Trajectories using Tactile Sensing and Proprioception for Tool Manipulation** — [2606.22251](https://arxiv.org/abs/2606.22251) (2026)
10. **Friction-Scaled Vibrotactile Feedback for Real-Time Slip Detection in Manipulation using Robotic Sixth Finger** — [2503.15447](https://arxiv.org/abs/2503.15447) (2025)

---

## 🔗 Cross references

- Gaps: [`research-gaps.md`](research-gaps.md)
- Protocol: [`research-protocol.md`](research-protocol.md)
- Metadata: [`papers.csv`](papers.csv)
- Paper index: [`papers/PAPERS.md`](papers/PAPERS.md)
- Glossary: [`GLOSSARY.md`](GLOSSARY.md)

---

*Created: 2026-09-05. Living document — update with every revision of the collection.*



