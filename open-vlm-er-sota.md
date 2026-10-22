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

---

## 7️⃣ The wider open ecosystem (specialists, datasets, general tier)

### 7.1 New unified ER models (2026) — watch these

| Model | arXiv | Date | Claim | Openness |
|---|---|---|---|---|
| **Vesta** — *A Generalist Embodied Reasoning Model* (NVIDIA: Bjorck, …, Birchfield, Blukis, Tremblay, Zhu, **Jim Fan**, Kautz) | [2606.20905](https://arxiv.org/abs/2606.20905) | 2026-06-18 | One model unifying **localisation + spatial reasoning + navigation + long-horizon planning**; curated spatial-grounding corpus + a **multimodal memory harness**. Beats individual SOTA baselines by **>20 %** on average, an *ensemble of per-category-best* baselines by **>10 %**, and improves **real-world task success by >35 %** on memory-and-reasoning tasks 🟡 | ⚠️ not stated in the abstract — verify before assuming weights |
| **ABot-ER** — *Unified Embodied Reasoning through Agentic Data-Model Co-Evolution* | [2610.18355](https://arxiv.org/abs/2610.18355) | 2026-10-13 | Single model with specialist depth in **perception** (spatial/scene/temporal), **planning** (long-horizon action organisation) and **execution** (point grounding, affordance). Uses an *Agentic Data-Model Self-Evolution Engine* and **task tokens that activate low-rank residuals** over a shared backbone. SOTA overall on **12 benchmarks** 🟡 | ⚠️ not stated in the abstract — verify |

Both are significant because they argue the same thesis this repo needs: **a single generalist ER model beats a stack of specialists** (Vesta) and **breadth and depth can coexist** via task-conditioned adapters (ABot-ER) — the latter being a directly reusable architecture idea for a multi-skill ROS 2 perception node.

### 7.2 Spatial specialists & open datasets (the raw material)

| Artefact | arXiv | What it gives you |
|---|---|---|
| **RoboPoint** | [2406.10721](https://arxiv.org/abs/2406.10721) | VLM for **spatial affordance prediction** — instruction-tuned to output point sets for placement/grasp; the reference work for "point where to put it" |
| **RoboSpatial** (CVPR 2025 **Oral**) | [2411.16537](https://arxiv.org/abs/2411.16537) | **1 M images, 5 k 3D scans, 3 M annotated spatial relations**, 2D- and 3D-ready; explicitly teaches **reference-frame comprehension** (ego- vs world- vs object-centric). Models trained on it beat baselines on affordance, relation prediction and manipulation |
| **SpatialLM** | [2506.07491](https://arxiv.org/abs/2506.07491) | LLM over **3D point clouds** → structured scene output (walls, doors, windows, oriented object boxes + semantics); fine-tuned from open LLMs; trained on **12,328 synthetic indoor scenes / 54,778 rooms**; SOTA layout estimation |
| **XVR — Cross-View Relations** (CVPR 2026) | [2603.27967](https://arxiv.org/abs/2603.27967) | **100 K VQA** from 18 K 3D scenes + **70 K manipulation trajectories**; correspondence / verification / localisation. Fine-tuned VLMs improve on **MindCube** and **RoboSpatial**, and as **VLA backbones improve RoboCasa success** |
| **VeBrain-8B / Magma-8B** | (in RoboBrain Table 2) | Earlier embodied VLMs; both score ~70–80 on BLINK/CV-Bench but **collapse on RefSpatial** (0.30 / 4.50) — evidence that generic embodied pretraining ≠ spatial referring |

> 📌 **Highest-leverage insight for a small lab:** you do not need to build an ER model. **RoboSpatial + XVR + PixMo-Points are open datasets**; post-training an existing open VLM (Qwen3-VL, Molmo2) on them is the cheap route, and the ECCV-2026 spatial-adaptation literature reports **+30.4 % on RoboSpatial and +9.3 % on ERQA** *without* hurting general capability (**+15.9 % V\*Bench, 88.9 % BLINK**). That mirrors Molmo2-ER's own *specialize-then-rehearse* finding.

### 7.3 General-purpose open VLMs (usable, not specialised)

| Model | Sizes | Licence | ER-relevant strength | Gap |
|---|---|---|---|---|
| **Qwen3-VL** | 4B … 235B-A22B (MoE) | Apache-2.0 | strong grounding + agentic tool use; the base of **Cosmos-Reason2** | no affordance/trajectory/reward heads |
| **InternVL3 / 3.5** | 1B – 78B | open (per checkpoint) | solid general multimodal, cheap tiers | not embodied-tuned |
| **GLM-4.6V / GLM-5.3 Flash** | — | open | MMMU 71.1 / 81.4 — strong general perception | no pointing specialisation |
| **Llama-3.2-Vision** | 11B, 90B | Llama licence | broad ecosystem, tool use | weak spatial referring |
| **Gemma 4** | 26B-A4B, 31B | open | cheap frontier-adjacent (MMMU ~74) | not embodied |

Use these when you need **one model for perception + dialogue + planning** and can accept prompt-engineered pointing; choose a dedicated ER model when **spatial accuracy is the product**.

### 7.4 The edge tier (Jetson / workstation, ROS 2-ready)

| Model | Params | VRAM class | Notes |
|---|---|---|---|
| **Florence-2** | 0.23 B / 0.77 B | <4 GB | already wrapped as a **ROS 2 native node** — [`papers.csv`](papers.csv) `2604.01179`, <50 ms, multi-mode (caption, OD, grounding) |
| **SmolVLM2** | 0.5 – 2.2 B | 4–8 GB | Apache-2.0, LeRobot-native, good pointing for size |
| **Molmo2-ER / Molmo2-4B** | 4.85 B | ~16 GB | Apache-2.0 ER specialist |
| **RoboBrain2.5-4B** | 4 B | ~16 GB | full ER task surface at small size |
| **Cosmos-Reason2-2B** | 2 B | **24 GB** (vendor min) | physics CoT; vLLM-servable |
| **Cosmos3-Edge** | 4 B | Jetson AGX Orin/Thor | on-device real-time tier |
| **Qwen3-VL-4B** | 4 B | ~12 GB | generalist fallback with tool use |

This tier is exactly what [`research-gaps.md`](research-gaps.md) asks for under *Edge AI / local inference*: an open, quantisable ER model that fits the robot instead of the datacentre.

---

## 8️⃣ Benchmark landscape — what to run, and what it proves

| Benchmark | Layer (§2) | What it measures | Open? |
|---|---|---|---|
| **ERQA** | E3/E6 | 400 multiple-choice embodied-reasoning questions | ✅ |
| **ERQA-Plus** ([2606.17639](https://arxiv.org/abs/2606.17639), 2026-06) | E3/E6 | **diagnostic** version with explicit control over *which* reasoning dependency is tested (spatial relations, actions, procedures, intentions, constraints, consequences) | ✅ |
| **Point-Bench** | E2 | pointing accuracy | ✅ |
| **PIO / Point-It-Out** ([2509.25794](https://arxiv.org/abs/2509.25794)) | E2 | **multi-stage visual grounding** — pointing, not MCQ; explicitly criticises MCQ-only ER evaluation | ✅ |
| **Where2Place** | E3 | free-space pointing for placement | ✅ |
| **RefSpatial-Bench** | E3 | spatial referring | ✅ |
| **RoboSpatial** | E3 | spatial relations + affordance, 2D & 3D | ✅ |
| **BLINK** (Depth/Spatial), **CV-Bench**, **EmbSpatial**, **SAT**, **VSI-Bench**, **MindCube** | E1/E3 | depth, spatial relations, video-space understanding | ✅ |
| **EgoPlan2**, **Multi-Robot-Plan**, **RoboBench** | E6 | long-horizon and multi-agent planning | ✅ |
| **ShareRobot-Bench** | E6 | robot-task reasoning | ✅ |
| **KinDER** ([2604.25788](https://arxiv.org/abs/2604.25788), **RSS 2026**) | physics | **kinematic & dynamic** embodied reasoning: 25 procedural environments, Gymnasium-compatible, 13 baselines (TAMP, IL, RL, foundation models), real-to-sim-to-real on a mobile manipulator | ✅ fully open |
| **FlagEvalMM** / **Cosmos Evaluator** | — | evaluation *frameworks* (BAAI / NVIDIA) | ✅ |

**KinDER's headline finding is the one to quote in a proposal:** *"existing methods struggle to solve many of the environments, indicating substantial gaps in current approaches to physical reasoning."* Spatial benchmarks are saturating; **kinematic/dynamic** reasoning is not.

> ⚠️ **Comparability warning.** RoboBrain's numbers come from FlagEvalMM, Molmo's from its own 13-benchmark suite, Cosmos's from NVIDIA's, and ER's from DeepMind's Table 19. Prompt formats for pointing differ (normalisation range, axis order, JSON shape). **Never compare two families' published numbers directly — re-run both on your data.** This is the same discipline the [slide deck](presentations/llm-vlm-vla-sota.html) applies to VLA leaderboards (slide 20).

---

## 9️⃣ Selection guide

### By requirement

| If you need… | Pick | Why |
|---|---|---|
| The closest **drop-in open ER replacement** (pointing + affordance + trajectory + planning) | **RoboBrain 2.5-8B** | one `UnifiedInference` API, task-switched, mirrors ER's surface |
| **Apache-2.0** certainty + reproducible training | **Molmo2-ER (4.85 B)** | weights + code + data; specialize-then-rehearse recipe published |
| Best published **spatial referring / free space** | **RoboBrain-32B-2.0** | RefSpatial 54.0 vs Gemini-2.5-Pro 38.16, GPT-4o 8.78 |
| **Metric 3D** traces, not 2D pixels | **RoboBrain 2.5** | `(x, y, depth)` keypoint sequences + absolute constraints ("1–5 cm above") |
| **Dense reward / progress** to train or evaluate a VLA | **RoboBrain 2.5 + Robo-Dopamine** | GRM: step-aware progress, execution-state, RL rewards |
| **Physics common sense**, video plausibility, safety monitoring | **Cosmos-Reason2 / Cosmos 3 Reasoner** | SFT+RL on physical common sense; video critic lineage |
| **Jetson / on-device** | **Cosmos3-Edge 4B**, **RoboBrain2.5-4B**, **Molmo2-4B**, **Florence-2** | vendor-validated edge tiers; Florence-2 already has a ROS 2 node |
| Shared lineage with your **VLA** | GR00T N1.7 → **Cosmos-Reason2**; MolmoAct2 → **Molmo2-ER** | same backbone family as the policy |
| **Multi-robot** coordination with memory | **RoboOS-Next** (+ any ER model) | lifelong, memory-based, scalable collaboration framework |
| Cheapest path: **fine-tune your own ER** | **Qwen3-VL / Molmo2** + **RoboSpatial + XVR + PixMo-Points** | open datasets, LoRA-scale compute, general ability preserved |
| Web-search grounding, code execution, managed agent loop | ⚠️ **Gemini Robotics-ER 2** (closed) | no open model ships this turnkey — you build it (§10) |

### By constraint

| Constraint | Recommendation |
|---|---|
| **Air-gapped / field robot** | any open model; ER is cloud-only and disqualified |
| **Must fine-tune on your cell** | Molmo2-ER (Apache-2.0) or RoboBrain 2.5; Cosmos via Cosmos Framework / TRL |
| **Commercial product, strict legal** | Apache-2.0 only → **Molmo2-ER**, Qwen3-VL, SmolVLM2. Verify RoboBrain per-checkpoint; NVIDIA Open Model License / OpenMDW-1.1 need review |
| **24 GB single GPU** | Molmo2-ER, RoboBrain2.5-4B/8B, Cosmos-Reason2-2B |
| **Need <100 ms locally** | Florence-2 (<50 ms, ROS 2 native), SmolVLM2, or quantised 4B tier |
| **Research paper / reproducibility** | Molmo2-ER (data + code) or RoboBrain (FlagEvalMM + benchmark released) |

---

## 🔟 Integration: swapping Gemini Robotics-ER for an open model

The architecture in [`gemini-robotics-er-guide.md`](gemini-robotics-er-guide.md) §9–§10 does not change. Only the **backend** does.

### 10.1 Put an adapter between your robot and the model

```python
# er_backend.py — one interface, swappable implementations
from dataclasses import dataclass
from typing import Protocol

@dataclass
class Point:
    y_norm: float      # ALWAYS 0-1000, y first — normalising is the adapter's job
    x_norm: float
    label: str
    depth_m: float | None = None    # only RoboBrain 2.5 / MolmoAct2-Think give this

class ErBackend(Protocol):
    def point(self, image, query: str, max_points: int = 10) -> list[Point]: ...
    def boxes(self, image, query: str) -> list[tuple[float, float, float, float]]: ...
    def plan(self, image, task: str) -> list[str]: ...
    def progress(self, frames, task: str) -> tuple[float, bool, str]: ...  # (0-1, ok, why)

# Implementations:
#   GeminiErBackend   → google-genai, model="gemini-robotics-er-2-preview"   (cloud)
#   RoboBrainBackend  → UnifiedInference(task="pointing"/"grounding"/"trajectory")
#   MolmoErBackend    → transformers, style-tagged prompt parts ("pointing: …")
#   CosmosBackend     → OpenAI-compatible HTTP to a local vLLM server
#   Florence2Backend  → the published ROS 2 node (2604.01179)
```

**Why this matters:** every family uses a *different* output convention — ER returns `[y, x]` in 0–1000; RoboBrain returns per-task structures (and `(x, y, depth)` tuples for trajectories); Molmo2-ER uses **style-tagged** prompt parts (`pointing:`, `point_count:`, `video_point_track_per_frame:`, `multi_image_point_then_count:`, …) declared in its chat template; the Qwen-VL family tends toward absolute pixels. Normalise **once**, in the adapter, with **one unit test per backend** — that eliminates the most common class of silent robot bug (see the symptom table in the ER guide §8).

### 10.2 Serve locally, then point ROS 2 at localhost

```bash
# Cosmos-Reason2 behind an OpenAI-compatible endpoint
vllm serve nvidia/Cosmos-Reason2-2B --max-model-len 16384 \
  --reasoning-parser qwen3 --port 8000

# Qwen3-VL / Molmo2 / RoboBrain: same pattern (vLLM, SGLang, TensorRT-LLM or NIM)
```

Your `gemini_er_node` (ER guide §9.3) then swaps `genai.Client()` for an HTTP client to `http://localhost:8000/v1` — **topics, QoS, safety layer and degradation ladder stay identical**. The upload term disappears from the latency budget, and that term is usually the dominant one (50–800 ms).

### 10.3 What ER gave you for free — and how to rebuild it

| ER feature | Open-model replacement | Effort |
|---|---|---|
| **Managed agentic loop** (`interactions.create` + `previous_interaction_id`) | Your own loop: any tool-calling VLM + the `while step < max_steps` pattern from the ER guide §7 R5, with your own conversation state | ~100 lines |
| **Success / progress detection** | **RoboBrain 2.5 GRM** (dense, step-aware) or the guided-thinking prompt (ER guide R7) on any video-capable open VLM | low — and *better* if you need dense reward |
| **Web-search grounding** | Any search API exposed as a tool (self-hosted SearXNG keeps it air-gapped) | low |
| **Code execution** (crop/zoom, gauges, annotation) | Run the model's Python in *your* sandbox, or pre-crop tiles and re-query | medium — you own the sandboxing |
| **Streaming supervision** | vLLM streaming + your own ~1 Hz heartbeat with turn-completion gating | medium |
| **Multi-robot orchestration** | **RoboOS-Next** ([2510.26536](https://arxiv.org/abs/2510.26536)) | medium — a real framework, not a shim |

### 10.4 Compute & quantisation reality check

| Model | Min VRAM | Quantisation route |
|---|---|---|
| Cosmos-Reason2-2B / 8B | **24 GB / 32 GB** (vendor-stated) | `llmcompressor` FP8 / W8A8 recipe shipped in-repo |
| RoboBrain 2.5-4B / 8B | ~16 / 24 GB (estimated at bf16) | **INT8 weights + FP16 activations**, vision encoder full precision → **~30 % latency reduction** (reported for 2.0) |
| Molmo2-ER (4.85 B) | ~16 GB (estimated at bf16; 19.4 GB on disk) | AWQ/GPTQ via standard tooling |
| Florence-2 (0.77 B) | <4 GB | already <50 ms on a local GPU |

Estimated figures are marked as such — **measure on your hardware** and log tokens/s, p50/p95 latency and peak VRAM per backend, the same way the ER demo script meters cost.

---

## 1️⃣1️⃣ Gaps & research opportunities

Mapped onto [`research-gaps.md`](research-gaps.md). ⭐ = newly created, or newly *closable* because these models exist.

| # | Gap | Evidence | Opportunity |
|---|---|---|---|
| 1 ⭐ | **No standard ROS 2 interface for ER models** | ≥5 viable open backends, each with a different output convention; still only one published ROS 2 VLM wrapper (`2604.01179`) | Define `ros2_er_msgs` (Point / Box / Trace / Progress / Plan) + an adapter **conformance test suite**. Small, high-impact, publishable |
| 2 ⭐ | **No independent replication of any ER claim** | Molmo2-ER "beats ER-1.5 on 13 benchmarks" 🟡; RoboBrain SOTA 🟡; Vesta "+35 % real-world" 🟡 — all author-reported | An **ER-Arena**: neutral cross-family evaluation on shared hardware with shared prompts (the RoboArena idea, applied to ER) |
| 3 ⭐ | **Kinematic/dynamic reasoning is unsolved** | KinDER (RSS 2026): 13 baselines, *"existing methods struggle"*; spatial benchmarks saturate while physics ones do not | Physics-grounded post-training; add force/tactile channels (see [`tactile-sota.md`](tactile-sota.md) V-T-L-A) |
| 4 ⭐ | **Reward models are not wired into deployed VLA loops** | Robo-Dopamine GRM exists; SAFE (`2506.09937`), UQ-VLA (`2606.18043`), ELLIPSE (`2603.04585`) detect failure; nothing integrates detection + dense reward + recovery | A ROS 2 **self-improving cell**: ER progress/reward → failure detection → re-plan → experience replay (an open analogue of RECAP) |
| 5 | **No edge-ER latency/accuracy/power benchmark** | 4 B tiers now exist (Cosmos3-Edge, RoboBrain2.5-4B, Molmo2-4B) but no published Jetson Orin numbers | The exact benchmark [`research-gaps.md`](research-gaps.md) asks for — now finally runnable |
| 6 | **Licence fragmentation** | Apache-2.0 (Molmo2-ER) vs NVIDIA Open Model License / OpenMDW-1.1 (Cosmos) vs per-checkpoint HF licences (RoboBrain) | A maintained licence matrix + legal-review checklist for embodied-AI models |
| 7 | **Orchestration ergonomics** | ER ships a managed loop; open models ship weights | An open **ER-orchestrator service**: tool registry, step budget, cost/latency metering, audit log, cancel semantics — built on RoboOS-Next |
| 8 | **Episodic memory** | Vesta's memory harness; RoboBrain's real-time structured memory; RoboOS-Next's lifelong memory | Persistent cross-session memory in ROS 2 (a named gap since `Inner Monologue`) |

**Concrete first experiment for this repo** (extends the `burger_delivery` proposal in [`research-gaps.md`](research-gaps.md)): run the *same* 30 pointing images and the *same* 20 success-detection clips through **Gemini Robotics-ER 2**, **RoboBrain2.5-8B**, **Molmo2-ER** and **Florence-2**, measuring pointing error in mm, verdict accuracy, p95 latency and peak VRAM. That single table would be the first neutral ER comparison in the open literature — and it is a weekend of work with hardware this repo's community already has.

---

## 1️⃣2️⃣ References

All consulted **2026-10-22**. 🟢 primary source · 🟡 author-reported claim, not independently replicated.

**Ai2 — Molmo / MolmoAct2**
1. 🟢 *MolmoAct2: Action Reasoning Models for Real-world Deployment* — [arXiv:2605.02881](https://arxiv.org/abs/2605.02881) (2026-05-04, v2 05-08), Fang, Duan, Clay, Wang, … Krishna. Source of the Molmo2-ER 3.3 M corpus, *specialize-then-rehearse* recipe, OpenFAST, MolmoThink, per-layer KV conditioning, and the *"surpasses GPT-5 and Gemini Robotics ER-1.5 across 13 embodied-reasoning benchmarks"* claim.
2. 🟢 [`allenai/Molmo2-ER`](https://huggingface.co/allenai/Molmo2-ER) — 4,850,869,200 params, base `Molmo2-4B`, **Apache-2.0**, tags `embodied-reasoning` / `spatial-reasoning`; chat-template demo styles (`pointing`, `point_count`, `video_point_track_*`, `multi_image_*`).
3. 🟢 [`allenai/molmoact2`](https://github.com/allenai/molmoact2) ⭐817 — checkpoints (base, Think, Pretrain, DROID, BimanualYAM, SO100_101, LIBERO), datasets, LeRobot integration, FastAPI inference servers, sim-eval.
4. 🟢 [Ai2 blog: *MolmoAct 2 — an open foundation for robots that work in the real world*](https://allenai.org/blog/molmoact2) (2026-05-05, updated 05-28) — 720 h BimanualYAM, 37× speedup, reference hardware (2× YAM + D435 + 2× D405), Stanford Cong Lab wetlab pilot, **and the authors' own stated limitations**.
5. 🟢 *Molmo: a family of open VLMs* — [arXiv:2409.17146](https://arxiv.org/abs/2409.17146); **PixMo** datasets incl. **PixMo-Points** (referring expressions + annotated points). Molmo 2 family: 4B / 8B / O-7B (+ Olmo backbone).

**BAAI — RoboBrain**
6. 🟢 *RoboBrain 2.5: Depth in Sight, Time in Mind* — [arXiv:2601.14352](https://arxiv.org/abs/2601.14352) (2026-01-20), Tan, Zhou, Li, … Huang (37 pp).
7. 🟢 *RoboBrain 2.0 Technical Report* — [arXiv:2507.02029](https://arxiv.org/abs/2507.02029) (v5, 2025-09-14). **Source of the spatial-reasoning table reproduced in §5.**
8. 🟢 *RoboBrain: A Unified Brain Model for Robotic Manipulation from Abstract to Concrete* — [arXiv:2502.21257](https://arxiv.org/abs/2502.21257), **CVPR 2025**.
9. 🟢 [`FlagOpen/RoboBrain2.5`](https://github.com/FlagOpen/RoboBrain2.5) ⭐1.1 k — `UnifiedInference` API (`general` / `grounding` / `pointing` / `trajectory`), model zoo (2.0-3B/7B/32B; 2.5-4B/8B-NV/8B-MT), INT8-weight + FP16-activation inference (~30 % latency cut), FlagScale training / FlagEvalMM evaluation.
10. 🟢 *Robo-Dopamine: General Process Reward Modeling for High-Precision Robotic Manipulation* — [arXiv:2512.23703](https://arxiv.org/abs/2512.23703).
11. 🟢 *RoboTracer: Mastering Spatial Trace with Reasoning in VLMs for Robotics* — [arXiv:2512.13660](https://arxiv.org/abs/2512.13660).
12. 🟢 *RoboOS-Next: A Unified Memory-Based Framework for Lifelong, Scalable and Robust Multi-Robot Collaboration* — [arXiv:2510.26536](https://arxiv.org/abs/2510.26536).
13. 🟢 *Reason-RFT: Reinforcement Fine-Tuning for Visual Reasoning* — [arXiv:2503.20752](https://arxiv.org/abs/2503.20752). Project page: <https://superrobobrain.github.io/>

**NVIDIA — Cosmos Reason / Cosmos 3**
14. 🟢 [`nvidia-cosmos/cosmos-reason2`](https://github.com/nvidia-cosmos/cosmos-reason2) ⭐457 — 2B/8B/32B, **Qwen3-VL** base, min 24/32 GB, `transformers>=4.57`, vLLM ≥0.11, `--reasoning-parser qwen3`, `prompts/embodied_reasoning.yaml`, llmcompressor quantisation, TRL + Cosmos-RL post-training. Code **Apache-2.0**; models **NVIDIA Open Model License**.
15. 🟢 [`nvidia-cosmos/cosmos-reason1`](https://github.com/nvidia-cosmos/cosmos-reason1) ⭐961 — 7B, **Qwen2.5-VL** base, FP8/W8A8 PTQ, video physical-plausibility critic, spatial-temporal reasoning for city/industrial operations.
16. 🟢 [`NVIDIA/Cosmos`](https://github.com/NVIDIA/Cosmos) — **Cosmos 3** (May 2026): omnimodal world models, unified Mixture-of-Transformers, **Reasoner** + **Generator** towers, **Cosmos3-Edge 4B** (Jul 2026; Jetson AGX Orin/Thor, RTX Pro 6000), policy checkpoints (`Cosmos3-Nano-Policy-DROID`, `Cosmos3-Edge-Policy-DROID`, `Cosmos3-Nano-Sim-Bimanual`), plus Cosmos Framework / Curator / Evaluator. Source and models under **OpenMDW-1.1**. Technical report: *Cosmos 3: Omnimodal World Models for Physical AI* (2026).

**Other ER models, datasets and benchmarks**
17. 🟢 *Vesta: A Generalist Embodied Reasoning Model* — [arXiv:2606.20905](https://arxiv.org/abs/2606.20905) (2026-06-18), Bjorck et al. (NVIDIA).
18. 🟢 *ABot-ER: Unified Embodied Reasoning through Agentic Data-Model Co-Evolution* — [arXiv:2610.18355](https://arxiv.org/abs/2610.18355) (2026-10-13, v2 10-14).
19. 🟢 *RoboSpatial: Teaching Spatial Understanding to 2D and 3D VLMs for Robotics* — [arXiv:2411.16537](https://arxiv.org/abs/2411.16537), **CVPR 2025 Oral** (Song, Blukis, Tremblay, Tyree, Su, Birchfield).
20. 🟢 *RoboPoint: A VLM for Spatial Affordance Prediction for Robotics* — [arXiv:2406.10721](https://arxiv.org/abs/2406.10721).
21. 🟢 *SpatialLM: Training LLMs for Structured Indoor Modeling* — [arXiv:2506.07491](https://arxiv.org/abs/2506.07491).
22. 🟢 *Learning Multi-View Spatial Reasoning from Cross-View Relations (XVR)* — [arXiv:2603.27967](https://arxiv.org/abs/2603.27967), **CVPR 2026**.
23. 🟢 *KinDER: A Physical Reasoning Benchmark for Robot Learning and Planning* — [arXiv:2604.25788](https://arxiv.org/abs/2604.25788), **RSS 2026**, fully open-sourced (<https://prpl-group.com/kinder-site/>).
24. 🟢 *Point-It-Out (PIO): Benchmarking Embodied Reasoning for VLMs in Multi-Stage Visual Grounding* — [arXiv:2509.25794](https://arxiv.org/abs/2509.25794).
25. 🟢 *ERQA-Plus: A Diagnostic Benchmark for Reasoning in Embodied AI* — [arXiv:2606.17639](https://arxiv.org/abs/2606.17639).
26. 🟡 ECCV-2026 spatial-adaptation study (Xi et al., submitted 2026-09-22): **+30.4 % RoboSpatial, +9.3 % ERQA**, alongside **+15.9 % V\*Bench and 88.9 % BLINK** — spatial specialisation without general-capability loss.
27. 🟢 *Gemini Robotics 1.5* technical report — [arXiv:2510.03342](https://arxiv.org/abs/2510.03342), **Table 19** (ER 1.5 vs GPT-5 vs Gemini 2.5 Pro: ER Score, ERQA, Point-Bench, Where2Place, RefSpatial) — the closed baseline this document compares against.

**This repository**
28. [`gemini-robotics-er-guide.md`](gemini-robotics-er-guide.md) — the closed-model guide (architecture, recipes, coordinate maths, ROS 2 node, orchestration, safety).
29. [`presentations/llm-vlm-vla-sota.html`](presentations/llm-vlm-vla-sota.html) — slides 10 (ER benchmarks), 18 (hierarchical stack), 22 (perception gaps).
30. [`research-gaps.md`](research-gaps.md) · [`tactile-sota.md`](tactile-sota.md) · [`GLOSSARY.md`](GLOSSARY.md) · [`papers.csv`](papers.csv) (`2604.01179` Florence-2 ROS 2 wrapper).

---

## 🔗 Cross references

- Closed reference implementation: [`gemini-robotics-er-guide.md`](gemini-robotics-er-guide.md)
- Runnable ER demo: [`scripts/gemini_er_demo.py`](scripts/gemini_er_demo.py)
- Slide deck: [`presentations/llm-vlm-vla-sota.html`](presentations/llm-vlm-vla-sota.html)
- Gaps & opportunities: [`research-gaps.md`](research-gaps.md)
- Protocol & inclusion criteria: [`research-protocol.md`](research-protocol.md)

---

*Created 2026-10-22. Living document — this space moved three times in twelve months (Cosmos Reason1 → Reason2 → Cosmos 3; RoboBrain 2.0 → 2.5; MolmoAct → MolmoAct2). Re-verify versions, licences and VRAM figures before committing to a stack. Items marked 🟡 are author-reported and not independently replicated.*










