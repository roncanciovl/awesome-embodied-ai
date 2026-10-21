"""
Gemini Robotics-ER demo — understand and exercise the Embodied Reasoning model.

Companion to ``gemini-robotics-er-guide.md``. Implements the recipes that matter
most, with the production safeguards described in the guide:

  point        R1/R6 — grounded pointing, normalized [y, x] in 0-1000
  plan         R1    — multi-step plan with a point for every referent
  orchestrate  R5    — agentic loop that drives a (mock) robot API
  success      R7    — Safari-SDK-style success detection verdict

Everything runs offline with --dry-run, which prints the exact request payloads
and executes the mock robot locally. Live calls need an API key and the SDK:

    pip install google-genai pillow
    export GEMINI_API_KEY="..."      # must be RESTRICTED or ER returns 403

Usage:
    python scripts/gemini_er_demo.py --dry-run --mode point --image scene.jpg
    python scripts/gemini_er_demo.py --dry-run --mode orchestrate
    python scripts/gemini_er_demo.py --mode point --image scene.jpg --query "the red block"
    python scripts/gemini_er_demo.py --mode success --video clip.mp4 --task "put the spoon in the compost bin"

Exit codes:
    0  success (for --mode success: the verdict was YES)
    1  runtime/parse error, or no points/verdict could be extracted
    2  file not found, or --mode success returned a NO verdict
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from typing import Any, Sequence

# Current model as of Oct 2026. ER 1.6 was deprecated 2026-08-31 and ER 1.5
# carries a deprecation notice. Pin the string; never use a "latest" alias.
DEFAULT_MODEL = "gemini-robotics-er-2-preview"
STREAMING_MODEL = "gemini-robotics-er-2-streaming-preview"

TIMEOUT_MS = 8_000          # hard ceiling: never block a robot on a cloud call
MAX_STEPS = 15              # agentic-loop safety limit (guide §7 R5)
NORM_RANGE = 1000.0         # ER normalizes coordinates to 0-1000, [y, x]

# Paid-tier price per 1M tokens (Oct 2026). Output includes thinking tokens.
# Announced change for 2027-01-01: input $2.00, output $10.00.
PRICE_IN_PER_M = 1.00
PRICE_OUT_PER_M = 5.00

POINT_RE = re.compile(
    r'"point"\s*:\s*\[\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*\]'
    r'(?:[^}]*?"label"\s*:\s*"([^"]*)")?'
)
FINAL_ANSWER_RE = re.compile(r"FINAL ANSWER:\s*(yes|no)", re.IGNORECASE)


# --------------------------------------------------------------------------- #
# Geometry helpers (guide §8)
# --------------------------------------------------------------------------- #
def norm_to_pixel(point_yx: Sequence[float], width: int, height: int) -> tuple[float, float]:
    """Convert an ER normalized [y, x] point (0-1000) to pixel (u, v).

    Note the axis order: ER returns **y first**. Treating it as [x, y] is the
    single most common integration bug.
    """
    y_norm, x_norm = float(point_yx[0]), float(point_yx[1])
    if not (0.0 <= y_norm <= NORM_RANGE and 0.0 <= x_norm <= NORM_RANGE):
        raise ValueError(f"point {point_yx} outside 0-{int(NORM_RANGE)}; wrong scale?")
    return x_norm / NORM_RANGE * width, y_norm / NORM_RANGE * height


def norm_to_meters_on_plane(
    point_yx: Sequence[float],
    width: int,
    height: int,
    intrinsics: dict[str, float],
    plane_z: float,
) -> tuple[float, float, float]:
    """Pixel -> camera 3D on a known plane (e.g. a table at z = plane_z).

    ``intrinsics`` needs fx, fy, cx, cy. Without a depth camera this planar
    assumption is what an AprilTag-fixed table frame gives you. Apply your
    hand-eye transform afterwards to reach the robot base frame.
    """
    u, v = norm_to_pixel(point_yx, width, height)
    fx, fy = intrinsics["fx"], intrinsics["fy"]
    cx, cy = intrinsics["cx"], intrinsics["cy"]
    return (u - cx) * plane_z / fx, (v - cy) * plane_z / fy, plane_z


def parse_points(text: str) -> list[dict[str, Any]]:
    """Extract [{"point": [y, x], "label": str}] from free-form model output."""
    return [
        {"point": [float(y), float(x)], "label": label or "unlabelled"}
        for y, x, label in POINT_RE.findall(text)
    ]


# --------------------------------------------------------------------------- #
# Prompts (guide §7)
# --------------------------------------------------------------------------- #
SYSTEM_INSTRUCTION = (
    "Be precise. When JSON is requested, reply with ONLY that JSON "
    "(no preface, no code block)."
)


def point_prompt(query: str, max_points: int = 10) -> str:
    """R1 — grounded pointing in normalized [y, x] 0-1000."""
    return (
        f'Point to "{query}" (at most {max_points} items).\n'
        'The answer should follow the json format: '
        '[{"point": <point>, "label": <label>}, ...].\n'
        "The points are in [y, x] format normalized to 0-1000."
    )


def plan_prompt(task: str) -> str:
    """R1 — plan plus a point for every referent."""
    return (
        "Explain how to complete the task step by step.\n"
        "Point to each object that you refer to.\n"
        'Each point should be in the format: [{"point": [y, x], "label": <label>}],\n'
        "where the coordinates are normalized between 0-1000.\n"
        f"Task: {task}"
    )


def free_space_prompt(size: str = "12 cm box", clearance: str = "15 cm") -> str:
    """R6 — Where2Place-style reasoning. Always state the physical constraints."""
    return (
        f"Point to a location where a {size} can be placed safely: flat, "
        f"unobstructed, at least {clearance} from any keep-out zone, inside the "
        "robot's reachable workspace.\n"
        'Reply JSON: [{"point": [y, x], "reason": <str>}] normalized 0-1000.'
    )


def success_prompt(task: str) -> str:
    """R7 — the Safari SDK guided-thinking success-detection scaffold."""
    return f"""Task: {task}

