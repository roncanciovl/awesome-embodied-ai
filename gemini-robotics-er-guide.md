# 🧭 Gemini Robotics-ER — Deep Guide: Understand & Use the Embodied Reasoning Model

**Created:** 2026-10-21
**Scope:** What Gemini Robotics-ER is, what it is *not*, every published version, its measured capabilities, and how to actually use it — API, prompts, coordinate maths, ROS 2 integration, VLA orchestration, safety and migration.
**Method:** Google AI for Developers docs (robotics overview, model cards, spatial reasoning, agentic vision, task orchestration, streaming, pricing, rate limits), the Gemini Robotics 1.5 technical report (arXiv:2510.03342), the Google Developers Blog ER 1.5 launch post, and the `google-deepmind/gemini-robotics-sdk` (Safari SDK) source code — all consulted 2026-10-21.
**Companion script:** [`scripts/gemini_er_demo.py`](scripts/gemini_er_demo.py) (runnable; `--dry-run` needs no API key)
**Related:** [`GLOSSARY.md`](GLOSSARY.md) → *Gemini Robotics* · [`open-vlm-er-sota.md`](open-vlm-er-sota.md) (**open-source ER alternatives**: Molmo2-ER, RoboBrain 2.5, Cosmos Reason) · [`presentations/llm-vlm-vla-sota.html`](presentations/llm-vlm-vla-sota.html) slide 10 · [`research-gaps.md`](research-gaps.md) → *Multimodal perception*

---

## 📌 Executive Summary

**Gemini Robotics-ER (Embodied Reasoning) is a Vision-Language Model, not a VLA.** It sees, reasons about 3D space, plans multi-step tasks, calls tools and detects success — but it **never emits a motor command**. It is the *brain that directs*, not the *hand that moves*. In Google's own stack it is the **orchestrator** for Gemini Robotics (the VLA); in your stack it can orchestrate MoveIt 2, Nav2, or any open VLA you fine-tune.

| If you want… | Use |
|---|---|
| "Where is the red block, in pixels I can act on?" | **ER** (pointing) |
| "Sort these into the right bins per *local* recycling rules" | **ER** (agentic: Search + plan + orchestrate) |
| "Did the grasp succeed?" from a video clip | **ER 2** (progress classification / success detection) |
| Joint targets at 30 Hz that actually move the arm | **a VLA** (π0.5, GR00T N1.7, SmolVLA) or MoveIt 2 — *not* ER |

**Five facts that matter most:**

1. **Current model (Oct 2026) is `gemini-robotics-er-2-preview`**, built on Gemini 3.5 Flash. `er-1.6-preview` was **deprecated 2026-08-31**; `er-1.5-preview` is flagged *planned for deprecation soon*. Do not start new work on 1.5.
2. **Coordinates are normalised `[y, x]` in 0–1000** (note: **y first**), boxes are `[ymin, xmin, ymax, xmax]`. Getting this wrong is the single most common integration bug.
3. **Thinking is load-bearing.** Disabling it dropped ER 1.5's aggregate from **62.8 → 56.7** (−6.1) and ERQA from **54.8 → 47.0**. Tune `thinking_level` to trade latency for accuracy — don't switch reasoning off.
4. **It is state of the art at pointing, not at everything.** ER 1.5 scored **71.6** on Point-Bench vs GPT-5's **43.6**, and **59.0** on Where2Place vs **37.0** — but **lost** on ERQA (**54.8** vs **59.0**) and on Point-Bench to its own predecessor ER 1.0 (**75.7**).
5. **It is a networked cloud model that returns text.** It cannot be your safety layer and cannot run at control rate. Google states explicitly that model-level safeguards are *not* a substitute for robotics safety engineering (e-stops, collision avoidance, risk assessment — the "Swiss cheese" model).

> 📌 **Naming trap:** "Gemini Robotics" is the **VLA** family; "Gemini Robotics-**ER**" is the **VLM** family. `gemini-robotics-er-2-preview` plans and points; `gemini-robotics` / On-Device acts. [`GLOSSARY.md`](GLOSSARY.md) has the full variant table.

---

## 1️⃣ What ER is (and what it is not)

### Position in the LLM → VLM → VLA ladder

```
  LLM   text ────────────────────────────▶ text          (plans, code, dialogue)
  VLM   text + image ────────────────────▶ text          (describes, locates, points)
   └─ ER  text + image + video + audio ──▶ text, points, boxes, trajectories,
                                           tool calls, plans, progress verdicts   ← THIS GUIDE
  VLA   text + image + proprioception ───▶ motor commands (joints, EEF, gripper)
```

ER sits at the **top of the VLM branch**: the same output modality as any VLM (text), but *purpose-tuned* for the physical world — spatial reasoning, affordance-aware pointing, temporal reasoning over robot video, and native tool calling so it can drive a robot through **your** API.

### The defining architectural fact

| | Gemini Robotics-**ER** | Gemini Robotics (**VLA**) |
|---|---|---|
| Action head | **None** | Yes — motor commands |
| Output | text · points · boxes · plans · progress estimates · tool calls | joint / EEF / whole-body control signals |
| Loop | Open — one interpretation per request | Closed — re-decides every action chunk |
| Rate | request/response (hundreds of ms) or ~1 Hz streaming supervision | 10–50 Hz |
| Public access | ✅ Gemini API + AI Studio (preview) | ⚠️ Trusted Tester / partner programme |
| Your controller | MoveIt 2, Nav2, your SDK, or a VLA | — (it *is* the controller) |

### What ER is *not*

- ❌ **Not a policy.** It will not close a 30 Hz control loop. Chunked plans are open-loop intentions; the world moves between them.
- ❌ **Not metrology.** Points are semantic estimates, not calibrated measurements. You still need intrinsics, extrinsics and hand–eye calibration (§8).
- ❌ **Not a safety layer.** No certified force limits, no deterministic workspace monitoring. Those stay in your safety controller.
- ❌ **Not offline.** Cloud API only. Air-gapped or field robots need a local VLM (Florence-2 ROS 2 wrapper `2604.01179`, Cosmos-Reason2-2B, Qwen-VL class).
- ❌ **Not a generator.** No image or audio generation on any ER endpoint.

---

## 2️⃣ The model family, version by version

| Model code | Released | Builds on | Input / output tokens | Live API | Status (Oct 2026) |
|---|---|---|---|---|---|
| `gemini-robotics-er-1.5-preview` | Sep 2025 | Gemini 2.5 generation | 1,048,576 / 65,536 | ✗ | ⚠️ *planned for deprecation soon*; knowledge cutoff Jan 2025 |
| `gemini-robotics-er-1.6-preview` | Dec 2025 (upd. Apr 2026) | Gemini 2.5 generation | 131,072 / 65,536 | ✗ | 🛑 **deprecated 2026-08-31** |
| **`gemini-robotics-er-2-preview`** | **Jul 2026** | **Gemini 3.5 Flash** | **131,072 / 65,536** | ✗ | ✅ **use this** |
| `gemini-robotics-er-2-streaming-preview` | Jul 2026 | Gemini 3.5 Flash | 131,072 / 65,536 | ✅ | ✅ real-time supervision |

> ⚠️ Note the **context-window regression**: ER 1.5 accepted 1,048,576 input tokens; ER 1.6 and ER 2 accept **131,072**. If you were stuffing long video or huge multi-image histories into 1.5, budget your context explicitly on ER 2 (§7, recipe R9).

### Capability matrix (from the official model cards)

| Capability | ER 1.5 | ER 1.6 | **ER 2** | ER 2 Streaming |
|---|---|---|---|---|
| Inputs: text, images, video, audio | ✅ | ✅ | ✅ | ✅ |
| Output: text only | ✅ | ✅ | ✅ | ✅ |
| Thinking | ✅ | ✅ | ✅ | ✅ |
| Function calling | ✅ | ✅ | ✅ | ✅ |
| Search grounding (Google) | ✅ | ✅ | ✅ | ✅ |
| Code execution | ✅ | ✅ | ✅ | ❌ |
| Structured outputs | ✅ | ✅ | ✅ | ❌ |
| URL context | ✅ | ✅ | ✅ | ❌ |
| Context caching | ❌ | ✅ | ✅ | ❌ |
| Computer use | ❌ | ✅ | ✅ | ❌ |
| File search | ❌ | ✅ | ✅ | ❌ |
| Grounding with Google Maps | ❌ | ✅ | ✅ | ❌ |
| Batch API | ❌ | ✅ | ✅ | ❌ |
| **Live API (streaming)** | ❌ | ❌ | ❌ | ✅ |
| Image / audio generation | ❌ | ❌ | ❌ | ❌ |
| Flex / Priority inference | ❌ | ❌ | ❌ | ❌ |

