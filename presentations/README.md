# 🎞️ Presentations — Awesome Embodied AI & Sim2Real

Self-contained HTML slide decks derived from the evidence in this repository.
No build step, no external dependencies: **open the file in any modern browser**.

| Deck | File | Slides | Scope | Compiled |
|------|------|--------|-------|----------|
| **LLM → VLM → VLA · From Words to Actions** | [`llm-vlm-vla-sota.html`](llm-vlm-vla-sota.html) | 24 | Difference between LLM, VLM and VLA + researched state of the art of each family | 2026-10-19 |

---

## ▶️ How to run a deck

```bash
# simplest: just open it
xdg-open presentations/llm-vlm-vla-sota.html   # Linux
open presentations/llm-vlm-vla-sota.html       # macOS

# or serve it (needed if you use deep links / localStorage themes)
python3 -m http.server 8000
# → http://localhost:8000/presentations/llm-vlm-vla-sota.html
```

### Controls

| Key | Action |
|-----|--------|
| `←` `→` `Space` `PgUp` `PgDn` | Navigate slides |
| `Home` / `End` | First / last slide |
| `O` | Overview grid (click a thumbnail to jump) |
| `N` | Toggle **speaker notes** (every slide has them) |
| `T` | Dark / light theme (persisted) |
| `F` | Fullscreen |
| `?` | Keyboard help · `Esc` closes overlays |
| Swipe | Touch navigation on mobile |

- **Deep links:** `llm-vlm-vla-sota.html#/12` opens slide 12.
- **Export to PDF:** `Ctrl+P` → the print stylesheet puts one slide per page.

---

## 🧠 Deck contents — `llm-vlm-vla-sota.html`

| # | Section | Slides |
|---|---------|--------|
| 1 | Start & foundations | Title · one-slide answer · roadmap · anatomy ("same trunk, different head") |
| 2 | **LLM** | The reasoning layer · frontier leaderboard (Oct 2026) · LLMs as planners (SayCan, Code as Policies, LLM+P, SayPlan, VoxPoser, TidyBot) |
| 3 | **VLM** | The perception layer · MMMU leaderboard · Embodied Reasoning (Gemini Robotics-ER 1.5 → ER 2) |
| 4 | **VLA** | Action representations & decoding · flagship models (π*0.6, π0.5, GR00T N1.7, Gemini Robotics 1.5/2, OpenVLA-OFT) · RECAP · whole-body intelligence · the latency wall |
| 5 | Choosing | Comparison matrix · "same task, three models" · hierarchical stack & decision guide |
| 6 | Frontier | Data pyramid · benchmarks & how to read them · 2026 research trends · open gaps · takeaways · sources |

### Core claim of the deck

> A **VLM** responds with *text*; a **VLA** responds with *physical actions*; an **LLM** responds with text and has never seen an image. The families are nested — a VLA contains a VLM, which contains an LLM — and what changes is the **output head**, the **training data** and the **metric**.

---

## 🔬 Provenance

Every number is sourced on the last slide of the deck. Primary sources: peer-reviewed papers / technical reports, official lab blogs and model cards. Secondary: public leaderboards (llm-stats.com, MMMU via pricepertoken.com) and the AY-Robots VLA catalogue. First-party internal evaluations (e.g. Gemini Robotics 2) are explicitly flagged as non-replicated.

Repository documents used as input: [`README.md`](../README.md), [`GLOSSARY.md`](../GLOSSARY.md), [`papers.csv`](../papers.csv), [`research-gaps.md`](../research-gaps.md), [`tactile-sota.md`](../tactile-sota.md).

---

## 🤝 Contributing a deck

1. Keep it **single-file** and dependency-free (inline CSS/JS, system fonts, no CDN) so it works offline and in CI-less environments.
2. Reuse the existing CSS conventions: `.slide`, `.card.{llm,vlm,vla,gold,warn}`, `.tbl`, `.bars`, `.kpis`, `.note`.
3. Add `data-section` and `data-notes` to every `<section class="slide">` — the HUD and the notes panel depend on them.
4. Date-stamp the deck and list sources on the final slide; mark vendor-claimed numbers.
5. Add a row to the table above.

---

## 🔗 Cross references

- Glossary of terms: [`GLOSSARY.md`](../GLOSSARY.md)
- Paper metadata: [`papers.csv`](../papers.csv) · index: [`papers/PAPERS.md`](../papers/PAPERS.md)
- Research gaps: [`research-gaps.md`](../research-gaps.md)
- Tactile & dexterity SOTA: [`tactile-sota.md`](../tactile-sota.md)

---

*Created 2026-10-19. Living documents — update with every revision of the collection.*
