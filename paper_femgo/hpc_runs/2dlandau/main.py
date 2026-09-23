#!/usr/bin/env python3
"""
2D Landau sampling: inherent-structure Wang-Landau density of states g(E, dZ)
of the Fe/MgO flat<->island transition on an AGOX GPR surrogate. No DFT.

Loads every seed database in data/femgo, trains a single GPR surrogate, then
runs WangLandau2DSampler (generator-based jump proposal -> dZ-ceiling GPR relax
-> 2D WL accept) to compute the joint inherent-structure g_IS(E, dZ), and from
it the island-height distribution <dZ(T)> and flat<->island free-energy
difference at a set of temperatures.

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python main.py [options]
"""

from __future__ import annotations

__version__ = "1.0.0"

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

from landau_2d.gpr_training import load_all_seeds, build_gpr, validate_gpr
from landau_2d.generator import DeltaZGenerator
from landau_2d.wang_landau_2d import WangLandau2DSampler
from landau_2d.thermodynamics import reweight_2d, E_min_curve

DATA_DIR = os.path.join(_HERE, "data", "femgo")


def main():
    p = argparse.ArgumentParser(
        description="2D Wang-Landau g(E,dZ) sampling on a GPR surrogate "
                    "(no DFT)")
    p.add_argument("--dataset", default=DATA_DIR,
                   help="Dataset dir holding seed_*/1_db/db_*.db")
    p.add_argument("--n-e-bins", type=int, default=35,
                   help="Energy bins (default 35)")
    p.add_argument("--e-min", type=float, default=0.0)
    p.add_argument("--e-max", type=float, default=0.7,
                   help="Upper E edge (eV/atom rel); 0.7 gives margin over the "
                        "flat branch (~0.67)")
    p.add_argument("--e-reject", type=float, default=None,
                   help="Rel E above which a trial is rejected (default "
                        "5*e_max)")
    p.add_argument("--n-dz-bins", type=int, default=12,
                   help="dZ bins (default 12 over [film-height min, natural-island])")
    p.add_argument("--dz-min", type=float, default=None,
                   help="Lower dZ edge (A, film height). Default: contact gap "
                        "(flat monolayer).")
    p.add_argument("--dz-max", type=float, default=None,
                   help="Upper dZ edge (A, film height). Default: the natural "
                        "island height (global-min structure's film height).")
    p.add_argument("--relax-steps", type=int, default=100,
                   help="GPR BFGS steps per trial (default 100)")
    p.add_argument("--flat-island-spread", type=float, default=1.0,
                   help="Fe z-spread threshold (A) for flat vs island labelling, "
                        "default 1.0")
    p.add_argument("--contact-gap", type=float, default=2.08,
                   help="Adsorption height of bottom Fe above MgO surface (A), "
                        "default 2.08")
    p.add_argument("--flatness-criterion", type=float, default=0.80)
    p.add_argument("--check-interval", type=int, default=5000)
    p.add_argument("--n-stages-standard", type=int, default=14)
    p.add_argument("--reference-steps", type=int, default=2000,
                   help="Torbrügge initial pass length (accessible-cell map)")
    p.add_argument("--mc-steps", type=int, default=50000,
                   help="WL MC steps")
    p.add_argument("--temperatures", default="100,200,300,500,1000",
                   help="Comma-separated temperatures (K)")
    p.add_argument("--output", default=os.path.join(_HERE, "output"),
                   help="Output directory")
    p.add_argument("--rng", type=int, default=42)
    p.add_argument("--use-ray", action="store_true")
    args = p.parse_args()

    # --- 1. Load the dataset ------------------------------------------------
    print("=" * 70)
    print(f"Loading dataset from {args.dataset}")
    structures, energies, db_paths = load_all_seeds(args.dataset)
    print(f"  Total: {len(structures)} structures, {len(db_paths)} databases")
    print(f"  Composition: {structures[0].get_chemical_formula()} "
          f"({len(structures[0])} atoms)")
    print(f"  E range: {energies.min():.4f} .. {energies.max():.4f} eV")

    # --- 2. Train the GPR surrogate -----------------------------------------
    print("\nTraining GPR on combined dataset...")
    gpr = build_gpr(structures, use_ray=args.use_ray)
    validate_gpr(gpr, structures, energies)

    # --- 3. Build the generator + sampler -----------------------------------
    print("\nBuilding DeltaZGenerator + WangLandau2DSampler...")
    gen = DeltaZGenerator(structures[0], z_contact=None,
                          contact_gap=args.contact_gap,
                          rng=np.random.default_rng(args.rng))
    print(f"  z_contact = {gen.z_contact:.4f} A (substrate top "
          f"{gen.substrate_top_z:.4f}, gap {args.contact_gap})")

    # dZ range in film height: flat monolayer ~ contact gap, top = the natural
    # island height (the global-min structure's film height).
    dz_min = args.dz_min if args.dz_min is not None else args.contact_gap
    if args.dz_max is not None:
        dz_max = args.dz_max
    else:
        i_min = int(np.argmin(energies))
        dz_max = gen.fe_film_height(structures[i_min])
    print(f"  dZ range (film height): [{dz_min:.3f}, {dz_max:.3f}] A "
          f"(natural island height {dz_max:.3f})")

    sampler = WangLandau2DSampler(
        gpr=gpr,
        generator=gen,
        E_ref=energies.min(),
        n_atoms=len(structures[0]),
        n_e_bins=args.n_e_bins,
        e_min=args.e_min,
        e_max=args.e_max,
        e_reject=args.e_reject,
        n_dz_bins=args.n_dz_bins,
        dz_min=dz_min,
        dz_max=dz_max,
        relax_steps=args.relax_steps,
        flat_island_spread_aa=args.flat_island_spread,
        flatness_criterion=args.flatness_criterion,
        check_interval=args.check_interval,
        n_stages_standard=args.n_stages_standard,
        reference_steps=args.reference_steps,
        rng=np.random.default_rng(args.rng + 1),
    )

    # --- 4. Run --------------------------------------------------------------
    sampler.initialize()
    sampler.run(n_steps=args.mc_steps,
                progress_every=max(args.check_interval, 1))

    # --- 5. Reweight -> <dZ(T)>, dF -----------------------------------------
    temps = [float(t) for t in args.temperatures.split(",") if t.strip()]
    e_centers, dz_centers, ln_g, H, accessible = sampler.g_of_E_dZ()
    rows = reweight_2d(
        sampler.ensemble_rows, ln_g, e_centers, dz_centers,
        args.e_min, sampler.e_width, dz_min, sampler.dz_width,
        sampler.n_atoms, temps, flat_island_spread_aa=args.flat_island_spread)

    # --- 6. Save (all machine-readable; PNGs derived) ------------------------
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    # g_of_E_dZ.json — full 2D result
    dzc, emin = E_min_curve(ln_g, e_centers, dz_centers, accessible)
    payload = {
        "e_min": args.e_min, "e_max": args.e_max, "n_e_bins": args.n_e_bins,
        "e_edges": (args.e_min + sampler.e_width * np.arange(args.n_e_bins + 1)).tolist(),
        "dz_min": dz_min, "dz_max": dz_max,
        "n_dz_bins": args.n_dz_bins,
        "dz_edges": (dz_min + sampler.dz_width * np.arange(args.n_dz_bins + 1)).tolist(),
        "ln_g": ln_g.tolist(),
        "H": H.tolist(),
        "accessible": accessible.tolist(),
        "E_min_dZ": emin.tolist(),
        "n_bins_visited": int((H > 0).sum()),
        "n_accessible": int(accessible.sum()),
        "flatness_criterion": args.flatness_criterion,
        "switched_to_1_over_t": sampler.switched_to_1_over_t,
        "stages": sampler.stage,
        "rng": args.rng,
        "temperatures_K": temps,
        "n_atoms": sampler.n_atoms,
    }
    with open(out / "g_of_E_dZ.json", "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\n  Wrote g_of_E_dZ.json")

    # g_of_E_dZ.csv — long-form dump
    with open(out / "g_of_E_dZ.csv", "w") as f:
        f.write("E_center_eV_per_atom,dZ_center_A,i,j,ln_g,H,visited\n")
        for i in range(args.n_e_bins):
            for j in range(args.n_dz_bins):
                f.write(f"{e_centers[i]:.6f},{dz_centers[j]:.6f},{i},{j},"
                        f"{ln_g[i, j]:.6f},{H[i, j]},"
                        f"{int(accessible[i, j])}\n")
    print("  Wrote g_of_E_dZ.csv")

    # delta_z_distribution.csv
    with open(out / "delta_z_distribution.csv", "w") as f:
        f.write("T_K,mean_dZ_A,std_dZ_A,dF_flat_island_eV\n")
        for r in rows:
            f.write(f"{r['T_K']:.1f},{r['mean_dZ_A']:.6f},"
                    f"{r['std_dZ_A']:.6f},{r['dF_flat_island_eV']:.6f}\n")
    print("  Wrote delta_z_distribution.csv")

    # ensemble.json — reweightable dump of accepted structures
    ens = []
    for (E_total, E_rel, dz, i, j, lab) in sampler.ensemble_rows:
        ens.append({"E_total_eV": E_total, "E_rel_eV_per_atom": E_rel,
                    "dZ_A": dz, "E_bin": i, "dZ_bin": j, "label": lab})
    with open(out / "ensemble.json", "w") as f:
        json.dump(ens, f, indent=2)
    print(f"  Wrote ensemble.json ({len(ens)} accepted structures)")

    # --- 7. Derived plots ----------------------------------------------------
    _plot_heatmap(e_centers, dz_centers, ln_g, accessible, out)
    _plot_dz_distribution(rows, out)

    print("\nIsland-height distribution <dZ(T)>:")
    print("  T(K)     <dZ>(A)    std(A)   dF_flat-island(eV)")
    for r in rows:
        print(f"  {r['T_K']:6.1f}  {r['mean_dZ_A']:9.4f}  "
              f"{r['std_dZ_A']:7.4f}  {r['dF_flat_island_eV']:9.4f}")

    print(f"\nDone. Results written to {out}")