Q1 Tell me about the state of task-relevant objects at each time by combining all
   views to form a complete picture.
Q2 What are the relationships between the relevant objects at each time?
Q3 What state should the objects be in if the robot successfully completed the task?
Q4 Are the objects currently in that state? What are the differences? Say which
   views and times your answer is based on.

After answering, tell me if the robot successfully completed the task.
Use the most lenient interpretation of completion: partial or indeterminate counts
as completed. If the task specifies a quantity, the minimum is met as soon as at
least that many items are in the correct final state; other similar items do not
matter.

If finished, answer:     'FINAL ANSWER: yes'
If not finished, answer: 'FINAL ANSWER: no'
Do not mention the word 'FINAL ANSWER' anywhere else."""


def _mime_for(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif", ".bmp": "image/bmp",
        ".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm",
        ".wav": "audio/wav", ".mp3": "audio/mp3",
    }.get(ext, "application/octet-stream")


def _dry_run_response(prompt: str) -> str:
    """Deterministic stand-in output so the pipeline can be exercised offline."""
    if "FINAL ANSWER" in prompt:
        return ("Q1: the spoon is on the table at the start and at the end...\n"
                "Q4: No, the spoon is not in the compost bin.\n"
                "FINAL ANSWER: no")
    if "step by step" in prompt:
        return ('1. Pick the [apple]. 2. Place it in the [blue lunch box].\n'
                '* [{"point": [899, 440], "label": "apple"}]\n'
                '* [{"point": [706, 529], "label": "blue lunch box"}]')
    if "placed safely" in prompt:
        return '[{"point": [612, 268], "reason": "flat, clear of the glass"}]'
    return '[{"point": [305, 449], "label": "red block"}]'
# --------------------------------------------------------------------------- #
# Client wrapper — isolate the SDK so a model change never reaches robot code
# --------------------------------------------------------------------------- #
class ErClient:
    """Gemini API wrapper with timeout, token/cost metering and a dry-run mode."""

    def __init__(self, model: str, thinking: str, dry_run: bool = False,
                 timeout_ms: int = TIMEOUT_MS):
        self.model = model
        self.thinking = thinking
        self.dry_run = dry_run
        self.timeout_ms = timeout_ms
        self.calls = 0
        self.total_in = 0
        self.total_out = 0
        self.total_thoughts = 0
        self._client = None
        self._types = None
        if dry_run:
            return
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            sys.exit("google-genai is not installed. Run: pip install google-genai\n"
                     "Or re-run with --dry-run to inspect payloads offline.")
        if not os.environ.get("GEMINI_API_KEY"):
            sys.exit("GEMINI_API_KEY is not set (it must be a RESTRICTED key, "
                     "otherwise ER returns 403). Use --dry-run to run offline.")
        self._client, self._types = genai.Client(), types

    def generate(self, prompt: str, media: str | None = None,
                 code_execution: bool = False) -> str:
        """One ER call. Returns raw text; parsing is the caller's job."""
        self.calls += 1
        if self.dry_run:
            payload = {
                "model": self.model,
                "media": media,
                "media_bytes": os.path.getsize(media) if media and os.path.exists(media) else 0,
                "mime": _mime_for(media) if media else None,
                "thinking_level": self.thinking,
                "code_execution": code_execution,
                "system_instruction": SYSTEM_INSTRUCTION,
                "timeout_ms": self.timeout_ms,
                "prompt_chars": len(prompt),
            }
            print("┌─ [dry-run] request " + "─" * 50)
            print(json.dumps(payload, indent=2))
            print("│  prompt:")
            for line in prompt.strip().splitlines():
                print("│    " + line)
            print("└" + "─" * 70)
            return _dry_run_response(prompt)

        contents: list[Any] = []
        if media:
            with open(media, "rb") as fh:
                data = fh.read()
            contents.append(self._types.Part.from_bytes(data=data,
                                                        mime_type=_mime_for(media)))
        contents.append(prompt)

        cfg: dict[str, Any] = {
            "system_instruction": SYSTEM_INSTRUCTION,
            "thinking_config": self._types.ThinkingConfig(thinking_level=self.thinking),
            "http_options": self._types.HttpOptions(timeout=self.timeout_ms),
        }
        if code_execution:
            cfg["tools"] = [self._types.Tool(
                code_execution=self._types.ToolCodeExecution())]

        t0 = time.perf_counter()
        resp = self._client.models.generate_content(
            model=self.model, contents=contents,
            config=self._types.GenerateContentConfig(**cfg))
        wall = time.perf_counter() - t0

        u = getattr(resp, "usage_metadata", None)
        n_in = getattr(u, "prompt_token_count", 0) or 0
        n_out = getattr(u, "candidates_token_count", 0) or 0
        n_th = getattr(u, "thoughts_token_count", 0) or 0
        self.total_in += n_in
        self.total_out += n_out
        self.total_thoughts += n_th
        cost = (n_in / 1e6 * PRICE_IN_PER_M
                + (n_out + n_th) / 1e6 * PRICE_OUT_PER_M)
        print(f"[er] {wall:.2f}s · in={n_in} out={n_out} thoughts={n_th} · ~${cost:.4f}")
        return resp.text or ""

    def report(self) -> None:
        cost = (self.total_in / 1e6 * PRICE_IN_PER_M
                + (self.total_out + self.total_thoughts) / 1e6 * PRICE_OUT_PER_M)
        print(f"\n[report] calls={self.calls} in={self.total_in} "
              f"out={self.total_out} thoughts={self.total_thoughts} "
              f"≈ ${cost:.4f} (paid tier, Oct 2026 rates)")