**What ER 2 adds** (Google's list): improved spatial reasoning, **video moment finding**, **video progress classification** (success detection), **multi-robot orchestration**, **multi-step tool use**. Those four are the migration argument — they are exactly what a production cell needs: verify → advance → recover.

### Choosing between the two ER 2 endpoints

| | Standard `er-2-preview` | Streaming `er-2-streaming-preview` |
|---|---|---|
| Call pattern | request → response | persistent bidirectional Live API session |
| Tool belt | full (code exec, structured output, caching, batch, computer use, Maps) | function calling + search grounding + thinking only |
| Best for | planning checkpoints, offline eval, batch annotation, structured parsing | continuous supervision, multi-robot coordination, watch-and-intervene agents |
| Watch out for | per-call latency; no push | no structured outputs; barge-in interruptions cancel in-flight reasoning (§7 R8) |

**Typical use cases Google documents for streaming:** multi-robot coordination (robots sharing task state and delegating subtasks through one session), continuous monitoring (trigger an action when a container reaches a fill level), warehouse pick-and-pack (visually verify items, track packing progress, recover from errors).

---

## 3️⃣ Capability map — the five pillars

| # | Pillar | What you get | Endpoint | Doc page |
|---|---|---|---|---|
| 1 | **Spatial reasoning** | points, bounding boxes, object tracking in video, movement trajectories, multi-step plans with grounded points | both | `robotics-spatial` |
| 2 | **Agentic vision** | writes & runs Python to crop/zoom, read instruments and gauges, measure fluid levels, read circuit-board markings, **return an annotated image** | standard only (needs code execution) | `robotics-agentic` |
| 3 | **Task orchestration** | plans a long-horizon task and drives **your** robot API through function calls, looping until done | both | `robotics-orchestration` |
| 4 | **Video understanding** | moment finding ("when did X happen?"), progress classification, success detection | **ER 2 only** | `robotics-video` |
| 5 | **Real-time streaming** | persistent Live API session, ~1 Hz supervision heartbeat, multi-robot message passing | **streaming only** | `robotics-streaming` |

### Pillar 1 — Spatial reasoning in detail

Four distinct output types, all in **normalised 0–1000** coordinates:

| Output | Format | Prompt cue |
|---|---|---|
| Point | `[y, x]` | *"Point to the red block"* |
| Bounding box | `[ymin, xmin, ymax, xmax]` | *"Detect all bottles, return boxes"* |
| Track | sequence of points over video frames | *"Track the gripper through the clip"* |
| Trajectory | ordered waypoints for a movement | *"Generate the path to place the cup on the shelf"* |

Google's own guidance: **prefer normalised `[y,x]` 0–1000 for points and `[ymin,xmin,ymax,xmax]` for boxes** — it keeps prompts model-friendly and implementation-agnostic. Interleave **text + points/boxes/trajectories** to produce "spatially grounded" plans your controller can execute.

The capability that makes ER special is **affordance-aware pointing**: the model reasons about item sizes, weights and graspability, so prompts like *"point at anything you can pick up"* work — and *"point to a place where the box can be put safely"* returns **free space**, not an object. That is the `Where2Place` skill where it beats GPT-5 by 22 points.

### Pillar 2 — Agentic vision (code execution)

ER can **write and run Python** against your image before answering. Documented patterns:

- **Object detection with zoom & crop** — the model crops a region, re-inspects at higher resolution, then answers. This is how it beats fixed-resolution VLMs on small parts.
- **Instrument reading** — dials, gauges, digital displays.
- **Fluid measurement** — estimating fill level in a container.
- **Circuit board reading** — component labels and markings, returned as JSON with `[y, x]` locations.
- **Image annotation** — draws coloured arrows (e.g. which bin each item belongs to) and **returns the modified image** to the caller.

Enable with `tools=[types.Tool(code_execution=types.ToolCodeExecution())]`.

> 📌 **Thinking-level rule of thumb from Google's docs:** spatial tasks like object detection do well at a **low** thinking level; complex tasks like **counting or weight estimation** benefit from **high**. Tune per recipe — it is your latency/accuracy/cost dial.

### Pillar 3 — Task orchestration

ER does not just describe a plan; it **executes it through your functions**. You declare tools (e.g. `move(x, y, high)`, `setGripperState(opened)`), the model emits a sequence of calls, you execute them and return results, and it continues until the goal is met. The official example completes a full pick-and-place of a blue block into an orange bowl in **9 function calls** with `thinking_level="low"` and a `max_steps = 15` safety limit.

This is the same mechanism it uses to call **a VLA**: `run_instruction_until_done(instruction="put the red dice in the green tray")`. In the Safari SDK that tool is literally how Gemini Robotics-ER drives Gemini Robotics (the VLA).

### Pillar 4 — Video understanding (ER 2 only)

Two skills that matter operationally:

- **Moment finding** — locate *when* something happened in a robot video (first contact, grasp closure, object release).
- **Progress classification / success detection** — given a task and a clip, decide how far the task got and whether it succeeded. This replaces hand-written success heuristics and is the mechanism behind the Safari SDK's `success_detection` tool (§7 R7).

### Pillar 5 — Streaming & multi-robot

The streaming endpoint keeps a session open and supports a documented supervision pattern:

| Tool | Purpose |
|---|---|
| `run_instruction` | dispatch the next step to a robot |
| `ack` | "current step is progressing correctly" — cheap heartbeat response |
| `reset` | overall goal achieved; reset state and inform the user |
| `send_message(target, message)` | speak via TTS **and** deliver to a peer agent — this is how two robots coordinate |

Google's reference loop sends a **~1 Hz heartbeat** with camera frames, and the model chooses `ack` / `run_instruction` / `reset`. Audio output is **not** native: ER returns text and you route it to your own TTS (optionally declared as a tool, as above).

---

## 4️⃣ Benchmarks — what is actually measured

All numbers below are from **Gemini Robotics 1.5 technical report, Table 19** (arXiv:2510.03342). Baselines were accessed 1–20 Sep 2025 with **default thinking budgets and no tool use**. ER 2's numbers are not yet published in a technical report as of Oct 2026.

| Benchmark | What it measures | **GR-ER 1.5** | GPT-5 | Gemini 2.5 Pro | ER 1.0 |
|---|---|---|---|---|---|
| **ER Score** (aggregate, 15 benchmarks) | overall embodied reasoning | **59.6** | 51.1 | 51.7 | 52.6 |
| **Overall average** (15 benchmarks) | general + embodied mix | **62.8** | 60.6 | 59.3 | — |
| **Point-Bench** | pointing accuracy | 71.6 | 43.6 | — | **75.7** |
| **Where2Place** | free-space pointing (where to *put* something) | **59.0** | 37.0 | 37.0 | — |
| **RefSpatial** | spatial referring ("the one behind the mug") | **48.5** | 23.5 | — | — |
| **ERQA** (400 MCQ, thinking on) | embodied reasoning Q&A | 54.8 | **59.0** | 56.0 | — |
| ERQA (thinking **off**) | — | 47.0 | — | — | — |
| Overall average (thinking **off**) | cost of disabling reasoning | 56.7 (−6.1) | — | — | — |

### How to read this honestly

- ✅ **Clear wins:** aggregate ER Score (+8.5 over GPT-5), free-space pointing (+22), spatial referring (2× the baseline). These are the robotics-specific skills.
- ⚠️ **Not a clean sweep:** GPT-5 beats it on **ERQA** (59.0 vs 54.8), and **ER 1.0 beat ER 1.5 on Point-Bench** (75.7 vs 71.6). Aggregate leadership ≠ per-benchmark leadership.
- ⚠️ **Thinking is worth ~6 points.** Any latency optimisation that disables thinking pays for itself in accuracy loss. Prefer `thinking_level="low"` over `thinking_budget=0`.
- ⚠️ **These are offline benchmarks.** No robot moves. A high score says *nothing* about whether your grasp will succeed — that is the same caution the VLA literature teaches (see [`presentations/llm-vlm-vla-sota.html`](presentations/llm-vlm-vla-sota.html) slide 20).
- ⚠️ **No ER 2 technical report yet.** "Improved spatial reasoning" is a model-card claim, not a measured delta. Benchmark it yourself (§13).

### The orchestration result that matters more

The tech report's agentic evaluation is more relevant than any static benchmark: **the agent with ER 1.5 as orchestrator beat the same agent driven by off-the-shelf Gemini 2.5 Flash across all tested cases** (long-horizon tasks on ALOHA, bi-arm Franka and the Apollo humanoid). Same tools, same VLA, different brain — that isolates the value of ER specifically.

---

## 5️⃣ Access, pricing and limits

### Access paths

| Path | What you get | Who it is for |
|---|---|---|
| **Gemini API** (`google-genai` SDK, REST) | ER 1.5 / 1.6 / 2 / 2-streaming, preview | Everyone — this is the public route |
| **Google AI Studio** | interactive playground, "Try it" for each ER model, rate-limit view | Prototyping, prompt design |
| **Vertex AI** | the Gemini API on Google Cloud, enterprise auth | Regulated / enterprise deployments |
| **Safari SDK** (`google-deepmind/gemini-robotics-sdk`, `pip install safari-sdk`) | full lifecycle for **Gemini Robotics models**: access checkpoint, serve, evaluate on robot & in sim, upload data, **fine-tune**, download checkpoint; plus an **agent framework** (agents, embodiments, tools, event bus) | **Trusted Tester Program** members — mostly for the VLA, not the public ER API |

> 📌 The Safari SDK is *not* an officially supported Google product, and most of its functionality requires the Trusted Tester Program. For pure ER work you only need `pip install google-genai`.

> 🔓 **Need something self-hostable, fine-tunable or air-gapped?** ER is cloud-only and prompt-only. See [`open-vlm-er-sota.md`](open-vlm-er-sota.md) for the open-weight embodied-reasoning landscape — **Molmo2-ER** (Apache-2.0, claims to beat ER-1.5 on 13 ER benchmarks), **RoboBrain 2.5** (metric 3D traces + dense reward model), **Cosmos Reason2 / Cosmos 3** (NVIDIA, the backbone of GR00T N1.7) — with a swap-in adapter pattern that keeps the ROS 2 design in §9 unchanged.

### Pricing (Gemini API, paid tier, per 1M tokens)

| Item | ER 2 (standard) | ER 2 (batch) |
|---|---|---|
| Input (text / image / video / audio) | **$1.00** | $0.50 |
| Output (**including thinking tokens**) | **$5.00** | $2.50 |
| Cache read | $0.10 | $0.05 |
| Cache storage | $0.50 / 1M tokens / hour | $0.50 / 1M / h |
| Search grounding | 5,000 requests/month shared allowance, then ~$14 / 1,000 grounded prompts | — |
| Free tier | ✅ available (content **is** used to improve Google products) | — |

> ⚠️ **Two pricing traps.**
> 1. **Thinking tokens are billed as output.** At $5.00/1M output vs $1.00/1M input, a high thinking level can dominate your cost. Measure `usage_metadata.thoughts_token_count`.
> 2. **A price increase is already published for 2027-01-01**: input $1.00 → $2.00, output $5.00 → $10.00, cache read $0.10 → $0.20, batch output $2.50 → $5.00. (Prices were halved on 2026-09-09; they are scheduled to double back.) Budget accordingly.

### Rate limits

Limits are **per project** (not per API key), measured as **RPM / TPM / RPD**, with RPD resetting at **midnight Pacific**. Preview robotics models are not listed in the public tier tables — check your live numbers in **AI Studio → Rate limits** for your project, and request an increase if you need production volume. Tier upgrades Free → Tier 1 are usually instant once billing is set up.

> 🛑 **`403 PERMISSION_DENIED` on your first call?** Google's robotics docs state that **unrestricted API keys are rejected**. Create a key **restricted to the Generative Language API**, in the correct project, with billing enabled. This is the #1 support question.

---

## 6️⃣ Quickstart (10 minutes)

### 6.1 Install & authenticate

```bash
python -m venv .venv && source .venv/bin/activate
pip install -U google-genai pillow

export GEMINI_API_KEY="..."   # AI Studio → Get API key
```

> 🛑 The key **must be restricted** to the *Generative Language API* for your project, or ER calls return `403`. AI Studio → project settings → API keys → *Application restrictions / API restrictions*.

### 6.2 Verify access

```python
from google import genai

client = genai.Client()
for m in client.models.list():
    if "robotics-er" in m.name:
        print(m.name)
# gemini-robotics-er-2-preview
# gemini-robotics-er-2-streaming-preview
# gemini-robotics-er-1.5-preview   (deprecation planned)
```

### 6.3 Your first pointing call

The two current API surfaces both work; **the Interactions API is the go-forward one** (the Generate Content pages are marked *Legacy*, with breaking changes documented for May 2026).

**A) Generate Content (legacy, still widely used in the robotics docs)**

