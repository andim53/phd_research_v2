# INSTRUCTION.md — Owner-side How-To Playbook

This file holds **owner-executable instructions**: step-by-step, line-by-line,
command-by-command guides that let YOU (the project owner) do the work by hand
that the AI agent would otherwise do. The agent's job is to **instruct** — to
write the how-to — not to perform the task.

## Convention (governed by `AGENTS.md`)

- **Append-only.** When the owner asks the agent to *prepare an instruction*
  for a task, the agent **appends** a new self-contained block **at the top of
  the instructions list** (newest first — the latest instruction is inserted
  immediately below the `---` divider above the oldest block). The agent never
  reads back and rewrites or replaces prior blocks; it only prepends the new one
  and moves the divider. (Convention updated 2026-09-06; earlier blocks were
  appended newest-last.)
- **Numbering.** Each block is headed `INSTR #N — <short title>` with a date.
  `N` increments with every append. The agent determines the next `N` by
  finding the highest existing `INSTR #N` header (a targeted header lookup,
  not a full re-read of prior content).
- **Voice.** Blocks are written in the second person, to the owner
  ("you run …", "edit `file.py:line` …"), covering: exact commands (with the
  right env python), where to edit and how, how to run the smoke test, and the
  expected output / how to verify.
- **Trigger.** The agent writes an instruction only on the owner's explicit
  request (e.g. "prepare an instruction for X"), after clarifying the specific
  task/approach when needed. It does not append one automatically for every task
  it executes.
- **Tracking.** The file is tracked and committed under the explicit `_run/0_lcb`
  pathspec; every append also gets an entry in `LOG.md`.

---

*(Owner-executable instructions begin below.)*

---

## INSTR #14 — Run the temperature-dependent XRD for all 17_PPt 10P–30P leaves in one command (Stage 1 + Stage 2 loop)

**Date:** 2026-09-09

**Goal:** Produce `xrd_by_temperature.png` (+ self-describing `xrd_temperature.json`) at
`--figsize 6,3` for the **9 leaves** of the three 17_PPt cells at **10P, 20P, 30P**, in a
**single one-line command**. Because none of these leaves have an `xrd_tdep/` dir yet, the
one-liner runs **Stage 1 first** (write CIFs + `manifest.json` via `xrd_extract_structures.py`
in agox_v2), then **Stage 2** (`xrd_simulate_temperature.py` in pymat_xrd). No source-code
change: `xrd_simulate_temperature.py` v1.1.0 already supports `--figsize`.

**The 9 leaves (10P–30P only):**
- `17_PPt/1_plus0cell/` → `1_10P`, `2_20P`, `3_30P`
- `17_PPt/2_plus3cell/` → `1_10P`, `2_20P`, `3_30P`
- `17_PPt/0_plus5cell/` → `4_3x3_10p` (lowercase `p`), `1_3x3_20P`, `2_3x3_30P`

> **`4_3x3_10p` note:** its DBs live under `seed_2/` and `end/` (not the usual multiple
> `seed_*/`), so `xrd_extract_structures.py` (glob `seed_*/1_db/db_*.db`) will load only the
> `seed_2` subset. That is valid and fine for a first pass; if you want every structure from
> `end/` too, extend Stage 1's glob for that leaf.

### The one-liner (run from `2_analysist/`)

```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist && for L in 17_PPt/1_plus0cell/{1_10P,2_20P,3_30P} 17_PPt/2_plus3cell/{1_10P,2_20P,3_30P} 17_PPt/0_plus5cell/{4_3x3_10p,1_3x3_20P,2_3x3_30P}; do /home/think/miniconda3/envs/agox_v2/bin/python scripts/xrd_extract_structures.py --dataset "$L" --outdir "$L/xrd_tdep" --e-max 0.5 --max-per-window 100000 && /home/think/miniconda3/envs/pymat_xrd/bin/python scripts/xrd_simulate_temperature.py --manifest "$L/xrd_tdep/manifest.json" --outdir "$L/xrd_tdep" --json --figsize 6,3; done
```

