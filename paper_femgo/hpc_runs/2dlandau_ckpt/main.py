#!/usr/bin/env python3
"""
2D Landau sampling: inherent-structure Wang-Landau density of states g(E, dZ)
of the Fe/MgO flat<->island transition on an AGOX GPR surrogate. No DFT.

Loads every seed database in data/femgo, trains a single GPR surrogate, then
runs WangLandau2DSampler (generator-based jump proposal -> dZ-ceiling GPR relax
-> 2D WL accept) to compute the joint inherent-structure g_IS(E, dZ), and from
it the island-height distribution <dZ(T)> and flat<->island free-energy
difference at a set of temperatures.

Crash-resilient (spec 202609271240, v8): every ``--checkpoint-interval`` MC
steps it writes ``--output/checkpoint.json`` (full WL state + config header) and
``--output/ensemble.traj`` (accepted geometries) atomically, plus derivation a
step-tagged set of thermodynamic outputs (``*.step{N}.*``) for convergence
analysis. If run is interrupted, re-running with the same ``--output``
auto-resumes from the last checkpoint and continues the walk (running only the
remaining steps).

Run with the agox_v2 conda env:
    /home/think/miniconda3/envs/agox_v2/bin/python main.py [options]
"""

from __future__ import annotations

__version__ = "1.1.0"

import argparse
import json
import os
import sys
import tempfile
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
CHECKPOINT_NAME = "checkpoint.json"
TRAJ_NAME = "ensemble.traj"
_SCHEMA_VERSION = 1


# -- Atomic writes ------------------------------------------------------------

def _atomic_write_bytes(path: Path, data: bytes):
    """Write bytes atomically (tmp already in target dir, then rename)."""
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".",
                               suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _atomic_write_json(path: Path, obj):
    _atomic_write_bytes(path, json.dumps(obj, indent=2).encode("utf-8"))


def _atomic_write_traj(sampler, path: Path):
    """Write the accumulated accepted geometries to a ASE trajectory atomically.

    Geometry-only: constraints (agox ``BoxConstraint``) and the calculator are
    stripped so the traj round-trips through ``ase.io.read`` (ASE's
    ``dict2constraint`` cannot reconstruct the agox box). Resume only needs the
    coordinates; constraints/calc are re-applied fresh during sampling.
    """
    from ase.io import write as ase_write
    structs = sampler.ensemble_structs
    if not structs:
        return  # nothing recorded yet — leave any existing traj untouched
    clean = []
    for a in structs:
        c = a.copy()
        c.set_constraint()
        c.calc = None
        clean.append(c)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".",
                               suffix=".tmp")
    os.close(fd)
    try:
        ase_write(tmp, clean, format="traj")
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


# -- Config header / resume guard (spec C1 / G2) ------------------------------

def _config_header(sampler, args, dz_min, dz_max, dataset_dir) -> dict:
    return {
        "version": _SCHEMA_VERSION,
        "n_e_bins": int(sampler.n_e_bins),
        "n_dz_bins": int(sampler.n_dz_bins),
        "e_min": float(sampler.e_min),
        "e_max": float(sampler.e_max),
        "dz_min": float(dz_min),
        "dz_max": float(dz_max),
        "n_atoms": int(sampler.n_atoms),
        "E_ref": float(sampler.E_ref),
        "contact_gap": float(args.contact_gap),
        "dataset": str(Path(dataset_dir).resolve()),
    }


def _try_load_checkpoint(path: Path):
    """Load a checkpoint file; return (state, header) or None-on-unusable.

    G4: unreadable/invalid/unknown-schema file -> warn and return None (fresh
    run). C1/G2: a *present but differing* config, or an unsupported schema
    version -> hard fail via SystemExit (never silently resume).
    """
    if not path.exists():
        return None
    try:
        with open(path) as f:
            ckpt = json.load(f)
    except (OSError, ValueError) as e:
        print(f"[WARN] checkpoint {path} unreadable ({e}); starting a fresh "
              f"run (it will be overwritten).")
        return None
    header = ckpt.get("config")
    state = ckpt.get("state")
    if not isinstance(header, dict) or not isinstance(state, dict):
        print(f"[WARN] checkpoint {path} has no config/state; starting a fresh "
              f"run (it will be overwritten).")
        return None
    if header.get("version") != _SCHEMA_VERSION:
        print(f"[WARN] checkpoint {path} uses schema v{header.get('version')} "
              f"!= expected v{_SCHEMA_VERSION}; starting a fresh run.")
        return None
    return state, header