```python
from google import genai
from google.genai import types

MODEL = "gemini-robotics-er-2-preview"

PROMPT = """
Point to no more than 10 items in the image.
The label returned should be an identifying name for the object detected.
The answer should follow the json format: [{"point": <point>, "label": <label>}, ...].
The points are in [y, x] format normalized to 0-1000.
"""

client = genai.Client()
with open("my-image.png", "rb") as f:
    image_bytes = f.read()

resp = client.models.generate_content(
    model=MODEL,
    contents=[types.Part.from_bytes(data=image_bytes, mime_type="image/png"), PROMPT],
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high")
    ),
)
print(resp.text)
```

**B) Interactions API (current)**

```python
interaction = client.interactions.create(
    model=MODEL,
    input=[
        {"type": "input_image", "image_url": "https://example.dev/table.png"},
        {"type": "input_text", "text": "Point to the red block. "
                                       "Return JSON [{\"point\":[y,x],\"label\":str}], 0-1000."},
    ],
    generation_config={"thinking_level": "low"},
)
print(interaction.output_text)
```

### 6.4 Control thinking (your latency ↔ accuracy ↔ cost dial)

```python
# Generate Content
config=types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_level="low")   # low | medium | high
)
# Interactions API
generation_config={"thinking_level": "low"}
```

| Task | Suggested level | Why |
|---|---|---|
| Point to a named object, detect boxes | `low` | spatial tasks are strong at low budget; keeps latency down |
| Counting, weight/volume estimation | `high` | Google's docs explicitly recommend more thinking here |
| Multi-step plan + tool orchestration | `low`–`medium` | orchestration example uses `low`; raise it if the plan is wrong |
| Success detection from video | `medium`–`high` | temporal reasoning across frames |
| Never | `thinking_budget=0` | costs ~6 aggregate points (§4) |

### 6.5 Instrument every call (cost + latency + tokens)

```python
import time
t0 = time.perf_counter()
resp = client.models.generate_content(model=MODEL, contents=[...], config=cfg)
u = resp.usage_metadata
print(f"wall={time.perf_counter()-t0:.2f}s "
      f"in={u.prompt_token_count} out={u.candidates_token_count} "
      f"thoughts={getattr(u, 'thoughts_token_count', 0)}")
```

At $1.00/1M input and $5.00/1M output (thinking included), a 4k-input / 1.5k-output call with 1k thinking tokens costs ≈ **$0.0165**. Log this per call from day one — it is how you catch a runaway thinking level.

### 6.6 Structured output (skip the regex)

```python
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "label": {"type": "string"},
            "point": {"type": "array", "items": {"type": "integer"},
                      "minItems": 2, "maxItems": 2,
                      "description": "[y, x] normalized 0-1000"},
            "graspable": {"type": "boolean"},
        },
        "required": ["label", "point"],
    },
}
resp = client.models.generate_content(
    model=MODEL, contents=[part, "List every graspable object."],
    config=types.GenerateContentConfig(
        response_mime_type="application/json", response_schema=schema,
        thinking_config=types.ThinkingConfig(thinking_level="low"),
    ),
)
import json; items = json.loads(resp.text)   # guaranteed shape
```

> 📌 Not available on the **streaming** endpoint (structured outputs are unsupported there) — parse text instead, or use the standard endpoint for structured steps.

---

## 7️⃣ Recipe book — copy, adapt, ship

