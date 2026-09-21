# LOG.md — paper_amorphous (append-only)

## Session 1 — 2026-09-21 (initialization)
**Goal (user-confirmed via clarify):** Initialize the `scientific-paper-writing` workflow on the amorphous Pt(P) system in `paper_amorphous`, mirroring the `paper_femgo` layout, and scaffold `papers/paper1` (amorphous generation + methods) with the SHC section as a placeholder.

**Actions taken:**
1. Scoped the task: inspected `data/` (17_PPt, 11_bTa, 16_bW), `tmp/` (FLAPW install + SHC example), and the `paper_femgo` reference layout.
2. Audited the Pt–P data: cell families `0_plus5cell` (+5%, 12.523 Å), `1_plus0cell` (+0%, 11.927 Å), `2_plus3cell` (+3%, 12.284 Å), `3_plus10cell` (+10%, 13.119 Å). Confirmed `3_plus10cell` is **excluded** (owner + `DISCUSSION.md`). Noted `main.py` `SCALE_CELL=1.05` is stale for the +0/+3 families.
3. Clarified 5 decisions with the owner (cell scope, systems, paper1 structure, SHC input structures, authors/venue) → spec approved.
4. Created project scaffold: `papers/paper1/` (main.tex + sections/ + figures/ + references.bib + supplementary/), `codes/`, `analysis/`. Copied `spieman.cls` + `spiejour.bst` from `paper_femgo`.
5. Wrote doc scaffold: AGENTS.md, README.md, README.AI.md, LOG.md, TUTORIAL.md, VERSIONS.md, .gitignore, paper_status.md, CLAIMS.md, and empty section stubs.

**Results:** Project skeleton in place; paper1 scaffolded with empty section stubs; SHC section marked as placeholder.

**Decisions & reasoning:**
- Full skill layout (`papers/paper1/` with per-section `.tex`) per owner choice.
- Cell scope: +0/+3/+5% in, +10% out (owner correction).
- Systems: Pt(P) 20/30% focus; 0/10% reference; bTa/bW in SI discussion.
- Paper1: scaffold now (no prose); SHC as placeholder section.
- Authors/venue: same as paper_femgo (Andi Muhammad Nur Fitrah Syamsul, Kohji Nakamura; APS RevTeX 4.2 main + SPIE SI).

**Open items:**
- [ ] Confirm contribution framing with owner (Phase A) before drafting prose.
- [ ] Decide which structures feed the SHC calculation (best-so-far vs representative set vs crystalline reference).
- [ ] Run the SHC calculation (in progress) and fill the placeholder section.
- [ ] Write `codes/` figure/analysis scripts and produce `analysis/` outputs.
- [ ] Commit Milestone 1.

**Time:** 2026-09-21 ~15:40–16:00 JST
