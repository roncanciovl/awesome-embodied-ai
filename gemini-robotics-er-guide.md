# 🧭 Gemini Robotics-ER — Deep Guide: Understand & Use the Embodied Reasoning Model

**Created:** 2026-10-21
**Scope:** What Gemini Robotics-ER is, what it is *not*, every published version, its measured capabilities, and how to actually use it — API, prompts, coordinate maths, ROS 2 integration, VLA orchestration, safety and migration.
**Method:** Google AI for Developers docs (robotics overview, model cards, spatial reasoning, agentic vision, task orchestration, streaming, pricing, rate limits), the Gemini Robotics 1.5 technical report (arXiv:2510.03342), the Google Developers Blog ER 1.5 launch post, and the `google-deepmind/gemini-robotics-sdk` (Safari SDK) source code — all consulted 2026-10-21.
**Companion script:** [`scripts/gemini_er_demo.py`](scripts/gemini_er_demo.py) (runnable; `--dry-run` needs no API key)
**Related:** [`GLOSSARY.md`](GLOSSARY.md) → *Gemini Robotics* · [`presentations/llm-vlm-vla-sota.html`](presentations/llm-vlm-vla-sota.html) slide 10 · [`research-gaps.md`](research-gaps.md) → *Multimodal perception*

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

All recipes target `gemini-robotics-er-2-preview` unless noted. Runnable versions of R1, R5 and R7 are in [`scripts/gemini_er_demo.py`](scripts/gemini_er_demo.py) (`--dry-run` prints exact payloads without an API key).

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

<!--GUIDE9-->