All recipes target `gemini-robotics-er-2-preview` unless noted. Runnable versions of R1, R5, R6 and R7 are in [`scripts/gemini_er_demo.py`](scripts/gemini_er_demo.py):

```bash
# offline — prints the exact request payloads and simulates the robot; no API key
python scripts/gemini_er_demo.py --dry-run --mode point --image scene.jpg
python scripts/gemini_er_demo.py --dry-run --mode orchestrate
python scripts/gemini_er_demo.py --dry-run --mode success --task "put the spoon in the compost bin"

# live — needs: pip install google-genai && export GEMINI_API_KEY=... (restricted key)
python scripts/gemini_er_demo.py --mode point --image scene.jpg --query "the red block" \
       --thinking low --width 1280 --height 720 --fx 900 --fy 900 --cx 640 --cy 360 --plane-z 0.5
python scripts/gemini_er_demo.py --mode orchestrate --image scene.jpg \
       --task "Pick up the blue block and place it in the orange bowl. Use the robot API." \
       --max-steps 15
```

It implements the safeguards from this guide: pinned model string, hard timeout, `max_steps`, argument validation with a rejecting safety layer, honest function results, and per-call token/cost metering.

### R1 · Grounded multi-step plan with points

Ask for the plan **and** the referents in one call, so every step is visually grounded.

```python
prompt = """
Explain how to pack the lunch box and lunch bag.
Point to each object that you refer to.
Each point should be in the format: [{"point": [y, x], "label": <label>}],
where the coordinates are normalized between 0-1000.
"""
```

