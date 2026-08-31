# 📋 Research Protocol — Awesome Embodied AI & Sim2Real

**Cutoff date:** 2026-08-30
**Version:** 1.0
**Lead researcher:** [Roncanciovl](https://github.com/roncanciovl)

---

## 🎯 Research Questions

### Main question
> How is generative artificial intelligence (LLMs, VLMs, VLAs) being integrated with production robotic frameworks (ROS 2) to bridge the gap between simulation and reality?

### Secondary questions
1. **Q1:** Which VLA/VLM/LLM models are most suitable for deployment on real robotic hardware with limited resources (Edge AI)?
2. **Q2:** What is the state of the art in Sim2Real transfer for manipulation and navigation with learned policies?
3. **Q3:** How does ROS 2 act as an orchestration layer ("harness") between AI models and physical actuators?
4. **Q4:** What benchmarks and metrics exist to reproducibly evaluate embodied systems with AI?
5. **Q5:** What are the open gaps in multimodal perception, semantic planning, and local inference?

---

## 📚 Sources Consulted

| Source | Type | Use |
|--------|------|-----|
| [arXiv](https://arxiv.org) (cs.RO, cs.AI, cs.CV, cs.CL) | Preprints | Primary paper source |
| [arXiv API](https://info.arxiv.org/help/api/) | Search API | Programmatic queries (`scripts/search_recent_papers.py`) |
| [GitHub](https://github.com) | Repositories | Open-source implementations (OpenVLA, Octo, etc.) |
| [Papers with Code](https://paperswithcode.com) | Index | Code availability verification |
| [ROS 2 Documentation](https://docs.ros.org) | Official docs | ROS 2 integration context |
| [IEEE Xplore / ACM DL](https://ieeexplore.ieee.org) | Publications | Conference references (ICRA, IROS, CoRL) |

---

## 🔍 Queries Performed (arXiv API)

```
# Query 1: Recent VLA
search_query=all:"vision-language-action" AND submittedDate:[202501 TO 202612]
sortBy=submittedDate&sortOrder=descending

# Query 2: Embodied AI
search_query=all:"embodied AI" AND submittedDate:[202501 TO 202612]

# Query 3: ROS 2 + LLM
search_query=all:"ROS 2" AND all:"language model"

# Query 4: Sim2Real
search_query=all:"sim-to-real" AND submittedDate:[202501 TO 202612]

# Query 5: LLM + manipulation
search_query=all:"large language model" AND all:"robot manipulation" AND submittedDate:[202501 TO 202612]

# Query 6: VLA + ROS
search_query=all:"vision-language-action" AND all:"ROS"
```

**Reproduction script:** `scripts/search_recent_papers.py`

---

## 📅 Search Period

| Parameter | Value |
|-----------|-------|
| Main period | 2017-01 → 2026-08 |
| Frontier emphasis | 2025-01 → 2026-08 |
| Cutoff date | 2026-08-30 |
| Last updated | 2026-08-30 |

---

## ✅ Inclusion Criteria

A paper is **included** if it meets at least 3 of 5:

1. **Thematic relevance:** Addresses Embodied AI, VLA/VLM/LLM in robotics, Sim2Real, or ROS/ROS 2 integration.
2. **Physical applicability:** Proposes or evaluates solutions on physical robots or simulators with real-world transfer.
3. **Framework integration:** Mentions or uses ROS, ROS 2, MoveIt, Nav2, Isaac Sim, or other robotic middleware.
4. **Reproducibility:** Has code, data, or implementation available (or is a foundational paper).
5. **Impact:** Widely cited, from a relevant group (Google DeepMind, NVIDIA, Stanford, ETH, etc.), or from 2025-2026.

---

## ❌ Exclusion Criteria

A paper is **excluded** if it meets any:

1. **No physical robotics:** Purely virtual agents (e.g., Minecraft, video games) without a path to real deployment.
2. **Benchmark without integration:** Datasets/benchmarks without connection to production robotic frameworks.
3. **Redundancy:** Duplicates methodology of another included paper with lesser contribution.
4. **Out of scope:** Synthetic data generation as the only goal, without robotic evaluation.
5. **No access:** PDF not publicly available on arXiv.

---

## 📊 Decision Log

| Paper | Decision | Justification |
|-------|----------|---------------|
| Voyager (2305.16291) | ❌ Excluded | Minecraft agent, no physical robotics |
| BEHAVIOR-1K (2306.03310) | ❌ Excluded | Stanford benchmark without ROS 2 integration |
| RoboGen (2311.01455) | ❌ Excluded | Sim data generation, too specific |
| GenSim (2310.01361) | ❌ Excluded | Redundant with RoboGen |
| ROS2SmolVLA (2608.23320) | ✅ Included | Native VLA on industrial ROS 2 |
| ROS 2 Wrapper Florence-2 (2604.01179) | ✅ Included | Local VLM as ROS 2 node |

---

## 🔁 Update Protocol

1. Run `python scripts/search_recent_papers.py` monthly.
2. Evaluate new papers against inclusion/exclusion criteria.
3. Update `papers.csv` (metadata) and `PAPERS.md` (narrative index).
4. Log decisions in the table of this document.
5. Commit with message `Update paper collection: YYYY-MM`.

---

## 📎 Related Documents

- [`papers/PAPERS.md`](papers/PAPERS.md) — Narrative paper index
- [`papers.csv`](papers.csv) — Structured metadata (machine-readable)
- [`research-gaps.md`](research-gaps.md) — Identified gaps
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — Contribution guide
- [`CITATION.cff`](CITATION.cff) — Repository citation

---

*This protocol follows best practices for systematic reviews adapted to an awesome repository.*