# 🤝 Contributing to Awesome Embodied AI & Sim2Real

Thank you for your interest in contributing! This repository is a curated collection of papers and resources about Embodied AI, VLA, Sim2Real and ROS 2 + AI.

---

## 📋 Before contributing

1. Read the [`research-protocol.md`](research-protocol.md) to understand the inclusion/exclusion criteria.
2. Check that the paper is not already in [`papers.csv`](papers.csv).
3. Make sure the paper meets **at least 3 of 5** inclusion criteria.

---

## ➕ How to add a paper

### Step 1: Verify eligibility
The paper must meet at least 3 of these criteria:
- [ ] Addresses Embodied AI, VLA/VLM/LLM in robotics, Sim2Real or ROS 2
- [ ] Proposes or evaluates solutions on physical robots or simulators with real-world transfer
- [ ] Mentions or uses ROS, ROS 2, MoveIt, Nav2, Isaac Sim or other robotic middleware
- [ ] Has code, data or implementation available (or is foundational)
- [ ] Is high-impact or from 2025-2026

### Step 2: Verify the paper license
**IMPORTANT:** PDFs are NOT versioned in git for license reasons. Each paper on arXiv has its own license:

| arXiv license | Redistribution allowed? |
|---------------|--------------------------|
| CC BY 4.0 | ✅ Yes, with attribution |
| CC BY-SA 4.0 | ✅ Yes, with attribution + share-alike |
| CC0 | ✅ Yes (public domain) |
| CC BY-NC-ND | ❌ No (non-commercial, no derivatives) |
| arXiv non-exclusive license | ❌ No (only arXiv distributes) |
| Author/editor copyright | ❌ No |

**Check the license:** Go to the paper's arXiv page → "License" section (bottom right corner).

The PDF is downloaded locally with:
```bash
# Add the entry in scripts/download_papers.py and run:
python scripts/download_papers.py
```

### Step 3: Update metadata
Add a row in [`papers.csv`](papers.csv) with all fields:

```csv
arxiv_id,title,year,authors_first,robot_type,task,model_type,ros_integration,simulator,dataset,hardware,sim2real,latency_ms,compute_resources,code_available,data_available,limitations,gap_category,category,license,arxiv_url
```

> **Note:** `file_path` refers to the local PDF downloaded by `scripts/download_papers.py`; PDFs are **not versioned in git** for license reasons (see `.gitignore` and Step 2).

### Step 4: Update the narrative index
Add the paper to the corresponding section of [`papers/PAPERS.md`](papers/PAPERS.md).

### Step 5: Log the decision
Add a row in the decision table of [`research-protocol.md`](research-protocol.md).

### Step 6: Pull Request
- Title: `Add paper: [short title]`
- Description: Justification of inclusion according to criteria
- Labels: `paper`, `category-XX`
---

## 🧹 How to propose removing a paper

A paper can be removed if:
- It no longer meets the inclusion criteria (see `research-protocol.md`)
- It is duplicated or redundant
- Its PDF is not accessible

Process:
1. Open an issue with label `removal`
2. Justify according to the exclusion criteria
3. Wait for maintainer approval

---

## 🔍 Metadata quality control

Any PR that modifies `papers.csv` must pass these checks:

| Field | Rule |
|-------|------|
| `arxiv_id` | Valid `YYMM.NNNNN` format |
| `year` | 2017-2026 |
| `title` | Matches the PDF |
| `file_path` | Points to the local PDF downloaded by the script (not versioned in git) |
| `category` | One of the 7 valid categories |
| `limitations` | Not empty (minimum 10 characters) |

Validation script (TODO): `scripts/validate_metadata.py`

---

## 📁 Repository structure

```
awesome-embodied-ai/
├── README.md                 # Main index
├── research-protocol.md      # Research protocol
├── research-gaps.md          # Identified gaps
├── papers.csv                # Structured metadata
├── CITATION.cff              # Repository citation
├── LICENSE                   # CC BY-SA 4.0 license
├── CONTRIBUTING.md           # This file
├── GLOSSARY.md               # Glossary of terms
├── ZENODO.md                 # Zenodo deposition guide
├── papers/                   # Local PDFs organized by category (gitignored)
│   ├── PAPERS.md             # Narrative index
│   ├── 01_VLA_Models/
│   ├── 02_Simulation_Environments/
│   ├── 03_Sim2Real_RL/
│   ├── 04_Robotics_Frameworks/
│   ├── 05_Surveys_Case_Studies/
│   ├── 06_ROS2_AI_LLMs/
│   └── 07_Recent_2025_2026/
└── scripts/
    ├── download_papers.py    # Resilient download with retries
    └── search_recent_papers.py  # arXiv API search
```

---

## 🏷️ Valid categories

| Category | Scope |
|----------|-------|
| `VLA_Models` | Vision-Language-Action models |
| `Simulation_Environments` | Simulators and 3D datasets |
| `Sim2Real_RL` | Sim2Real transfer and RL |
| `Robotics_Frameworks` | ROS 2, MoveIt, Nav2, middleware |
| `Surveys_Case_Studies` | Surveys and case studies |
| `ROS2_AI_LLMs` | ROS 2 + LLM/VLM integration |
| `Recent_2025_2026` | Frontier papers (2025-2026) |

---

## ⚖️ License

By contributing, you agree that your contribution is licensed under [CC BY-SA 4.0](LICENSE).
Paper PDFs belong to their original authors (see arXiv licenses).

---

## 📧 Contact

- Maintainer: [Roncanciovl](https://github.com/roncanciovl)
- Issues: [GitHub Issues](https://github.com/roncanciovl/awesome-embodied-ai/issues)

---

*Last updated: 2026-08-30*