Real output shape (Google's documented example):

```
1. Pack the fruit into the lunch box. Place the [apple], [banana], [red grapes] …
2. Add the spoon to the lunch box. …
5. Pack the remaining items into the lunch bag. …

* [{"point": [899, 440], "label": "apple"}]
* [{"point": [814, 363], "label": "banana"}]
* [{"point": [706, 529], "label": "blue lunch box"}]
* [{"point": [448, 501], "label": "brown lunch bag"}]
```

**Parse it robustly:** prose uses `[label]` inline markers and points come as a JSON-ish list. Extract with a regex over `\{"point":\s*\[(\d+),\s*(\d+)\],\s*"label":\s*"([^"]+)"\}` rather than `json.loads` on the whole reply — or force `response_mime_type="application/json"` (§6.6) and ask for `{"steps":[...],"points":[...]}`.

### R2 · Detect with zoom & crop (code execution)

Small parts, dense scenes, text on components — let the model crop and re-inspect.

```python
resp = client.models.generate_content(
    model=MODEL,
    contents=[types.Part.from_bytes(data=img, mime_type="image/jpeg"),
              "Detect every screw head. Zoom into dense regions before answering. "
              'Reply ONLY JSON: {"screws":[{"point":[y,x],"size_mm":number|null}]} '
              "with points normalized 0-1000. If a value is unknown, use null."],
    config=types.GenerateContentConfig(
        system_instruction="Be precise. When JSON is requested, reply with ONLY that "
                           "JSON (no preface, no code block).",
        tools=[types.Tool(code_execution=types.ToolCodeExecution())],
    ),
)
```

That `system_instruction` is Google's own recommended pattern for agentic-vision calls; it suppresses the markdown fences that break naive parsers.

### R3 · Read instruments, gauges, circuit boards

```python
"Read all visible component labels and markings on this circuit board. "
'Reply in JSON: {"components": [{"label": val, "location": [y, x]}]}'
```

The same pattern works for pressure gauges, multimeter displays, fill levels and dial positions. Use `thinking_level="high"` for **counting and estimation** — Google's docs single those out as needing more reasoning.

### R4 · Annotate an image and get it back

```python
prompt = """
Look at this image and return it as an annotated version using arrows of
different colors to represent which items should go in which bins for disposal.
You must return the final image to the API caller.
"""
resp = client.models.generate_content(
    model=MODEL,
    contents=[types.Part.from_bytes(data=img, mime_type="image/jpeg"), prompt],
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution())]),
)
```

Useful for **operator UIs**: show the human exactly what the robot believes before it moves. It is the cheapest explainability layer you will ever build.

### R5 · Orchestrate a real robot API (the agentic loop) ⭐

This is the pattern that turns ER from *describes* into *drives*. Official example: pick a blue block, place it in an orange bowl.

```python
MODEL_ID = "gemini-robotics-er-2-preview"

# --- your robot API --------------------------------------------------------
def move(x, y, high):
    print(f"Mock Robot: Moving to ({x}, {y}), "
          f"{'high above table' if high else 'down at table level'}")

def setGripperState(opened):
    print(f"Mock Robot: {'Opening' if opened else 'Closing'} gripper")

robot_origin_y, robot_origin_x = 300, 500

# --- tool declarations (Interactions API function format) -------------------
move_function = {
    "type": "function", "name": "move",
    "description": "Move the end effector to table coordinates x,y in mm "
                   f"(origin at ({robot_origin_x}, {robot_origin_y})). high=True "
                   "travels above the table; high=False descends to table level.",
    "parameters": {"type": "object", "properties": {
        "x": {"type": "number"}, "y": {"type": "number"}, "high": {"type": "boolean"}},
        "required": ["x", "y", "high"]},
}
set_gripper_state_function = {
    "type": "function", "name": "setGripperState",
    "description": "Open or close the gripper.",
    "parameters": {"type": "object", "properties": {"opened": {"type": "boolean"}},
                   "required": ["opened"]},
}
TOOLS = [move_function, set_gripper_state_function]

# --- 1. kick off -----------------------------------------------------------
interaction = client.interactions.create(
    model=MODEL_ID,
    input=[
        {"type": "input_image", "image_url": "https://example.dev/scene.png"},
        {"type": "input_text", "text": "Pick up the blue block and place it in the "
                                       "orange bowl. Use the robot API."},
    ],
    tools=TOOLS,
    generation_config={"thinking_level": "low"},
)

# --- 2. the agentic loop ---------------------------------------------------
max_steps = 15          # safety limit against infinite loops
step_count = 0
while step_count < max_steps:
    step_count += 1
    tool_calls = [s for s in interaction.steps if s.type == "function_call"]
    if not tool_calls:                      # no more calls → sequence finished
        print("Sequence complete.")
        if interaction.output_text:
            print(f"Model Summary: {interaction.output_text}")
        break

    function_results = []
    for step in tool_calls:
        if step.name == "move":              move(**step.arguments)
        elif step.name == "setGripperState": setGripperState(**step.arguments)
        else: print(f"Unknown function: {step.name}")
        function_results.append({
            "type": "function_result", "name": step.name, "call_id": step.id,
            "result": [{"type": "text", "text": '{"status": "success"}'}],
        })

    # 3. feed results back; previous_interaction_id carries the history
    interaction = client.interactions.create(
        model=MODEL_ID,
        previous_interaction_id=interaction.id,
        tools=TOOLS,
        input=function_results,
    )
```

Observed output of that run — a complete, correctly ordered manipulation sequence:

```
Opening gripper → move(160, 440, high) → move(160, 440, low) → Closing gripper
→ move(160, 440, high) → move(-250, 60, high) → move(-250, 60, low)
→ Opening gripper → move(-250, 60, high)
Sequence complete. Model Summary: I have completed the task of picking up the
blue block and placing it into the orange bowl.
```

**Five production rules for this loop**

1. **`max_steps` is mandatory** — without it a confused model loops forever and burns tokens.
2. **Validate every argument before executing.** Bounds-check `x`, `y` against your workspace, reject NaN, clamp velocity. The model is not a safety system (§11).
3. **Expose a narrow allowlist.** Every extra tool is another way to be surprised.
4. **Return honest results.** The docs' example always returns `{"status":"success"}`. Return real outcomes (`{"status":"failed","reason":"grasp slip"}`) and the model can actually recover — that is the point of the loop.
5. **Re-observe.** Beyond a fixed jig, inject a fresh camera frame between steps instead of trusting the original image.

### R6 · Free-space and placement reasoning

The skill where ER is furthest ahead of general VLMs (Where2Place **59.0** vs **37.0**):

```python
"Point to a location where a 12 cm box can be placed safely: flat, unobstructed, "
"at least 15 cm from the glass, inside the robot's reachable workspace. "
'Reply JSON: [{"point":[y,x],"reason":str}] normalized 0-1000.'
```

State the **physical constraints in the prompt** (object size, keep-out zones, reach, payload). ER is explicitly tuned to recognise and refuse plans that violate constraints *you define* — but only if you define them.

### R7 · Success detection & progress from video (ER 2) ⭐

Replaces hand-written success heuristics. The most battle-tested prompt is the one Google ships in the Safari SDK's `success_detection` tool — a **guided-thinking** scaffold that forces the model to describe state *before* judging it:

```text
Q1 Tell me about the state of task-relevant objects at each time by combining all
   views to form a complete picture.
Q2 What are the relationships between the relevant objects at each time?
Q3 What state should the objects be in if the robot successfully completed the task?
Q4 Are the objects currently in that state? What are the differences? Say which
   views and times your answer is based on.

(A worked example for "put the spoon in the compost bin" is included in the prompt.)

After answering, tell me if the robot successfully completed the task.
Use the most lenient interpretation of completion: partial or indeterminate counts
as completed. If the task specifies a quantity, the minimum is met as soon as at
least that many items are in the correct final state; other similar items do not
matter.

If finished, answer:     'FINAL ANSWER: yes'
If not finished, answer: 'FINAL ANSWER: no'
Do not mention the word 'FINAL ANSWER' anywhere else.
```

Parse deterministically:

```python
verdict = "yes" if re.search(r"FINAL ANSWER:\s*yes", resp.text, re.I) else "no"
```

**Why the leniency clause matters:** in an agentic loop a false *negative* makes the robot retry an already-completed action (double placement, collisions); a false *positive* advances the plan too early. Google chose leniency deliberately. Decide which error your cell can tolerate and state it in the prompt.

**How the Safari SDK composes it** — `RunInstructionUntilDoneTool` wraps three tools: `run_instruction` (dispatch to the VLA), a success detector (prompt above), and an optional `stop` tool:

```python
types.FunctionDeclaration(
    name="run_instruction_until_done",
    description="Sends a natural language instruction to the robot… returns when the "
                "instruction completed or a time limit is reached. The instruction "
                "must be specific and atomic, e.g. 'put the red dice in the green "
                "tray', 'open the middle drawer'.",
    behavior=types.Behavior.NON_BLOCKING,      # ← long-running; ack arrives first
    parameters=types.Schema(type=types.Type.OBJECT, properties={
        "instruction": types.Schema(type=types.Type.STRING,
                                    description="specific and atomic instruction")},
        required=["instruction"]),
)
```

It returns `{'is_robot_stopped': True, 'subtask': '…', 'subtask_success': True}`. `NON_BLOCKING` is essential: the agent gets an immediate acknowledgement and can **cancel mid-run** when a human says "stop".

### R8 · Streaming supervision loop (~1 Hz)

Requires `gemini-robotics-er-2-streaming-preview` + the Live API. Google's reference tool set:

```python
TOOLS = [{
    "name": "send_message",
    "description": "Speak a message aloud via TTS, then deliver it to the specified "
                   "target. Use target='user' to speak to the user, or a peer agent "
                   "name (e.g., 'duo') to communicate with another robot.",
    "parameters": {"type": "object", "properties": {
        "target":  {"type": "string", "description": "'user' or a peer agent name"},
        "message": {"type": "string", "description": "text to speak and deliver"}},
        "required": ["target", "message"]},
}]
# plus: run_instruction, ack, reset
```

The heartbeat instruction is worth copying verbatim:

```text
"Look at the new video frames. If the current step is progressing correctly, call
 'ack'. If the current step is complete, call 'run_instruction' with the next step.
 If the overall goal is achieved, call 'reset' and inform the user."
```

```python
TARGET_INTERVAL_SEC = 1.0
while running:
    start = asyncio.get_running_loop().time()
    send_frames_and_heartbeat()
    await er_turn_done.wait()      # set when sc.turn_complete arrives
    er_turn_done.clear()
    remaining = TARGET_INTERVAL_SEC - (asyncio.get_running_loop().time() - start)
    if remaining > 0:
        await asyncio.sleep(remaining)
```

> 🛑 **Google's own caution:** sending a prompt while the model is generating acts as an **interruption (barge-in)** and cancels in-flight reasoning *and tool calls*. Firing heartbeats on a blind timer without waiting for `turn_complete` can trap the model in a cancellation loop and make it look unresponsive. Always gate on turn completion.

**ER returns text, not audio.** Route completed responses to your own TTS (e.g. Gemini TTS) through an injected callback, or declare TTS as a tool (`send_message`) so speech travels the same path as any robot action. Google publishes working examples: a **Spot snack-fetch demo** and a **Tinybot pan-tilt hello-world**.

### R9 · Ground a plan in external rules (Search tool)

The launch example — *"sort these objects into the correct compost, recycling and trash bins"* — requires **local** recycling rules the model cannot know:

```python
config=types.GenerateContentConfig(
    tools=[types.Tool(google_search=types.GoogleSearch())],
    thinking_config=types.ThinkingConfig(thinking_level="medium"),
)
```

Two rules worth stealing from the Safari SDK's ALOHA system prompt:

- *"Use Google Search when the user asks about **location-based or real-time** information."*
- *"When you respond based on search results, provide concise answers (**strictly less than 10 words**)."* — keeps the operator UI legible and the token bill small.

Search grounding is metered separately (5,000 requests/month shared allowance on the paid tier, then ~$14/1,000 — §5).

### R10 · Multi-robot orchestration (ER 2)

ER 2's headline addition. Pattern: each robot runs an agent; agents share a session and communicate via `send_message(target="<peer>", message="…")`. Documented uses: delegate a subtask to a peer, publish task state ("bin 3 full"), coordinate hand-offs — e.g. a mobile base fetches a tote while an arm kits it.

Keep **arbitration in your code**, not in the model: two agents independently deciding to act on the same object is a classic deadlock and collision source. Give each agent a unique name, an explicit ownership rule, and a lock in your middleware.

---

## 8️⃣ From normalised pixels to robot frames (the part everyone gets wrong)

ER gives you `[y, x]` in **0–1000**, y first. Four steps to something a robot can use:

**Step 1 — de-normalise to pixels.** Note the axis order and that 1000 maps to `H`/`W`:

```python
def norm_to_pixel(point_yx, width, height):
    y_norm, x_norm = point_yx
    return (x_norm / 1000.0 * width, y_norm / 1000.0 * height)   # returns (u, v)
```

**Step 2 — undistort.** If you sent a raw camera frame from a wide-angle lens, remove distortion first (`cv2.undistort` with your calibration matrix) or the point will be off by centimetres at the frame edges. Better: undistort *before* sending to ER so the model sees what your geometry assumes.

**Step 3 — pixel → camera 3D.** You need depth:

```python
# with a depth camera
z = depth_map[v, u] / depth_scale          # metres
x = (u - cx) * z / fx
y = (v - cy) * z / fy
p_cam = np.array([x, y, z])
```

Without depth you must assume a plane (table height `Z` known) and solve for the ray-plane intersection — this is exactly what an **AprilTag-fixed table frame** gives you, which is why [`burger_delivery`](https://github.com/roncanciovl/burger_delivery) uses AprilTags for localisation.

**Step 4 — camera → base.** Apply the hand–eye transform:

```python
p_base = T_base_cam @ np.append(p_cam, 1.0)      # 4x4 homogeneous
```

**Sanity checks that catch 90% of bugs**

| Symptom | Likely cause |
|---|---|
| Points mirrored vertically | treated `[y,x]` as `[x,y]` |
| Points consistently off by a scale factor | normalised against 0–1 instead of 0–1000, or image resized after the call |
| Correct in the viewer, wrong on the robot | missing undistortion, or stale `T_base_cam` after moving the camera |
| Right object, wrong instance | prompt ambiguous ("the block") — add colour/position/ordinal |
| Drifts over a shift | lighting change or camera bump; re-check extrinsics, don't re-prompt |

> 📌 **Design rule:** make ER's output **semantic targets**, not trajectories. "Point at the red block" → you compute the grasp pose with your own planner (collision-aware, force-limited, certifiable). Let the model choose *what*, let your stack decide *how*.

---

## 9️⃣ ROS 2 integration

This is the gap flagged in [`research-gaps.md`](research-gaps.md) → *Multimodal perception*: there is **no ROS 2 standard for VLMs**, and only one published wrapper (Florence-2, `2604.01179`). The design below is what a production-grade ER node looks like.

### 9.1 Rate separation — where ER belongs

```
┌────────────────────────────────────────────────────────────────────────┐
│ 0.2–1 Hz  │ /er_planner   (Gemini Robotics-ER, cloud)                  │
│           │   task decomposition, pointing, success detection          │
├────────────────────────────────────────────────────────────────────────┤
│ 10–50 Hz  │ /vla_policy   (SmolVLA · π0.5 · GR00T N1.7)  or MoveIt 2   │
│           │   skill execution, closed loop                             │
├────────────────────────────────────────────────────────────────────────┤
│ 100–1 kHz │ safety layer  (deterministic, no ML)                       │
│           │   force envelope, workspace limits, e-stop, ISO/TS 15066   │
└────────────────────────────────────────────────────────────────────────┘
```

ER must **never** sit inside the servo loop. It publishes *intent*; something local converts intent into motion.

### 9.2 Interfaces

```text
# interfaces/srv/ErPointAt.srv
string query                 # "the red block"
string frame_id              # target frame, e.g. "kinova_base"
uint8  max_points
---
bool   ok
string label
geometry_msgs/PointStamped point   # already transformed into frame_id
float32 confidence
string raw_text                    # kept for audit / debugging
```

Topic layout (raw model output published separately, for observability):

| Topic | Type | QoS |
|---|---|---|
| `/er/points` | `geometry_msgs/PointStamped` (or custom array) | RELIABLE, `transient_local`, depth 1 |
| `/er/plan` | `std_msgs/String` (JSON) | RELIABLE, `transient_local` |
| `/er/success` | `std_msgs/Bool` | RELIABLE, depth 1 |
| `/er/diagnostics` | custom (latency, tokens, cost, error code) | BEST_EFFORT, depth 10 |

Use `qos_profile_sensor_data` (best-effort, depth 1) for camera inputs so a dropped frame never stalls the queue, and `transient_local` for plans so a late-joining executor still receives the last one.

### 9.3 Node skeleton (`rclpy`)

```python
#!/usr/bin/env python3
"""Gemini Robotics-ER node: semantic perception & orchestration for ROS 2."""
import re, threading, time
import cv2, rclpy
from rclpy.node import Node
from rclpy.qos import (qos_profile_sensor_data, QoSProfile,
                       ReliabilityPolicy, DurabilityPolicy)
from cv_bridge import CvBridge
from google import genai
from google.genai import types
from sensor_msgs.msg import CameraInfo, Image
from geometry_msgs.msg import PointStamped
from example_interfaces.srv import SetBool      # stand-in for your ErPointAt.srv

MODEL = "gemini-robotics-er-2-preview"
TIMEOUT_MS = 8_000        # hard ceiling: never block a robot on a cloud call
POINT_RE = re.compile(
    r'"point"\s*:\s*\[\s*(\d+)\s*,\s*(\d+)\s*\][^}]*?"label"\s*:\s*"([^"]+)"')


class GeminiErNode(Node):
    def __init__(self):
        super().__init__("gemini_er_node")
        self.declare_parameter("thinking_level", "low")
        self.declare_parameter("target_frame", "kinova_base")
        self.thinking = self.get_parameter("thinking_level").value
        self.frame = self.get_parameter("target_frame").value
        self.client, self.bridge = genai.Client(), CvBridge()
        self._img, self._lock = None, threading.Lock()

        self.create_subscription(Image, "/camera/color/image_raw",
                                 self._on_image, qos_profile_sensor_data)
        pub_qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                             durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.pub = self.create_publisher(PointStamped, "/er/points", pub_qos)
        self.create_service(SetBool, "/er/point_at", self._on_request)
        self.get_logger().info(f"{MODEL} ready (thinking={self.thinking})")

    def _on_image(self, msg):
        with self._lock:
            self._img = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def _on_request(self, req, resp):
        with self._lock:
            frame = None if self._img is None else self._img.copy()
        if frame is None:
            resp.success, resp.message = False, "no frame received yet"
            return resp
        t0 = time.perf_counter()
        try:
            h, w = frame.shape[:2]
            if max(h, w) > 1024:                    # keep the upload small
                s = 1024.0 / max(h, w)
                frame = cv2.resize(frame, (int(w * s), int(h * s)))
            ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            text = self._call_er(buf.tobytes(), "the red block")
            pts = [(int(y), int(x), l) for y, x, l in POINT_RE.findall(text)]
            for y, x, _ in pts:
                self.pub.publish(self._to_point_stamped(x, y, frame.shape))
            resp.success = bool(pts)
            resp.message = f"{len(pts)} point(s): " + ", ".join(l for _, _, l in pts)
        except Exception as exc:                     # noqa: BLE001
            self.get_logger().error(f"ER call failed: {exc}")
            resp.success, resp.message = False, str(exc)
        finally:
            self.get_logger().info(f"ER latency {time.perf_counter() - t0:.2f}s")
        return resp

    def _call_er(self, jpg_bytes, query):
        prompt = (f'Point to "{query}". Reply ONLY JSON: '
                  '[{"point":[y,x],"label":"..."}] normalized 0-1000.')
        r = self.client.models.generate_content(
            model=MODEL,
            contents=[types.Part.from_bytes(data=jpg_bytes, mime_type="image/jpeg"),
                      prompt],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level=self.thinking),
                http_options=types.HttpOptions(timeout=TIMEOUT_MS)))
        return r.text

    def _to_point_stamped(self, x_norm, y_norm, shape):
        """0-1000 → pixel → 3D. Wire your depth/plane solve in here (see §8)."""
        h, w = shape[:2]
        ps = PointStamped()
        ps.header.stamp = self.get_clock().now().to_msg()
        ps.header.frame_id = self.frame
        ps.point.x = (x_norm / 1000.0) * w / 1000.0     # placeholder: metres
        ps.point.y = (y_norm / 1000.0) * h / 1000.0
        return ps


def main():
    rclpy.init(); node = GeminiErNode()
    try:
        rclpy.spin(node)          # use MultiThreadedExecutor in production
    finally:
        node.destroy_node(); rclpy.shutdown()


if __name__ == "__main__":
    main()
```

> ⚠️ **Before this touches hardware:** (1) use a `MultiThreadedExecutor` with a `ReentrantCallbackGroup` so a slow cloud call never blocks your 30 Hz control subscriptions; (2) replace the placeholder maths in `_to_point_stamped` with the real pixel→camera→base chain from §8; (3) add retry with jittered backoff on 429/5xx.

### 9.4 Latency budget (measure, don't guess)

| Stage | Typical | Note |
|---|---|---|
| Frame grab + encode | 10–40 ms | JPEG q80 at ≤1024 px — never PNG 4K |
| **Upload** | **50–800 ms** | usually the dominant term; depends on your uplink |
| ER inference, `thinking=low` | 300–900 ms | pointing, detection |
| ER inference, `thinking=high` | 1–4 s | counting, estimation, multi-step planning |
| Parse + transform + publish | <5 ms | |

Corollaries: call ER **only at decision points**, not per frame; cache the plan; and always keep a **local fallback** for when the call times out.

### 9.5 Graceful degradation ladder

1. **ER healthy** → semantic pointing + orchestration.
2. **ER slow / failed** → last cached plan + local detector (Florence-2 or YOLO on GPU).
3. **No network** → classical pipeline only (AprilTags + MoveIt 2); the robot continues in an explicitly announced reduced mode.
4. **Any anomaly** → the deterministic safety layer stops motion. ER is never in that path.

---

## 🔟 Orchestrating a VLA with ER

This is the architecture Google ships: **ER 1.5/2 thinks, Gemini Robotics (VLA) acts.** The tech report shows the ER-orchestrated agent beating the same agent driven by off-the-shelf Gemini 2.5 Flash on every tested case — same tools, same VLA, better brain.

### Three ways to build it with hardware you can actually buy

| Pattern | Orchestrator | Executor | When |
|---|---|---|---|
| **A · Google stack** | Gemini Robotics-ER 2 | Gemini Robotics 1.5/2 (Trusted Tester) | You have partner access; ALOHA 2 / Apollo / Franka |
| **B · ER + open VLA** ⭐ | Gemini Robotics-ER 2 (cloud) | π0.5 via `openpi`, GR00T N1.7, or SmolVLA via LeRobot | **The practical 2026 recipe** for a lab or pilot cell |
| **C · ER + classical** | Gemini Robotics-ER 2 | MoveIt 2 + your skill library | Auditability and certification matter most; this is what `burger_delivery` does |

### Pattern B wiring (ER → your VLA)

Declare your VLA as a single tool and let ER sequence it — mirroring the Safari SDK's `run_instruction_until_done`:

```python
vla_tool = {
    "type": "function",
    "name": "run_instruction_until_done",
    "description": "Send an ATOMIC natural-language instruction to the robot policy "
                   "(pick/place/push/open/close/fold). Blocks until the policy "
                   "reports completion or timeout. One instruction at a time.",
    "parameters": {"type": "object", "properties": {
        "instruction": {"type": "string",
                        "description": "specific and atomic, e.g. 'put the red dice "
                                       "in the green tray'"}},
        "required": ["instruction"]},
}
```

Your side of the call runs the VLA (LeRobot/openpi inference server, or a ROS 2 action), then answers with a **truthful** result — ideally from a second ER call using the R7 success-detection prompt on the post-action video:

```python
{"status": "success"}                             # or
{"status": "failed", "reason": "grasp slipped, object on floor at [y,x]"}
```

**Instruction-writing rules from Google's own ALOHA system prompt** (they matter more than any hyper-parameter):

- Instructions must be **atomic**: a single low-level action — grab/hold, pick, place, move, push/pull, open/close gripper, wipe, stack, zip, fold.
- Instructions must name a **specific object and a concrete destination**: "place the red cup on the white bowl", not "clean up".
- **Decompose complex requests yourself** in the system prompt; prefer *not* to ask the user for clarification.
- **One function at a time** (`ONLY RUN A SINGLE FUNCTION AT A TIME`).
- Always **cancel an in-flight instruction** if the user asks to stop, reset, or switch tasks.
- If the request is already satisfied by visual reasoning, **announce it and stop** — don't act for the sake of acting.

### Why this beats a monolithic VLA (and when it doesn't)

| | ER + VLA (hierarchical) | Monolithic VLA |
|---|---|---|
| Long-horizon tasks | ✅ explicit decomposition, re-planning | ⚠️ degrades with horizon |
| Interpretability | ✅ text plan + tool-call log | ❌ opaque action chunks |
| External knowledge (local rules, manuals) | ✅ Search / URL / file-search tools | ❌ none |
| Success detection & recovery | ✅ built-in loop | ⚠️ needs an external monitor (SAFE, UQ-VLA) |
| Latency per skill | ⚠️ +300 ms–4 s per decision point | ✅ no cloud hop |
| Offline operation | ❌ | ✅ (with on-device VLA) |

Rule of thumb: **hierarchical when the task is long and semantic; monolithic when it is short and reactive.** Most real cells want both, at different rates (§9.1).

---

## 1️⃣1️⃣ Safety, limits and failure modes

### What Google built in

| Mechanism | What it does |
|---|---|
| **Semantic safety** | understands and refuses plans for dangerous or harmful tasks; evaluated against the **ASIMOV benchmark** (including ASIMOV-2.0 physical-safety splits: latent risk, risk severity, action effect, activated risk) |
| **Physical-constraint awareness** | significantly better at recognising when a request would violate a constraint **you define** — payload capacity, workspace limits |
| **Auto-red-teaming (ART)** | Attacker / Target / AutoRater game: prompt attacks, scene attacks (corrupted images), environment attacks (moving obstacles). Used to find ER hallucinations — e.g. asking it to point at an entity that does not exist |
| **Safety Council + responsible deployment** | standard DeepMind review for the Robotics family |

### What Google explicitly says is *your* job

> *"These model-level safeguards are not a substitute for the rigorous safety engineering required for physical systems. We advocate a 'Swiss cheese approach' to safety, where multiple layers of protection work together. Developers are responsible for implementing standard robotics safety best practices, including emergency stops, collision avoidance, and thorough risk assessments."*

Concretely, your layers:

1. **Deterministic safety PLC / controller** — force and speed limits per ISO/TS 15066, protected workspace, e-stop. No ML in this path.
2. **Argument validation** — bounds, joint limits, payload, singularity and reachability checks before executing any ER-requested motion.
3. **Allowlisted tools** — ER can only call functions you expose; no arbitrary code execution against your robot.
4. **Human-in-the-loop gates** for irreversible or contact-rich steps.
5. **Audit trail** — persist prompt, image hash, raw model text, tool calls, arguments, results, latency and cost. This is what makes a post-incident analysis possible (and it is the same "tactile/telemetry as evidence" argument in [`tactile-sota.md`](tactile-sota.md) §8).

### Known failure modes and mitigations

| Failure mode | Evidence / mechanism | Mitigation |
|---|---|---|
| **Hallucinated pointing** — points at an object that isn't there | discovered by Google's own auto-red-teaming on ER | ask for a confidence + reason; verify with a second view or a local detector before acting |
| **Reasoning collapse when thinking is off** | ERQA 54.8 → 47.0; aggregate 62.8 → 56.7 | never set budget to 0; use `low` instead |
| **Regression vs predecessor on a specific skill** | Point-Bench: ER 1.0 **75.7** > ER 1.5 **71.6** | benchmark *your* skill per model version before migrating (§13) |
| **Loses on general embodied QA** | ERQA: GPT-5 **59.0** > ER 1.5 **54.8** | don't assume "robotics model" wins every multimodal task |
| **Network latency / outage** | cloud-only | timeout, cached plan, degradation ladder (§9.5) |
| **Runaway agentic loop** | model keeps calling tools | `max_steps`, per-call cost budget, kill switch |
| **Prompt injection via the scene** | text in the image ("ignore previous instructions…") can steer a VLM | strip/ignore scene text for safety-critical prompts; validate every tool argument; keep the allowlist narrow |
| **Context overflow on ER 2** | input limit dropped 1,048,576 → **131,072** vs ER 1.5 | trim video, downscale images, summarise history |
| **Preview instability** | all ER models are `-preview` | pin the model string, keep a rollback path, isolate the client behind your own interface |
| **Privacy / GDPR** | robot video may capture identifiable people | data minimisation *before* the call: crop to the task, blur faces, drop audio, don't retain raw streams; note free-tier content **is** used to improve Google products |

---

## 1️⃣2️⃣ Migration & deprecations

| Change | Date | Action |
|---|---|---|
| ER 1.5 GA in the Gemini API | Sep 2025 | first broadly available Gemini Robotics model |
| ER 1.6 released | Dec 2025 (upd. Apr 2026) | added caching, computer use, file search, Maps grounding, Batch |
| **ER 1.6 deprecated** | **2026-08-31** | move to ER 2 |
| ER 2 + ER 2 Streaming + On-Device 2 + Gemini Robotics 2 | Jul 2026 | ER 2 built on Gemini 3.5 Flash |
| ER 1.5 deprecation | *planned soon* (flagged on the model card) | do not start new work here |
| Generate Content API → **Interactions API** | breaking changes May 2026 | robotics doc pages for spatial/agentic are marked *Legacy*; orchestration docs already use `client.interactions` |

**Migration is a behaviour change, not a string replacement.** When you swap `er-1.5-preview` → `er-2-preview`:

1. Inventory every hardcoded model ID (config, notebooks, CI, containers).
2. Re-run your **representative** images/videos — your camera placement, your lighting, your SKUs.
3. Measure: task completion, pointing error in mm, false tool calls, plan validity.
4. Compare **standard vs streaming** latency for your call pattern.
5. Verify real token cost with real prompts (thinking tokens are billed as output).
6. Keep a rollback path and isolate the Gemini client behind an interface so a future model change never reaches robot-control code directly.
7. Re-check the context window (1M → 131k) — this silently breaks long-video workflows.

---

## 1️⃣3️⃣ Evaluate ER on *your* cell before you trust it

Published benchmarks say nothing about your camera placement, lighting or SKUs. A one-day harness:

| Axis | Test | Metric | Suggested pass bar |
|---|---|---|---|
| **Pointing** | 30 images × 5 known objects, ground-truth pixel centres | mean pixel error, % within 20 px | ≥90% within 20 px at your resolution |
| **Metric accuracy** | after the §8 transform, verify with calipers | mean absolute error in mm | ≤3 mm for grasp-critical parts |
| **Free-space** | 20 cluttered scenes, human-annotated valid placements | % valid | ≥85% |
| **Plan validity** | 20 tasks; is every step executable and correctly ordered? | % valid plans, hallucinated skills | ≥90% valid, **0** hallucinated skills |
| **Success detection** | 40 clips (20 success / 20 failure) | accuracy, false-negative rate | FN ≤10% (a missed success retries a done action) |
| **Tool-call correctness** | 20 orchestration runs | % correct first call, mean steps to goal, out-of-bounds args | **0** out-of-bounds args accepted |
| **Latency & cost** | 100 calls per thinking level | p50/p95 seconds, $/task | p95 inside your decision budget |
| **Robustness** | vary lighting, viewpoint ±15°, 25% occlusion | Δ accuracy | degradation <10 pp |

Store every raw response. Two axes — pointing error in **mm** and hallucinated skills — are the ones that predict field behaviour; the rest explain *why*.

> 📌 This harness is also the missing artefact named in [`research-gaps.md`](research-gaps.md): *"Semantic calibration — no papers on VLM-robot calibration → metric-semantic grounding benchmark."* Publishing yours would be a real contribution.

---

## 1️⃣4️⃣ Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `403 PERMISSION_DENIED` on every call | unrestricted API key (rejected for robotics) | restrict the key to the Generative Language API; right project; billing on |
| Model not found / not listed | preview access, wrong project, deprecated ID | `client.models.list()` filtered on `robotics-er`; use `gemini-robotics-er-2-preview` |
| Points look transposed | `[y, x]` read as `[x, y]` | swap; render an overlay to confirm |
| Points scaled wrong | normalised to 0–1/0–100 instead of 0–1000, or image resized after the call | resize **before** sending; assert `0 ≤ v ≤ 1000` |
| Markdown fences break the parser | JSON wrapped in ```json | add R2's `system_instruction`, or use `response_mime_type="application/json"` |
| Very slow responses | `thinking_level="high"` on a simple spatial task | drop to `low`; keep `high` for counting/estimation |
| Bill higher than expected | thinking tokens billed as output at $5/1M | log `thoughts_token_count`; cap the level; cache repeated scenes |
| Streaming model looks frozen | heartbeat fired during generation → barge-in cancelled reasoning | await `turn_complete` before the next heartbeat (R8) |
| Agentic loop never ends | no step cap, or results always "success" | `max_steps`, honest results, cost ceiling |
| Context errors on long video | ER 2 limit is 131,072 tokens | sample frames, shorten clips, lower resolution |
| Answers vary run to run | preview model + sampling | pin the model ID, fix the prompt, lower temperature, average over N runs |

---

## 1️⃣5️⃣ Production checklist

**Before you write code**
- [ ] Pinned `gemini-robotics-er-2-preview` (not `latest`, not 1.5/1.6)
- [ ] Restricted API key, billing enabled, rate limits checked in AI Studio
- [ ] Chose standard vs streaming endpoint per call pattern
- [ ] Confirmed the cloud dependency is acceptable (otherwise use a local VLM)

**Per prompt**
- [ ] Coordinates specified as `[y, x]` normalised 0–1000 (boxes `[ymin,xmin,ymax,xmax]`)
- [ ] Output format fixed; `system_instruction` says "ONLY that JSON"
- [ ] Physical constraints stated (payload, reach, keep-out zones, object sizes)
- [ ] Thinking level chosen per task type, not left at default

**Per call**
- [ ] Timeout set; retry with jittered backoff on 429/5xx
- [ ] Latency, token counts, cost and raw text logged with a correlation ID
- [ ] Images downscaled/compressed; PII minimised *before* upload

**Per tool call**
- [ ] Allowlisted function set; every argument validated and bounds-checked
- [ ] `max_steps` and a cost ceiling on every agentic loop
- [ ] Truthful function results returned, so the model can recover
- [ ] Cancellation path for in-flight instructions

**System level**
- [ ] Deterministic safety layer independent of ER (ISO/TS 15066, e-stop, force envelope)
- [ ] Degradation ladder implemented and tested *by unplugging the network*
- [ ] Evaluation harness (§13) re-run for every model-version change
- [ ] Audit trail sufficient for post-incident analysis
- [ ] Rollback path to the previous model version

---

## 📚 References

**Official documentation (consulted 2026-10-21)**
1. Gemini Robotics ER — overview & model cards: <https://ai.google.dev/gemini-api/docs/robotics-overview>
2. ER 1.5 model card: <https://ai.google.dev/gemini-api/docs/models/gemini-robotics-er-1.5-preview>
3. ER 2 model card: <https://ai.google.dev/gemini-api/docs/models/gemini-robotics-er-2-preview>
4. Spatial reasoning (points, boxes, tracking, trajectories): <https://ai.google.dev/gemini-api/docs/generate-content/robotics-spatial>
5. Agentic vision (code execution, instruments, annotation): <https://ai.google.dev/gemini-api/docs/generate-content/robotics-agentic>
6. Task orchestration (agentic loop with a custom robot API): <https://ai.google.dev/gemini-api/docs/robotics-orchestration>
7. Robotics with streaming (Live API): <https://ai.google.dev/gemini-api/docs/robotics-streaming>
8. Pricing: <https://ai.google.dev/gemini-api/docs/pricing> · Rate limits: <https://ai.google.dev/gemini-api/docs/rate-limits>
9. Interactions API migration (breaking changes, May 2026): <https://ai.google.dev/gemini-api/docs/migrate-interactions>

**Official announcements & research**
10. *Building the Next Generation of Physical Agents with Gemini Robotics-ER 1.5* — Google Developers Blog, 2025-09-25: <https://developers.googleblog.com/en/building-the-next-generation-of-physical-agents-with-gemini-robotics-er-15/>
11. *Gemini Robotics 1.5: Pushing the Frontier of Generalist Robots with Advanced Embodied Reasoning, Thinking, and Motion Transfer* — [arXiv:2510.03342](https://arxiv.org/abs/2510.03342) (ER benchmarks in **Table 19**; agentic evaluation; ASIMOV-2.0; auto-red-teaming)
12. *Gemini Robotics 1.5 brings AI agents into the physical world* — DeepMind blog, Sep 2025
13. Safari SDK (`google-deepmind/gemini-robotics-sdk`) — agent framework, `success_detection`, `run_instruction_until_done`, ALOHA `simple_agent.py` system prompt: <https://github.com/google-deepmind/gemini-robotics-sdk>
14. Gemini API Cookbook: <https://github.com/google-gemini/cookbook>

**Third-party price & version tracking (cross-checked against Google's pages)**
15. Physical AI Lab, *Gemini Robotics ER 2 Pricing and API Access* (checked 2026-08-06, updated 2026-10-13 — ER 1.6 deprecation date)
16. Bertrande price ledger for `gemini-robotics-er-2-preview` (observed 2026-10-17; 2027-01-01 increase announced)

**This repository**
17. [`GLOSSARY.md`](GLOSSARY.md) — LLM/VLM/VLA definitions and the Gemini Robotics variant table
18. [`presentations/llm-vlm-vla-sota.html`](presentations/llm-vlm-vla-sota.html) — slides 10 (ER benchmarks), 18 (hierarchical stack), 22 (perception gaps)
19. [`research-gaps.md`](research-gaps.md) — *Multimodal perception*, *Semantic planning*, *Edge AI*
20. [`papers.csv`](papers.csv) — `2604.01179` Florence-2 ROS 2 wrapper · `2506.09937` SAFE · `2606.18043` UQ-VLA · `2603.04585` ELLIPSE

---

## 🔗 Cross references

- Slide deck: [`presentations/llm-vlm-vla-sota.html`](presentations/llm-vlm-vla-sota.html)
- **Open-source ER alternatives:** [`open-vlm-er-sota.md`](open-vlm-er-sota.md)
- Runnable demo: [`scripts/gemini_er_demo.py`](scripts/gemini_er_demo.py)
- Glossary: [`GLOSSARY.md`](GLOSSARY.md)
- Gaps: [`research-gaps.md`](research-gaps.md)
- Tactile & dexterity SOTA: [`tactile-sota.md`](tactile-sota.md)

---

*Created 2026-10-21. Living document — every ER model version and every published price has an expiry date; re-verify before relying on it. Vendor-claimed numbers are flagged as such throughout.*
