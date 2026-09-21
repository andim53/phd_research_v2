"""main.py — Run B: FLAPW spin Hall conductivity (SHC) stage for amorphous Pt(P).

Adapted from tmp/SHC Calculation/HEA_SHC_Auto_Python_FLAPW/main.py. Runs the full
FLAPW chain — ground-state SCF -> SOC restart -> optics -> xoptics (spin Hall
conductivity) -> FLclean — for every structure in a traj, then PARSES the SHC
conductivity (in (ohm cm)^-1) from the xoptics output into a per-structure
JSON/CSV so paper1's placeholder SHC section can be filled later.

CALC DIR (self-contained) — run main.py from a directory holding ALL of:
  flapw.py          standalone ASE FLAPW calculator. `from flapw import FLAPW`
                    works because flapw.py sits in the CWD (it is NOT a pip
                    package). Do not move it into site-packages.
  README_MT-default read by flapw.py write_lapwin from CWD.
  pflapw            FLAPW SCF/SOC binary (run as ./pflapw). Large HPC build.
  opt/              xoptics binary + opticsin (read by prepare_optics).
The small source/config files (flapw.py, README_MT-default, opt/opticsin) are
committed in this directory; pflapw and opt/xoptics are gitignored binaries staged
by ./setup_calc.sh from the FLAPW calc source before submit (spec G8 clarification).

Env: gpaw_env on HPC (has gpaw + agox; FLAPW `pflapw` invoked under this env —
spec C2, `flapw_2` retired). MPI via mpiexec; proc count matches the pjsub header.

Input traj: path from env TRAJ_FILE or `--traj` CLI (default opt_novel_<leaf>.traj).
One pjsub submission per leaf traj (spec M3) — 4 amorphous leaves + 1 reference.

Units: SHC parsed and reported in (ohm cm)^-1. Note (from the example opticsin):
  spin Hall conductivity: 10^15 [1/s] = 1112.56 (ohm cm)^-1  (flapw >= 4.16)
  before flapw-4.16: 556.28. FLAPW 4.58 here => 1112.56/conversion.
The xoptics output format is assumed readable from the example files; exact fields are
confirmed against the first real run (spec G7). This parser targets the common
xoptics/optics output block values; adjust FIELD patterns once a run has produced output.
"""
from __future__ import annotations

__version__ = "1.0.0"

import argparse
import json
import os
import pickle  # noqa: F401  (kept from example import surface)
import re
import shutil
import traceback
from pathlib import Path

from ase.io import read, write
from flapw import FLAPW


# ============================================================================
# Configuration
# ============================================================================
TRAJ_ENV = "TRAJ_FILE"
DEFAULT_TRAJ = "opt_novel_1_3x3_20P.traj"  # one SHC pjsub per leaf traj (spec M3)
MPI = True
BIN = "pflapw" if MPI else "flapw"
START = 0
BASE_LATTICE_SCALE = 1.00
MAX_LATTICE_SCALE = 1.20
LATTICE_STEP = 0.01
NPROCS = 24                       # matches pjsub --mpi proc=24 (spec C2)
KPTS = (2, 2, 2)
SOCKPTS = (10, 10, 10)

# SHC units conversion (from example opticsin note; flapw >= 4.16)
CONV_1_per_s_to_ohmcm = 1.0 / 1112.56   # 10^15 1/s = 1112.56 (ohm cm)^-1