Per leaf it runs exactly your Stage-2 template (`--manifest …/xrd_tdep/manifest.json`,
`--outdir …/xrd_tdep`, `--json`, `--figsize 6,3`), but only after that leaf's `manifest.json`
is written by Stage 1 (`&&` chains them, so a Stage-1 failure skips that leaf's Stage 2).

### What each leaf should produce

- `…/xrd_tdep/manifest.json` + `…/xrd_tdep/windows/*/seed_*_sNNNN.cif` (Stage 1)
- `…/xrd_tdep/xrd_by_temperature.png` — 5 solid tab10 curves, `figsize 6,3` (Stage 2)
- `…/xrd_tdep/xrd_temperature.json` — self-describing, schema `0_lcb_xrd_simulate_temperature/v1`

### Verify

1. The loop prints, per leaf, the Stage-1 per-window `[lo,hi): n_total -> n_sampled` lines
   then Stage-2 `T=… K <E>(T)=… eV/atom` lines (5 of them, `<E>` rising with `T`).
2. Confirm 9 leaves were processed: `find 17_PPt -name xrd_temperature.json | wc -l` → `9`.
3. Open any `xrd_by_temperature.png` and check it is 6×3 in and has the 5-curve overlay.
4. Confirm `4_3x3_10p` produced a pattern (its smaller seed set means fewer structures but
   the run must still complete).

> If you only want to re-render figures from already-existing manifests (no Stage 1), run just
> the Stage-2 loop (the `&&` Stage-1 half omitted); but as of today no 17_PPt `xrd_tdep`
> manifest exists, so the full one-liner above is the correct starting point.

---

## INSTR #13 — Add a `--figsize` flag to `xrd_simulate_temperature.py`

**Date:** 2026-09-09

**Goal:** Let you control the size of the temperature-dependent-XRD figure
(`xrd_by_temperature.png`) from the command line, via a `--figsize 'W,H'` flag
in inches, matching the same convention already used by
`xrd_groundstate_compare.py` (INSTR #5). This edit is **already applied and
committed** to `2_analysist/scripts/xrd_simulate_temperature.py`
(`__version__ = "1.1.0"`); the block below documents the change and the
verification so you can reproduce or extend it.

### 1. What changed (4 spots in `scripts/xrd_simulate_temperature.py`)

1. **Version** — `__version__ = "1.1.0"` (line 3).
2. **`plot_from_data` signature** — now takes `figsize=(8, 4.5)` and unwraps it:
   ```python
   def plot_from_data(data, outdir, figsize=(8, 4.5)):
       leaf = data["leaf"]
       w, h = figsize
       fig, ax = plt.subplots(figsize=(w, h))
   ```
   (so the hardcoded `(8, 4.5)` is replaced by `(w, h)`).
3. **Argparse** — new flag before `args = parser.parse_args()`:
   ```python
   parser.add_argument("--figsize", default="8,4.5",
                       help="figure size 'W,H' in inches (default 8,4.5)")
   args = parser.parse_args()
   args.figsize = tuple(float(x) for x in args.figsize.split(","))
   ```
4. **Call site** — `plot_from_data(data, args.outdir, figsize=args.figsize)`.

### 2. Run (pymat_xrd env)

```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python

# default size (8 x 4.5 in)
$PY_X scripts/xrd_simulate_temperature.py \
  --manifest 11_bTa/10_fxg_5b/xrd_tdep/manifest.json \
  --outdir 11_bTa/10_fxg_5b/xrd_tdep --json

# custom size, e.g. 12 x 5 inches
$PY_X scripts/xrd_simulate_temperature.py \
  --manifest 11_bTa/10_fxg_5b/xrd_tdep/manifest.json \
  --outdir 11_bTa/10_fxg_5b/xrd_tdep --json --figsize 12,5
```

### 3. Verify

1. `--help` shows `--figsize FIGSIZE   figure size 'W,H' in inches (default 8,4.5)`.
2. Rerun with two different sizes; each `xrd_by_temperature.png` re-draws at the
   requested `(W, H)` (check the pixel dimensions or open the file) while the
   data, curves, and `xrd_temperature.json` are unchanged.
3. Default (no flag) still produces the 8×4.5 figure as before.

---

## INSTR #12 — Temperature-dependent XRD: Boltzmann thermal-ensemble-average pattern per T, built from the Stage-3 probability-density energy coordinate

**Date:** 2026-09-09

**Goal:** Build and run a new analysis that produces a **temperature-dependent
simulated powder XRD** for a fixed-composition AGOX leaf. The method is the
canonical configurational thermal (Boltzmann) average: each DFT-relaxed structure
contributes its own XRD weighted by its thermal population at temperature `T`,

$$I(2\theta;\,T) \;=\; \frac{\displaystyle\sum_{i}\,w_i(T)\;I_i(2\theta)}
{\displaystyle\sum_{i}\,w_i(T)},
\qquad w_i(T)=\exp\!\Big(-\frac{\Delta E_i}{k_B T}\Big),
\qquad k_B = 8.6173\times10^{-5}\ \text{eV/K},$$

where `\Delta E_i` is the **per-atom relative energy** `(E_i - E_glob)/N` — the
*same* energy coordinate used by the Stage-3 probability density `P_T(E)` (see
INSTR #11) and recorded in each Stage-1 manifest's `rel_energies`. At low `T` the
ground-state (crystalline) population dominates and the pattern is sharp; as `T`
rises the higher-energy (more disordered) configurations gain weight and the
average pattern broadens / peaks drop.

> **Why not "pick the highest-probability energy"?** A pure Boltzmann factor
> decays monotonically with energy, so the peak of `P_T(E)` sits at the ground
> state for *every* `T` — a mode-filter gives ~no `T`-dependence. The ensemble
> average above is the physically meaningful temperature dependence. (Confirmed
> with the owner on 2026-09-09.)
>
> **Leaf correction (owner, 2026-09-09):** the Ta target is `11_bTa/10_fxg_5b`
> (run-10 leaf), **not** `11_p_Ta10b`. W target is `16_bW/4_p_w10b`. Both leaves
> have `seed_*/1_db/db_*.db` and a density-mode `stage3_probability.json`
> (`10_fxg_5b`: 59 atoms, 1486 structs; `4_p_w10b`: 60 atoms, 546 structs).
> `16_bW/4_p_w10b` has **no** existing XRD output, so the whole env-bridge
> (Stage 1 CIF-writing) must run there first.

Because AGOX (agox_v2) and pymatgen (pymat_xrd) live in **separate conda envs**,
the work is two stages exactly like the existing per-window XRD pipeline
(`xrd_extract_structures.py` → `xrd_simulate_crystallinity.py`):

- **Stage 1 (reuse, unchanged, agox_v2):** `xrd_extract_structures.py` loads the
  leaf DBs, computes `(E-E_glob)/N`, bins into energy windows up to `--e-max`,
  and writes one CIF per sampled structure + a `manifest.json` holding each
  window's `cifs` list and matching `rel_energies`. **Run with a large
  `--max-per-window` so every kept structure is written** (the thermal average
  should not be starved of high-energy members).
- **Stage 2 (NEW, pymat_xrd):** `xrd_simulate_temperature.py` (below) reads the
  manifest, computes each sampled structure's powder XRD once, then forms the
  Boltzmann average at the five Stage-3 temperatures
  `[298.15, 348.60, 447.875, 547.15, 646.425]` K. Outputs
  `xrd_by_temperature.png` (overlay, one **solid tab10** curve per `T`, no
  dash/dot styles) and (with `--json`) a self-describing `xrd_temperature.json`.

**Environment pythons:**
- Stage 1 (CIF writing): `/home/think/miniconda3/envs/agox_v2/bin/python`
- Stage 2 (XRD): `/home/think/miniconda3/envs/pymat_xrd/bin/python`

**Two target leaves (per-leaf output in `<leaf>/xrd_tdep/` so the existing
per-window `xrd_out/` is untouched):**
- `2_analysist/11_bTa/10_fxg_5b`
- `2_analysist/16_bW/4_p_w10b`

---

### 1. Create the new Stage-2 script

In `2_analysist/scripts/` create `xrd_simulate_temperature.py` with exactly this
content (module `__version__ = "1.0.0"`):

```python
#!/usr/bin/env python3
"""Stage 2 (temperature-dependent XRD) — Boltzmann thermal-ensemble average.

Runs in the pymat_xrd env (pymatgen + numpy/scipy/matplotlib, NO ase/AGOX).
Reads a Stage-1 manifest.json (windows -> per-sampled-structure CIF paths +
rel_energies, written by xrd_extract_structures.py under agox_v2). For every
sampled structure it computes one powder-XRD pattern, then forms the canonical
configurational thermal (Boltzmann) average

    I(2theta; T) = sum_i w_i(T) * I_i(2theta) / sum_i w_i(T),
    w_i(T) = exp( -DeltaE_i / (kB * T) ),  DeltaE_i = rel_energies[i] (eV/atom)

at each temperature T. kB = 8.6173e-5 eV/K. DeltaE_i is the per-atom relative
energy (E_i - E_glob)/N -- the SAME coordinate as the Stage-3 probability density
P_T(E), so the T list here matches the one used there. At low T the near-ground
(crystalline) population dominates (sharp pattern); as T rises the higher-energy
(disordered) configurations gain weight and the average broadens / peaks drop.

Prints per T the population-weighted mean relative energy
    <E>(T) = sum_i w_i*DeltaE_i / sum_i w_i  (eV/atom)
as a rising-disorder diagnostic.

Writes, under --outdir:
  xrd_by_temperature.png : overlaid thermal-average patterns, one SOLID tab10
                           curve per T (x = 2theta)
  xrd_temperature.json   : with --json, a self-describing payload (schema v1)

Usage (pymat_xrd):
  PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
  $PY_X xrd_simulate_temperature.py --manifest <leaf>/xrd_tdep/manifest.json \
        --outdir <leaf>/xrd_tdep [--json]
"""
from __future__ import annotations

__version__ = "1.0.0"

import argparse
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pymatgen.analysis.diffraction.xrd import XRDCalculator
from pymatgen.core import Structure

plt.rcParams.update({
    "font.size": 12, "font.family": "serif",
    "axes.linewidth": 1.0, "axes.edgecolor": "black",
    "figure.autolayout": True, "figure.dpi": 300,
})

TT_MIN_DEFAULT, TT_MAX_DEFAULT = 10.0, 90.0
TT_STEP = 0.02          # 2theta grid step (deg)
BROADEN_SIGMA = 0.15    # deg Gaussian broadening per reflection (instrument)
KB = 8.6173e-5          # eV/K (Boltzmann)
TEMPS_DEFAULT = [298.15, 348.60, 447.875, 547.15, 646.425]  # matches Stage-3 TEMPS
E_LABEL = r"$\Delta E$ (eV/atom)"


def xrd_temperature_description(leaf, composition, temps, e_max):
    """Self-describing 'description' embedded in xrd_temperature.json."""
    return {
        "kind": "Temperature-dependent simulated powder XRD of one fixed-"
                "composition AGOX leaf via a Boltzmann thermal-ensemble average",
        "schema": "0_lcb_xrd_simulate_temperature/v1",
        "leaf": leaf,
        "composition": composition,
        "e_max": e_max,
        "method": (
            "For every sampled DFT-relaxed structure read from the Stage-1 "
            "manifest, pymatgen XRDCalculator (Cu K-alpha, scaled=False true "
            "relative intensity) on a 2theta grid of step 0.02 deg, each "
            "reflection Gaussian-broadened with sigma 0.15 deg. Thermal pattern "
            "at T: I(2T;T) = sum_i w_i(T)*I_i(2T) / sum_i w_i(T), with "
            "w_i(T)=exp(-DeltaE_i/(kB*T)), DeltaE_i = per-atom relative energy "
            "(E_i-E_glob)/N from the manifest rel_energies, kB=8.6173e-5 eV/K."
        ),
        "energy_units": "rel_energies and mean_rel are eV/atom",
        "units": {
            "grid": "two-theta angle in degrees",
            "intensity": "true relative diffracted intensity (a.u.), weighted "
                         "mean over the sampled ensemble at that T (comparable "
                         "across T: not rescaled to max=1)",
            "T": "temperature in Kelvin",
            "mean_rel": "population-weighted mean relative energy <E>(T) in eV/atom",
        },
        "fields": {
            "series": "one entry per T: T (K), grid = 2theta (deg), "
                      "intensity = Boltzmann-averaged pattern at T, mean_rel = "
                      "population-weighted mean relative energy (eV/atom), "
                      "n = number of sampled structures contributing",
            "num_sampled": "total sampled structures read from the manifest",
            "e_max": "relative-energy cutoff (eV/atom) applied upstream "
                     "(xrd_extract_structures --e-max)",
        },
    }


def load_calc():
    return XRDCalculator(wavelength="CuKa")


def structure_pattern(calc, cif_path, manifest_dir, tt_min, tt_max, grid):
    """Return the Gaussian-broadened intensity array of one CIF on ``grid``."""
    full = cif_path if os.path.isabs(cif_path) else os.path.join(manifest_dir, cif_path)
    struct = Structure.from_file(full)
    pat = calc.get_pattern(struct, two_theta_range=(tt_min, tt_max), scaled=False)
    inten = np.zeros_like(grid)
    for x, y in zip(pat.x, pat.y):
        gi = int(round((x - tt_min) / TT_STEP))
        if 0 <= gi < len(grid):
            inten[gi] += y
    from scipy.ndimage import gaussian_filter1d
    return gaussian_filter1d(inten, sigma=BROADEN_SIGMA / TT_STEP)


def collect_from_manifest(manifest_path, tt_min, tt_max):
    """Flatten every window's sampled (cif, rel_energy) pairs; compute XRD once."""
    with open(manifest_path) as f:
        man = json.load(f)
    man_dir = os.path.dirname(os.path.abspath(manifest_path))
    grid = np.arange(tt_min, tt_max + TT_STEP, TT_STEP)
    calc = load_calc()
    rel_energies, patterns = [], []
    for w in man["windows"]:
        for cif, relE in zip(w.get("cifs", []), w.get("rel_energies", [])):
            patterns.append(structure_pattern(calc, cif, man_dir, tt_min, tt_max, grid))
            rel_energies.append(relE)
    if not patterns:
        raise SystemExit("manifest has no sampled structures")
    return man, grid, np.asarray(rel_energies), patterns


def thermal_average(rel_energies, patterns, T):
    """I(T) = sum_i w_i(T)*I_i / sum_i w_i(T); also returns <E>(T) and w sum."""
    w = np.exp(-rel_energies / (KB * T))
    Z = w.sum()
    num = np.zeros_like(patterns[0])
    for wi, pi in zip(w, patterns):
        num += wi * pi
    mean_rel = float((w * rel_energies).sum() / Z) if Z > 0 else float("nan")
    return num / Z, mean_rel, len(w)


def plot_from_data(data, outdir):
    """Draw xrd_by_temperature.png from a plots-data dict (overlay per T)."""
    leaf = data["leaf"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    tab10 = plt.get_cmap("tab10")
    for i, s in enumerate(data["series"]):
        ax.plot(s["grid"], s["intensity"], lw=1.8,
                color=tab10(i % tab10.N), label=f"{s['T']:g} K")
    ax.set_xlabel(r"2$\theta$ (deg)"); ax.set_ylabel("Intensity (a.u.)")
    ax.set_title(f"{leaf} — temperature-dependent XRD (Boltzmann average)")
    ax.legend(title="T", fontsize=9, ncol=2, loc="upper right")
    ax.set_xlim(data["xlim"])
    fig.savefig(os.path.join(outdir, "xrd_by_temperature.png"))
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="Stage 2 (pymat_xrd): temperature-dependent powder XRD via "
                    "Boltzmann thermal-ensemble average over a leaf's sampled "
                    "structures (reads a Stage-1 manifest).")
    parser.add_argument("--manifest", required=True,
                        help="path to Stage-1 manifest.json (xrd_extract_structures.py)")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--2theta-min", type=float, default=TT_MIN_DEFAULT)
    parser.add_argument("--2theta-max", type=float, default=TT_MAX_DEFAULT)
    parser.add_argument("--temps", type=float, nargs="*", default=None,
                        help="temperatures in K; default matches Stage-3 TEMPS "
                             f"{TEMPS_DEFAULT}")
    parser.add_argument("--json", action="store_true",
                        help="also write xrd_temperature.json (self-describing)")
    args = parser.parse_args()

    temps = list(args.temps) if args.temps else list(TEMPS_DEFAULT)
    os.makedirs(args.outdir, exist_ok=True)
    man, grid, rel_energies, patterns = collect_from_manifest(
        args.manifest, getattr(args, "2theta_min"), getattr(args, "2theta_max"))
    leaf = man["leaf"]
    composition = man.get("composition", {})
    e_max = man.get("e_max")

    print("=" * 70)
    print("XRD Stage 2 (pymat_xrd) — temperature-dependent XRD (Boltzmann average)")
    print(f"leaf: {leaf}  comp={composition}  n_sampled={len(patterns)}")
    print(f"T(K): {temps}")
    print("=" * 70)

    series = []
    for T in temps:
        iten, mean_rel, n = thermal_average(rel_energies, patterns, T)
        series.append({"T": T,
                       "grid": grid.tolist(),
                       "intensity": iten.tolist(),
                       "mean_rel": mean_rel,
                       "n": n})
        print(f"  T={T:8.3f} K   <E>(T)={mean_rel:+.4f} eV/atom   (n={n})")

    data = {"leaf": leaf, "composition": composition,
            "e_max": e_max, "num_sampled": len(patterns),
            "xlim": [getattr(args, "2theta_min"), getattr(args, "2theta_max")],
            "series": series}
    plot_from_data(data, args.outdir)

    if args.json:
        out = dict(data)
        out["description"] = xrd_temperature_description(leaf, composition,
                                                         temps, e_max)
        jp = os.path.join(args.outdir, "xrd_temperature.json")
        with open(jp, "w") as f:
            json.dump(out, f, indent=1)
        print(f"  -> xrd_temperature.json written to {jp}")

    print(f"\nDONE. figures under {os.path.abspath(args.outdir)}")


if __name__ == "__main__":
    main()
```

*(Tips: the file must be chmod +x only if you want to execute it directly; the
commands below invoke it via the pymat_xrd interpreter so no shebang chmod is
needed.)*

---

### 2. Run Stage 1 (CIF writing) for both leaves

From `2_analysist/`, run the **existing** `xrd_extract_structures.py` in
**agox_v2**. Output goes to a fresh `<leaf>/xrd_tdep/` dir. Use a large
`--max-per-window` so every kept structure is written (the thermal average must
not be starved of high-energy members); `--e-max 0.5` drops bad/unrelaxed
outliers the same way the Stage-3 plots do.

```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
PY_A=/home/think/miniconda3/envs/agox_v2/bin/python

$PY_A scripts/xrd_extract_structures.py \
  --dataset 11_bTa/10_fxg_5b --outdir 11_bTa/10_fxg_5b/xrd_tdep \
  --e-max 0.5 --max-per-window 100000 --bin-width 0.1

$PY_A scripts/xrd_extract_structures.py \
  --dataset 16_bW/4_p_w10b --outdir 16_bW/4_p_w10b/xrd_tdep \
  --e-max 0.5 --max-per-window 100000 --bin-width 0.1
```

Expected: each leaf prints `relE/atom: min … max`, drops any structures above
`0.5 eV/atom`, then per-window `[lo,hi): n_total -> n_sampled` (n_sampled should
equal n_total since the cap is huge), and finishes with `DONE. manifest ->
…/xrd_tdep/manifest.json`. `xrd_tdep/windows/*/seed_*_sNNNN.cif` files are
written.

---

### 3. Run Stage 2 (temperature-dependent XRD) for both leaves

From the same `2_analysist/` dir, run the **new** `xrd_simulate_temperature.py`
in **pymat_xrd**, one leaf at a time, with `--json` so the self-describing
payload is emitted:

```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python

$PY_X scripts/xrd_simulate_temperature.py \
  --manifest 11_bTa/10_fxg_5b/xrd_tdep/manifest.json \
  --outdir 11_bTa/10_fxg_5b/xrd_tdep --json

$PY_X scripts/xrd_simulate_temperature.py \
  --manifest 16_bW/4_p_w10b/xrd_tdep/manifest.json \
  --outdir 16_bW/4_p_w10b/xrd_tdep --json
```

Expected per leaf:
- stdout prints one line per T, e.g. `T=298.150 K <E>(T)=+0.000x eV/atom` … and
  `T=646.425 K <E>(T)=+0.0xxx eV/atom`, with the mean rising monotonically with
  `T` (disorder increasing). If `<E>` is flat, the leaf's sampled energy spread
  is too small or Stage 1 capped the high-energy tail — check `n_sampled` equals
  the DB structure count.
- `xrd_by_temperature.png` shows 5 solid tab10 curves overlaid on `x=2theta`;
  the low-T (dark purple) curve is sharpest, high-T (orange) curves broader /
  lower peaks (peak broadening, not full amorphization).
- `xrd_temperature.json` present with `description.schema ==
  "0_lcb_xrd_simulate_temperature/v1"`, `data.series[*].intensity` and `mean_rel`
  matching the printed `<E>(T)`.

---

### 4. Verify (grounded in real output)

1. `grep -c "seed_" 11_bTa/10_fxg_5b/xrd_tdep/manifest.json` CIF references match
   the DB structure count for that leaf (1486 for `10_fxg_5b` above `e_max`;
   fewer if some were dropped). Confirm `n_sampled == n_total` per window.
2. Recompute one temperature by hand from the JSON: pick `T`, `w =
   np.exp(-relE/(8.6173e-5*T))`, `I = sum(w*I_i)/sum(w)` and check against
   `series[i].intensity` (spot-check a few 2theta bins).
3. Visually confirm low `T` (298.15 K) is the sharpest and high `T`
   (646.425 K) is the broadest in `xrd_by_temperature.png`; `<E>(T)` printed
   rising confirms the thermal population is spreading to higher energy.
4. Update `VERSIONS.md` (new row:
   `xrd_simulate_temperature.py` `1.0.0` — new: temperature-dependent XRD,
   Boltzmann thermal-ensemble average) and add a `LOG.md` entry. Commit the two
   source/version files; `xrd_tdep/` (CIFs, PNG, JSON) is a regenerable artifact
   and is gitignored, so do not commit it.

---

## INSTR #11 — Stage-3 probability density P(E): how it is computed from the state density g(E) (LaTeX derivation)

**Date:** 2026-09-09

**Goal:** Write down, in LaTeX notation, exactly how the Stage-3 "probability
density" `P(E)` is calculated from the state density `g(E)` in
`2_analysist/run_analysis_indices.py`. This is a *derivation reference* — no code
changes. Everything below maps 1:1 onto the current code
(`__version__ = "2.12.0"`): read `_probability_data` (runner `:750`),
`_boltzmann_density` (`:739`), `calculate_boltzmann_probs` (`:724`) and the
stage-3 self-describing `description` (`:294`). There is **no literal `gE`
variable** in the project — the density of states is the **Gaussian-KDE state
density `rho(E)`** described below.

### 0. Inputs and energy normalisation

The input is the set of DFT-relaxed structures kept from the seed DBs
(`iteration >= --start-iter`, default 10). Every structure has the same
`N = num_atoms` atoms in the fixed supercell. With raw total energies `{E_i}`
and global minimum `E_min = min_i E_i`, define the **relative per-atom energy**

$$e_i \;=\; \frac{E_i - E_{\min}}{N}\qquad\text{(eV/atom)}\qquad i=1,\dots,n,$$

computed in code as `rel = (energies - energies.min()) / num_atoms`
(runner `:761`). This is the energy coordinate used throughout Stage 3 (and the
plot x-axis label is `E_i - E_glob` (eV/atom), `E_LABEL` at `:108`).

### 1. State density g(E) — the Gaussian-KDE over the sample

The state (configuration) density is **not** read from a `gE` file: it is the
kernel-density estimate of the observed sample `{e_i}`,

$$g(e) \;=\; \frac{1}{n\,b}\sum_{i=1}^{n} K\!\left(\frac{e - e_i}{b}\right),
\qquad K(u)=\frac{1}{\sqrt{2\pi}}\,e^{-u^{2}/2}\ \text{(Gaussian kernel)},$$

which is `rho = scipy.stats.gaussian_kde(rel, bw_method=h)` evaluated at `e`
(runner `:762`). The bandwidth `b` follows Scott's rule by default; a scalar
`--h` flag multiplies the Scott bandwidth (so `b = h\cdot b_\text{scott}`).
Units of `g` are (config./eV-atom). A tiny floor `+1e-15` is added before any
evaluation to avoid a zero density (`:743`).

### 2. Boltzmann weight

For a temperature `T` and a chosen reference `E_ref = min_i e_i` (which is `0`,
because `rel` is already relative to its own min; set at `:764`), the thermal
weight is

$$w_T(e) \;=\; \exp\!\left(-\frac{e - E_{\mathrm{ref}}}{k_B T}\right),
\qquad k_B = 8.6173\times10^{-5}\ \text{eV/K}.$$

### 3. Probability density P(E) — default "density" mode (∫P dE = 1)

On a dense grid `{E_k}_{k=1}^{500} = \texttt{np.linspace}(e_{lo},\,e_{hi},\,500)`
(`:777`; `e_{lo}=-0.1` when `--e-max` is set else `0`; `e_{hi}=\texttt{e-max}`
or `rel.max()+0.05`), the unnormalised measure is `g(E)\,w_T(E)` and the
normalisation is its **trapezoid integral** over the grid:

$$P_T(e) \;=\;
\frac{g(e)\,w_T(e)}{\displaystyle \int_{e_{lo}}^{e_{hi}} g(e')\,w_T(e')\,\mathrm{d}e'}
\;=\;
\frac{g(e)\,\exp\!\left(-\dfrac{e-E_{\mathrm{ref}}}{k_B T}\right)}
{\displaystyle \int_{e_{lo}}^{e_{hi}} g(e')\,\exp\!\left(-\dfrac{e'-E_{\mathrm{ref}}}{k_B T}\right)\mathrm{d}e'}.$$

This is exactly `_boltzmann_density` (`:739`): `num = rho*w`, `norm =
trapezoid(num, egrid)`, `return num/norm`. Because `norm` is the trapezoid
integral of the numerator, the resulting curve satisfies

$$\int_{e_{lo}}^{e_{hi}} P_T(e)\,\mathrm{d}e \;=\; 1 \qquad\text{per temperature }T.$$

So `P_T` is a genuine probability **density** on the plotted window; its peak can
exceed `1` when the window is narrow. It is plotted as a smooth curve per `T`
(`:804`). The temperature list is `TEMPS = [298.15, 348.60, 447.875, 547.15,
646.425]` K (`:112`).

### 4. Legacy "peak" mode (--peak-norm, scatter)

With the flag, the computation is instead done only at the *observed* energies
`{e_i}` and rescaled so the global peak equals 1 (`calculate_boltzmann_probs`,
`:724`):

$$P_i \;=\; \frac{g(e_i)\,w_T(e_i)}{\displaystyle\sum_{j} g(e_j)\,w_T(e_j)}
\qquad\longrightarrow\qquad \frac{P_i}{\max_j P_j}
\qquad\text{(peak $=1$),}$$

with `dE_i = e_i - E_ref`. This is a *relative likelihood* (not a density) and is
not comparable across `T` since every temperature touches `1`. Plotted as a
scatter (`:807`).

### 5. How to verify

1. In any leaf `analysis_indices/`, open `stage3_probability.json` and confirm
   `data.norm == "density"` and each `series[].probs` trapezoid-integrates to
   ~1 over `data.series[].egrid`.
2. `description.method` (schema v2) restates the formula inline — check it
   matches the notation above.
3. Recompute by hand for one `T`: `rho = gaussian_kde(rel, bw_method=0.05)`,
   `P = rho(egrid)*exp(-egrid/kB/T)` / `trapezoid(...)` and compare with the JSON
   `probs` array.

---

## INSTR #10 — Regenerate all analysis_indices (JSONs + PNGs) with the ∫P dE=1 density default and `--h 0.05`, via a new material-grouped script (11_bTa, 16_bW, 17_PPt)

**Date:** 2026-09-08

**Goal:** Create and run a new command that **regenerates every `analysis_indices`
dir (the 3 stage JSONs + 3 PNGs)** for the **21 leaves** that carry BOTH an
`analysis_indices` dir AND an xrd dir, across the **11_bTa (5), 16_bW (4),
17_PPt (12)** families — now using the **new ∫P dE = 1 continuous-density default**
(no `--peak-norm`) and the **`--h 0.05`** sharper KDE bandwidth, both at
`--e-max 0.5` eV/atom. The command is written as **explicit per-leaf commands
grouped by material family** (the existing `json_export/regenerate_analysis_json.sh`
style) so you can run a whole family, or comment out any leaf to skip it.

**Why these 21:** the leaves that have an xrd dir AND an analysis_indices dir.
`15_bPt` is excluded (its leaves have no per-leaf xrd dir — only a family-level
`xrd_gs_compare`). `17_PPt/0_plus5cell/0_PPt_4x4_20P` is excluded (it has `xrd_out`
but **no** `analysis_indices`/runner dataset). List:

- **11_bTa (5):** `7_fxg_0b`, `8_fxg_1b`, `9_fxg_3b`, `10_fxg_5b`, `11_p_Ta10b`
- **16_bW (4):** `1_w0b`, `2_w1b`, `3_w3b`, `4_p_w10b`
- **17_PPt (12):** `0_plus5cell/{1_3x3_20P,2_3x3_30P,3_3x3_0P,4_3x3_10p}`,
  `1_plus0cell/{0_0P,1_10P,2_20P,3_30P}`, `2_plus3cell/{0_0P,1_10P,2_20P,3_30P}`

**Environment python:** `/home/think/miniconda3/envs/agox_v2/bin/python`
(AGOX 3.10.2 + ASE + GPAW). Base `python3` has none of these.

**Note:** the runner is now **v2.12.0** — the density mode is the *default*, so each
command emits `stage3_probability.json` with `data.norm = "density"`, per-series
`egrid` (500-pt) + `probs` (each integrates to ~1), and a schema-v2 self-describing
`description`. `--h 0.05` now actually sharpens Stage 3 (the 2.12.0 fix). No
`--peak-norm` is passed, so every leaf is regenerated in density mode.

---

### 1. Create the new command script

Save this as `json_export/regenerate_all_density.sh` (in
`/home/think/Desktop/research/_run/0_lcb/2_analysist/json_export/`), then
`chmod +x` it:

```bash
#!/bin/bash
# Regenerate the analysis_indices JSONs + PNGs for every leaf that has BOTH an
# analysis_indices dir AND an xrd dir, across the xrd-bearing families 11_bTa,
# 16_bW, 17_PPt (21 leaves). Uses the runner's new DEFAULT continuous probability
# density (integral P dE = 1; no --peak-norm) and --h 0.05 (sharper KDE) at
# --e-max 0.5 eV/atom. One command per leaf, grouped by material family.
# Run from: /home/think/Desktop/research/_run/0_lcb/2_analysist
# Heavy (~1 h for all 21 leaves). To skip a leaf, comment its line out.
set -u
PY=/home/think/miniconda3/envs/agox_v2/bin/python
H=0.05
EMX=0.5
cd /home/think/Desktop/research/_run/0_lcb/2_analysist || exit 1
echo "Regenerating analysis_indices with density default (integral P dE = 1), --h $H, --e-max $EMX"

# ===================== 11_bTa (Ta-B) =====================
"$PY" run_analysis_indices.py --dataset "11_bTa/7_fxg_0b"   --outdir "11_bTa/7_fxg_0b/analysis_indices"   --json-dir "11_bTa/7_fxg_0b/analysis_indices"   --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "11_bTa/8_fxg_1b"   --outdir "11_bTa/8_fxg_1b/analysis_indices"   --json-dir "11_bTa/8_fxg_1b/analysis_indices"   --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "11_bTa/9_fxg_3b"   --outdir "11_bTa/9_fxg_3b/analysis_indices"   --json-dir "11_bTa/9_fxg_3b/analysis_indices"   --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "11_bTa/10_fxg_5b"  --outdir "11_bTa/10_fxg_5b/analysis_indices"  --json-dir "11_bTa/10_fxg_5b/analysis_indices"  --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "11_bTa/11_p_Ta10b" --outdir "11_bTa/11_p_Ta10b/analysis_indices" --json-dir "11_bTa/11_p_Ta10b/analysis_indices" --e-max "$EMX" --h "$H"

# ===================== 16_bW (W-B) =====================
"$PY" run_analysis_indices.py --dataset "16_bW/1_w0b"     --outdir "16_bW/1_w0b/analysis_indices"     --json-dir "16_bW/1_w0b/analysis_indices"     --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "16_bW/2_w1b"     --outdir "16_bW/2_w1b/analysis_indices"     --json-dir "16_bW/2_w1b/analysis_indices"     --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "16_bW/3_w3b"     --outdir "16_bW/3_w3b/analysis_indices"     --json-dir "16_bW/3_w3b/analysis_indices"     --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "16_bW/4_p_w10b"  --outdir "16_bW/4_p_w10b/analysis_indices"  --json-dir "16_bW/4_p_w10b/analysis_indices"  --e-max "$EMX" --h "$H"

# ===================== 17_PPt (Pt-P), 0_plus5cell =====================
"$PY" run_analysis_indices.py --dataset "17_PPt/0_plus5cell/1_3x3_20P" --outdir "17_PPt/0_plus5cell/1_3x3_20P/analysis_indices" --json-dir "17_PPt/0_plus5cell/1_3x3_20P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/0_plus5cell/2_3x3_30P" --outdir "17_PPt/0_plus5cell/2_3x3_30P/analysis_indices" --json-dir "17_PPt/0_plus5cell/2_3x3_30P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/0_plus5cell/3_3x3_0P"  --outdir "17_PPt/0_plus5cell/3_3x3_0P/analysis_indices"  --json-dir "17_PPt/0_plus5cell/3_3x3_0P/analysis_indices"  --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/0_plus5cell/4_3x3_10p" --outdir "17_PPt/0_plus5cell/4_3x3_10p/analysis_indices" --json-dir "17_PPt/0_plus5cell/4_3x3_10p/analysis_indices" --e-max "$EMX" --h "$H"

# ===================== 17_PPt (Pt-P), 1_plus0cell =====================
"$PY" run_analysis_indices.py --dataset "17_PPt/1_plus0cell/0_0P" --outdir "17_PPt/1_plus0cell/0_0P/analysis_indices" --json-dir "17_PPt/1_plus0cell/0_0P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/1_plus0cell/1_10P" --outdir "17_PPt/1_plus0cell/1_10P/analysis_indices" --json-dir "17_PPt/1_plus0cell/1_10P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/1_plus0cell/2_20P" --outdir "17_PPt/1_plus0cell/2_20P/analysis_indices" --json-dir "17_PPt/1_plus0cell/2_20P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/1_plus0cell/3_30P" --outdir "17_PPt/1_plus0cell/3_30P/analysis_indices" --json-dir "17_PPt/1_plus0cell/3_30P/analysis_indices" --e-max "$EMX" --h "$H"

# ===================== 17_PPt (Pt-P), 2_plus3cell =====================
"$PY" run_analysis_indices.py --dataset "17_PPt/2_plus3cell/0_0P" --outdir "17_PPt/2_plus3cell/0_0P/analysis_indices" --json-dir "17_PPt/2_plus3cell/0_0P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/2_plus3cell/1_10P" --outdir "17_PPt/2_plus3cell/1_10P/analysis_indices" --json-dir "17_PPt/2_plus3cell/1_10P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/2_plus3cell/2_20P" --outdir "17_PPt/2_plus3cell/2_20P/analysis_indices" --json-dir "17_PPt/2_plus3cell/2_20P/analysis_indices" --e-max "$EMX" --h "$H"
"$PY" run_analysis_indices.py --dataset "17_PPt/2_plus3cell/3_30P" --outdir "17_PPt/2_plus3cell/3_30P/analysis_indices" --json-dir "17_PPt/2_plus3cell/3_30P/analysis_indices" --e-max "$EMX" --h "$H"

echo "DONE: all 21 leaves regenerated (density default, --h $H, --e-max $EMX)"
```

---

### 2. Smoke test ONE leaf first (scratch outdir, so no tracked output is touched)

Before the full run, verify the exact behaviour on one leaf into `/tmp` (do **not**
overwrite the leaf's tracked `analysis_indices/` yet):

```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
  --dataset "11_bTa/7_fxg_0b" --outdir /tmp/instr10_smoke \
  --json-dir /tmp/instr10_smoke/analysis_json --e-max 0.5 --h 0.05
```

**Verify:** `/tmp/instr10_smoke/binding_probability_vs_temperature.png` shows smooth
per-temperature curves (density mode), and the JSON is a density payload:

```python
/home/think/miniconda3/envs/agox_v2/bin/python -c "
import json
from scipy.integrate import trapezoid
d = json.load(open('/tmp/instr10_smoke/analysis_json/stage3_probability.json'))
print('schema      :', d['description']['schema'])     # expect 0_lcb_analysis_stage3/v2
print('data.norm   :', d['data']['norm'])              # expect density
print('series keys :', list(d['data']['series'][0].keys()))  # egrid+probs+norm+T+color
for s in d['data']['series']:
    print(f\"  {s['T']:8.2f} K  area={trapezoid(s['probs'], s['egrid']):.5f}  peak={max(s['probs']):.3f}\")
"
```

Each series area should be `~1.0000` and the peak **> 1** (a narrow ∫=1 density).
`--h 0.05` should give visibly sharper (narrower, taller) curves than the Scott
default. If any area is far from 1 or the JSON is not density mode, **stop** and
check the runner version is 2.12.0.

---

### 3. Run the full regeneration

```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
bash json_export/regenerate_all_density.sh
```

This regenerates, for each of the 21 leaves, its `analysis_indices/` content:
`progression_seed_split_0.png` (under `progression_plots/`), `conf_space.png`,
`binding_probability_vs_temperature.png`, and the 3 stage JSONs
(`stage1_progression.json`, `stage2_landscape.json`, `stage3_probability.json`) —
all now in **density mode** with `--h 0.05`. It writes directly into each leaf's
tracked `analysis_indices/` (the per-leaf convention). Expect ~1 h total.

---

### 4. Verify every leaf is density mode + ∫=1

Run a check across all 21 `stage3_probability.json` files:

```bash
cd /home/think/Desktop/research/_run/0_lcb
/home/think/miniconda3/envs/agox_v2/bin/python -c "
import json, glob
from scipy.integrate import trapezoid
paths = glob.glob('2_analysist/*/*/analysis_indices/stage3_probability.json') + \
        glob.glob('2_analysist/*/*/*/analysis_indices/stage3_probability.json')
paths = [p for p in paths if any(f in p for f in ('11_bTa','16_bW','17_PPt'))]
bad = 0
for p in sorted(paths):
    d = json.load(open(p))
    data = d.get('data', {})
    norm = data.get('norm'); schema = d.get('description',{}).get('schema')
    s0 = data.get('series',[{}])[0]
    areas = [trapezoid(s['probs'], s['egrid']) for s in data.get('series',[]) if 'egrid' in s]
    ok = norm=='density' and schema.endswith('/v2') and areas and all(abs(a-1)<1e-3 for a in areas)
    bad += 0 if ok else 1
    print(('OK ' if ok else 'BAD') + f'  {norm:7} {schema:22} nseries={len(data.get(\"series\",[]))} n={data.get(\"n_structures\")}  {p}')
print('total', len(paths), 'files,', bad, 'not in density/∫=1 form')
"
```

Expect all 21 lines `OK` with `norm=density`, schema `.../v2`, and area ≈ 1.

---

### 5. Commit (script + regenerated outputs + LOG/VERSIONS)

The regenerated `analysis_indices` JSONs/PNGs ARE tracked for these leaves, so stage
the script and all regenerated outputs plus the docs and commit under the explicit
`_run/0_lcb` pathspec:

```bash
cd /home/think/Desktop/research/_run/0_lcb
git add 2_analysist/json_export/regenerate_all_density.sh \
        2_analysist/11_bTa/ 2_analysist/16_bW/ 2_analysist/17_PPt/
git commit -m "feat(0_lcb): regenerate 21 analysis_indices dirs in density mode (∫P dE=1 default) with --h 0.05 (11_bTa/16_bW/17_PPt)"
```

Before committing, confirm the staged set only contains what you expect
(`git status --short` + `git diff --cached --stat`); stage 15_bPt etc. only if you
also want them. Add a `LOG.md` entry describing the regeneration (runner stays
2.12.0 — the `.sh` script is not versioned). Do **not** commit the `/tmp` smoke dir.

---

## INSTR #9 — Add a Stage-3 flag for a true continuous probability density (∫ P dE = 1); make it the default, with `--peak-norm` to reproduce the old peak=1 figure, and forward `--h` into Stage 3

**Date:** 2026-09-08

**Goal:** In `2_analysist/run_analysis_indices.py` (currently v2.11.0), change the
Stage-3 Boltzmann output (`binding_probability_vs_temperature.png` +
`stage3_probability.json`) so that **by default** it plots a *true continuous
probability density* normalized so **∫ P dE = 1** over the plotted energy window
(smooth curve per temperature, auto-scaled y-axis). Keep the old behaviour
reachable via a new `--peak-norm` flag (per-structure scatter scaled to peak = 1,
y in [0, 1.05]) so existing figures stay reproducible. While touching the Stage-3
plumbing, **also forward the existing `--h` (KDE bandwidth) into Stage 3** — it is
wired for it (`step3_probability`/`_probability_data` accept `kde_bw`) but `main()`
never passes it, so Stage 3 currently ignores `--h`.

The `∫ P dE = 1` normalization is done as a **continuous** trapezoid integral over
a dense energy grid:

```python
P(E) = rho(E) * exp(-(E - E_min) / k_B T) / trapezoid( rho(E) * exp(...), E_grid )
```

This is sample-spacing independent (unlike the MrAfi/`tmp` script's discrete
trapezoid over the observed points, which double-normalizes and depends on the
arbitrary spacing of your structures). It is the definition a reviewer means by a
Boltzmann-weighted probability density, and it makes hot-vs-cold curves genuinely
comparable (all carry total area 1).

**Environment python:** `/home/think/miniconda3/envs/agox_v2/bin/python`
(AGOX 3.10.2 + ASE + GPAW). Base `python3` has none of these.

---

### 1. Add the `trapezoid` import

File: `2_analysist/run_analysis_indices.py`, the import block (current line 72).
Find:

```python
from scipy.stats import gaussian_kde
```

Add the line directly below it:

```python
from scipy.integrate import trapezoid
```

---

### 2. Replace the whole Stage-3 function block

In the same file, select **everything from the `def calculate_boltzmann_probs(`
line through the end of `step3_probability`** — i.e. the current v2.11.0 block at
approximately lines 685-752, which runs:

```python
def calculate_boltzmann_probs(energies, kde_model, T):
    ...
def _probability_data(structures, energies, e_max=None, kde_bw=None):
    ...
def _plot_probability_from_data(data, outdir):
    ...
def step3_probability(structures, energies, outdir, e_max=None, json_dir=None,
                      dataset=None, kde_bw=None):
    ...
    return _plot_probability_from_data(data, outdir)
```

(the block ends right before the `# ---` banner above the `replot_from_json`
function). Replace that entire selection with:

```python
def calculate_boltzmann_probs(energies, kde_model, T):
    """Legacy per-structure Boltzmann likelihood scaled so peak = 1.

    Pi = rho(E)*exp(-dE/kbT)/Z, then /max. Used only under --peak-norm
    (scatter over the observed energy points)."""
    kb = 8.6173e-5  # eV/K
    rho_i = kde_model.evaluate(energies) + 1e-15
    relative_e = energies - np.min(energies)
    weights = np.exp(-relative_e / (kb * T))
    numerator = rho_i * weights
    Z = np.sum(numerator)
    probs = numerator / Z
    return probs / probs.max()


def _boltzmann_density(kde, E_ref, T, egrid):
    """Continuous Boltzmann density P(E) = rho*w / trapezoid(rho*w, E) on a grid,
    so the trapezoid area under P over the grid equals 1 (integral P dE = 1)."""
    kb = 8.6173e-5  # eV/K
    rho = kde.evaluate(egrid) + 1e-15
    w = np.exp(-(egrid - E_ref) / (kb * T))
    num = rho * w
    norm = trapezoid(num, egrid)
    return num / norm


def _probability_data(structures, energies, e_max=None, kde_bw=None,
                      peak_norm=False):
    """Return the Stage-3 plotting data (rel energies/grid, per-T P, temps,
    colors, axis windows, normalization mode) as a JSON-safe dict.

    peak_norm=False (DEFAULT): true continuous probability density, each T
    normalized so integral P dE = 1 over the plotted window (smooth curve;
    ylim auto-scales, peak can exceed 1).
    peak_norm=True: legacy per-structure likelihood scaled so peak = 1
    (scatter; ylim [0, 1.05])."""
    num_atoms = len(structures[0])
    rel = (energies - energies.min()) / num_atoms
    kde = gaussian_kde(rel, bw_method=kde_bw)
    e_lim = (-0.1, e_max) if e_max is not None else (0.0, float(rel.max()) + 0.05)
    E_ref = float(rel.min())
    series = []
    if peak_norm:
        # legacy scatter (peak = 1) — exactly the pre-2.12.0 behaviour
        for T, color in zip(TEMPS, COLORS_PLASMA):
            series.append({
                "T": T, "color": color, "rel": rel.tolist(),
                "probs": calculate_boltzmann_probs(rel, kde, T).tolist(),
                "norm": "peak",
            })
        ylim = [0.0, 1.05]
    else:
        # default: continuous density, integral P dE = 1 over the plotted window
        egrid = np.linspace(e_lim[0], e_lim[1], 500)
        for T, color in zip(TEMPS, COLORS_PLASMA):
            Pgrid = _boltzmann_density(kde, E_ref, T, egrid)
            series.append({
                "T": T, "color": color, "egrid": egrid.tolist(),
                "probs": Pgrid.tolist(), "norm": "density",
            })
        top = max(max(s["probs"]) for s in series) * 1.05
        ylim = [0.0, top]
    return {
        "num_atoms": num_atoms,
        "series": series,
        "e_max": e_max,
        "norm": "peak" if peak_norm else "density",
        "xlim": list(e_lim),
        "ylim": ylim,
    }


def _plot_probability_from_data(data, outdir):
    """Draw the Stage-3 Boltzmann P(T) PNG from a data dict (live run or JSON)."""
    print("\n[STAGE 3] Boltzmann probability analysis")
    norm = data.get("norm", "peak")  # legacy JSONs (no 'norm') = peak scatter
    fig, ax = plt.subplots(figsize=(4, 3), dpi=120)
    for s in data["series"]:
        if norm == "density" and "egrid" in s:
            ax.plot(s["egrid"], s["probs"], color=s["color"], linewidth=1.5,
                    label=f"{s['T']} K")
        else:
            ax.scatter(s["rel"], s["probs"], color=s["color"], s=15, alpha=0.5,
                       edgecolors="none", label=f"{s['T']} K")
    ax.set_xlabel(E_LABEL)
    ax.set_ylabel("Probability Density P(E)\n(\u222b P dE = 1)"
                  if norm == "density" else "Probability P(E)")
    ax.legend(frameon=False, loc="upper right")
    ax.set_ylim(*data["ylim"])
    ax.set_xlim(*data["xlim"])
    plt.tight_layout()

    out_path = os.path.join(outdir, "binding_probability_vs_temperature.png")
    os.makedirs(outdir, exist_ok=True)
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> probability plot saved to {out_path}")
    return out_path


def step3_probability(structures, energies, outdir, e_max=None, json_dir=None,
                      dataset=None, kde_bw=None, peak_norm=False):
    """Stage 3: emit JSON (if json_dir), then draw the Boltzmann P(T) PNG."""
    data = _probability_data(structures, energies, e_max=e_max, kde_bw=kde_bw,
                             peak_norm=peak_norm)
    if json_dir:
        n_atoms, formula = _num_atoms_formula(structures)
        _write_stage_json(json_dir, 3, data,
                          description=_stage_description(3, dataset,
                                                         n_atoms, formula))
    return _plot_probability_from_data(data, outdir)
```

> **Why the block stays backward-compatible on replot:** a Stage-3 JSON written
> *before* this change has no `"norm"` key, so `_plot_probability_from_data`
> defaults `norm` to `"peak"` and draws the old scatter. Only newly emitted JSONs
> carry `"norm": "density"` and the `egrid` arrays.

---

### 3. Add the `--peak-norm` CLI flag

Still in `run_analysis_indices.py`, find the existing `--h` argument block:

```python
    parser.add_argument("--h", dest="kde_bw", type=float, default=None,
                        help="Gaussian-KDE bandwidth as a scalar multiplier on "
                             "Scott's rule for Stages 2 & 3: <1 = sharper/"
                             "narrower density & probability curves, >1 = broader/"
                             "smoother, 1 or omitted = Scott default "
                             "(gaussian_kde(bw_method=...)). Default: None.")
```

Immediately below it, add:

```python
    parser.add_argument("--peak-norm", action="store_true",
                        help="(Stage 3 only) use the legacy peak-normalized "
                             "Boltzmann likelihood (per-structure scatter, peak "
                             "= 1) instead of the default continuous probability "
                             "density normalized so integral P dE = 1 (smooth "
                             "curve). Default: off (integral=1 density).")
```

---

### 4. Forward `--h` and pass `--peak-norm` in `main()`

Find the Stage-3 call in `main()`:

```python
    step3_probability(structures, energies, args.outdir, e_max=args.e_max,
                      json_dir=json_dir, dataset=args.dataset)
```

Replace it with:

```python
    step3_probability(structures, energies, args.outdir, e_max=args.e_max,
                      json_dir=json_dir, dataset=args.dataset,
                      kde_bw=args.kde_bw, peak_norm=args.peak_norm)
```

This is the fix that makes `--h` actually reach Stage 3 (it now flows into
`gaussian_kde(rel, bw_method=kde_bw)` in `_probability_data`).

---

### 5. Bump the version and the module docstring (optional but recommended)

- `run_analysis_indices.py`, line ~56: change `__version__ = "2.11.0"` to
  `__version__ = "2.12.0"` (behavior/API change → minor bump).
- In the module docstring, update the Stage-3 line (~line 25):
  `Stage 3 — Boltzmann probability (per-atom KDE + Pi = rho*exp(-dE/kT)/Z), vs T.`
  → note that by default it is a continuous density with integral P dE = 1 and
  that `--peak-norm` reverts to the legacy peak = 1 likelihood.
- Update the `run_analysis_indices.py` row in `VERSIONS.md` (2.11.0 → 2.12.0) and
  append a `LOG.md` entry (see Step 7).

---

### 6. Smoke test (into a scratch outdir, so no tracked outputs are touched)

Run Stage-3 in the new default (density) mode on one 11_bTa leaf. Use a fresh
`--outdir` under `/tmp` — do **not** write into the leaf's tracked
`analysis_indices/`:

```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

# new default: integral P dE = 1 density (curve)
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
  --dataset 11_bTa/7_fxg_0b --outdir /tmp/instr9_density \
  --e-max 0.5 --h 0.05

# legacy reproduction: peak = 1 scatter
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
  --dataset 11_bTa/7_fxg_0b --outdir /tmp/instr9_peak \
  --e-max 0.5 --h 0.05 --peak-norm

# replot from the emitted JSON must reproduce the density figure
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
  --outdir /tmp/instr9_density_replot --from-json /tmp/instr9_density/analysis_json
```

**Verify (expected outputs):**

1. `/tmp/instr9_density/binding_probability_vs_temperature.png` shows **smooth
   curves** per temperature; the y-axis upper limit is **auto-scaled and can be
   > 1** (a narrow ∫ = 1 density peaks above 1) — this is the intended change.
2. `/tmp/instr9_density/analysis_json/stage3_probability.json` has top-level
   `"norm": "density"` and each series holds `egrid` + `probs` (500 points). Sanity
   check that each series integrates to 1:
   ```python
   import json, numpy as np
   d = json.load(open("/tmp/instr9_density/analysis_json/stage3_probability.json"))
   data = d["data"] if "data" in d else d          # depends on emitter layout
   for s in data["series"]:
       a = np.trapezoid(s["probs"], s["egrid"])
       print(f"{s['T']} K  area = {a:.6f}")          # expect ~1.0000 for each
   ```
   (If the emitter nests under a different key, inspect the JSON first with
   `python -c "import json;print(json.load(open('...')).keys())"` and adjust.)
3. `/tmp/instr9_peak/binding_probability_vs_temperature.png` reproduces the **old**
   scatter look: peaks touch 1, y-axis is `[0, 1.05]`, JSON has `"norm": "peak"`.
4. The `--from-json` replot re-draws the density figure identically (JSON-driven).
5. Confirm `--h 0.05` now actually sharpens the Stage-3 density (compare the same
   leaf with and without `--h`; without the old wiring this had no Stage-3 effect).

> **Committed-output caveat:** because the ∫ = 1 density is the *new default*,
> the meaning of every previously committed `binding_probability_vs_temperature.png`
> and `stage3_probability.json` (peak = 1) is now the *opt-in* legacy form. If you
> want those tracked outputs to reflect the new default, re-run each family without
> `--peak-norm` and commit the regenerated figures/JSONs. To keep a historical
> figure reproducible as-is, note which run used `--peak-norm`.

---

### 7. Version, log, commit

- Bump `VERSIONS.md` for `run_analysis_indices.py` (2.11.0 → 2.12.0).
- Append a `LOG.md` entry describing the change (old → new).
- Commit under the explicit `_run/0_lcb` pathspec:

```bash
cd /home/think/Desktop/research/_run/0_lcb
git add _run/0_lcb/2_analysist/run_analysis_indices.py \
        _run/0_lcb/VERSIONS.md _run/0_lcb/LOG.md
git commit -m "feat(0_lcb): Stage-3 continuous probability density (∫P dE=1) as default + --peak-norm opt-out; forward --h into Stage 3 (runner 2.12.0)"
```

Do **not** commit the `/tmp` smoke outputs (they are outside the repo and
regenerable). This INSTR #9 edit to `INSTRUCTION.md` is tracked separately below.

---

## INSTR #8 — Reproduce the 11_bTa analysis (leaves 7/8/9/11) with `--e-max 0.5` and `--h 0.05`, then plot the 3 graphs from JSON

**Date:** 2026-09-08

**Goal:** Re-run the analysis for the **11_bTa** leaves **7_fxg_0b, 8_fxg_1b,
9_fxg_3b, 11_p_Ta10b** with a shared energy window `--e-max 0.5` (eV/atom) and a
**sharper** Gaussian-KDE bandwidth `--h 0.05` (the INSTR #7 flag, live in the
runner at v2.11.0), producing each leaf's stage JSONs, then re-draw the **three
graphs** — `progression_seed_split_0.png` (energy progression), `conf_space.png`,
and `binding_probability_vs_temperature.png` — from those JSONs. This is a
**two-step** recipe: (1) run the analysis (writes JSON + PNGs together), (2) a
`--from-json` replot command that draws the 3 graphs purely from the saved JSONs
(no DB re-load). (`10_fxg_5b` is **not** in this set — you named 7/8/9/11.)

Uses the canonical runner `2_analysist/run_analysis_indices.py` (v2.11.0, has
`--h`/`kde_bw`), under the **agox_v2** env.

### Step 1 — run the analysis for the 4 leaves (writes JSON + PNGs)

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

for leaf in 11_bTa/7_fxg_0b 11_bTa/8_fxg_1b 11_bTa/9_fxg_3b 11_bTa/11_p_Ta10b; do
    echo "=== analysing $leaf ==="
    $PY run_analysis_indices.py --dataset "$leaf" \
        --outdir "$leaf/analysis_indices" \
        --json-dir "$leaf/analysis_indices" \
        --e-max 0.5 --h 0.05
done
```

What this does per leaf:
- loads all `seed_*/1_db/db_*.db` (iteration ≥ 10),
- draws `progression_seed_split_0.png` (energy progression), `conf_space.png`,
  `binding_probability_vs_temperature.png` **and** writes
  `stage1_progression.json`, `stage2_landscape.json`, `stage3_probability.json`
  (all under `<leaf>/analysis_indices/`),
- applies `--e-max 0.5` to every energy axis (comparable across leaves) and
  `--h 0.05` (sharp KDE) to the Stage-2 density + Stage-3 probability.

Each leaf pass ends `DONE. Outputs under ...` + `JSON data under .../analysis_indices`.
(The JSONs are written with the self-describing `description` block from v2.9.0.)

### Step 2 — re-draw the 3 graphs from the saved JSONs (no DB)

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

for leaf in 11_bTa/7_fxg_0b 11_bTa/8_fxg_1b 11_bTa/9_fxg_3b 11_bTa/11_p_Ta10b; do
    echo "=== replot $leaf from JSON ==="
    $PY run_analysis_indices.py \
        --from-json "$leaf/analysis_indices" \
        --outdir "$leaf/analysis_indices"
done
```

Each pass ends `Re-plotted all 3 graphs from JSON <leaf>/analysis_indices ...`.
This reproduces `progression_seed_split_0.png`, `conf_space.png`, and
`binding_probability_vs_temperature.png` for each leaf **purely from the stage
JSONs** (Stage 2 re-runs `plot_structure_landscape` with the stored inputs
including `kde_bw=0.05` in `params`, so the sharp bandwidth is preserved on
replot).

### Step 3 — verify

```bash
# each leaf should have all 3 PNGs + 3 stage JSONs
for leaf in 11_bTa/7_fxg_0b 11_bTa/8_fxg_1b 11_bTa/9_fxg_3b 11_bTa/11_p_Ta10b; do
    echo "$leaf : $(ls "$leaf/analysis_indices"/stage*_*.json 2>/dev/null | wc -l)/3 JSONs, "\
         "$(ls "$leaf/analysis_indices"/*.png 2>/dev/null | wc -l) PNGs (+ progression_plots/)"
done

# confirm the sharp bandwidth is recorded in each Stage-2 JSON
python3 -c "
import json,glob
for f in sorted(glob.glob('11_bTa/*/analysis_indices/stage2_landscape.json')):
    d=json.load(open(f))['data']
    print(f, 'params.kde_bw=', d['params'].get('kde_bw'), 'e_max=', d.get('e_limit',[None,None,None])[1])
"
```

Expected: `params.kde_bw = 0.05` and the energy axis cap `= 0.5` for every leaf.
Open one `conf_space.png` and one `binding_probability_vs_temperature.png` to
confirm the density/probability curves are visibly sharper than a default run.

### Step 4 — record + commit (under the explicit `_run/0_lcb` pathspec)

```bash
# append-only LOG.md. No VERSIONS bump needed — this only re-runs existing code.
cd /home/think/Desktop/research   # parent repo
git add _run/0_lcb/LOG.md
git diff --cached --stat          # confirm only LOG.md (docs)
git commit -m "docs(0_lcb): INSTR #8 reproduce 11_bTa 7/8/9/11 analysis (e-max 0.5, h 0.05) + plot from JSON"
```

> Do **not** stage regenerated PNGs/JSONs (`analysis_indices/*.png`,
> `stage*_*.json` are gitignored regenerable outputs). Do **not** run a blanket
> `git add -A`.

**Verification checklist:** Step 1 runs all 4 leaves with `--e-max 0.5 --h 0.05`
and writes 3 PNGs + 3 stage JSONs per leaf; Step 2 replots all 3 graphs from
JSON; Step 3 shows `kde_bw=0.05` and energy cap `0.5` in each Stage-2 JSON and
visibly sharper curves; `LOG.md` appended + committed under the `_run/0_lcb`
pathspec only.

---

## INSTR #7 — Add a `--h` Gaussian-KDE bandwidth flag (sharper / broader) to `conf_space.png` + `binding_probability` analysis

**Date:** 2026-09-08

**Goal:** `run_analysis_indices.py` (v2.10.0) draws the state-density curve on
`conf_space.png` (Stage 2) and the `binding_probability_vs_temperature.png`
(Stage 3) using `scipy.stats.gaussian_kde` with the **default (Scott) bandwidth**.
You want a CLI flag to control the KDE bandwidth so you can make the density /
probability curves **sharper** or **broader**. The flag is `--h <factor>`: a
**scalar multiplier on Scott's rule** (`gaussian_kde(..., bw_method=h)`), so
`h < 1` = sharper/narrower, `h > 1` = broader/smoother, and `h = 1` (or absent)
= the Scott default. It controls the KDE in **both** Stage 2 and Stage 3.

Two KDE call sites, so this spans two files:
- **Stage 3** — `run_analysis_indices.py:700` → `kde = gaussian_kde(rel)`. This
  KDE also feeds `calculate_boltzmann_probs` (via `kde_model`).
- **Stage 2** — the density KDE lives in the **dependency**
  `2_analysist/scripts/plot_structure_landscape.py:236` →
  `kde = gaussian_kde(data_array)`, reached from `run_analysis_indices.py:638`.

`__version__` is `2.10.0` at `run_analysis_indices.py:56` and `1.1.0` at
`plot_structure_landscape.py:3`. Per-run `scripts/` copies are snapshots — edit
only the canonical top-level files.

### Step 1 — add the parser flag (run_analysis_indices.py)

Find the `--novelty-dist` `parser.add_argument` block (around line 803) and
insert this argument just after it:

```python
    parser.add_argument("--h", dest="kde_bw", type=float, default=None,
                        help="Gaussian-KDE bandwidth as a scalar multiplier on "
                             "Scott's rule for Stages 2 & 3: <1 = sharper/"
                             "narrower density & probability curves, >1 = broader/"
                             "smoother, 1 or omitted = Scott default "
                             "(gaussian_kde(bw_method=...)). Default: None.")
```

### Step 2 — thread `h` into Stage 3 (run_analysis_indices.py)

(a) Add `kde_bw=None` to `_probability_data` and pass it to `gaussian_kde`
(currently `run_analysis_indices.py:695,700`):

```python
def _probability_data(structures, energies, e_max=None, kde_bw=None):
    ...
    kde = gaussian_kde(rel, bw_method=kde_bw)
```

(b) Add `kde_bw=None` to `step3_probability` and forward it:

```python
def step3_probability(structures, energies, outdir, e_max=None, json_dir=None,
                      dataset=None, kde_bw=None):
    ...
    data = _probability_data(structures, energies, e_max=e_max, kde_bw=kde_bw)
```

### Step 3 — thread `h` into Stage 2 (run_analysis_indices.py + dependency)

(a) In `run_analysis_indices.py`, add `kde_bw=None` to `_landscape_data`, store
it in the returned `params` dict (which `_plot_landscape_from_data` forwards to
`plot_structure_landscape`):

```python
def _landscape_data(structures, energies, e_max=None, normalize_density=False,
                    kde_bw=None):
    ...
    "params": {
        ...
        "plot_density_only": False,
        "kde_bw": kde_bw,
    },
```

(b) In `run_analysis_indices.py`, in `_plot_landscape_from_data`'s call to
`plot_structure_landscape` (line 638), add the forwarding argument:

```python
    result = plot_structure_landscape(
        X_eigen, rel, z_data=None,
        ...
        plot_z_vs_e=p["plot_z_vs_e"], return_data=True,
        kde_bw=p.get("kde_bw"),
    )
```

(c) In `run_analysis_indices.py`, add `kde_bw=None` to `step2_landscape` and
forward it into `_landscape_data`.

(d) In the **dependency** `2_analysist/scripts/plot_structure_landscape.py`:
add `kde_bw=None` to the `plot_structure_landscape` signature (near
`normalize_density=False`, line 57) and use it in the KDE call (line 236):

```python
def plot_structure_landscape(
    ...
    normalize_density=False,  # if True, scale density x-axis to [0, 1]
    kde_bw=None,              # Gaussian-KDE bandwidth (bw_method scalar); None = Scott default
    ...
):
    ...
            kde = gaussian_kde(data_array, bw_method=kde_bw)
```

### Step 4 — forward `args.kde_bw` in `main()` (run_analysis_indices.py)

At the Stage 2/3 calls (lines 895–899), add `kde_bw=args.kde_bw` to both:

```python
    step2_landscape(structures, energies, args.outdir,
                    e_max=args.e_max, normalize_density=args.normalize_density,
                    json_dir=json_dir, dataset=args.dataset, kde_bw=args.kde_bw)
    step3_probability(structures, energies, args.outdir, e_max=args.e_max,
                      json_dir=json_dir, dataset=args.dataset, kde_bw=args.kde_bw)
```

> The Stage-2 `kde_bw` also round-trips through the JSON: it is stored in
> `params`, so a `--from-json` replot re-applies the same bandwidth. Old JSONs
> without `kde_bw` in `params` fall back to `p.get("kde_bw")` → `None` → Scott.

### Step 5 — bump versions

- `run_analysis_indices.py:56` `"2.10.0"` → `"2.11.0"` (new feature → minor).
- `plot_structure_landscape.py:3` `"1.1.0"` → `"1.2.0"` (new optional param →
  minor; signature gains an argument).

Update both rows in `VERSIONS.md` and append a `LOG.md` entry.

### Step 6 — compile gates

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
$PY -m py_compile 2_analysist/run_analysis_indices.py
$PY -m py_compile 2_analysist/scripts/plot_structure_landscape.py
```

Expected: exit 0 each, no output. (AGOX/ASE imports flag as Pyright/LSP
unresolved under base python — judge by these `py_compile`s.)

### Step 7 — smoke test: sharper vs broader vs default on one leaf

```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
$PY run_analysis_indices.py --dataset 11_bTa/8_fxg_1b \
    --outdir /tmp/h_default --json-dir /tmp/h_default --e-max 0.5
$PY run_analysis_indices.py --dataset 11_bTa/8_fxg_1b \
    --outdir /tmp/h_sharp --json-dir /tmp/h_sharp --e-max 0.5 --h 0.5
$PY run_analysis_indices.py --dataset 11_bTa/8_fxg_1b \
    --outdir /tmp/h_broad --json-dir /tmp/h_broad --e-max 0.5 --h 2.0
```

Expected: all three write `conf_space.png` + `binding_probability_vs_temperature.png`.
Open them and confirm `--h 0.5` gives **narrower/sharp** density + probability
peaks, `--h 2.0` gives **broader/smoother** curves, and the no-flag run is the
unchanged Scott default. The default run must be visually identical to before
the change.

### Step 8 — verify via JSON (optional, numeric check)

```bash
python3 -c "
import json
for name in ['h_sharp','h_default','h_broad']:
    d=json.load(open(f'/tmp/{name}/stage2_landscape.json'))
    print(name, 'params.kde_bw=', d['data']['params'].get('kde_bw'),
          'density sum=', round(sum(d['data']['plot_arrays']['total_density']),3))
"
```

The `total_density` curve shape should differ across `--h` values (sharper
`--h 0.5` concentrates density into fewer bins; broader `--h 2.0` spreads it),
while `params.kde_bw` records the value used (None for the default run).

### Step 9 — record + commit (under the explicit `_run/0_lcb` pathspec)

```bash
# append-only VERSIONS.md (runner -> 2.11.0, plot_structure_landscape -> 1.2.0)
# + LOG.md. NOTE: run_analysis_indices.py also still carries the uncommitted
# INSTR #6 --novelty-dist work (v2.10.0) in the same working tree — committing
# now lands #6 + #7 together unless you commit #6 first.
cd /home/think/Desktop/research   # parent repo
git add _run/0_lcb/2_analysist/run_analysis_indices.py \
        _run/0_lcb/2_analysist/scripts/plot_structure_landscape.py \
        _run/0_lcb/VERSIONS.md _run/0_lcb/LOG.md
git diff --cached --stat          # confirm ONLY those intended files
git commit -m "feat(0_lcb): --h KDE bandwidth flag for conf_space + binding_probability stages (INSTR #7)"
```

> Do **not** stage regenerated PNGs/JSONs (`/tmp/h_*`, `nv_*`, analysis output —
> all gitignored). Do **not** run a blanket `git add -A`.

**Verification checklist:** compile gates pass (Step 6); `--h 0.5` visibly
sharper and `--h 2.0` visibly broader on both conf_space density and probability,
default run unchanged (Step 7); `params.kde_bw` stored in Stage-2 JSON and
re-applied on `--from-json` (Step 8); `VERSIONS.md` at runner 2.11.0 +
plot_structure_landscape 1.2.0, `LOG.md` appended; commit staged under the
`_run/0_lcb` pathspec only.

---

## INSTR #6 — Add a structural-novelty filter (raw Euclidean Fingerprint distance) to `conf_space.png` + `binding_probability` analysis

**Date:** 2026-09-08

**Goal:** The analysis runner `2_analysist/run_analysis_indices.py` (v2.9.0) draws
`conf_space.png` (Stage 2) and `binding_probability_vs_temperature.png` (Stage 3)
from **every** DFT-relaxed structure across all seeds. You want an optional
**novelty filter** so these two plots use only structurally *distinct* structures
(removing near-duplicate relaxations = variety without double counting), measured
by the **raw Euclidean distance of the AGOX Oganov/Fingerprint descriptor vectors**
— the same greedy measure as `_run/9_novelFilter/run_filter.py` + the
`NoveltyLCBAcquisitor`. A **CLI flag activates the filter and sets the distance
threshold**. Stage 1 (progression) is **not** filtered — it always uses the full
raw set. Filtering happens **after** all seeds are loaded, and only the
`structures`/`energies` arrays fed to Stages 2 & 3 are replaced by the novel
subset. Off by default (no behaviour change until you pass the flag).

The greedy rule (mirrors `novel_filter/filter.py:filter_novel`): process
structures **lowest energy first**; keep a structure iff its minimum Euclidean
distance in Fingerprint space to **every already-kept** structure is **strictly
greater** than the threshold. The lowest-energy member of each basin is kept.

**Where (canonical):** `2_analysist/run_analysis_indices.py`. `__version__` is on
**line 56**; `Fingerprint` is already imported (**line 70**, `from
agox.models.descriptors.fingerprint import Fingerprint`); the load call + Stage
2/3 calls are near the end of `main()` (**lines 835–849**); the `--start-iter`
parser arg is ~**line 768**. Per-run `scripts/` copies are snapshots — edit only
this canonical top-level file.

### Step 1 — add the parser flag

Find the `--start-iter` `parser.add_argument` block (line ~768) and insert this
argument just after it:

```python
    parser.add_argument("--novelty-dist", type=float, default=None,
                        help="activate a structural-novelty filter for Stages 2/3 "
                             "only: deduplicate structures by raw Euclidean "
                             "Fingerprint distance, keeping a structure iff its "
                             "min distance to all already-kept (lower-energy) "
                             "structures is strictly > this value (raw descriptor "
                             "units). Larger = fewer, more diverse structures. "
                             "Stage 1 progression always uses the full raw set. "
                             "Default: None (filter off).")
```

### Step 2 — add the self-contained filter helper

Insert this function right after `load_all_seeds_by_seed(...)` (it ends ~line
371, before the `# ---- Stage 1 ----` header). It needs `np` and `Fingerprint`,
both already imported:

```python
def _filter_novel_structures(structures, energies, threshold):
    """Return (kept_structs, kept_energies) of structurally distinct structures.

    Greedy, lowest-energy-first dedup by RAW Euclidean Fingerprint (Oganov)
    distance: keep a structure iff its min distance to every already-kept
    structure is strictly > threshold. Mirrors
    _run/9_novelFilter/novel_filter/filter.py:filter_novel and the
    NoveltyLCBAcquisitor novelty measure. Threshold is in raw descriptor units
    (NOT row-normalised); distinct minima are typically ~1-6 apart, near-duplicate
    relaxations much closer.
    """
    fp = Fingerprint.from_atoms(structures[0])
    feats = np.vstack([fp.create_features(s).ravel() for s in structures])
    order = np.argsort(energies, kind="stable")   # lowest energy first
    keep_idx, kept_feats = [], []
    for i in order:
        f = feats[i]
        if kept_feats:
            dmin = float(np.linalg.norm(np.vstack(kept_feats) - f, axis=1).min())
            if dmin <= threshold:
                continue
        else:
            dmin = float("inf")
        keep_idx.append(int(i)); kept_feats.append(f)
    keep_idx = np.asarray(keep_idx, dtype=int)
    print(f"[novelty] threshold={threshold:.4f}: kept {len(keep_idx)}/"
          f"{len(structures)} novel structures "
          f"(removed {len(structures) - len(keep_idx)} near-duplicates)")
    return ([structures[i] for i in keep_idx],
            np.asarray([energies[i] for i in keep_idx]))
```

### Step 3 — gate Stages 2/3 onto the filtered set (Stage 1 stays raw)

In `main()`, the code currently is (lines 835–849):

```python
    structures, energies = load_all_seeds(args.dataset, start_iter=args.start_iter)
    print(f"\nTotal: {len(structures)} structures, {len(structures[0])} atoms each "
          f"(iteration >= {args.start_iter})")

    os.makedirs(args.outdir, exist_ok=True)
    step1_progression(args.dataset, args.outdir, start_iter=args.start_iter,
                      e_max=args.e_max, json_dir=json_dir, seeds=seeds,
                      xlabel=args.xlabel, x_max=args.x_max,
                      show_bullets=not args.no_bullets,
                      show_gs_star=not args.no_gs_star)
    step2_landscape(structures, energies, args.outdir,
                    e_max=args.e_max, normalize_density=args.normalize_density,
                    json_dir=json_dir, dataset=args.dataset)
    step3_probability(structures, energies, args.outdir, e_max=args.e_max,
                      json_dir=json_dir, dataset=args.dataset)
```

Replace it with (note: filtering is applied **between** Stage 1 and Stages 2/3,
so `step1_progression` still gets the raw set via `args.dataset`, while
`step2_landscape`/`step3_probability` receive the novel subset):

```python
    structures, energies = load_all_seeds(args.dataset, start_iter=args.start_iter)
    print(f"\nTotal: {len(structures)} structures, {len(structures[0])} atoms each "
          f"(iteration >= {args.start_iter})")

    os.makedirs(args.outdir, exist_ok=True)
    # Stage 1 always uses the full raw set (per-seed best-so-far progression).
    step1_progression(args.dataset, args.outdir, start_iter=args.start_iter,
                      e_max=args.e_max, json_dir=json_dir, seeds=seeds,
                      xlabel=args.xlabel, x_max=args.x_max,
                      show_bullets=not args.no_bullets,
                      show_gs_star=not args.no_gs_star)

    # Optional novelty filter -> Stages 2 & 3 use only structurally distinct
    # structures (raw Euclidean Fingerprint distance > --novelty-dist).
    if args.novelty_dist is not None:
        structures, energies = _filter_novel_structures(structures, energies,
                                                        args.novelty_dist)
        print(f"[novelty] Stages 2/3 now analyse {len(structures)} novel "
              f"structures")

    step2_landscape(structures, energies, args.outdir,
                    e_max=args.e_max, normalize_density=args.normalize_density,
                    json_dir=json_dir, dataset=args.dataset)
    step3_probability(structures, energies, args.outdir, e_max=args.e_max,
                      json_dir=json_dir, dataset=args.dataset)
```

### Step 4 — bump the module version

At **line 56** change `__version__ = "2.9.0"` → `"2.10.0"` (new feature →
minor bump per `AGENTS.md` rule 8). Update the `run_analysis_indices.py` row in
`VERSIONS.md` and append a `LOG.md` entry.

### Step 5 — compile gate (run under `agox_v2`)

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
$PY -m py_compile 2_analysist/run_analysis_indices.py
```

Expected: exit 0, no output. (AGOX/ASE imports will show as Pyright/LSP
unresolved under base python — judge by this `py_compile`.)

### Step 6 — smoke test with the filter ON, on one leaf

```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
$PY run_analysis_indices.py --dataset 11_bTa/8_fxg_1b \
    --outdir /tmp/nv_smoke --json-dir /tmp/nv_smoke \
    --e-max 0.5 --novelty-dist 1.0
```

Expected stdout: the normal pipeline PLUS a line like
`[novelty] threshold=1.0000: kept <K>/<N> novel structures (removed <R>
near-duplicates)` and `[novelty] Stages 2/3 now analyse <K> novel structures`.
`conf_space.png` and `binding_probability_vs_temperature.png` are written under
`/tmp/nv_smoke` using only the `<K>` novel structures; `stage1_progression.json`
still reflects the full raw set.

### Step 7 — verify the filter actually changes the Stage 2/3 data

Compare a run with `--novelty-dist` against a run without it:

```bash
$PY run_analysis_indices.py --dataset 11_bTa/8_fxg_1b \
    --outdir /tmp/nv_off --json-dir /tmp/nv_off --e-max 0.5            # no filter
$PY run_analysis_indices.py --dataset 11_bTa/8_fxg_1b \
    --outdir /tmp/nv_on --json-dir /tmp/nv_on --e-max 0.5 --novelty-dist 1.0
# stage2 X_eigen length should shrink from N to K; stage3 series[].rel likewise
python3 -c "import json;print('no-filter X_eigen:',len(json.load(open('/tmp/nv_off/stage2_landscape.json'))['data']['X_eigen']));print('filtered X_eigen:',len(json.load(open('/tmp/nv_on/stage2_landscape.json'))['data']['X_eigen']))"
```

Expected: filtered `X_eigen` length = K < N (the number kept). Stage 1
`stage1_progression.json` is unchanged between the two runs.

### Step 8 — calibrate the threshold (recommended, not guesswork)

The filter prints how many it keeps. Threshold is in **raw** Fingerprint units:
for Fe/MgO, distinct minima are ~1–6 apart and near-duplicates much closer, so
~1.0 is a reasonable start. Sweep to find a sensible value for your system:

```bash
for t in 0.5 1.0 1.5 2.0; do
  echo "=== --novelty-dist $t ==="
  $PY run_analysis_indices.py --dataset 11_bTa/8_fxg_1b \
      --outdir /tmp/nv_t$t --json-dir /tmp/nv_t$t --e-max 0.5 --novelty-dist $t \
      | grep -E '\[novelty\]|Total:'
done
```

Pick the largest threshold that still keeps enough distinct structures for a
meaningful KDE (Stage 2/3). Re-run your production leaves with that `--novelty-dist`.

### Step 9 — record + commit (under the explicit `_run/0_lcb` pathspec)

```bash
# append-only VERSIONS.md (run_analysis_indices.py -> 2.10.0) + LOG.md
cd /home/think/Desktop/research   # parent repo
git add _run/0_lcb/2_analysist/run_analysis_indices.py \
        _run/0_lcb/VERSIONS.md _run/0_lcb/LOG.md
git diff --cached --stat          # confirm ONLY those intended files
git commit -m "feat(0_lcb): --novelty-dist novelty filter for conf_space + binding_probability stages (INSTR #6)"
```

> Do **not** stage regenerated PNGs/JSONs (gitignored). Do **not** run a blanket
> `git add -A`.

**Verification checklist:** compile gate passes (Step 5); a `--novelty-dist` run
prints the kept/removed line and writes Stage 2/3 PNGs (Step 6); filtered
`X_eigen`/`series[].rel` are shorter than the no-filter run while Stage 1 is
unchanged (Step 7); threshold chosen from the sweep, not guessed (Step 8);
`VERSIONS.md` at 2.10.0 + `LOG.md` appended; commit staged under the `_run/0_lcb`
pathspec only. With no `--novelty-dist` flag, behaviour is byte-identical to
before (filter fully off by default).

---

## INSTR #5 — `xrd_groundstate_compare.py`: add a `--figsize` flag + tab10 solid recolor of the concentration XRD overlay

**Date:** 2026-09-08

**Goal:** The **concentration-based** XRD figure (one ground-state XRD curve per
dopant concentration, saved as `xrd_averaged_by_window.png`) is drawn by
`xrd_groundstate_compare.py` — a dedicated script that already reads from its
`xrd_plots.json` (`family` + `leaves`, each with `concentration_pct`, `grid`,
`intensity`). It is currently **viridis**-coloured with a **hard-coded**
`figsize=(8, 4.5)`. You want (a) a **`--figsize`** CLI flag to control figure
size (e.g. `4,4`, `6,4`, `10,5`) and (b) the figure recoloured to the **tab10
solid, color-only** scheme (no viridis, no dash/dot line styles, thicker
`lw=1.8`) consistent with the colour decision made for the by-window script in
INSTR #4. This script IS the concentration plotter — no new "concentration
mode" flag is needed; the additions are the `--figsize` flag and the recolor.

**Where (canonical):** `2_analysist/scripts/xrd_groundstate_compare.py`
(v2.1.0). Per-run `scripts/` copies are snapshots — do NOT edit them. Function
`plot_from_data(data, outdir)` starts at **line 116**; the Figure-1 (overlay)
body is **lines 127–142**; `__version__` is on **line 27**.

### Step 1 — add the `--figsize` parser argument

In `main()`, in the `parser.add_argument` block, insert right after the
`--from-json` argument (currently lines ~170–172):

```python
    parser.add_argument("--figsize", default="8,4.5",
                        help="overlay figure size 'W,H' in inches (default 8,4.5)")
```

Then, immediately after `args = parser.parse_args()` (line ~210), add one line
to convert the string to a float tuple:

```python
    args.figsize = tuple(float(x) for x in args.figsize.split(","))
```

### Step 2 — pass `figsize` through `plot_from_data`

Change the signature on **line 116**:

```python
def plot_from_data(data, outdir, figsize=(8, 4.5)):
```

and update BOTH call sites to forward it — the `--from-json` call (near line
178) and the live-run call (near line 224). Both currently read
`plot_from_data(data, args.outdir)`; change each to:

```python
    plot_from_data(data, args.outdir, figsize=args.figsize)
```

### Step 3 — recolor Figure 1 (the concentration XRD overlay) to tab10 solid

In `plot_from_data`, replace the Figure-1 body — currently lines **128–137**
(the `cmap = plt.get_cmap("viridis")` ramp and the loop that plots each leaf
with a viridis-normalised colour at `lw=1.1`) — with:

```python
    cmap = plt.get_cmap("tab10")
    ordered = sorted((l for l in leaves if l["grid"]),
                     key=lambda l: _conc_key(l))
    for i, l in enumerate(ordered):
        ax.plot(l["grid"], l["intensity"], lw=1.8,
                color=cmap(i % cmap.N), label=_formula_label(l, inter))
```

Also on the line just above that block, replace the hard-coded figure size —
`fig, ax = plt.subplots(figsize=(8, 4.5))` (line ~127) — with:

```python
    w, h = figsize
    fig, ax = plt.subplots(figsize=(w, h))
```

Effect: each concentration's ground-state curve is a **solid, distinct tab10
colour** (blue, orange, green, red, … in increasing dopant %, never yellow) at
`lw=1.8`; no line-style cycling; the overlay size follows `--figsize`.
(Figure 2, the CI-vs-concentration panel, keeps its own 6×4 size — leave it.)

### Step 4 — bump the module version

At **line 27** change `__version__ = "2.1.0"` → `"2.1.1"` (feature+cosmetic,
patch bump).

### Step 5 — compile gate (run under `pymat_xrd`)

```bash
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
$PY_X -m py_compile 2_analysist/scripts/xrd_groundstate_compare.py
```

Expected: exit 0, no output.

### Step 6 — reproduce ONE concentration graph from its JSON (example: 11_bTa)

```bash
$PY_X 2_analysist/scripts/xrd_groundstate_compare.py \
    --from-json 2_analysist/11_bTa/xrd_gs_compare \
    --outdir /tmp/xrd_conc_example --figsize 6,4
xdg-open /tmp/xrd_conc_example/xrd_averaged_by_window.png
```

**Check:** 4 curves (Ta₅₄B₀ → Ta₅₄B₅) are distinct solid tab10 colours, none
yellow, ~1.8 thick; no dashed/dotted lines; image is 6×4 in; legend shows the
subscript formula + concentration (e.g. `Ta₅₄B₁ (1.8% B)`); x = 2θ (10–90°).

### Step 7 — one command to (re)produce the concentration XRD graph for EVERY system

All 5 existing `xrd_gs_compare` dirs already hold an `xrd_plots.json`, so this
loop replots each family from its own JSON into place (no DB / no CIF / no
re-simulation), with a chosen figure size:

```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
for gs in 11_bTa/xrd_gs_compare 16_bW/xrd_gs_compare \
          17_PPt/0_plus5cell/xrd_gs_compare \
          17_PPt/1_plus0cell/xrd_gs_compare \
          17_PPt/2_plus3cell/xrd_gs_compare; do
    [ -f "$gs/xrd_plots.json" ] || continue
    echo "=== replot $gs ==="
    $PY_X scripts/xrd_groundstate_compare.py --from-json "$gs" \
        --outdir "$gs" --figsize 6,4
done
```

Each pass ends `DONE. Re-plotted ground-state PNGs from …`. The 5 families are:
Ta–B (`11_bTa`), W–B (`16_bW`), and the three Pt–P supercell families under
`17_PPt` (`0_plus5cell`, `1_plus0cell`, `2_plus3cell`). The PNGs are gitignored,
so this is cosmetic.

### Step 8 — record + commit (under the explicit `_run/0_lcb` pathspec)

```bash
# append-only LOG.md + VERSIONS.md updates (bump the row for
# 2_analysist/scripts/xrd_groundstate_compare.py: 2.1.0 -> 2.1.1)
cd /home/think/Desktop/research   # parent repo
git add _run/0_lcb/2_analysist/scripts/xrd_groundstate_compare.py \
        _run/0_lcb/INSTRUCTION.md _run/0_lcb/LOG.md _run/0_lcb/VERSIONS.md
git diff --cached --stat          # confirm ONLY the intended 4 files
git commit -m "feat(0_lcb/xrd): --figsize flag + tab10 solid recolor of concentration XRD overlay in xrd_groundstate_compare.py (INSTR #5)"
```

> Do **not** stage the regenerated PNGs (gitignored). Do **not** run a blanket
> `git add -A`. Note: this script was CLEAN in git before Step 1 (unlike
> `xrd_simulate_crystallinity.py`, which still carries your uncommitted INSTR #3
> recolor) — this commit touches `xrd_groundstate_compare.py` only.

**Verification checklist:** compile gate passes (Step 5); single example replot
(Step 6) shows 4 solid tab10, non-yellow, ~1.8-thick curves at the given
`--figsize`; all-5 loop (Step 7) prints a `DONE` per family; `VERSIONS.md` row at
2.1.1 and `LOG.md` appended; commit staged under the `_run/0_lcb` pathspec only.

---

## INSTR #4 — XRD figure: color-only recolor (drop the dash/dot line styles)

**Date:** 2026-09-08

**Goal:** You applied INSTR #3 (working tree, uncommitted — `xrd_simulate_crystallinity.py`
is at `__version__ 1.4.1`, tab10 colours + an `ls_cycle` of solid/dash/dot line
styles). You **don't want the dash/dot line styles** — you want each energy
window distinguished **by colour only**. This refines INSTR #3: keep the tab10
colours (distinct, never yellow) and the thicker `lw=1.8`, but drop the
`ls_cycle` entirely so every curve is a **solid** line. Windows are few
(≤ ~6), so colour alone cleanly separates them. Recolour already applied — the
only remaining edit is removing the line-style machinery.

**Where (canonical):** `2_analysist/scripts/xrd_simulate_crystallinity.py`,
function `plot_patterns_from_data(data, outdir)`, active block **lines 129–137**.
Per-run `scripts/` copies are snapshots — do NOT edit them. `__version__` is on
**line 35** (currently `"1.4.1"`).

### Step 1 — locate the active plotting block

In the canonical script, the block currently reads (lines 129–137):

```python
    tab10 = plt.get_cmap("tab10")
    ls_cycle = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 2))]
    ordered = sorted((w for w in data["windows"] if w["grid"]),
                     key=lambda w: w["center"])
    for i, w in enumerate(ordered):
        ax.plot(w["grid"], w["intensity"], lw=1.8,
                color=tab10(i % tab10.N),
                linestyle=ls_cycle[i % len(ls_cycle)],
                label=w["label"])
```

### Step 2 — replace that block with the color-only version

Select and replace **exactly** the 9 lines in Step 1 (from `tab10 =` through the
`label=w["label"])`) with:

```python
    tab10 = plt.get_cmap("tab10")
    ordered = sorted((w for w in data["windows"] if w["grid"]),
                     key=lambda w: w["center"])
    for i, w in enumerate(ordered):
        ax.plot(w["grid"], w["intensity"], lw=1.8,
                color=tab10(i % tab10.N),
                label=w["label"])
```

What it does: deletes the `ls_cycle` list and the `linestyle=...` argument, so
every window plots as a **solid** tab10 colour (blue, orange, green, red, … in
energy order) at `lw=1.8` — colour-only distinction, no dash or dot.

### Step 3 — (clean-up, recommended) remove the commented-out legacy block

Directly below the loop, INSTR #3 left the old viridis code commented out
(lines ~138–147, beginning `# cmap = plt.get_cmap("tab10")`). Delete those
commented lines and the stray blank line, so the function reads cleanly from the
loop straight to `ax.set_xlabel(...)`. This is cosmetic; if you prefer to leave
it, skip — it has no effect on the figure.

### Step 4 — bump the module version

At line 35 change `__version__ = "1.4.1"` → `"1.4.2"` (figure edit, patch bump).

### Step 5 — compile gate (run under `pymat_xrd`)

```bash
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
$PY_X -m py_compile 2_analysist/scripts/xrd_simulate_crystallinity.py
```

Expected: exit 0, no output. (The working tree is already uncommitted-modified,
so compile checks the current file, not HEAD.)

### Step 6 — regenerate ONE test figure from a saved JSON

```bash
$PY_X 2_analysist/scripts/xrd_simulate_crystallinity.py \
    --from-json 2_analysist/11_bTa/8_fxg_1b/xrd_out \
    --outdir /tmp/xrd_instr4
xdg-open /tmp/xrd_instr4/xrd_averaged_by_window.png
```

**Check:** curves are distinct tab10 **colours** with **no** dashed/dotted
lines — every line solid and ~1.8 thick; highest-energy window is not yellow;
legend intact and energy-labelled; 2θ axis ~10–90°.

### Step 7 — record + commit (under the explicit `_run/0_lcb` pathspec)

This step also commits the not-yet-committed INSTR #3 recolor already in the
working tree (script `1.4.0 → 1.4.1 → 1.4.2` lands in one commit).

```bash
# append-only LOG.md + VERSIONS.md updates (bump the row for
# 2_analysist/scripts/xrd_simulate_crystallinity.py to 1.4.2)
cd /home/think/Desktop/research   # parent repo
git add _run/0_lcb/2_analysist/scripts/xrd_simulate_crystallinity.py \
        _run/0_lcb/INSTRUCTION.md _run/0_lcb/LOG.md _run/0_lcb/VERSIONS.md
git diff --cached --stat          # confirm ONLY the intended 4 files
git commit -m "fix(0_lcb/xrd): XRD figure color-only recolor (tab10+lw1.8, drop dash/dot line styles) (INSTR #3+#4)"
```

> Do **not** stage the regenerated PNGs (gitignored). Do **not** run a blanket
> `git add -A`.

**Verification checklist:** compile gate passes (Step 5); test PNG shows solid,
colour-distinct, non-yellow curves (Step 6); `VERSIONS.md` row at 1.4.2 and
`LOG.md` appended; commit staged under the `_run/0_lcb` pathspec only.

---

## INSTR #3 — Recolor `xrd_averaged_by_window.png` for presentation legibility (tab10 + thicker lines + distinct line styles)

**Date:** 2026-09-08

**Goal:** The figure colours each energy-window's averaged XRD curve with the
`viridis` colormap (`xrd_simulate_crystallinity.py:128`), so the highest-energy
window renders **yellow** — hard to see on a white projector/slide, especially
for an older audience. Recolour it to high-contrast **tab10** categorical
colours in energy order, raise the line width to **1.8**, and give each window a
**distinct line style** as a second channel (colour-blind/legibility safety).
This one edit updates every leaf's figure because all `xrd_averaged_by_window.png`
are drawn by the same shared function — no per-leaf work needed.

**Where (canonical):** `2_analysist/scripts/xrd_simulate_crystallinity.py`,
function `plot_patterns_from_data(data, outdir)` — currently lines **124–140**,
plotting body **128–135**. This is the canonical Stage-2 XRD script under
`pymat_xrd`. Per-run `scripts/` copies under each leaf are **snapshots — do NOT
edit them**; edit the top-level canonical copy only (see `AGENTS.md §3a`). The
module `__version__` is on **line 35**.

### Step 1 — open the canonical script and locate the block

```bash
cd /home/think/Desktop/research/_run/0_lcb
# open 2_analysist/scripts/xrd_simulate_crystallinity.py
# go to: def plot_patterns_from_data(data, outdir):  (~line 124)
```

The plotting body you will replace currently reads (lines 128–135):

```python
    cmap = plt.get_cmap("viridis")
    centers = [w["center"] for w in data["windows"] if w["grid"]]
    vmin, vmax = min(centers), max(centers)
    for w in data["windows"]:
        if not w["grid"]:
            continue
        color = cmap((w["center"] - vmin) / (vmax - vmin + 1e-9)) if vmax > vmin else "C0"
        ax.plot(w["grid"], w["intensity"], lw=1.1, color=color, label=w["label"])
```

### Step 2 — replace those lines with the presentation-ready version

Select and replace **exactly** the 8 lines in Step 1 with:

```python
    tab10 = plt.get_cmap("tab10")
    ls_cycle = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 2))]
    ordered = sorted((w for w in data["windows"] if w["grid"]),
                     key=lambda w: w["center"])
    for i, w in enumerate(ordered):
        ax.plot(w["grid"], w["intensity"], lw=1.8,
                color=tab10(i % tab10.N),
                linestyle=ls_cycle[i % len(ls_cycle)],
                label=w["label"])
```

What it does: drops `viridis`/the `center`-normalized colour ramp; instead sorts
windows by energy `center` (low → high) and assigns the high-contrast `tab10`
colours in order (blue, orange, green, red, … — never yellow), raises `lw` to
**1.8**, and cycles solid/dashed/dash-dot/dotted line styles so curves stay
distinguishable even where colours are close or vision is impaired. `ordered`
also drops empty windows (same guard the old `if not w["grid"]: continue` gave).

### Step 3 — bump the module version

At line 35 change `__version__ = "1.4.0"` → `"1.4.1"` (cosmetic figure edit,
patch bump per `AGENTS.md` rule 8).

### Step 4 — compile gate (run under `pymat_xrd`)

```bash
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
$PY_X -m py_compile 2_analysist/scripts/xrd_simulate_crystallinity.py
```

Expected: exit 0, no output (success). Ignore any LSP/Pyright colouring under
base `python3` — judge by this compile.

### Step 5 — regenerate ONE test figure from a saved JSON (no DB/CIF needed)

Pick any leaf with an existing `xrd_plots.json` (e.g. `11_bTa/8_fxg_1b/xrd_out`):

```bash
$PY_X 2_analysist/scripts/xrd_simulate_crystallinity.py \
    --from-json 2_analysist/11_bTa/8_fxg_1b/xrd_out \
    --outdir /tmp/xrd_instr3
```

Expected stdout ends `DONE. Re-plotted XRD PNGs from ... -> /tmp/xrd_instr3`.
Then open the figure to verify:

```bash
xdg-open /tmp/xrd_instr3/xrd_averaged_by_window.png
```

**Check:** the highest-energy curve is no longer yellow; curves are thicker
(~1.8); each window has a distinct colour **and** line style; 2θ axis still
~10–90°; the legend is intact and still energy-labelled.

### Step 6 — (optional) regenerate every other figure from its JSON

Same `--from-json <leaf_dir> --outdir <leaf_dir>` command per leaf that holds an
`xrd_plots.json` (39 exist; `xrd_gs_compare/` dirs too). Output PNGs are
regenerable/gitignored, so this is cosmetic — no need to re-run if you only want
the test figure recoloured.

### Step 7 — record + commit (under the explicit `_run/0_lcb` pathspec)

```bash
# append-only LOG.md + VERSIONS.md updates (bump the row for
# 2_analysist/scripts/xrd_simulate_crystallinity.py: 1.4.0 -> 1.4.1)
cd /home/think/Desktop/research   # parent repo
git add _run/0_lcb/2_analysist/scripts/xrd_simulate_crystallinity.py \
        _run/0_lcb/INSTRUCTION.md _run/0_lcb/LOG.md _run/0_lcb/VERSIONS.md
git diff --cached --stat          # confirm ONLY the intended 4 files
git commit -m "fix(0_lcb/xrd): tab10+lw1.8+line-styles recolor of xrd_averaged_by_window.png (INSTR #3)"
```

> Do **not** stage the regenerated PNGs (they are gitignored outputs). Do **not**
> run a blanket `git add -A`.

**Verification checklist:** compile gate passes (Step 4); test PNG regenerated
and eyeballed (Step 5) showing non-yellow, thicker, distinctly-styled curves;
`VERSIONS.md` row bumped and `LOG.md` appended; commit staged under the explicit
`_run/0_lcb` pathspec only.

---

## INSTR #2 — Stand up Fe/MgO LCB runs with more MgO layers (`1_runs/2_femgo_3mgo`, `3_femgo_5mgo`, `4_femgo_10mgo`)

**Date:** 2026-09-06 · **Goal:** create three self-contained run dirs under
`1_runs/` that replicate the `0_lcb_femgo` system (Fe(001) overlayer on
MgO(001), **no B**, LCB/GPR AGOX search, **no dipole correction**) but with a
**thicker MgO substrate**: `mgo_layer_number = 3, 5, 10`, and a **vacuum grown
to keep the same clearance as the single-layer run**. Each dir gets a corrected
`main.py`, a job script, and a **stacking smoke test** that verifies the produced
MgO/Fe stacking on the generator structure. The heavy 100-iteration HPC run is
out of scope here.

**Source of truth:** copy from `2_analysist/0_lcb_femgo/` (its `main.py` +
`scripts/`). Env for all compile/run steps = **`agox_v2`**:
`/home/think/miniconda3/envs/agox_v2/bin/python`. Geometry (measured by importing
the real `build_*` scripts): each MgO monolayer in this builder is one **coplanar
Mg+O plane**, inter-plane spacing **2.106 Å** (`dist_mgo`, = `a_mgo/2`); after
the 5×5 repeat each plane holds 25 Mg + 25 O. `build_mgo_stack` auto-grows the
substrate cell with each added layer, so raising `vacuum` keeps the Fe-on-top
clearance constant.

---

### Step 1 — Create the three run dirs and copy the source files

```bash
cd /home/think/Desktop/research/_run/0_lcb
for d in 2_femgo_3mgo 3_femgo_5mgo 4_femgo_10mgo; do
  mkdir -p 1_runs/$d
  cp -r 2_analysist/0_lcb_femgo/scripts 1_runs/$d/scripts
  cp 2_analysist/0_lcb_femgo/main.py 1_runs/$d/main.py
  cp 2_analysist/0_lcb_femgo/job_5x5_9.sh 1_runs/$d/j_5x5.sh
done
ls 1_runs/2_femgo_3mgo 1_runs/3_femgo_5mgo 1_runs/4_femgo_10mgo
```

Expected: each dir holds `main.py`, `j_5x5.sh`, `scripts/` (with
`build_fe_stack.py`, `build_mgo_stack.py`, `build_heteroStruct.py`,
`hetero_struct_randomize.py`, `plot_structure.py`, …). **Do not** copy
`seed_*/`, `stop_16/`, `trash/`, or any run output — these dirs start empty of data.

### Step 2 — Edit each `main.py`: layer count + vacuum

In **all three** files the two edits are the two parameter assignments near the
top of `main.py` (in the copied `0_lcb_femgo` source these are the
`# ==== Slab Number of Layer` / `vacuum` block around lines 39–52). Set:

```python
# 2_femgo_3mgo:
mgo_layer_number = 3
vacuum = 24.2
```

```python
# 3_femgo_5mgo:
mgo_layer_number = 5
vacuum = 28.4
```

```python
# 4_femgo_10mgo:
mgo_layer_number = 10
vacuum = 39.0
```

**Why these `vacuum` values:** the single-layer `0_lcb_femgo` used `vacuum = 20`
and each extra MgO monolayer adds ~2.106 Å to the stack. To hold the Fe-on-top
clearance (~the same as the N=1 run) use `vacuum = 20 + 2.106*(N-1)` → N=3:
`24.2`; N=5: `28.4`; N=10: `39.0`. Measured result of the real builder with
these values (verified by importing `build_*`): O and Mg land **coplanar** in N
distinct planes spaced **2.106 Å**, Fe sits **0.50 Å** above the top MgO plane,
and the substrate cell leaves **27–42 Å** of vacuum above the Fe — plenty.

Do **not** change any other physical parameter (`a_mgo=4.212`, `a_fe=2.870190`,
`supercell=(5,5,1)`, `kpts=(1,1,1)`, `kappa=2`, `N_iterations=100`,
LCAO/dzp/PBE, spinpol, `ncores=24`). Keep `main.py` **dipole-free** (no
`poissonsolver` line) — these runs replicate plain `0_lcb_femgo`.

### Step 3 — Point each job script at its `main.py`

Each `j_5x5.sh` is a straight copy of `job_5x5_9.sh` (PJM headers, `gpaw_env`,
`python ./main.py`). Confirm it runs `main.py` from the dir's own cwd (it does —
the command is relative). Leave seed/iteration scope as-is unless you want a
narrower first run. Keep it a bare `#PJM` script; **never** add `pjsub -x`.