# --------------------------------------------------------------------------- #
# Mock robot API (guide §7 R5) — with the validation layer the guide requires
# --------------------------------------------------------------------------- #
class MockRobot:
    """Stand-in for a real robot API. Rejects out-of-workspace commands."""

    WORKSPACE_X = (-400.0, 400.0)     # mm, table frame
    WORKSPACE_Y = (-300.0, 500.0)

    def __init__(self) -> None:
        self.gripper_open = True
        self.log: list[str] = []
        self.rejected: list[str] = []

    def move(self, x: float, y: float, high: bool) -> dict[str, str]:
        try:
            x, y = float(x), float(y)
        except (TypeError, ValueError):
            return self._reject("move", f"non-numeric args x={x!r} y={y!r}")
        if x != x or y != y:                       # NaN guard
            return self._reject("move", "NaN coordinates")
        if not (self.WORKSPACE_X[0] <= x <= self.WORKSPACE_X[1]):
            return self._reject("move", f"x={x} outside workspace {self.WORKSPACE_X}")
        if not (self.WORKSPACE_Y[0] <= y <= self.WORKSPACE_Y[1]):
            return self._reject("move", f"y={y} outside workspace {self.WORKSPACE_Y}")
        level = "high above table" if high else "down at table level"
        entry = f"move({x}, {y}, {level})"
        self.log.append(entry)
        print(f"  Mock Robot: Moving to ({x}, {y}), {level}")
        return {"status": "success"}

    def setGripperState(self, opened: bool) -> dict[str, str]:
        self.gripper_open = bool(opened)
        entry = "gripper OPEN" if self.gripper_open else "gripper CLOSE"
        self.log.append(entry)
        print(f"  Mock Robot: {'Opening' if self.gripper_open else 'Closing'} gripper")
        return {"status": "success"}

    def _reject(self, fn: str, reason: str) -> dict[str, str]:
        self.rejected.append(f"{fn}: {reason}")
        print(f"  ⛔ SAFETY LAYER rejected {fn}: {reason}")
        # Truthful results let the model recover (guide §7 R5, rule 4).
        return {"status": "failed", "reason": reason}

    def dispatch(self, name: str, arguments: dict[str, Any]) -> dict[str, str]:
        if name == "move":
            return self.move(**arguments)
        if name == "setGripperState":
            return self.setGripperState(**arguments)
        return {"status": "failed", "reason": f"unknown function '{name}' (not allowlisted)"}


