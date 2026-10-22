# 🧠 Open-Source Embodied-Reasoning VLMs — State of the Art

**Created:** 2026-10-22
**Scope:** Open-weight / open-source alternatives to **Gemini Robotics-ER** — models that do *embodied reasoning* (spatial grounding, pointing, affordance, trajectory, progress & success detection, task planning) without emitting motor commands, and that you can download, inspect, fine-tune and self-host.
**Question answered:** *"Is there any other open-source VLM-ER?"* → **Yes: at least four dedicated families plus a general-purpose tier.** One of them (Ai2 **Molmo2-ER**) claims to beat Gemini Robotics ER-1.5 on 13 embodied-reasoning benchmarks under Apache-2.0.
**Method:** primary sources only — arXiv technical reports, official GitHub READMEs (via `gh api`), Hugging Face model cards, vendor docs. Consulted 2026-10-22. Full list in [§12](#12--references).
**Related:** [`gemini-robotics-er-guide.md`](gemini-robotics-er-guide.md) (the closed reference implementation) · [`GLOSSARY.md`](GLOSSARY.md) · [`research-gaps.md`](research-gaps.md) · [`tactile-sota.md`](tactile-sota.md)

---

## 📌 Executive Summary

Gemini Robotics-ER is **not** alone. The open ecosystem now covers every capability ER offers, and in two places it goes *further*:

| Capability (ER terms) | Best open equivalent | Verdict |
|---|---|---|
| Pointing / spatial referring | **Molmo2-ER** (Ai2), **RoboBrain 2.5** (BAAI) | ✅ open models lead on published spatial benchmarks |
| Bounding boxes / grounding | RoboBrain 2.5 `task="grounding"`, Qwen3-VL | ✅ parity |
| Free-space / placement ("where to put") | RoboBrain 2.5 `task="pointing"` (vacancy detection) | ✅ parity |
| Trajectory prediction | **RoboBrain 2.5** `task="trajectory"` → `[(x, y, depth), …]` | 🟢 **open is ahead: metric 3D, not 2D pixels** |
| Progress / success detection from video | **RoboBrain 2.5 + Robo-Dopamine** (General Reward Model), Cosmos-Reason2 | 🟢 **open is ahead: dense per-step reward, usable for VLA RL** |
| Physics common sense / video reasoning | **Cosmos-Reason2** (2B/8B/32B) → **Cosmos 3 Reasoner** | ✅ parity, edge tier available |
| Task orchestration / tool calling | any open VLM with tool support + **RoboOS-Next** (memory, multi-robot) | ⚠️ framework exists, less turnkey than ER's managed loop |
| Web-search grounding | Qwen3-VL / GLM-4.6V + your own search tool | ⚠️ you build it |
| Fully open *data* + training code | **Molmo2-ER / MolmoAct2** (Apache-2.0, weights + code + data) | 🟢 **open is ahead — ER is closed on all three** |

**The three families to know**

1. **Ai2 Molmo2-ER** (`allenai/Molmo2-ER`, 4.85 B, **Apache-2.0**) — a VLM backbone *specialised* for spatial and embodied reasoning, trained on a **3.3 M-sample** corpus with a *specialize-then-rehearse* recipe. Paper claim: **"MolmoER surpasses GPT-5 and Gemini Robotics ER-1.5 across 13 embodied-reasoning benchmarks"** ([arXiv:2605.02881](https://arxiv.org/abs/2605.02881)). It is the ER backbone of MolmoAct2 (Ai2's open VLA), i.e. the exact same "ER thinks / VLA acts" split Google uses.
2. **BAAI RoboBrain 2.0 → 2.5** (3B/7B/32B → 4B/8B, checkpoints on HF) — the closest *functional* clone of ER's API surface: one `UnifiedInference` object with `task=` in {`general`, `grounding`, `pointing`, `trajectory`} plus temporal value estimation. **RoboBrain 2.5 adds two things ER does not expose: absolute-metric 3D traces and a dense process-reward model** ([arXiv:2601.14352](https://arxiv.org/abs/2601.14352), [2507.02029](https://arxiv.org/abs/2507.02029)).
3. **NVIDIA Cosmos Reason** (Reason1-7B → Reason2-2B/8B/32B → **Cosmos 3** Reasoner tower, incl. **Cosmos3-Edge 4B** for Jetson) — physical common sense + embodied decisions through long CoT, post-trained with SFT **and RL**; already the System-2 backbone of GR00T N1.7 ([Apache-2.0 code](https://github.com/nvidia-cosmos/cosmos-reason2), NVIDIA Open Model License weights; Cosmos 3 under **OpenMDW-1.1**).

**Plus a general-purpose open tier** — Qwen3-VL, InternVL3.5, GLM-4.6V, Llama-3.2-Vision, Gemma 4 — which ground and point reasonably but are *not* embodied-reasoning-specialised, and a **small/edge tier** — Florence-2 (already has a ROS 2 wrapper in [`papers.csv`](papers.csv), `2604.01179`), SmolVLM2, Molmo2-4B, Cosmos3-Edge-4B, RoboBrain2.5-4B.

> 📌 **The strategic finding:** the interesting open-source advantage is *not* "cheaper ER". It is that **RoboBrain 2.5 and Molmo2-ER release the pieces ER keeps server-side** — 3D metric traces, dense reward signals, training data and code. That changes what you can build: reward-shaped VLA RL, offline evaluation, air-gapped deployment, and auditability.

---

## 1️⃣ Method & inclusion criteria

Follows [`research-protocol.md`](research-protocol.md). A model was included if **all** of the following hold:

1. **Open weights** downloadable without a partner programme or waitlist.
2. **Embodied-reasoning capability**: spatial grounding/pointing, affordance, trajectory, or task-progress/success reasoning — i.e. the ER skill set, not just captioning.
3. **No action head** required for the ER role (models that also ship a VLA variant are included for their *reasoning* backbone and flagged).
4. Verifiable primary source (arXiv report, official repo, or HF model card) as of **2026-10-22**.

**Excluded:** closed APIs (Gemini Robotics-ER, GPT-5.x vision, Claude) — covered in [`gemini-robotics-er-guide.md`](gemini-robotics-er-guide.md); pure VLAs (π0.5, GR00T N1.7, OpenVLA, SmolVLA) — covered in the [slide deck](presentations/llm-vlm-vla-sota.html); world *generators* without a reasoning tower (Cosmos-Predict, Genie).

**Evidence quality flags used throughout:** 🟢 primary paper/repo · 🟡 vendor claim, not independently replicated · 🔴 community report only.

---

## 2️⃣ Taxonomy — what "VLM-ER" actually means

"Embodied reasoning" is not one skill. Decomposing it is what makes the comparison fair:

| Layer | Skill | Example query | ER equivalent |
|---|---|---|---|
| **E1 · Perceive** | detection, boxes, OCR, state | "is the drawer open?" | image understanding |
| **E2 · Localise** | pointing, boxes in normalised coords | "point at the red block" | Point-Bench, pointing API |
| **E3 · Relate** | spatial referring, free space, metric distance | "the mug behind the laptop"; "where can a 12 cm box go?" | RefSpatial, Where2Place |
| **E4 · Predict** | trajectory, future state, video moment finding | "reach for the banana" → waypoint list | ER 2 video understanding |
| **E5 · Evaluate** | progress %, success/failure, reward | "did the grasp succeed?" | ER 2 progress classification |
| **E6 · Plan** | decomposition, multi-step, closed-loop re-planning | "clear the table" → ordered atomic steps | ER agentic orchestration |
| **E7 · Act (via tools)** | function calling on *your* robot API | `move(x, y, high)` | ER task orchestration |

**Every open model below covers E1–E3 and E6. The differentiators are E4 (metric 3D traces), E5 (dense reward) and E7 (turnkey tool loop).**

```
        E7 Act ──────────────► tool calls ──► your robot API / a VLA
        E6 Plan ─────────────► ordered atomic instructions
        E5 Evaluate ─────────► progress, success, dense reward   ← RoboBrain 2.5 GRM
        E4 Predict ──────────► 3D traces, future frames           ← RoboBrain 2.5, Cosmos 3
        E3 Relate ───────────► referring, free space, metrics
        E2 Localise ─────────► points [y,x], boxes                ← Molmo2-ER specialty
        E1 Perceive ─────────► labels, states, OCR
   ──────────────────────────────────────────────────────────────
        all layers above are TEXT/COORDINATE outputs → still a VLM
        add an action head + robot data → it becomes a VLA
```

> 📌 **Boundary rule (same as in [`GLOSSARY.md`](GLOSSARY.md)):** if the output is text or coordinates, it is a **VLM-ER**; if the output is a motor command, it is a **VLA**. MolmoAct2 and Cosmos3-Policy cross that line — they are listed here only for their ER backbones (`Molmo2-ER`, `Cosmos3-Reasoner`).

---

## 3️⃣ Capability matrix vs Gemini Robotics-ER

Legend: ✅ native · 🟡 partial / needs your glue · ❌ absent · 🔒 closed

| Capability | **Gemini Robotics-ER 2** 🔒 | **Molmo2-ER** (Ai2) | **RoboBrain 2.5** (BAAI) | **Cosmos-Reason2 / Cosmos 3** (NVIDIA) | **Qwen3-VL** (general) |
|---|---|---|---|---|---|
| Pointing (`[y,x]` normalised) | ✅ 0–1000 | ✅ trained on PixMo-Points + video point/track | ✅ `task="pointing"` | 🟡 via prompt | ✅ grounding mode |
| Bounding boxes | ✅ | ✅ object detection | ✅ `task="grounding"` | 🟡 | ✅ |
| Affordance prediction | 🟡 via prompt | 🟡 | ✅ explicit affordance task | 🟡 physics-aware | ❌ |
| Spatial referring / free space | ✅ (RefSpatial 48.5, Where2Place 59.0) | ✅ 13-benchmark ER suite | ✅ RefSpatial 54.0 (32B, v2.0) | 🟡 | 🟡 |
| **Metric 3D output (depth)** | ❌ 2D points only | 🟡 depth *tokens* in MolmoAct2-Think | ✅ **`(x, y, depth)` traces** | 🟡 3D-aware reasoning | ❌ |
| Trajectory / waypoints | ✅ trajectories | 🟡 | ✅ `task="trajectory"` | 🟡 | ❌ |
| Video moment finding | ✅ ER 2 | ✅ video point-track, timestamps | ✅ temporal perception | ✅ temporal localisation | 🟡 |
| **Progress / success detection** | ✅ ER 2 progress classification | 🟡 | ✅ **dense step-aware progress + state** (GRM) | 🟡 video critic | ❌ |
| **Dense reward for VLA RL** | ❌ | ❌ | ✅ **Robo-Dopamine GRM** | 🟡 (Cosmos-RL) | ❌ |
| Task planning / decomposition | ✅ | 🟡 | ✅ long-horizon + closed-loop | ✅ planning model | ✅ |
| Function calling / your robot API | ✅ managed loop | 🟡 you wire it | 🟡 + **RoboOS-Next** multi-robot | 🟡 | ✅ |
| Web-search grounding | ✅ Google Search | ❌ | ❌ | ❌ | 🟡 bring your own |
| Code execution (crop/zoom, gauges) | ✅ | ❌ | ❌ | ❌ | 🟡 |
| Image annotation returned | ✅ | ❌ | ✅ `plot=True` visualisation | ❌ | ❌ |
| Streaming / Live API | ✅ ER 2 streaming | ❌ (you serve it) | ❌ (you serve it) | ✅ vLLM/NIM streaming | ✅ vLLM |
| Self-host / air-gapped | ❌ cloud only | ✅ | ✅ | ✅ | ✅ |
| Fine-tunable | ❌ (prompt only) | ✅ weights + code + data | ✅ weights + training code | ✅ SFT/LoRA/RL (Cosmos Framework, TRL) | ✅ |
| Weights licence | 🔒 | **Apache-2.0** | HF checkpoint licence (verify per model) | **NVIDIA Open Model License** / Cosmos 3 **OpenMDW-1.1** | Apache-2.0 |
| Training data released | ❌ | ✅ **9 open ER/robotics collections + 720 h bimanual** | 🟡 benchmark + some data | 🟡 curation tooling (Cosmos Curator) | 🟡 |
| Edge deployment | 🟡 On-Device 2 is a VLA | ✅ 4B | ✅ 4B / 8B | ✅ **Cosmos3-Edge 4B** (Jetson AGX Orin/Thor) | ✅ 4B tiers |

**Reading of the matrix**

- **ER wins on E7 (managed tool loop), web grounding and code execution** — the "agent" conveniences. None of these are model capabilities you cannot build; they are product surface.
- **Open wins on E4/E5 (metric 3D + dense reward), on openness, and on cost/latency control.** RoboBrain 2.5's `(x, y, depth)` traces and GRM reward have *no* ER equivalent at any price.
- **Molmo2-ER is the closest like-for-like ER replacement** — same role (specialised ER backbone feeding a VLA), fully open, and the only one with a published head-to-head claim against ER-1.5 and GPT-5.

---

## 4️⃣ Family A — Ai2 **Molmo2-ER** (+ MolmoAct2) 🟢

| | |
|---|---|
| **Model** | [`allenai/Molmo2-ER`](https://huggingface.co/allenai/Molmo2-ER) — 4.85 B params (4,850,869,200), fine-tune of `allenai/Molmo2-4B` |
| **Released** | 2026-05-04 (paper v1), v2 2026-05-08; code + data 2026-05-28 |
| **Paper** | *MolmoAct2: Action Reasoning Models for Real-world Deployment* — [arXiv:2605.02881](https://arxiv.org/abs/2605.02881), Fang, Duan, Clay, Wang, … Krishna (Ai2 / UW / Stanford) |
| **Licence** | **Apache-2.0** — weights, code and training data all released |
| **Role** | Dedicated **embodied-reasoning VLM backbone**; the "System 2" that MolmoAct2 (the VLA) is built on |

### Why it matters

Molmo is the family that *invented* open pointing: **PixMo-Points** (images + referring expressions + annotated points) shipped with Molmo 1 in 2024 ([arXiv:2409.17146](https://arxiv.org/abs/2409.17146)) and made "answer by pointing" a mainstream VLM capability. Molmo2-ER is that lineage specialised for robots.

**The headline claim** 🟡 *(author-reported, from the paper's own evaluation)*:

> "MolmoER surpasses **GPT-5** and **Gemini Robotics ER-1.5** across **13 embodied-reasoning benchmarks**."

That is a direct, like-for-like challenge to ER on ER's own turf — and because the weights, training code and data are public, it is **verifiable**, which ER's numbers are not.

### Training recipe (reproducible — this is the rare part)

| Component | Detail |
|---|---|
| Corpus | **3.3 M samples**: image embodied QA, video embodied QA, **pointing & object detection**, multi-image + **ego–exo correspondence**, abstract embodied reasoning |
| Recipe | **specialize-then-rehearse** — Stage 1 *embodied specialisation*, Stage 2 *joint refinement* (rehearses general data so specialisation does not wreck general VLM ability) |
| Open data | 9 collections: video captions, video QA, **video point** (pixels + timestamps), **video track** (multi-object through occlusion and re-entry), multi-image, plus `molmo2-er-datasets` (spatial, 3D, robotics, visual reasoning) |
| Base family | Molmo 2: **4B / 8B / O-7B** — O-7B pairs with **Olmo**, a fully open LLM, so *every* component (language backbone, vision encoder, checkpoints) is inspectable |

### The action-reasoning sibling (context, not ER)

**MolmoAct2** = Molmo2-ER + robot state/action modelling + a **flow-matching continuous action expert** grafted on via **per-layer KV-cache conditioning** (the expert cross-attends to *every* VLM layer, not just the final hidden state).

- **OpenFAST** — open-weight, open-data action tokenizer trained on millions of trajectories across **5 embodiments**.
- **MolmoThink** — adaptive-depth reasoning: re-predicts depth tokens *only* for scene regions that changed between timesteps → keeps geometric grounding at a fraction of the latency.
- **MolmoAct2-BimanualYAM** — **720 h** of teleoperated bimanual trajectories, the largest open bimanual dataset; plus quality-filtered DROID (Franka) and SO-100/101 subsets.
- Up to **37× faster** than MolmoAct v1; outperforms **π0.5** across 7 sim + real benchmarks 🟡; **LeRobot-integrated**; fine-tuned checkpoints for DROID, BimanualYAM, SO-100/101 and LIBERO; 400 K+ artifact downloads by 2026-05-28.
- **Ai2's own stated weaknesses** (quote these in any proposal — rare honesty): it *"plans a batch of 10–30 moves and executes the whole sequence without inferring again"* → no mid-batch reactivity, jerky transitions; and it works out of the box **only** on SO-100, bimanual YAM and Franka.
- Published reference hardware: 2× YAM arms + overhead RealSense **D435** + 2× **D405** close-up cameras.
- Piloted by the **Stanford Cong Lab** toward a self-driving wetlab (CRISPR sample handling, benchtop equipment).

### When to choose it

✅ You want a **drop-in open replacement for ER's pointing/localisation role** — Apache-2.0, 4 B, fits a 24 GB card.
✅ You want to **reproduce or extend** an ER training recipe (data + code + weights).
✅ You are building an ER→VLA stack and want *both* halves open and from one lineage.
❌ You need a managed tool-calling loop, web grounding or code execution out of the box.
❌ You need metric 3D traces (→ RoboBrain 2.5) or dense reward (→ Robo-Dopamine).

---

## 5️⃣ Family B — BAAI **RoboBrain 1.0 → 2.0 → 2.5** 🟢

| | |
|---|---|
| **Models** | 2.0: **3B / 7B / 32B** · 2.5: **4B / 8B** (`RoboBrain2.5-8B-NV`, `-8B-MT`), 32B pending |
| **Papers** | 1.0 [arXiv:2502.21257](https://arxiv.org/abs/2502.21257) (**CVPR 2025**) · 2.0 [arXiv:2507.02029](https://arxiv.org/abs/2507.02029) · **2.5 [arXiv:2601.14352](https://arxiv.org/abs/2601.14352)** (2026-01-20, 37 pp) |
| **Code** | [`FlagOpen/RoboBrain2.5`](https://github.com/FlagOpen/RoboBrain2.5) ⭐1.1 k · [`FlagOpen/RoboBrain`](https://github.com/FlagOpen/RoboBrain) ⭐565 · ecosystem: **RoboOS**, **Robo-Dopamine**, **RoboTracer**, **Reason-RFT**, `RoboBrain-X0`, `RoboBrain_Dex` |
| **Infra** | Training **FlagScale** · evaluation **FlagEvalMM** (BAAI) |
| **Training** | 3 stages: foundational spatiotemporal learning → embodied spatiotemporal enhancement → **CoT reasoning in embodied contexts**, plus reinforcement fine-tuning |

### The API surface is the closest functional match to ER

One class, task-switched — which is what makes RoboBrain the easiest ER substitute to wire up:

```python
from inference import UnifiedInference
model = UnifiedInference("BAAI/RoboBrain2.5-8B-NV")

model.inference("What is shown in this image?", image, task="general")
model.inference("the person wearing a red hat", image, task="grounding", plot=True)          # bbox
model.inference("the affordance area for holding the cup", image, task="pointing", plot=True) # affordance
model.inference("Identify spot within the vacant space that's between the two mugs",
                image, task="pointing", plot=True, do_sample=True)                            # free space
model.inference("Identify spot within toilet in the house", image, task="pointing")           # navigation
model.inference("reach for the banana on the plate", image, task="trajectory", plot=True)     # 3D trace
#   → [(x1, y1, d1), (x2, y2, d2), ...]   x, y pixel coords + depth per keypoint
```

### RoboBrain 2.5's two upgrades — both *beyond* ER's published surface

1. **Precise 3D spatial reasoning.** From 2D pixel-relative grounding to **depth-aware coordinate prediction** and **absolute metric constraint comprehension** — it understands instructions like *"hovering 1–5 cm above"* — and from a single pick point to a **complete 3D manipulation trace as an ordered keypoint sequence under physical constraints**. Research line: **RoboTracer** ([arXiv:2512.13660](https://arxiv.org/abs/2512.13660)).
2. **Dense Temporal Value Estimation.** A **General Reward Model (GRM)** giving multi-granularity **progress prediction** across tasks, viewpoints and embodiments; **execution-state estimation** (success, failure, error onset); and **real-time dense reward for VLA reinforcement learning**. Claim: with **only one demonstration** it reaches **95 %+** success in complex fine-grained manipulation 🟡. Evaluated against human reference reward on AgiLex, RoboCasa, LIBERO and Franka rollouts — tracking the human signal more faithfully than the VLAC baseline and sharply penalising incorrect insertions, low positions and misalignments. Research line: **Robo-Dopamine** ([arXiv:2512.23703](https://arxiv.org/abs/2512.23703)).

Retained from 2.0: interactive reasoning with long-horizon planning and closed-loop feedback; spatial perception (point + bbox from complex instructions); temporal perception (future trajectory estimation); scene reasoning through **real-time structured memory** construction and update.

### Measured evidence — RoboBrain 2.0, Table 2 (spatial reasoning) 🟢

| Model | BLINK-All | CV-Bench | EmbSpatial | RoboSpatial-All | RefSpatial |
|---|---|---|---|---|---|
| **RoboBrain-32B-2.0** | **83.63** | 83.92 | **78.57** | **72.43** | **54.00** |
| **RoboBrain-7B-2.0** | 83.95 | **85.75** | 76.32 | 54.23 | 32.50 |
| Gemini-2.5-Pro (05-06) | 81.83 | 84.59 | 78.74 | 59.87 | 38.16 |
| GPT-o4-mini | 83.57 | 85.21 | 78.29 | 51.25 | 17.29 |
| Qwen2.5-VL-72B-Instruct | 76.26 | 82.68 | 73.30 | 48.33 | 19.67 |
| Qwen2.5-VL-32B-Instruct | 81.37 | 81.59 | 74.45 | 52.16 | 13.72 |
| GPT-4o (2024-11-20) | 77.90 | 78.63 | 71.92 | 44.42 | 8.78 |
| Claude-Sonnet-4 | 78.12 | 78.43 | 64.26 | 51.26 | 7.69 |
| VeBrain-8B | 79.68 | 78.57 | 70.52 | 42.48 | 0.30 |
| Cosmos-Reason1-7B | 68.57 | 74.71 | 65.22 | 38.81 | 5.44 |
| Magma-8B | 65.88 | 60.98 | 64.59 | 33.71 | 4.50 |
| RoboBrain-7B-1.0 | 77.07 | 76.22 | 68.13 | 51.53 | 9.92 |

Reported best across **BLINK-Spatial, RoboSpatial, RefSpatial-Bench, Where2Place, EgoPlan2 and Multi-Robot-Plan** — beating *proprietary* general VLMs on the robotics-relevant splits, not just other open models. **RefSpatial 54.0** vs Gemini-2.5-Pro 38.16 and GPT-4o 8.78 shows exactly where general VLMs collapse: spatial referring.

> ⚠️ **Two caveats.** (1) These are the *authors'* evaluations on their own framework (FlagEvalMM); pointing/trajectory prompt formats differ per model, so cross-family numbers are not automatically comparable. (2) RoboBrain 2.5's headline 3D and reward results are **not** accompanied by a public head-to-head table against Gemini Robotics-ER 2 at the time of writing.

### Two engineering details worth stealing

- **Mixed-precision inference:** vision encoder kept at full precision, LLM weights **INT8** with **FP16 activations** → **~30 % latency reduction** on end-to-end embodied tasks with negligible accuracy loss, and minimally invasive to existing pipelines.
- **Multi-robot:** **RoboOS-Next** ([arXiv:2510.26536](https://arxiv.org/abs/2510.26536)) — a unified **memory-based framework for lifelong, scalable and robust multi-robot collaboration**. The open analogue of ER 2's multi-robot orchestration, and a direct answer to the *robotic episodic memory* gap in [`research-gaps.md`](research-gaps.md).

### When to choose it

✅ You need the **full ER feature set self-hosted** (general VQA + grounding + pointing + affordance + navigation + 3D trajectory) behind one API.
✅ You want **metric 3D** output and a **reward/progress model** to close a VLA RL loop or automate evaluation.
✅ You want **multi-robot** coordination with persistent memory (RoboOS-Next).
✅ You want a **4B/8B** tier for a workstation or Jetson-class device.
❌ You need Apache-2.0 certainty — **check the licence on each HF checkpoint** before shipping.
❌ You need web-search grounding or code execution.

---

## 6️⃣ Family C — NVIDIA **Cosmos Reason** → **Cosmos 3** 🟢

| Generation | Models | Base architecture | Status |
|---|---|---|---|
| **Cosmos-Reason1** (2025) | 7B | **Qwen2.5-VL** | maintenance; spatial-temporal reasoning for city/industrial ops added Aug 2025; video physical-plausibility critic Jun 2025 |
| **Cosmos-Reason2** (Dec 2025 → Apr 2026) | **2B / 8B / 32B** | **Qwen3-VL** | repo now maintenance-only; 32B added 2026-04-29 |
| **Cosmos 3** (May 2026) | Nano / Super / **Edge (4B)** tiers, **Reasoner** + **Generator** towers | unified **Mixture-of-Transformers**, omnimodal | ✅ current; repos moved to [`NVIDIA/Cosmos`](https://github.com/NVIDIA/Cosmos) |

**What it is:** "an open, customizable, reasoning VLM for physical AI and robotics… understands space, time and fundamental physics, and can serve as a **planning model** to reason what steps an embodied agent might take next." Post-trained with **physical common sense + embodied reasoning data using SFT *and* reinforcement learning**, with chain-of-thought reasoning about world dynamics *without* human annotations.

### Why it is strategically different

Cosmos Reason is **already the System-2 backbone of a production VLA**: GR00T N1.7 uses **Cosmos-Reason2-2B** as its VLM (see [`gemini-robotics-er-guide.md`](gemini-robotics-er-guide.md) and the [slide deck](presentations/llm-vlm-vla-sota.html) slide 12). So choosing Cosmos Reason means your ER model and your VLA share a lineage — the same bet Google makes with Gemini Robotics-ER + Gemini Robotics.

**Cosmos 3 collapses the distinction entirely.** One model, two towers:

| Tower | Inputs | Outputs | Use for |
|---|---|---|---|
| **Reasoner** | text, vision | text | world understanding, **grounding**, **task planning**, **embodied reasoning** |
| **Generator** | text, vision, audio, **action** | vision, audio, **action** | world simulation, future prediction, synthetic data, **policy learning** |

That is: the *same* family now spans the VLM-ER role **and** the world-model role **and** the VLA role — with checkpoints like `Cosmos3-Nano-Policy-DROID` ("open SOTA DROID robot policy, runs on RTX Pro 6000"), `Cosmos3-Edge-Policy-DROID` (edge-deployable) and `Cosmos3-Nano-Sim-Bimanual` (closed-loop interactive robot policy simulation).

### Deployment facts (verified from the repos)

| Item | Cosmos-Reason2 | Cosmos 3 |
|---|---|---|
| Min GPU memory | 2B → **24 GB**, 8B → **32 GB** | Nano/Edge tiers target **Jetson AGX Orin / Thor**, RTX Pro 6000 |
| Tested platforms | H100, GB200, DGX Spark, **Jetson AGX Thor (Edge)** | same + edge |
| Library support | `transformers>=4.57`, **vLLM ≥0.11** serving | Diffusers, Transformers, vLLM, vLLM-Omni, SGLang, TensorRT-LLM, **NIM** |
| Reasoning trace | `--reasoning-parser qwen3` | same family |
| Quantisation | `llmcompressor` recipe (FP8/W8A8) | Cosmos Framework (SFT · LoRA · distillation · RL) |
| Post-training | **TRL** notebooks + **Cosmos-RL** | Cosmos Framework |
| Ready prompts | `prompts/embodied_reasoning.yaml`, `caption.yaml`, `temporal_localization.yaml` | Cookbook recipes per industry |
| **Licence** | code **Apache-2.0**; models **NVIDIA Open Model License** | source **and** models under **OpenMDW-1.1** |
| Tooling | — | **Cosmos Curator** (data curation), **Cosmos Evaluator** (automated eval of world generation & reasoning) |

Serving is a one-liner, which matters for a ROS 2 integration:

```bash
vllm serve nvidia/Cosmos-Reason2-2B \
  --allowed-local-media-path "$(pwd)" \
  --max-model-len 16384 \
  --media-io-kwargs '{"video": {"num_frames": -1}}' \
  --reasoning-parser qwen3 --port 8000

cosmos-reason2-inference online -v --port 8000 \
  -i prompts/embodied_reasoning.yaml --reasoning --images assets/sample.png
```

### Honest weaknesses

- On **RoboBrain 2.0's** spatial table, **Cosmos-Reason1-7B scores poorly** (BLINK 68.57, RoboSpatial 38.81, RefSpatial 5.44) — it is a *physics/common-sense* reasoner, not a *spatial-referring* specialist. Do not assume "Cosmos" ⇒ good pointing. Verify Reason2/3 on your own pointing tasks.
- Cosmos 3's own limitations note: artifacts in long, high-resolution or physically complex outputs (temporal inconsistency, object morphing, implausible dynamics); **safety-critical applications need additional validation and system-level safety analysis**; generation ships with guardrails on by default.
- **NVIDIA Open Model License / OpenMDW-1.1 ≠ Apache-2.0.** Read the terms before commercial deployment; custom licences are available.
- Migration churn: three generations in ~15 months, and the Reason2 repo is already in maintenance. Pin versions.

### When to choose it

✅ You are on **NVIDIA hardware** (Jetson Thor/Orin, RTX Pro, DGX) and want vendor-supported edge deployment + NIM/TensorRT-LLM serving.
✅ You want **physical common sense and video-level plausibility judgement** (safety monitoring, video critic, incident review).
✅ You plan to use **GR00T N1.x** as the VLA and want a shared backbone lineage.
✅ You want a single family that can also **generate** simulation data and policies (Cosmos 3 Generator tower).
❌ Your primary need is precise pointing/spatial referring (→ RoboBrain 2.5 or Molmo2-ER).
❌ You require Apache-2.0 (→ Molmo2-ER, Qwen3-VL).

<!--DOC7-->