def _validate_config(header, sampler, args, dz_min, dz_max, dataset_dir):
    """C1: refuse to resume on any config mismatch against the current args."""
    expected = _config_header(sampler, args, dz_min, dz_max, dataset_dir)
    for k in expected:
        if header.get(k) != expected[k]:
            raise SystemExit(
                f"[ABORT] checkpoint config mismatch on '{k}': checkpoint has "
                f"{header.get(k)!r}, current run has {expected[k]!r}. "
                "Refusing to resume. Remove the checkpoint or use a clean "
                "--output.")


# -- Outputs ------------------------------------------------------------------

def _emit_outputs(sampler, args, out: Path, tag=None):
    """Reweight + write checkpoint/traj (M1 order) and the derived outputs.

    ``tag``: None -> canonical (final) filenames; int N -> step-tagged
    ``*.step{N}.*`` provisional convergence snapshots (spec m2).
    """
    suffix = "" if tag is None else f".step{tag}"
    name = str(tag) if tag is not None else f"final(step {sampler.step})"
    print(f"\n  [emit] step-tag={name}: reweighting + writing outputs...")

    e_centers, dz_centers, ln_g, H, accessible = sampler.g_of_E_dZ()
    temps = [float(t) for t in args.temperatures.split(",") if t.strip()]
    rows = reweight_2d(
        sampler.ensemble_rows, ln_g, e_centers, dz_centers,
        sampler.e_min, sampler.e_width, sampler.dz_min, sampler.dz_width,
        sampler.n_atoms, temps, flat_island_spread_aa=args.flat_island_spread)

    # 1) geometries FIRST, then checkpoint.json = authoritative commit (M1)
    traj_path = out / TRAJ_NAME
    _atomic_write_traj(sampler, traj_path)
    cp_path = out / CHECKPOINT_NAME
    _atomic_write_json(cp_path, {
        "config": _config_header(sampler, args, sampler.dz_min,
                                 sampler.dz_max, args.dataset),
        "state": sampler.state_dict(),
    })

    # 2) derived outputs (g / delta-z / ensemble + PNGs), step-tagged or canonical
    dzc, emin = E_min_curve(ln_g, e_centers, dz_centers, accessible)
    payload = {
        "e_min": sampler.e_min, "e_max": sampler.e_max,
        "n_e_bins": sampler.n_e_bins,
        "e_edges": (sampler.e_min + sampler.e_width *
                    np.arange(sampler.n_e_bins + 1)).tolist(),
        "dz_min": sampler.dz_min, "dz_max": sampler.dz_max,
        "n_dz_bins": sampler.n_dz_bins,
        "dz_edges": (sampler.dz_min + sampler.dz_width *
                     np.arange(sampler.n_dz_bins + 1)).tolist(),
        "ln_g": ln_g.tolist(),
        "H": H.tolist(),
        "accessible": accessible.tolist(),
        "E_min_dZ": emin.tolist(),
        "n_bins_visited": int((H > 0).sum()),
        "n_accessible": int(accessible.sum()),
        "flatness_criterion": args.flatness_criterion,
        "switched_to_1_over_t": sampler.switched_to_1_over_t,
        "stages": sampler.stage,
        "step": sampler.step,
        "rng": args.rng,
        "temperatures_K": temps,
        "n_atoms": sampler.n_atoms,
    }
    _atomic_write_json(out / f"g_of_E_dZ{suffix}.json", payload)

    with open(out / f"g_of_E_dZ{suffix}.csv", "w") as f:
        f.write("E_center_eV_per_atom,dZ_center_A,i,j,ln_g,H,visited\n")
        for i in range(sampler.n_e_bins):
            for j in range(sampler.n_dz_bins):
                f.write(f"{e_centers[i]:.6f},{dz_centers[j]:.6f},{i},{j},"
                        f"{ln_g[i, j]:.6f},{H[i, j]},"
                        f"{int(accessible[i, j])}\n")
    print(f"  Wrote g_of_E_dZ{suffix}.csv")

    with open(out / f"delta_z_distribution{suffix}.csv", "w") as f:
        f.write("T_K,mean_dZ_A,std_dZ_A,dF_flat_island_eV\n")
        for r in rows:
            f.write(f"{r['T_K']:.1f},{r['mean_dZ_A']:.6f},"
                    f"{r['std_dZ_A']:.6f},{r['dF_flat_island_eV']:.6f}\n")
    print(f"  Wrote delta_z_distribution{suffix}.csv")

    ens = []
    for (E_total, E_rel, dz, i, j, lab) in sampler.ensemble_rows:
        ens.append({"E_total_eV": E_total, "E_rel_eV_per_atom": E_rel,
                    "dZ_A": dz, "E_bin": i, "dZ_bin": j, "label": lab})
    _atomic_write_json(out / f"ensemble{suffix}.json", ens)
    print(f"  Wrote ensemble{suffix}.json ({len(ens)} accepted structures)")

    _plot_heatmap(e_centers, dz_centers, ln_g, accessible, out, suffix)
    _plot_dz_distribution(rows, out, suffix)

    print("Island-height distribution <dZ(T)>:")
    print("  T(K)     <dZ>(A)    std(A)   dF_flat-island(eV)")
    for r in rows:
        print(f"  {r['T_K']:6.1f}  {r['mean_dZ_A']:9.4f}  "
              f"{r['std_dZ_A']:7.4f}  {r['dF_flat_island_eV']:9.4f}")
    return rows


