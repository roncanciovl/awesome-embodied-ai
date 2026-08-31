# 🏛️ Zenodo Deposition Guide

This document describes the process for archiving a stable release of the repository in [Zenodo](https://zenodo.org) and obtaining a permanent **DOI**.

---

## 📋 Prerequisites

- [x] `CITATION.cff` configured (GitHub will show "Cite this repository")
- [x] `LICENSE` defined (CC BY-SA 4.0)
- [x] `papers.csv` with structured metadata
- [x] `research-protocol.md` with reproducible methodology
- [x] GitHub release created (`v1.0.0`, 2026-08-30)
- [x] Zenodo file published: [release v1.0.0](https://doi.org/10.5281/zenodo.22179172) · Concept DOI: [10.5281/zenodo.22179171](https://doi.org/10.5281/zenodo.22179171)

---

## 🔗 Step 1: Connect GitHub with Zenodo

1. Go to [https://zenodo.org/account/settings/github/](https://zenodo.org/account/settings/github/)
2. Sign in with your GitHub account
3. Authorize Zenodo to access the repositories
4. Enable the toggle for `roncanciovl/awesome-embodied-ai`

> **Official documentation:** [Zenodo GitHub Integration](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content)

---

## 🏷️ Step 2: Create a GitHub release

```bash
# From the repository directory:
git tag -a v1.0.0 -m "Release v1.0.0: 41 papers, research protocol, gaps analysis"
git push origin v1.0.0
```

Then on GitHub:
1. Go to **Releases** → **Draft a new release**
2. Tag: `v1.0.0`
3. Title: `v1.0.0 — Initial Research Compendium`
4. Description:
   ```
   ## Awesome Embodied AI & Sim2Real v1.0.0

   First stable release of the research compendium:
   - 41 foundational papers (2017-2026)
   - Structured metadata in papers.csv
   - Reproducible research protocol
   - Gap analysis in 4 sublines
   - Experimental proposal with burger_delivery

   Classification: Dataset / Research compendium
   ```
5. Publish the release

---

## 📦 Step 3: Verify the archive in Zenodo

When the release is published, Zenodo automatically:
1. Archives the repository content
2. Assigns a **DOI** (e.g., `10.5281/zenodo.XXXXXXX`)
3. Creates a registration page with metadata

### Recommended Zenodo metadata

| Field | Value |
|-------|-------|
| **Upload type** | Dataset |
| **Publication type** | Other |
| **Title** | Awesome Embodied AI & Sim2Real: A Living Evidence Map for ROS 2, VLA, and Sim2Real |
| **Description** | (use the abstract from CITATION.cff) |
| **Keywords** | embodied-ai, vision-language-action, sim2real, ros2, llm |
| **License** | CC BY-SA 4.0 |
| **Communities** | Robotics, AI |

---

## 📝 Step 4: Update CITATION.cff with the DOI

Once the Zenodo DOI is obtained, update:

```yaml
identifiers:
  - type: doi
    value: "10.5281/zenodo.XXXXXXX"
    description: "Zenodo archive DOI"
```

And add the badge to README.md:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

---

## 🔄 Future versioning

For each major update of the collection:
1. Increment the version in `CITATION.cff`
2. Create a new tag (`v1.1.0`, `v2.0.0`, etc.)
3. Zenodo will archive automatically and assign a new DOI
4. The "concept" DOI (covers all versions) remains stable

---

## 📊 Deposit classification

| Aspect | Classification |
|--------|----------------|
| **Type** | Dataset / Research compendium |
| **It is not** | Software (the scripts are auxiliary) |
| **Main content** | Structured metadata, reproducible protocol and gap analysis; PDFs are not redistributed |
| **Research value** | Reproducible protocol + gap analysis |

---

## 📎 References

- [Zenodo GitHub Integration](https://zenodo.org/account/settings/github/)
- [GitHub: Referencing and citing content](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content)
- [Citation File Format](https://citation-file-format.github.io/)
- [Zenodo DOI](https://help.zenodo.org/guides/doi/)

---

*Last updated: 2026-08-30 — v1.0.0 archived and verified on Zenodo.*