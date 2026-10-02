#!/usr/bin/env python3
"""
1D nested-sampling validation of the 2D Wang-Landau inherent-structure DOS
g_IS(E, dZ) of the Fe/MgO flat<->island transition, on the same AGOX GPR
surrogate. No DFT.

Two stages (spec 202610012020, v18):
  Stage 1 (runs independently, first): train the GPR, run 1D nested sampling
    over the full (E, dZ) space, relax each live point to its basin minimum
    (inherent structure), and write the NS DOS g_NS(E). Does NOT require a
    converged WL DOS.
  Stage 2 (deferred, done later): load a converged WL DOS (g_of_E_dZ.json),
    compute its energy marginal g_IS(E) via log-sum-exp, and compare against
    g_NS(E) (overlay + max/mean |dln g| + flat<->island dF_flat_island).

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python main.py [options]
"""

from __future__ import annotations

__version__ = "1.1.0"

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import matplotlib
matplotlib.use("Agg")

from ns_validate.gpr_training import load_all_seeds, build_gpr, validate_gpr
from ns_validate.generator import DeltaZGenerator
from ns_validate.nested_sampler import NestedSampler
from ns_validate.utils import K_B, _logsumexp

DATA_DIR = os.path.join(_HERE, "..", "..", "data", "femgo")


# -- Stage 1: compute the NS DOS ---------------------------------------------

def run_stage1(args, out: Path):
    print("=" * 70)
    print("STAGE 1 — compute the NS DOS (independent, no WL required)")
    print("=" * 70)

    # 1. Load dataset + train GPR (same recipe as 2dlandau)
    structures, energies, db_paths = load_all_seeds(args.dataset)
    print(f"  {len(structures)} structures, {len(db_paths)} DBs, "
          f"E range {energies.min():.4f}..{energies.max():.4f} eV")
    gpr = build_gpr(structures, use_ray=args.use_ray)
    validate_gpr(gpr, structures, energies)
    E_ref = float(energies.min())
    n_atoms = len(structures[0])

    # 2. Build the generator
    gen = DeltaZGenerator(structures[0], z_contact=None,
                          contact_gap=args.contact_gap,
                          rng=np.random.default_rng(args.rng))
    print(f"  z_contact={gen.z_contact:.4f} A, substrate_top={gen.substrate_top_z:.4f} A")

    # 3. Run nested sampling
    sampler = NestedSampler(
        gpr=gpr, generator=gen, E_ref=E_ref, n_atoms=n_atoms,
        n_live=args.n_live, n_iterations=args.n_iterations,
        e_min=args.e_min, e_max=args.e_max, n_e_bins=args.n_e_bins,
        relax_steps=args.relax_steps, fmax=args.fmax,
        dz_min=args.dz_min, dz_max=args.dz_max,
        dz_retry=args.dz_retry,
        progress_every=args.progress_every,
        rng=np.random.default_rng(args.rng + 1),
    )
    sampler.initialize()
    sampler.run()

    # 4. Write outputs
    e_centers, ln_g, H, accessible = sampler.g_of_E()
    out.mkdir(parents=True, exist_ok=True)

    payload = {
        "e_min": sampler.e_min, "e_max": sampler.e_max,
        "n_e_bins": sampler.n_e_bins,
        "e_edges": (sampler.e_min + sampler.e_width *
                    np.arange(sampler.n_e_bins + 1)).tolist(),
        "ln_g": ln_g.tolist(),
        "H": H.tolist(),
        "accessible": accessible.tolist(),
        "n_bins_visited": int((H > 0).sum()),
        "n_live": sampler.n_live,
        "n_iterations": sampler.iteration,
        "alpha": sampler.alpha,
        "relax_steps": sampler.relax_steps,
        "fmax": sampler.fmax,
        "rng": args.rng,
        "n_atoms": n_atoms,
        "E_ref": E_ref,
    }
    with open(out / "g_NS.json", "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  Wrote {out / 'g_NS.json'}")

    with open(out / "g_NS.csv", "w") as f:
        f.write("E_center_eV_per_atom,ln_g,H,visited\n")
        for i in range(sampler.n_e_bins):
            f.write(f"{e_centers[i]:.6f},{ln_g[i]:.6f},{H[i]},"
                    f"{int(accessible[i])}\n")
    print(f"  Wrote {out / 'g_NS.csv'}")

    # acceptance diagnostic (G8)
    acc = sampler.acceptance_report()
    acc["e_sampled_min"] = float(min(sampler.removed_rel)) if sampler.removed_rel else None
    acc["e_sampled_max"] = float(max(sampler.removed_rel)) if sampler.removed_rel else None
    with open(out / "ns_acceptance.json", "w") as f:
        json.dump(acc, f, indent=2)
    print(f"  Wrote {out / 'ns_acceptance.json'}")
    print("  Acceptance:", json.dumps(acc, indent=2))

    _plot_ns(e_centers, ln_g, accessible, out)
    return sampler, e_centers, ln_g, accessible


def _plot_ns(e_centers, ln_g, accessible, out: Path):
    import matplotlib.pyplot as plt
    ln = np.where(accessible, ln_g, np.nan)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(e_centers, ln, "o-", ms=3)
    ax.set_xlabel(r"$(E - E_\mathrm{min})/N$  (eV/atom)")
    ax.set_ylabel(r"$\ln g_{\mathrm{NS}}(E)$")
    ax.set_title(r"NS inherent-structure DOS $g_{\mathrm{NS}}(E)$")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(out / "g_NS.png"), dpi=150)
    plt.close(fig)
    print(f"  Wrote {out / 'g_NS.png'}")