def _plot_heatmap(e_centers, dz_centers, ln_g, accessible, out, suffix=""):
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
    fig.savefig(str(out / f"g_of_E_dZ{suffix}.png"), dpi=150)
    plt.close(fig)
    print(f"  Wrote g_of_E_dZ{suffix}.png")


def _plot_dz_distribution(rows, out, suffix=""):
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
    fig.savefig(str(out / f"delta_z_distribution{suffix}.png"), dpi=150)
    plt.close(fig)
    print(f"  Wrote delta_z_distribution{suffix}.png")


# -- Driver -------------------------------------------------------------------

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
                   help="WL MC steps (absolute total target; on resume only the "
                        "remaining steps are run)")
    p.add_argument("--checkpoint-interval", type=int, default=100,
                   help="Save a checkpoint every N MC steps (default 100)")
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

    # --- 4. Resume or fresh run ---------------------------------------------
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    cp_path = out / CHECKPOINT_NAME

    ckpt = _try_load_checkpoint(cp_path)
    if ckpt is not None:
        state, header = ckpt
        _validate_config(header, sampler, args, dz_min, dz_max, args.dataset)
        sampler.load_state(state)
        # rebuild accepted geometries from ensemble.traj (M1: traj-first/commit)
        traj_path = out / TRAJ_NAME
        if traj_path.exists():
            from ase.io import read as ase_read
            structs = list(ase_read(str(traj_path), index=":"))
            n_rows = len(sampler.ensemble_rows)
            if len(structs) > n_rows:
                structs = structs[:n_rows]  # commit point = checkpoint rows
            elif len(structs) < n_rows:
                print(f"[WARN] ensemble.traj has {len(structs)} structures but "
                      f"checkpoint has {n_rows} rows (inconsistent pair); scalar "
                      f"rows are authoritative, geometry will be short.")
            sampler.ensemble_structs = structs
        else:
            sampler.ensemble_structs = []
        loaded_step = sampler.step
        print(f"\n[RESUME] loaded checkpoint at step {loaded_step}; "
              f"{len(sampler.ensemble_rows)} accepted structures, "
              f"{int(sampler.accessible.sum())} accessible cells. "
              f"Reference pass + init SKIPPED.")
    else:
        print("\n[FRESH RUN] no usable checkpoint; running reference pass + init.")
        sampler.initialize()
        loaded_step = 0

    # --- 5. Run --------------------------------------------------------------
    # M2: --mc-steps is an absolute total target.
    remaining = args.mc_steps - loaded_step
    if remaining < 0:
        raise SystemExit(
            f"[ABORT] --mc-steps {args.mc_steps} < checkpoint step "
            f"{loaded_step}. Refusing to run. Raise --mc-steps or remove the "
            f"checkpoint / use a clean --output.")

    if remaining > 0:
        print(f"[RUN] sampling {remaining} more steps toward "
              f"--mc-steps={args.mc_steps} "
              f"(checkpoint every {args.checkpoint_interval} steps)...")
        def _checkpoint_cb(s):
            _emit_outputs(s, args, out, tag=s.step)
        sampler.run(n_steps=remaining,
                    progress_every=max(args.check_interval, 1),
                    checkpoint_interval=args.checkpoint_interval,
                    checkpoint_callback=_checkpoint_cb)
    else:
        print(f"[DONE] --mc-steps {args.mc_steps} already reached by the "
              f"checkpoint (step {loaded_step}); skipping sampling, re-deriving "
              f"final outputs from the loaded state.")

    # --- 6. Final (canonical) outputs ---------------------------------------
    _emit_outputs(sampler, args, out, tag=None)
    print(f"\nDone. Results (canonical + per-checkpoint snapshots) in {out}")


if __name__ == "__main__":
    main()