def _plot_heatmap(e_centers, dz_centers, ln_g, accessible, out):
    import matplotlib.pyplot as plt
    ln = np.where(accessible, ln_g, np.nan)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    im = ax.imshow(ln.T, aspect="auto", origin="lower",
                   extent=[e_centers[0], e_centers[-1],
                           dz_centers[0], dz_centers[-1]],
                   cmap="viridis")
    ax.set_xlabel(r"$(E - E_\mathrm{min})/N$  (eV/atom)")
    ax.set_ylabel(r"$\Delta Z$  (\AA)")
    ax.set_title(r"$\ln g_{\mathrm{IS}}(E, \Delta Z)$")
    fig.colorbar(im, ax=ax, label=r"$\ln g$")
    fig.tight_layout()
    fig.savefig(out / "g_of_E_dZ.png", dpi=150)
    plt.close(fig)
    print("  Wrote g_of_E_dZ.png")


def _plot_dz_distribution(rows, out):
    import matplotlib.pyplot as plt
    T = [r["T_K"] for r in rows]
    mean = [r["mean_dZ_A"] for r in rows]
    std = [r["std_dZ_A"] for r in rows]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(T, mean, yerr=std, fmt="o-", capsize=3)
    ax.set_xlabel("T (K)")
    ax.set_ylabel(r"$\langle \Delta Z \rangle$  (\AA)")
    ax.set_title(r"Island height vs temperature")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "delta_z_distribution.png", dpi=150)
    plt.close(fig)
    print("  Wrote delta_z_distribution.png")


if __name__ == "__main__":
    main()