# -- Stage 2: validate against the WL DOS ------------------------------------

def _wl_energy_marginal(wl_path: Path):
    """Compute ln g_IS(E) = logsumexp_dZ(ln_g[E, :]) over accessible bins (C6)."""
    with open(wl_path) as f:
        d = json.load(f)
    ln_g = np.asarray(d["ln_g"], dtype=float)
    accessible = np.asarray(d["accessible"], dtype=bool)
    n_e = ln_g.shape[0]
    ln_marg = np.full(n_e, -np.inf)
    for i in range(n_e):
        row = ln_g[i, accessible[i, :]]
        if row.size:
            ln_marg[i] = _logsumexp(row)
    return ln_marg, d


def run_stage2(ns_ln_g, ns_accessible, ns_e_centers, wl_path: Path, out: Path,
               temperatures):
    print("\n" + "=" * 70)
    print(f"STAGE 2 — validate against WL DOS: {wl_path}")
    print("=" * 70)
    wl_ln_marg, wl = _wl_energy_marginal(wl_path)
    wl_e_centers = wl["e_min"] + (wl["e_max"] - wl["e_min"]) / wl["n_e_bins"] * (
        np.arange(wl["n_e_bins"]) + 0.5)

    # shared energy range (m1): intersection of WL bins and NS-sampled range
    ns_sampled = np.isfinite(ns_ln_g) & ns_accessible
    shared = np.isfinite(wl_ln_marg) & ns_sampled
    n_shared = int(shared.sum())
    coverage = n_shared / max(int(np.isfinite(wl_ln_marg).sum()), 1)

    # align (M5): shift NS to match WL at the lowest-energy shared bin
    if n_shared > 0:
        ref = int(np.where(shared)[0][0])
        shift = wl_ln_marg[ref] - ns_ln_g[ref]
        ns_ln_aligned = ns_ln_g + shift
    else:
        ns_ln_aligned = ns_ln_g
        shift = 0.0

    # metric
    dln = np.abs(wl_ln_marg[shared] - ns_ln_aligned[shared])
    metric = {
        "n_shared_bins": n_shared,
        "coverage": coverage,
        "max_abs_dln_g": float(dln.max()) if dln.size else None,
        "mean_abs_dln_g": float(dln.mean()) if dln.size else None,
        "alignment_shift": float(shift),
    }
    print("  Metric:", json.dumps(metric, indent=2))

    _plot_compare(wl_e_centers, wl_ln_marg, ns_e_centers, ns_ln_aligned,
                  shared, out)
    with open(out / "validation_metric.json", "w") as f:
        json.dump(metric, f, indent=2)
    print(f"  Wrote {out / 'validation_metric.json'}")
    return metric


def _plot_compare(wl_e, wl_ln, ns_e, ns_ln, shared, out: Path):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(wl_e, wl_ln, "o-", ms=3, label="WL (energy marginal)")
    ax.plot(ns_e, ns_ln, "s-", ms=3, label="NS (aligned)")
    ax.set_xlabel(r"$(E - E_\mathrm{min})/N$  (eV/atom)")
    ax.set_ylabel(r"$\ln g(E)$")
    ax.set_title("WL vs NS inherent-structure DOS")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(out / "validation_overlay.png"), dpi=150)
    plt.close(fig)
    print(f"  Wrote {out / 'validation_overlay.png'}")


# -- Driver ------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="1D nested-sampling validation of the 2D WL DOS (no DFT)")
    p.add_argument("--dataset", default=DATA_DIR,
                   help="Dataset dir holding seed_*/1_db/db_*.db")
    p.add_argument("--n-live", type=int, default=50)
    p.add_argument("--n-iterations", type=int, default=300)
    p.add_argument("--n-e-bins", type=int, default=35)
    p.add_argument("--e-min", type=float, default=0.0)
    p.add_argument("--e-max", type=float, default=0.7,
                   help="Max relative energy accepted into g_NS (G2)")
    p.add_argument("--relax-steps", type=int, default=300)
    p.add_argument("--fmax", type=float, default=0.1,
                   help="Relax convergence tolerance (empirical default 0.1)")
    p.add_argument("--dz-min", type=float, default=2.08)
    p.add_argument("--dz-max", type=float, default=5.73)
    p.add_argument("--dz-retry", type=int, default=5,
                   help="Total proposal attempts per NS step (each draws a fresh dZ)")
    p.add_argument("--contact-gap", type=float, default=2.08)
    p.add_argument("--progress-every", type=int, default=20)
    p.add_argument("--temperatures", default="298,573,623,673,773",
                   help="Comma-separated temperatures (K) for dF_flat_island")
    p.add_argument("--wl-dos", default=None,
                   help="Path to a converged WL g_of_E_dZ.json (Stage 2). "
                        "If omitted, only Stage 1 runs.")
    p.add_argument("--output", default=os.path.join(_HERE, "output"))
    p.add_argument("--rng", type=int, default=42)
    p.add_argument("--use-ray", action="store_true")
    args = p.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    sampler, e_centers, ln_g, accessible = run_stage1(args, out)

    if args.wl_dos:
        temps = [float(t) for t in args.temperatures.split(",") if t.strip()]
        run_stage2(ln_g, accessible, e_centers, Path(args.wl_dos), out, temps)
    else:
        print("\n[Stage 2 skipped] --wl-dos not provided. Run Stage 1 only; "
              "add --wl-dos <converged g_of_E_dZ.json> later to validate.")

    print(f"\nDone. Results in {out}")


if __name__ == "__main__":
    main()
