#!/usr/bin/env python3
"""
Analyze Wang-Landau HPC outputs for c_landausampling (c1 = Fe/MgO, c2 = B3).

Auto-discovers every `wl_output_*` directory under each run dir in `2_analysist/`,
and for each extracts:

  - State density g(E):  `g_of_E.csv`  (rel_eV_per_atom, ln_g, H)
  - Thermodynamics:      `thermodynamics.csv`  (T, beta, logZ, Z, F)
  - Heat capacity:       `heat_capacity.csv`   (T, C_V)
  - Convergence / process metrics parsed from the job `.out` log:
      init rel E (eV/atom) and start bin, number of Wang-Landau stages reached,
      the ln_f stage trajectory, the visited-bin count at each progress step,
      rattle/swap move counts, whether the run reached the 1/t switch, and the
      last ln_f (refinement factor).

Then writes:
  - One comparison figure per system plotting g(E) (ln_g vs rel eV/atom) for every
    output of that system (c1: mc1000 + sweep 10k/30k/50k; c2: sweep 10k/30k/50k).
  - A per-run summary CSV + a console table.

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python analyze_wl_outputs.py \
      [--runs c1_mgofe_N40_Emax04 c2_boron3_N40_Emax04] [--outdir .]
"""

from __future__ import annotations

__version__ = "1.0.0"

import argparse
import csv
import glob
import os
import re
from collections import OrderedDict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

E_LABEL = r"$(E - E_{\mathrm{min}})/N$  (eV/atom)"  # single backslash (math-text safe)
DEFAULT_RUNS = ["c1_mgofe_N40_Emax04", "c2_boron3_N40_Emax04"]


# --- CSV loaders ------------------------------------------------------------

def load_csv(path):
    """Return a list of rows (list of float) from a numeric CSV with a header."""
    with open(path) as f:
        rdr = csv.reader(f)
        header = next(rdr)
        rows = []
        for line in rdr:
            if not line or line[0].startswith("#"):
                continue
            try:
                rows.append([float(x) for x in line])
            except ValueError:
                continue
    return header, np.asarray(rows, dtype=float)


# --- .out log parser --------------------------------------------------------

def _wrote_to(content, out_name):
    """True if the log contains '... to <out_name>' as an exact output-dir token
    (i.e. not followed by '_', so wl_output_c1 does not match wl_output_c1_sweep_*)."""
    for m in re.finditer(r"to ([\w./\-]+)", content):
        if m.group(1) == out_name:
            return True
    return False


def parse_out(log_path, out_name):
    """Extract per-run convergence/process metrics from a Wang-Landau .out log,
    keyed to the segment that wrote ``out_name``.

    A single sweep .out contains several sequential runs; each segment ends with
    "Wrote g_of_E.csv ... to <output>". We parse the segment whose written output
    dir matches ``out_name`` (or ``wl_output_c1`` when out_name is
    ``wl_output_c1_mc1000`` and the log wrote to the bare name).
    """
    if not os.path.isfile(log_path):
        return {}
    txt = open(log_path).read()
    # Each run segment starts at its "Wang-Landau: <n> MC steps" header and ends
    # right before the next one (its "Wrote ... to <out>" line is inside it).
    segments = re.split(r"(?=Wang-Landau: \d+ MC steps)", txt)
    seg = None
    for i, s in enumerate(segments):
        if _wrote_to(s, out_name):
            seg = s
            break
    if seg is None and out_name == "wl_output_c1_mc1000":
        for s in segments:
            if _wrote_to(s, "wl_output_c1"):
                seg = s
                break
    if seg is None:
        return {}
    info = _parse_segment(seg)
    # The "init: rel E" line for this run is printed just BEFORE the run's
    # "Wang-Landau: N MC steps" header. For a single-run log the init sits at
    # the very top (inside the first segment); for a sweep log it is in the
    # previous segment's tail. Search the text before the segment start first,
    # then the segment's own leading region. Use the same token (with bare
    # fallback) as the segment match above.
    for token in ([out_name] if out_name != "wl_output_c1_mc1000"
                  else [out_name, "wl_output_c1"]):
        for s in segments:
            if _wrote_to(s, token):
                start = txt.index(s)
                head = txt[:start]
                m = list(re.finditer(
                    r"init: rel E = ([0-9eE.+-]+) eV/atom \(bin (\d+)\)", head))
                if not m:
                    m = list(re.finditer(
                        r"init: rel E = ([0-9eE.+-]+) eV/atom \(bin (\d+)\)", s[:4000]))
                if m:
                    info["init_rel_E"] = float(m[-1].group(1))
                    info["init_bin"] = int(m[-1].group(2))
                break
    return info