def parse_shc_conductivity(workdir: Path):
    """Extract spin Hall conductivity from xoptics output.

    Returns a dict of parsed fields (best-effort). Field patterns are targeted at the
    FLAPW xoptics output files (e.g. `band.out`, `lapwout`, xoptics stdout captured in
    the FLAPW run). Confirmed against a real run during the first execution (spec G7).
    """
    result = {
        "shc_ohm_per_cm": None,
        "shc_1_per_s": None,
        "source_file": None,
        "conversion_note": "flapw>=4.16: 10^15 1/s = 1112.56 (ohm cm)^-1",
    }
    # xoptics often writes conductivity tables into `lapwout` or a `.opt*/xoptics` log.
    candidates = list(workdir.glob("*")) + list(workdir.glob("**/*opt*"))
    pat = re.compile(
        r"(?i)(?:spin[ _-]?hall[ _-]?conduct|shc|sigma\s*xy|sigmaxy|conductivity)"
        r"[^\d]*([-+]?\d+(?:\.\d+)?[eE][-+]?\d+|[-\d.]+)"
    )
    for f in candidates:
        if not f.is_file():
            continue
        try:
            text = f.read_text(errors="ignore")
        except Exception:  # noqa: BLE001
            continue
        m = pat.search(text)
        if m:
            val = float(m.group(1))
            result["shc_1_per_s"] = val
            result["shc_ohm_per_cm"] = val * CONV_1_per_s_to_ohmcm
            result["source_file"] = str(f)
            break
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traj", default=os.environ.get(TRAJ_ENV, DEFAULT_TRAJ))
    ap.add_argument("--start", type=int, default=START)
    ap.add_argument("--outdir", default="shc_out")
    args = ap.parse_args()

    path_traj = Path(args.traj)
    if not path_traj.exists():
        raise SystemExit(f"TRAJ not found: {path_traj} (set {TRAJ_ENV} or --traj)")
    atoms_list = read(str(path_traj), index=":")
    Path(args.outdir).mkdir(parents=True, exist_ok=True)

    results = []
    for i, atoms in enumerate(atoms_list, start=args.start):
        formula = atoms.get_chemical_formula()
        dirname = f"{i}_{formula}"
        workdir = Path(dirname)
        workdir.mkdir(exist_ok=True)
        entry = {"index": i, "formula": formula, "directory": dirname}
        energy = None
        try:
            shutil.copy2(BIN, workdir / BIN)
            write(workdir / "atoms.xsf", atoms)

            # Phases 2-3: SCF (with lattice-scale loop for MT overlap) then SOC
            lattice_scale = BASE_LATTICE_SCALE
            while lattice_scale <= MAX_LATTICE_SCALE:
                atoms.calc = FLAPW(
                    mpi=MPI, directory=str(workdir), lattice_scale=lattice_scale,
                    nprocs=NPROCS, kpts=KPTS, sockpts=SOCKPTS,
                )
                atoms.calc.write_input(atoms)
                atoms.calc.run_flapw()
                atoms.calc.read_results()
                energy = atoms.calc.results["energy"]
                lapwout = workdir / "lapwout"
                mtoverlap = False
                if lapwout.exists():
                    mtoverlap = "MT overlap" in lapwout.read_text(errors="ignore")
                if mtoverlap:
                    lattice_scale += LATTICE_STEP
                    try:
                        atoms.calc.clean()
                    except Exception:  # noqa: BLE001
                        pass
                    continue
                break
            entry["energy_eV"] = energy

            atoms.calc.copy_scf()
            atoms.calc.prepare_soc_lapwin()
            atoms.calc.execute()

            # Phase 4: optics + xoptics (SHC)
            atoms.calc.prepare_optics()
            atoms.calc.run_xoptics()

            # Phase 5: parse SHC, then FLclean
            entry.update(parse_shc_conductivity(workdir))
            atoms.calc.copy_soc()
            atoms.calc.clean()

        except Exception as e:  # noqa: BLE001
            entry["error"] = str(e)
            traceback.print_exc()

        results.append(entry)

    # Write per-run summary JSON + CSV (SHC in (ohm cm)^-1)
    summary = {
        "traj": str(path_traj),
        "description": {
            "kind": "Run B: FLAPW SHC stage per structure.",
            "method": "SCF->SOC->optics->xoptics (flapw.py, pflapw, MPI); SHC parsed "
                      "from xoptics output.",
            "units": "energy eV; shc_ohm_per_cm in (ohm cm)^-1; shc_1_per_s in 10^15 1/s.",
            "conversion": "flapw>=4.16: 10^15 1/s = 1112.56 (ohm cm)^-1",
        },
        "structures": results,
    }
    with open(Path(args.outdir) / "shc_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    import csv
    with open(Path(args.outdir) / "shc_summary.csv", "w", newline="") as f:
        cols = ["index", "formula", "directory", "energy_eV", "shc_1_per_s",
                "shc_ohm_per_cm", "source_file", "error"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in results:
            w.writerow({c: r.get(c, "") for c in cols})

    print(f"Processed {len(results)} structures -> {args.outdir}")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