### Step 4 — Smoke test: compile gate

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb
for d in 2_femgo_3mgo 3_femgo_5mgo 4_femgo_10mgo; do
  $PY -m py_compile 1_runs/$d/main.py && echo "$d COMPILE OK"
done
```

Expected: three `COMPILE OK` lines. (LSP under base `python3` flags AGOX/ASE
imports — ignore it; judge by `agox_v2`'s `py_compile`.)

### Step 5 — Smoke test: stacking check on the produced generator structure

This verifies the **actual MgO/Fe stacking** the run would produce, per layer
count, by importing the real `build_*` scripts and building the heterostructure
the way `main.py` does (MgO substrate + Fe deposition, 5×5 repeat). It asserts:
(1) exactly N coplanar MgO planes, each with 25 Mg + 25 O; (2) inter-plane
spacing ≈ 2.106 Å; (3) Mg and O are coplanar per plane (rocksalt (001) registry —
no O/Mg on different heights within a plane); (4) Fe is a single plane **0.50 Å**
above the top MgO plane; (5) cell clearance above Fe ≥ 10 Å. Run it **inside each
run dir** (it imports that dir's own `scripts/`), passing N as an argument.

Create `1_runs/2_femgo_3mgo/smoke_stack.py` (then copy to the other two dirs and
edit `N` + `VAC` to 5/28.4 and 10/39.0):

```python
"""Stacking smoke: verify the Fe/MgO structure main.py would build has good MgO
stacking + correct Fe placement for the requested layer count.
Usage:  $PY smoke_stack.py    (edit N and VAC below per run dir)"""
import sys
import numpy as np
from ase.build import surface
sys.path.insert(0, 'scripts')
from build_mgo_stack import build_mgo_stack
from build_heteroStruct import build_heteroStruct
from build_fe_stack import build_fe_stack