def _parse_segment(txt):
    info = {}
    # init rel energy + bin
    m = re.search(r"init: rel E = ([0-9eE.+-]+) eV/atom \(bin (\d+)\)", txt)
    if m:
        info["init_rel_E"] = float(m.group(1))
        info["init_bin"] = int(m.group(2))
    # stages reached + 1/t switch
    m = re.search(r"Total MC steps = \d+, stages reached = (\d+)", txt)
    if m:
        info["stages_reached"] = int(m.group(1))
    info["used_1_over_t"] = "1/t algorithm" in txt and "did not reach the 1/t" not in txt
    info["note_1_over_t"] = "did not reach the 1/t switch" in txt
    # move counts
    m = re.search(r"moves: (\d+) rattle, (\d+) swap", txt)
    if m:
        info["n_rattle"] = int(m.group(1))
        info["n_swap"] = int(m.group(2))
    # last ln_f (final refinement factor) from last stage line
    ln_f_vals = [float(x) for x in re.findall(r"ln_f ([0-9.eE+-]+)", txt)]
    if ln_f_vals:
        info["final_ln_f"] = ln_f_vals[-1]
    # visited-bin trajectory: list of (step, visited)
    visited = [(int(s), int(v)) for s, v in
               re.findall(r"step\s+(\d+)\s+stage\s+\d+\s+ln_f [0-9.eE+-]+\s+visited (\d+)/\d+", txt)]
    info["visited_traj"] = visited
    # stage trajectory: list of (stage, ln_f, step)
    stages = [(int(st), float(lf), int(s)) for st, lf, s in
              re.findall(r"stage (\d+): ln_f = ([0-9.eE+-]+) \(flat at step (\d+)\)", txt)]
    info["stage_traj"] = stages
    return info


# --- per-output extraction -------------------------------------------------

def analyze_output(run_dir, out_name, log_path):
    """Return a dict of extracted data for one wl_output dir."""
    out = os.path.join(run_dir, out_name)
    d = {"outdir": out_name}
    # g_of_E
    gpath = os.path.join(out, "g_of_E.csv")
    if os.path.isfile(gpath):
        _, g = load_csv(gpath)
        d["rel_E"] = g[:, 0]
        d["ln_g"] = g[:, 1]
        d["H"] = g[:, 2]
        nz = g[:, 1] != 0
        d["n_bins_total"] = len(g)
        d["n_bins_visited"] = int(nz.sum())
        d["energy_spread"] = float(g[:, 0].max() - g[:, 0][nz].min()) if nz.any() else 0.0
        d["ln_g_max"] = float(g[:, 1].max())
    # thermodynamics
    tpath = os.path.join(out, "thermodynamics.csv")
    if os.path.isfile(tpath):
        _, t = load_csv(tpath)
        d["T_K"] = t[:, 0]
        d["logZ"] = t[:, 2]
        d["F_eV"] = t[:, 4]
    # heat capacity
    cpath = os.path.join(out, "heat_capacity.csv")
    if os.path.isfile(cpath):
        _, c = load_csv(cpath)
        d["C_V"] = c[:, 1]
    # .out log metrics
    d.update(parse_out(log_path, out_name))
    return d


# --- state-density figure per system ---------------------------------------

