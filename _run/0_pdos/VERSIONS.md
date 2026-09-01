# VERSIONS.md — Version Manifest for _run/0_pdos

One row per tracked source file, with its current module-level `__version__`.
Bump rules (user standing rule): **patch** on every edit; **minor** on
API/behaviour change. Record old→new version in `LOG.md` on every edit.

Source files in this project:

| File | `__version__` | Notes |
|---|---|---|
| `_results/analyze_dos.py` | — | analysis/plot script (not yet versioned) |
| `1_runs/1_pdos_boron3_gs/main.py` | — | DOS/PDOS entry point (not yet versioned) |

## Bump rules

- Any code edit bumps that file's patch version (`1.0.0 → 1.0.1`).
- API/behaviour change bumps minor (`1.0.1 → 1.1.0`).
- On every bump: update this table **and** append a `LOG.md` entry recording
  old→new version.
- Regenerable artifacts (`.traj`, `.xsf`, `.csv`, `.png`, `.db`, `.log`) are
  **not** versioned.

## Placement

Module-level `__version__` goes after the shebang / module docstring / any
`from __future__` import (putting it before `from __future__` raises
`SyntaxError`).
