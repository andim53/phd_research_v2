"""DFT re-relaxation of the selected low-force distinct structures (GPAW).

Reads relaxation/selected/manifest.csv, and for each structure:
  - loads the geometry,
  - freezes the substrate (template_indices from the manifest),
  - attaches a GPAW calculator with the SAME settings as the search runs
    (LCAO/dzp, PBE, kpts (1,1,1), Fermi-Dirac 0.05 eV, spinpol, hund),
  - relaxes with ASE BFGS to fmax (default 0.05 eV/A),
  - writes the relaxed structure + a results CSV row.

Crash-safe: structures whose relaxed output already exists are skipped (re-run safe).

Run on HPC (gpaw_env) via relaxation/job_relax.sh, or directly:
  python relax.py --manifest relaxation/selected/manifest.csv --fmax 0.05
"""
import argparse, os, csv, sys, time
import numpy as np
from ase.io import read, write
from ase.constraints import FixAtoms
from ase.optimize import BFGS


def get_calc(txt, **over):
    from gpaw import GPAW, FermiDirac, Mixer
    kw = dict(
        mode='lcao', basis='dzp', xc='PBE',
        mixer=Mixer(backend='pulay', beta=0.05, nmaxold=5, weight=100),
        convergence={'energy': 1e-4, 'density': 1e-3, 'eigenstates': 1e-3},
        kpts=(1, 1, 1), symmetry='off', nbands='nao', maxiter=100,
        occupations=FermiDirac(0.05), hund=True, spinpol=True, txt=txt,
    )
    kw.update(over)
    return GPAW(**kw)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', default='relaxation/selected/manifest.csv')
    ap.add_argument('--outdir', default='relaxation/relaxed')
    ap.add_argument('--fmax', type=float, default=0.05)
    ap.add_argument('--max-steps', type=int, default=300)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.manifest)))
    results_path = os.path.join(args.outdir, 'relax_results.csv')
    done = set()
    if os.path.exists(results_path):
        done = {r['file'] for r in csv.DictReader(open(results_path))}
    os.makedirs(args.outdir, exist_ok=True)

    new_file = not os.path.exists(results_path)
    fout = open(results_path, 'a', newline='')
    w = csv.DictWriter(fout, fieldnames=['file','system','E_initial','E_final',
                                         'max_force_final','n_steps','converged'])
    if new_file:
        w.writeheader()

    for r in rows:
        if r['file'] in done:
            print(f"skip (done): {r['file']}")
            continue
        src = os.path.join('relaxation/selected', r['file'])
        atoms = read(src)
        tinds = [int(x) for x in r['template_indices'].split(';')] if r['template_indices'] else []
        if tinds:
            atoms.set_constraint(FixAtoms(indices=tinds))
        outdir_sys = os.path.join(args.outdir, r['system'])
        os.makedirs(outdir_sys, exist_ok=True)
        base = os.path.splitext(os.path.basename(r['file']))[0]
        txt = os.path.join(outdir_sys, f'{base}_gpaw.txt')

        E0 = float(r['E_total'])
        print(f"relaxing {r['file']} (E0={E0:.3f} eV, {len(atoms)} atoms, "
              f"{len(tinds)} frozen)")
        atoms.calc = get_calc(txt)
        dyn = BFGS(atoms, logfile=os.path.join(outdir_sys, f'{base}_opt.log'))
        t0 = time.time()
        try:
            dyn.run(fmax=args.fmax, steps=args.max_steps)
        except Exception as e:
            print(f"  ERROR on {r['file']}: {e}", file=sys.stderr)
            continue
        fmax_final = float(np.linalg.norm(atoms.get_forces(), axis=1).max())
        Ef = float(atoms.get_potential_energy())
        conv = fmax_final <= args.fmax + 1e-6
        write(os.path.join(outdir_sys, f'{base}_relaxed.xyz'), atoms)
        write(os.path.join(outdir_sys, f'{base}_relaxed.traj'), atoms)
        w.writerow({'file': r['file'], 'system': r['system'], 'E_initial': f'{E0:.6f}',
                    'E_final': f'{Ef:.6f}', 'max_force_final': f'{fmax_final:.4f}',
                    'n_steps': dyn.get_number_of_steps(), 'converged': conv})
        fout.flush()
        print(f"  done: E {E0:.3f} -> {Ef:.3f} eV, max|F|={fmax_final:.4f}, "
              f"{dyn.get_number_of_steps()} steps, {time.time()-t0:.0f}s, converged={conv}")

    fout.close()
    print(f"Results -> {results_path}")


if __name__ == '__main__':
    main()