N   = 3                     # EDIT per dir: 3 | 5 | 10
VAC = 24.2                  # EDIT per dir: 24.2 | 28.4 | 39.0
a_mgo, a_fe = 4.212, 2.870190
dist_z_fe2o, SC = 0.5, (5, 5, 1)

slab_fe_base = surface('Fe', (0, 0, 1), layers=1, vacuum=VAC)
sm = build_mgo_stack(slab_fe_base, num_layers=N, vacuum=VAC)
mgo = sm[[a.symbol != 'Fe' for a in sm]].repeat(SC)          # MgO substrate
fe  = build_fe_stack(slab_fe_base, num_layers=1, vacuum=VAC).repeat(SC)
het = build_heteroStruct(mgo.copy(), fe.copy(), dist_inter=dist_z_fe2o, vacuum=VAC)

ok = True
def chk(msg, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and cond

o   = het[[a.symbol == 'O'  for a in het]]
mg  = het[[a.symbol == 'Mg' for a in het]]
fea = het[[a.symbol == 'Fe' for a in het]]
oz  = np.sort(np.unique(np.round(o.positions[:, 2], 3)))
mz  = np.sort(np.unique(np.round(mg.positions[:, 2], 3)))
fz  = np.sort(np.unique(np.round(fea.positions[:, 2], 3)))
cz  = mgo.cell[2, 2]; zmax = het.positions[:, 2].max()

chk(f'{N} MgO layers (O planes={len(oz)})', len(oz) == N)
chk(f'{N} MgO layers (Mg planes={len(mz)})', len(mz) == N)
chk('O and Mg coplanar per plane', np.allclose(oz, mz, atol=0.01))
chk('plane spacing ~ 2.106 A', np.allclose(np.diff(oz), 2.106, atol=0.01))
chk('25 Mg + 25 O per plane (5x5)', len(o) == 25*N and len(mg) == 25*N)
chk('single Fe plane (25)', len(fea) == 25 and len(fz) == 1)
chk(f'Fe sits 0.50 A above top MgO (gap {fz.min()-oz.max():.2f})',
    np.isclose(fz.min() - oz.max(), dist_z_fe2o, atol=0.02))
chk(f'cell clearance above Fe >= 10 A (={cz-zmax:.1f})', cz - zmax >= 10.0)
chk('no atom below cell bottom / above cell top', zmax < cz - 1.0)

print('--- per-MgO-plane z (O and Mg coincide):', oz)
print('STACKING SMOKE ' + ('PASS' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
```

Run it in each dir (each time with the matching `N`/`VAC`):

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/1_runs/2_femgo_3mgo
$PY smoke_stack.py
# repeat in 3_femgo_5mgo (N=5, VAC=28.4) and 4_femgo_10mgo (N=10, VAC=39.0)
```

**Expected output (N=3):**
```
PASS 3 MgO layers (O planes=3)
PASS 3 MgO layers (Mg planes=3)
PASS O and Mg coplanar per plane
PASS plane spacing ~ 2.106 A
PASS 25 Mg + 25 O per plane (5x5)
PASS single Fe plane (25)
PASS Fe sits 0.50 A above top MgO (gap 0.50)
PASS cell clearance above Fe >= 10 A (=27.4)
PASS no atom below cell bottom / above cell top
--- per-MgO-plane z (O and Mg coincide): [24.2  26.306 28.412]
STACKING SMOKE PASS
```
(Verified with the real `build_*` scripts. N=5/VAC=28.4: planes
`[28.4 30.506 32.612 34.718 36.824]`, clearance 31.6. N=10/VAC=39.0: 10 planes
`[39. 41.106 43.212 ... 57.954]`, clearance 42.2.)

**Failures to watch for:**
- A **FAIL on layer count / spacing** → `mgo_layer_number` or `vacuum` edit didn't
  land, or the wrong `N`/`VAC` was set in the smoke for that dir.
- **FAIL "Fe sits 0.50 A above top MgO"** → the substrate/deposition gap changed
  (`dist_z_fe2o`); it should be 0.5. Revert it.
- **FAIL "cell clearance < 10 A"** → `vacuum` too small; use the `20+2.106*(N-1)`
  rule. Clearance is not a stacking fault per se, but a cramped cell lets the slab
  interact with its periodic image.

### Step 6 — Verify & clean up

- Confirm each `main.py` has the right `mgo_layer_number`/`vacuum`:
  `grep -nE 'mgo_layer_number|^vacuum' 1_runs/2_femgo_3mgo/main.py 1_runs/3_femgo_5mgo/main.py 1_runs/4_femgo_10mgo/main.py`.
- Confirm **no** `poissonsolver`/`dipolelayer` line in any of the three (these are
  plain runs): `grep -L dipolelayer 1_runs/*/main.py`.
- Delete throwaway smoke logs if any; keep real run data out of git (`seed_*/`,
  `*.db`, `*.out`, `gpaw_logs/` are ignored project-wide). Keep `smoke_stack.py`
  if you want to re-verify.
- Tracked additions for a commit: `main.py`, `j_5x5.sh`, `scripts/*.py` per dir.

**Pitfalls:** (1) three dirs, three distinct `N`/`vacuum` — don't mix them up; the
smoke must be run with the value matching the dir; (2) `vacuum` grows only the
clearance — it does not change the 2.106 Å inter-layer spacing or the 0.50 Å
Fe–MgO gap, so don't "fix" those; (3) keep the runs dipole-free (plain
`0_lcb_femgo`); (4) judge compile by `agox_v2`, never the base-python LSP; (5) the
heavy 100-iteration HPC runs are deferred — this instruction stops at the passing
stacking smoke.

---

## INSTR #1 — Stand up a Fe/MgO LCB run with a dipole correction (`1_runs/0_femgo_dip`)

**Date:** 2026-09-06 · **Goal:** create a self-contained run dir under `1_runs/` that
replicates the `0_lcb_femgo` system (Fe(001) overlayer on MgO(001), **no B**,
LCB/GPR AGOX search) and adds a **dipole correction on the vacuum axis (z)** to
the GPAW calculator. You do this by hand; follow the steps in order. When done you
have a compile-clean `main.py` wired with `poissonsolver={'dipolelayer': 'xy'}`,
a matching job script, and a passing smoke test. The heavy 100-iteration HPC run is
out of scope here.

**Source of truth:** copy from
`2_analysist/0_lcb_femgo/` (its `main.py` + `scripts/`). Env for all compile/run
steps below = **`agox_v2`**: `/home/think/miniconda3/envs/agox_v2/bin/python`.
GPAW here is **25.7.0**; in this version the dipole layer is spelled
`dipolelayer` inside a `poissonsolver` dict (verified against
`site-packages/gpaw/test/test_dipole.py`). `SubprocessGPAW` forwards every
`**kwargs` verbatim into the GPAW constructor (`agox/helpers/gpaw_subprocess.py`
→ `gpaw_process`), so adding a `poissonsolver` kwarg is all you need.

---

### Step 1 — Create the run dir and copy the source files

```bash
cd /home/think/Desktop/research/_run/0_lcb
mkdir -p 1_runs/0_femgo_dip
cp -r 2_analysist/0_lcb_femgo/scripts 1_runs/0_femgo_dip/scripts
cp 2_analysist/0_lcb_femgo/main.py 1_runs/0_femgo_dip/main.py
# job script (name it to fit the 1_runs j_*.sh convention; adjust as you like)
cp 2_analysist/0_lcb_femgo/job_5x5_9.sh 1_runs/0_femgo_dip/j_5x5_dip.sh
ls 1_runs/0_femgo_dip 1_runs/0_femgo_dip/scripts | head
```

Expected: the dir holds `main.py`, `j_5x5_dip.sh`, `scripts/` (with
`build_fe_stack.py`, `build_mgo_stack.py`, `build_heteroStruct.py`,
`hetero_struct_randomize.py`, `plot_structure.py`, …). **Do not** copy the
`seed_*/`, `stop_16/`, `trash/`, or any run output — this dir starts empty of data.

### Step 2 — Edit `main.py`: add the dipole correction

Open `1_runs/0_femgo_dip/main.py`. Find the `SubprocessGPAW(...)` call (in the
copied `0_lcb_femgo` source it is the `calc = SubprocessGPAW(` block, roughly
lines 156–171). It currently opens:

```python
    calc = SubprocessGPAW(
        ncores=ncores,
        mode={"name": "lcao"},
        basis="dzp",
        xc="PBE",
        ...
        spinpol=True
    )
```

Add **one line** to the keyword list. Insert immediately after `ncores=ncores,`
(and update the script docstring/comment to note the dipole correction):

```python
    calc = SubprocessGPAW(
        ncores=ncores,
        poissonsolver={"dipolelayer": "xy"},
        mode={"name": "lcao"},
        ...
    )
```

**Why `'xy'`:** the dipole layer is the plane perpendicular to the non-periodic
(vacuum) axis. Here `pbc = [True, True, False]`, so the vacuum/relaxed direction is
**z** and the correction plane is **xy**. `dipolelayer` (no second underscore)
must match the non-periodic axis or GPAW raises `ValueError: System must be
non-periodic perpendicular to dipole-layer`.

That is the only code change required. Do **not** change the physical parameters
(`a_mgo=4.212`, `a_fe=2.870190`, `supercell=(5,5,1)`, `kpts=(1,1,1)`, `kappa=2`,
`N_iterations=100`, LCAO/dzp/PBE, spinpol, `ncores=24`).

### Step 3 — Point the job script at the new `main.py`

`j_5x5_dip.sh` is a straight copy of `job_5x5_9.sh` (PJM headers, `gpaw_env`,
`python ./main.py`). Confirm it still runs `main.py` **from the new dir's cwd**
(it does — `python ./main.py` is relative). Edit the seed/iteration scope only if
you want a narrower first run; otherwise leave as-is. Keep it a bare `#PJM` script;
**never** add `pjsub -x`.

### Step 4 — Smoke test (compile gate first)

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb
$PY -m py_compile 1_runs/0_femgo_dip/main.py && echo "COMPILE OK"
```

Expected: `COMPILE OK`. (The LSP under base `python3` will flag AGOX/ASE imports —
ignore it; judge by `agox_v2`'s `py_compile`.)

### Step 5 — Smoke test (GPAW dipole acceptance run)

Run a reduced slab through a real GPAW calc with the same `poissonsolver` kwarg to
prove the option is **accepted** (config errors surface at initialization, before
the SCF loop) **without** a full 100-iteration AGOX loop. Create
`1_runs/0_femgo_dip/smoke_dipole.py`:

```python
"""Smoke: prove poissonsolver={'dipolelayer':'xy'} is ACCEPTED by GPAW 25.7
(basis must be a top-level kwarg, not inside mode). Full SCF convergence is NOT
required — reaching the SCF loop without a config error is the pass condition."""
import sys
from ase.build import fcc111, add_adsorbate
from gpaw import GPAW, KohnShamConvergenceError

# Tiny asymmetric slab carrying a net dipole along z; not periodic in z.
slab = fcc111('Pt', size=(1, 1, 3), a=3.975534, vacuum=8.0)
add_adsorbate(slab, 'O', height=1.6, position='ontop')
slab.center(vacuum=8.0, axis=2)
slab.pbc = [True, True, False]

# NOTE: 'basis' is a TOP-LEVEL GPAW kwarg, NOT a key inside mode={...}.
calc = GPAW(mode={'name': 'lcao'}, basis='dzp', xc='PBE',
            kpts=(1, 1, 1), poissonsolver={'dipolelayer': 'xy'},
            txt='smoke_dipole.txt', maxiter=8, hund=True, spinpol=True)
slab.calc = calc

try:
    e = slab.get_potential_energy()
    print(f'converged (unexpected): E={e:.4f} eV')
except KohnShamConvergenceError:
    # Reached the SCF loop and ran iterations — dipole kwarg accepted,
    # no config error fired. That is the smoke pass.
    print('SCF loop reached (dipole kwarg accepted, not converged) -> DIPOLE KWARG ACCEPTED')
except Exception as ex:
    print(f'FAIL {type(ex).__name__}: {ex}')
    sys.exit(1)
```

Run it:

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/1_runs/0_femgo_dip
$PY smoke_dipole.py
```

**Expected output:** a line `SCF loop reached (dipole kwarg accepted, not converged)
-> DIPOLE KWARG ACCEPTED`, process exit code 0. (It need **not** fully converge —
an O/Pt metallic slab is slow and may not reach the default tolerance in a handful
of SCF steps; that is expected and acceptable here. A real `ConvergenceError`
means the kwarg was accepted, which is what we are testing.)

#### If Step 5 errored: `LCAO.__init__() got an unexpected keyword argument 'basis'`

**Why:** the earlier (original) smoke script put `basis='dzp'` **inside** the
`mode` dict (`mode={'name': 'lcao', 'basis': 'dzp'}`). In GPAW 25.7 the `mode`
dict's keys are passed straight to the wave-function mode constructor
(`gpaw.wavefunctions.mode.create_wave_function_mode` → `LCAO(...)`), and
`LCAO.__init__` accepts only `atomic_correction`, `interpolation`,
`force_complex_dtype` — **not** `basis`. So `basis` must be a **top-level** GPAW
kwarg, exactly as your real `main.py` already writes it
(`mode={"name": "lcao"}, basis="dzp"` as two separate kwargs). The two `calc`
lines in the earlier smoke had this bug; the corrected script above fixes it
(`mode={'name': 'lcao'}, basis='dzp'`). The error is a `TypeError` raised at
calculator initialization — it has nothing to do with the dipole correction
(which is spelled correctly), so do not "fix" the `dipolelayer` line.

**Fix:** apply the smoke script exactly as written above (move `basis='dzp'` out
of the `mode={...}` dict to a top-level kwarg) and re-run. When it prints
`DIPOLE KWARG ACCEPTED`, Step 5 passes.

### Step 6 — Verify & clean up

- Confirm `grep dipolelayer 1_runs/0_femgo_dip/main.py` shows the kwarg once.
- Delete the throwaway `smoke_dipole.txt` log (and `smoke_dipole.py` if you don't
  want to keep it); keep the real run dir data out of git (`seed_*/`, `*.db`,
  `*.out`, `gpaw_logs/` are ignored project-wide).
- Tracked additions for a commit: `main.py`, `j_5x5_dip.sh`, `scripts/*.py`.

**Pitfalls:** (1) spell it `dipolelayer`, not `dipole_layer`, and put it **inside**
`poissonsolver={...}`, not as a top-level GPAW kwarg; (2) `basis` is a **top-level**
GPAW kwarg — do **not** nest it inside `mode={...}` (that raises
`LCAO.__init__() got an unexpected keyword argument 'basis'`); (3) keep `pbc` z
non-periodic or GPAW errors; (4) don't bump physical params while smoke-testing —
the dipole line must be the only diff vs `0_lcb_femgo`; (5) judge compile by
`agox_v2`, never the base-python LSP.