# Interactions API tool declarations — a narrow allowlist on purpose.
ROBOT_TOOLS = [
    {
        "type": "function", "name": "move",
        "description": "Move the end effector to table coordinates x,y in mm "
                       "(origin at the robot base). high=True travels above the "
                       "table; high=False descends to table level.",
        "parameters": {"type": "object", "properties": {
            "x": {"type": "number"}, "y": {"type": "number"},
            "high": {"type": "boolean"}}, "required": ["x", "y", "high"]},
    },
    {
        "type": "function", "name": "setGripperState",
        "description": "Open or close the gripper.",
        "parameters": {"type": "object", "properties": {
            "opened": {"type": "boolean"}}, "required": ["opened"]},
    },
]

# Scripted stand-in for the model's tool-call sequence, so --dry-run exercises
# the whole loop (including a rejected out-of-workspace command).
SCRIPTED_CALLS: list[list[tuple[str, dict[str, Any]]]] = [
    [("setGripperState", {"opened": True})],
    [("move", {"x": 160, "y": 440, "high": True})],
    [("move", {"x": 160, "y": 440, "high": False})],
    [("setGripperState", {"opened": False})],
    [("move", {"x": 160, "y": 440, "high": True})],
    [("move", {"x": 9999, "y": 60, "high": True})],      # ← rejected by the safety layer
    [("move", {"x": -250, "y": 60, "high": True})],
    [("move", {"x": -250, "y": 60, "high": False})],
    [("setGripperState", {"opened": True})],
    [("move", {"x": -250, "y": 60, "high": True})],
]
# --------------------------------------------------------------------------- #
# Modes
# --------------------------------------------------------------------------- #
def mode_point(client: ErClient, args: argparse.Namespace) -> int:
    """R1/R6 — grounded pointing, then the normalized → pixel → metres chain."""
    prompt = (free_space_prompt(args.object_size, args.clearance)
              if args.free_space else point_prompt(args.query, args.max_points))
    media = args.image or args.video
    if not media and not args.dry_run:
        print("warning: no --image given; a real call needs one", file=sys.stderr)
    text = client.generate(prompt, media=media, code_execution=args.code_execution)
    print("\n--- raw model output ---\n" + text + "\n")

    points = parse_points(text)
    if not points:
        print("⚠ no points parsed — inspect the raw output above")
        return 1
    print(f"--- {len(points)} point(s): normalized → pixel → metres ---")
    intrinsics = {"fx": args.fx, "fy": args.fy, "cx": args.cx, "cy": args.cy}
    for p in points:
        u, v = norm_to_pixel(p["point"], args.width, args.height)
        x, y, z = norm_to_meters_on_plane(p["point"], args.width, args.height,
                                          intrinsics, args.plane_z)
        print(f'  {p["label"]:<22} [y,x]={p["point"]} → pixel=({u:.1f}, {v:.1f}) '
              f"→ camera=({x:.3f}, {y:.3f}, {z:.3f}) m")
    print("\nnext: apply T_base_cam (hand-eye) before sending this to a planner.")
    return 0


