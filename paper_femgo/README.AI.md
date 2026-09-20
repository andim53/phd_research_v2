# README.AI.md — paper_femgo (agent spec)

## Purpose
Initialize the `scientific-paper-writing` workflow on a finished Fe/MgO manuscript and regenerate all figures from raw AGOX/GPAW data. The manuscript's prose is frozen (ported verbatim); the agent's job is structure, figure regeneration, and data-consistency auditing.

## File layout
```
paper_femgo/
├── AGENTS.md            # governing rules (read first)
├── README.md            # human overview
├── README.AI.md         # this file
├── LOG.md               # append-only action log
├── TUTORIAL.md          # reproduction guide
├── VERSIONS.md          # per-file __version__ manifest
├── papers/
│   └── paper1/
│       ├── main.tex             # RevTeX 4.2 container, \input sections
│       ├── sections/            # 01_abstract … 06_ack_dataavail (.tex per section)
│       ├── figures/             # main-manuscript figures (PNG)
│       ├── references.bib       # main bibliography
│       ├── CLAIMS.md            # frozen claim list
│       ├── paper_status.md      # checkpoint/resume handoff
│       └── supplementary/       # SI: article.tex (SPIE), figures/, report.bib, spieman.cls, spiejour.bst
├── codes/               # figure-regeneration scripts (each has __version__)
├── analysis/            # regenerated figures + result JSONs
├── data/                # raw results (read-only reference)
│   ├── femgo/           # Fe-on-MgO: seed_3..15 (1_db/db_*.db), stop_16 (truncated)
│   ├── mgofe/           # reverse deposition (SI Fig_mgo): seed_0..5
│   └── dos_femgo_flatngs/  # DOS CSVs (dos_seed_3.csv, dos_seed_4.csv) + xsf
└── tmp/draft_paper/     # original finished-draft zips (provenance)
```

## Entry points & commands
- **Compile main:** `cd papers/paper1 && ~/.local/bin/tectonic main.tex`
- **Compile SI:** `cd papers/paper1/supplementary && ~/.local/bin/tectonic article.tex`
- **Regenerate figures:** `cd codes && /home/think/miniconda3/envs/agox_v2/bin/python <script>.py` (see TUTORIAL.md)
- **Env python:** `/home/think/miniconda3/envs/agox_v2/bin/python` (AGOX 3.10.2, ASE 3.25.0). Set `matplotlib.use('Agg')` before plotting.

## Data model (AGOX databases)
- Load: `Database(filename=db); db.restore_to_memory()` (REQUIRED before `get_all_candidates()`).
- Per-atom relative energy: `(E_i - gmin)/len(atoms)`, global min = 0, per system.
- **Minimum-ensemble filter:** keep only `iteration >= 10` (Phase II onward, GPR-relaxed). This is the paper's ensemble definition.
- ΔZ (film flatness) = `z(Fe_max) - z(Fe_min)` over Fe atoms.
- PCA: AGOX `Fingerprint` descriptors → center → covariance → top eigenvector → `psi_1d = Xc @ evecs[:,0]`.

## Expected inputs/outputs
- **Input:** `data/femgo/seed_*/1_db/db_*.db`, `data/mgofe/seed_*/1_db/db_*.db`, `data/dos_femgo_flatngs/dos_seed_*.csv`.
- **Output:** `analysis/figures/*.png` (Fig_Prog, Fig_ConDen, Fig_Boltz, Fig_dos, Fig_convStateDens, Fig_env, Fig_sup, Fig_mgo) + result JSONs.

## Error handling & edge cases
- `stop_16/` (36 configs, iters 1–37) and `mgofe/seed_5` (26 configs) are **truncated** — exclude from pooled statistics; flag in report.
- Only 2 DOS seeds exist (`dos_seed_3.csv`, `dos_seed_4.csv`) — Fig_dos is limited to these.
- Manuscript numbers (seeds 0–13, 1,207 configs) are **kept as drafted**; on-disk reality (seeds 3–15, 1,180) is flagged in the report, never silently edited into prose.

## Provenance
Draft ported from `tmp/draft_paper/RevTeX 4.2 Manuscript.zip` + `Supplementary.zip` (extracted to `tmp/draft_paper/_extracted/`). Figure PNGs copied from the zips; regenerated versions live in `analysis/figures/`.
