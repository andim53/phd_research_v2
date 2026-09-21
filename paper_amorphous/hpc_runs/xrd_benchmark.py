"""xrd_benchmark.py — simulate powder XRD of the amorphous minima vs the reference.

Bridges the EXISTING XRD pipeline (reused as-is, agox-xrd-crystallinity skill) so our
SHC-selected amorphous minima (and the 0%-P reference) get a simulated powder XRD on a
common concentration axis for the comparison against the reference paper's experimental
XRD trend (I(220)/I(111) 0.33->3.14, peak shift, amorphization — spec G8 S4).

Pipeline (env split, unchanged from the source project):
  Stage 1 (agox_v2):  write each structure to a CIF.
  Stage 2 (pymat_xrd): XRDCalculator("CuKa") + crystallinity index, per composition.
This script only writes the CIFs + a manifest; the actual XRD is produced by the
canonical `_run/0_lcb/2_analysist/scripts/xrd_simulate_crystallinity.py` /
`xrd_groundstate_compare.py`. It is a thin adapter so our trajs can be fed in — no new
XRD engine.

Usage (agox_v2):
  PY_A=/home/think/miniconda3/envs/agox_v2/bin/python
  $PY_A xrd_benchmark.py --trajs opt_novel_*.traj ref_0P_gmin.traj --outdir ./xrd_bench

Then (pymat_xrd) run the canonical Stage-2 script on the emitted manifest/CIFs.
"""
from __future__ import annotations

__version__ = "1.0.0"

import argparse
import json
import os
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trajs", nargs="*", required=True)
    ap.add_argument("--outdir", default="xrd_bench")
    args = ap.parse_args()

    from ase.io import read, write

    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    manifest = {"kind": "amorphous-vs-ref XRD benchmark inputs",
                "description": {
                    "kind": "CIF manifest for the existing agox-xrd-crystallinity "
                            "pipeline (Stage 2 in pymat_xrd).",
                    "method": "write selected/relaxed amorphous Pt-P minima + 0%-P "
                              "reference to CIF; XRD via pymatgen CuKa in the canonical "
                              "xrd_simulate_crystallinity.py / xrd_groundstate_compare.py.",
                    "units": "none (CIF)", "note": "reference paper: I220/I111 0.33->3.14 "
                              "and peak shift as P dose rises (Fukuma S4)."},
                "structures": []}
    for tr in args.trajs:
        atoms_list = read(tr, index=":")
        for i, a in enumerate(atoms_list):
            label = f"{Path(tr).stem}_{i}"
            cif = Path(args.outdir) / f"{label}.cif"
            write(str(cif), a)
            manifest["structures"].append({
                "label": label, "traj": tr, "index": i,
                "formula": a.get_chemical_formula(),
                "cif": str(cif),
            })
    with open(Path(args.outdir) / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"wrote {len(manifest['structures'])} CIFs -> {args.outdir}/manifest.json")
    print("Next (pymat_xrd): "
          "$PY_X xrd_simulate_crystallinity.py --manifest <dir>/manifest.json "
          "--outdir <dir> [--json]")


if __name__ == "__main__":
    main()