def mode_plan(client: ErClient, args: argparse.Namespace) -> int:
    """R1 — a grounded multi-step plan with a point for every referent."""
    text = client.generate(plan_prompt(args.task), media=args.image)
    print("\n--- plan ---\n" + text + "\n")
    points = parse_points(text)
    print(f"--- {len(points)} grounded referent(s) ---")
    for p in points:
        u, v = norm_to_pixel(p["point"], args.width, args.height)
        print(f'  {p["label"]:<22} pixel=({u:.1f}, {v:.1f})')
    return 0
def mode_orchestrate(client: ErClient, args: argparse.Namespace) -> int:
    """R5 — the agentic loop, with max_steps, validation and honest results."""
    robot = MockRobot()
    print(f"--- orchestrating: {args.task!r} (max_steps={args.max_steps}) ---\n")

    if client.dry_run:
        print("┌─ [dry-run] client.interactions.create " + "─" * 33)
        print(json.dumps({"model": client.model, "tools": ROBOT_TOOLS,
                          "generation_config": {"thinking_level": client.thinking},
                          "input": [{"type": "input_image", "image_url": args.image},
                                    {"type": "input_text", "text": args.task}]},
                         indent=2))
        print("└" + "─" * 70 + "\n--- Executing Orchestrated Plan ---")
        for i, calls in enumerate(SCRIPTED_CALLS[: args.max_steps], 1):
            print(" step %d: %s" % (i, ", ".join(f"{n}({a})" for n, a in calls)))
            for name, arguments in calls:
                robot.dispatch(name, arguments)
        print("\nSequence complete. Model Summary: I have completed the task of "
              "picking up the blue block and placing it into the orange bowl.")
    else:
        _orchestrate_live(client, robot, args)

    print(f"\n[audit] {len(robot.log)} command(s) executed")
    for entry in robot.log:
        print("   ✓ " + entry)
    if robot.rejected:
        print(f"[audit] {len(robot.rejected)} command(s) REJECTED by validation")
        for entry in robot.rejected:
            print("   ⛔ " + entry)
    print("[audit] the model only proposes; the validation layer decides.")
    return 0


def _orchestrate_live(client: ErClient, robot: MockRobot,
                      args: argparse.Namespace) -> None:
    """Real Interactions-API agentic loop (guide §7 R5)."""
    raw = client._client          # noqa: SLF001 — deliberate: Interactions API
    interaction = raw.interactions.create(
        model=client.model,
        input=[{"type": "input_image", "image_url": args.image},
               {"type": "input_text", "text": args.task}],
        tools=ROBOT_TOOLS,
        generation_config={"thinking_level": client.thinking},
    )
    client.calls += 1
    print("--- Executing Orchestrated Plan ---")
    for step_count in range(1, args.max_steps + 1):
        tool_calls = [s for s in interaction.steps if s.type == "function_call"]
        if not tool_calls:
            print("\nSequence complete.")
            if interaction.output_text:
                print(f"Model Summary: {interaction.output_text}")
            return
        results = []
        for step in tool_calls:
            print(f" step {step_count}: {step.name}({step.arguments})")
            outcome = robot.dispatch(step.name, dict(step.arguments or {}))
            results.append({"type": "function_result", "name": step.name,
                            "call_id": step.id,
                            "result": [{"type": "text", "text": json.dumps(outcome)}]})
        interaction = raw.interactions.create(
            model=client.model, previous_interaction_id=interaction.id,
            tools=ROBOT_TOOLS, input=results)
        client.calls += 1
    print(f"\n⚠ hit max_steps={args.max_steps}; stopping the loop.")