def plot_g_of_E_system(system_label, run_dir, outputs, outdir):
    """Overlay ln g(E) vs rel energy for every output of one system."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for data in outputs:
        if "rel_E" not in data or "ln_g" not in data:
            continue
        label = data["outdir"].replace("wl_output_", "").replace("_", " ")
        # use H (histogram) linewidth scaled by log10(steps) if available else default
        ax.plot(data["rel_E"], data["ln_g"], "-o", ms=2.5, lw=1.4, label=label)
    ax.set_xlabel(E_LABEL)
    ax.set_ylabel(r"$\ln g(E)$")
    ax.set_title(f"Wang-Landau state density g(E) — {system_label}")
    ax.legend(frameon=False, fontsize=8, loc="best")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out_path = os.path.join(outdir, f"state_density_{system_label}.png")
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  saved -> {out_path}")


# --- summary ---------------------------------------------------------------

def make_summary(runs):
    """Return list of summary rows (one per wl_output)."""
    rows = []
    for run_dir, outputs in runs.items():
        for data in outputs:
            rows.append({
                "run": run_dir,
                "output": data["outdir"],
                "mc_steps": data["outdir"].split("_")[-1],
                "n_bins_total": data.get("n_bins_total", ""),
                "n_bins_visited": data.get("n_bins_visited", ""),
                "energy_spread_eVatom": (f"{data['energy_spread']:.4f}"
                                         if "energy_spread" in data else ""),
                "ln_g_max": (f"{data['ln_g_max']:.2f}" if "ln_g_max" in data else ""),
                "init_rel_E_eVatom": (f"{data.get('init_rel_E', ''):.4f}"
                                      if "init_rel_E" in data else ""),
                "stages_reached": data.get("stages_reached", ""),
                "final_ln_f": (f"{data.get('final_ln_f', ''):.4e}"
                               if "final_ln_f" in data else ""),
                "n_rattle": data.get("n_rattle", ""),
                "n_swap": data.get("n_swap", ""),
                "used_1_over_t": data.get("used_1_over_t", ""),
                "logZ@100K": (f"{data['logZ'][0]:.3f}" if "logZ" in data and len(data["logZ"]) else ""),
                "F@100K_eV": (f"{data['F_eV'][0]:.3f}" if "F_eV" in data and len(data["F_eV"]) else ""),
            })
    return rows


def print_table(rows):
    cols = ["run", "output", "mc_steps", "n_bins_visited", "energy_spread_eVatom",
            "init_rel_E_eVatom", "stages_reached", "final_ln_f", "n_rattle",
            "n_swap", "used_1_over_t", "logZ@100K"]
    w = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    print(" | ".join(c.ljust(w[c]) for c in cols))
    print("-+-".join("-" * w[c] for c in cols))
    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(w[c]) for c in cols))


def main():
    p = argparse.ArgumentParser(description="Analyze c_landausampling Wang-Landau HPC outputs")
    p.add_argument("--runs", nargs="+", default=DEFAULT_RUNS,
                   help="run dir names under 2_analysist/ (default c1, c2)")
    p.add_argument("--outdir", default=".",
                   help="output dir for summary CSV + figures (default current dir)")
    p.add_argument("--log-suffix", default=".out",
                   help="suffix of job log files to scan (default .out)")
    args = p.parse_args()

    _HERE = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(_HERE, args.outdir)
    os.makedirs(outdir, exist_ok=True)

    runs = OrderedDict()
    for run in args.runs:
        run_dir = os.path.join(_HERE, run)
        if not os.path.isdir(run_dir):
            print(f"WARN: run dir not found: {run_dir}")
            continue
        out_dirs = sorted(glob.glob(os.path.join(run_dir, "wl_output_*")))
        run_outputs = []
        for od in out_dirs:
            out_name = os.path.basename(od)
            # find the job .out log whose written output dir matches this output
            # (exact token; bare fallback for wl_output_c1_mc1000 -> wl_output_c1,
            # but NOT matching wl_output_c1_sweep_* which are distinct dirs)
            log_path = ""
            tokens = [out_name]
            if out_name == "wl_output_c1_mc1000":
                tokens.append("wl_output_c1")
            for lf in glob.glob(os.path.join(run_dir, f"*{args.log_suffix}")):
                content = open(lf).read()
                if any(_wrote_to(content, t) for t in tokens):
                    log_path = lf
                    break
            data = analyze_output(run_dir, out_name, log_path)
            run_outputs.append(data)
        runs[run] = run_outputs
        print(f"\n=== {run}: {len(run_outputs)} wl_output dirs ===")
        for d in run_outputs:
            print(f"  {d['outdir']}: visited {d.get('n_bins_visited','?')}/"
                  f"{d.get('n_bins_total','?')} bins, "
                  f"init_rel_E={d.get('init_rel_E','?')}, "
                  f"stages={d.get('stages_reached','?')}")

    # summary CSV + table
    rows = make_summary(runs)
    if rows:
        fieldnames = list(rows[0].keys())
        with open(os.path.join(outdir, "wl_analysis_summary.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
        print("\n=== Summary table ===")
        print_table(rows)
        print(f"\n  wrote -> {os.path.join(outdir, 'wl_analysis_summary.csv')}")

    # one state-density figure per system
    print("\n=== State-density figures ===")
    for run_dir, run_outputs in runs.items():
        if not run_outputs:
            continue
        system = run_dir.split("_")[0]  # c1 / c2
        plot_g_of_E_system(system, run_dir, run_outputs, outdir)

    print("\nDone.")


if __name__ == "__main__":
    main()