def mode_success(client: ErClient, args: argparse.Namespace) -> int:
    """R7 — success detection with the guided-thinking scaffold."""
    media = args.video or args.image
    text = client.generate(success_prompt(args.task), media=media)
    print("\n--- raw model output ---\n" + text + "\n")
    m = FINAL_ANSWER_RE.search(text)
    if not m:
        print("⚠ no 'FINAL ANSWER' marker — treat as UNKNOWN; do not advance the plan")
        return 1
    verdict = m.group(1).lower()
    print(f"--- verdict: {verdict.upper()} ---")
    print("note: a false NEGATIVE retries a completed action; a false POSITIVE "
          "advances too early. Pick the leniency your cell can tolerate.")
    return 0 if verdict == "yes" else 2
# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Gemini Robotics-ER demo (companion to gemini-robotics-er-guide.md)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--mode", choices=["point", "plan", "orchestrate", "success"],
                   default="point", help="which recipe to run (guide §7)")
    p.add_argument("--dry-run", action="store_true",
                   help="print exact payloads and simulate; no API key needed")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help=f"model code (streaming: {STREAMING_MODEL})")
    p.add_argument("--thinking", choices=["low", "medium", "high"], default="low",
                   help="thinking level: low=spatial, high=counting/estimation")
    p.add_argument("--timeout-ms", type=int, default=TIMEOUT_MS,
                   help="hard ceiling per call — never block a robot on the cloud")
    p.add_argument("--image", help="path to the scene image")
    p.add_argument("--video", help="path to the robot video (success mode)")
    p.add_argument("--query", default="the red block", help="what to point at")
    p.add_argument("--task", default="Pick up the blue block and place it in the "
                                     "orange bowl. Use the robot API.",
                   help="natural-language task for plan/orchestrate/success")
    p.add_argument("--max-points", type=int, default=10)
    p.add_argument("--max-steps", type=int, default=MAX_STEPS,
                   help="agentic-loop safety limit")
    p.add_argument("--free-space", action="store_true",
                   help="point mode: ask WHERE to place something (R6)")
    p.add_argument("--object-size", default="12 cm box")
    p.add_argument("--clearance", default="15 cm")
    p.add_argument("--code-execution", action="store_true",
                   help="enable the code-execution tool (R2/R3/R4)")
    # camera + plane for the normalized → metres chain (guide §8)
    p.add_argument("--width", type=int, default=1280, help="image width in px")
    p.add_argument("--height", type=int, default=720, help="image height in px")
    p.add_argument("--fx", type=float, default=900.0)
    p.add_argument("--fy", type=float, default=900.0)
    p.add_argument("--cx", type=float, default=640.0)
    p.add_argument("--cy", type=float, default=360.0)
    p.add_argument("--plane-z", type=float, default=0.5,
                   help="table plane distance from the camera, metres")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    for path in (args.image, args.video):
        if path and not args.dry_run and not os.path.exists(path):
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2

    print("=" * 72)
    print(f"Gemini Robotics-ER · mode={args.mode} · model={args.model} "
          f"· thinking={args.thinking} · dry_run={args.dry_run}")
    print("=" * 72)

    client = ErClient(args.model, args.thinking, dry_run=args.dry_run,
                      timeout_ms=args.timeout_ms)
    handlers = {"point": mode_point, "plan": mode_plan,
                "orchestrate": mode_orchestrate, "success": mode_success}
    try:
        rc = handlers[args.mode](client, args)
    except Exception as exc:                      # noqa: BLE001
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    finally:
        client.report()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())





