"""Wetting-metric analysis for Fe/MgO vs Fe-B/MgO AGOX/GOFEE structure-search DBs.

Context: AGOX global optimization (GOFEE surrogate + LCB) finds the global-minimum
structure of each system. This script selects candidate structures by RELATIVE ENERGY
PER ATOM, normalizing each system's global minimum to 0 eV/atom:

    dE/N  =  (E_i - E_globalmin) / N_atoms        [eV/atom],  min -> 0

and reports the GEOMETRIC wetting metrics (the paper's focus) within that energy
window. Per-atom normalization makes the Fe/MgO (75 atoms) vs Fe-B/MgO (78 atoms)
energy windows directly comparable (an absolute eV window is not).

Wetting metrics (per candidate, computed from atomic positions):
  Fe_contact_frac : fraction of Fe with an O within D_CUT (interfacial bonding)
  Fe_roughness    : std of Fe z-positions above the MgO surface (lower = flatter film)
  Fe_height_mean  : mean Fe z above the MgO interface plane
  fe_coverage     : fraction of lateral (x,y) grid covered by low-lying Fe (2D footprint)
  B_contact_frac  : fraction of B with an O within D_CUT (Febmgo only)

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/wetting_metrics.py \
      --e-window-per-atom 0.05
"""
import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os, csv, argparse
from agox.databases import Database

D_CUT = 2.6            # Angstrom; Fe-O / B-O bonding cutoff for interfacial contact
COVERAGE_DXY = 1.2     # Angstrom lateral bin for 2D coverage footprint
COVERAGE_WINDOW = 1.5  # Angstrom; Fe within this of the lowest-Fe plane = 'low'


def load_cands(dbp):
    db = Database(filename=dbp)
    db.restore_to_memory()
    return db.get_all_candidates()


def substrate_top_z(atoms, sym):
    """z0 = max z of substrate (Mg/O) atoms = interface plane."""
    mask = (sym == 'Mg') | (sym == 'O')
    return atoms.get_positions()[mask, 2].max()


def min_dist_to_O(pos, opos):
    """min distance from each atom to any O atom."""
    d = np.linalg.norm(pos[:, None, :] - opos[None, :, :], axis=2)
    return d.min(axis=1)


def structure_metrics(atoms):
    sym = np.array(atoms.get_chemical_symbols())
    pos = atoms.get_positions()
    n_atoms = len(atoms)
    z0 = substrate_top_z(atoms, sym)
    opos = pos[sym == 'O']

    result = {'n_atoms': n_atoms, 'z0': z0}
    for sp in ['Fe', 'B']:
        if sp not in sym:
            continue
        idx = np.where(sym == sp)[0]
        p = pos[idx]
        z = p[:, 2] - z0
        dO = min_dist_to_O(p, opos)
        n_contact = int((dO < D_CUT).sum())
        result[f'{sp}_n'] = len(idx)
        result[f'{sp}_contact'] = n_contact
        result[f'{sp}_contact_frac'] = n_contact / len(idx) if len(idx) else np.nan
        result[f'{sp}_roughness'] = float(z.std()) if len(idx) > 1 else 0.0
        result[f'{sp}_height_mean'] = float(z.mean())
        result[f'{sp}_spread'] = float(z.max() - z.min()) if len(idx) else 0.0

    if 'Fe' in sym:
        idx = np.where(sym == 'Fe')[0]
        p = pos[idx]
        z = p[:, 2]
        zlow = z.min()
        low = p[np.abs(z - zlow) <= COVERAGE_WINDOW]
        if len(low) == 0:
            result['fe_coverage'] = 0.0
        else:
            xy = low[:, :2]
            xmin, ymin = xy.min(axis=0) - 0.01
            nx = max(int(np.ceil((xy[:, 0].max() - xmin) / COVERAGE_DXY)), 1)
            ny = max(int(np.ceil((xy[:, 1].max() - ymin) / COVERAGE_DXY)), 1)
            gx = ((xy[:, 0] - xmin) / COVERAGE_DXY).astype(int).clip(0, nx - 1)
            gy = ((xy[:, 1] - ymin) / COVERAGE_DXY).astype(int).clip(0, ny - 1)
            grid = np.zeros((nx, ny), dtype=bool)
            grid[gx, gy] = True
            result['fe_coverage'] = float(grid.sum() / (nx * ny))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--e-window-per-atom', type=float, default=0.05,
                    help='keep structures with dE/N <= this (eV/atom); global min = 0')
    ap.add_argument('--out', default='analysis/wetting_metrics.csv')
    args = ap.parse_args()

    os.makedirs('analysis', exist_ok=True)
    rows = []
    for system in ['femgo', 'febmgo']:
        dbs = sorted(glob.glob(f'data/{system}/seed_*/1_db/db_*.db'))
        emins, allc = [], []
        for dbp in dbs:
            for c in load_cands(dbp):
                emins.append(c.get_potential_energy())
                allc.append((c, dbp))
        gmin = min(emins)
        n_kept = 0
        for c, dbp in allc:
            n_atoms = len(c)
            dE_per_atom = (c.get_potential_energy() - gmin) / n_atoms
            if dE_per_atom > args.e_window_per_atom:
                continue
            n_kept += 1
            m = structure_metrics(c)
            m['system'] = system
            m['dE_per_atom'] = dE_per_atom
            m['E_total'] = c.get_potential_energy()
            m['seed'] = os.path.basename(os.path.dirname(os.path.dirname(dbp)))
            rows.append(m)
        print(f"{system}: {len(allc)} cands, {n_kept} within {args.e_window_per_atom} "
              f"eV/atom of gmin={gmin:.2f} eV")

    cols = ['system', 'seed', 'E_total', 'dE_per_atom', 'n_atoms',
            'Fe_n', 'Fe_contact', 'Fe_contact_frac', 'Fe_roughness',
            'Fe_height_mean', 'Fe_spread', 'fe_coverage']
    if any('B_n' in r for r in rows):
        cols += ['B_n', 'B_contact', 'B_contact_frac', 'B_roughness', 'B_height_mean', 'B_spread']

    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print("\n=== Aggregate (mean +- std across candidates; global min = 0 eV/atom) ===")
    for system in ['femgo', 'febmgo']:
        rr = [r for r in rows if r['system'] == system]
        if not rr:
            continue
        print(f"\n{system} (n={len(rr)})")
        dE = np.array([r['dE_per_atom'] for r in rr], float)
        print(f"  dE_per_atom window used: <= {args.e_window_per_atom} eV/atom")
        for k in ['Fe_contact_frac', 'Fe_roughness', 'Fe_height_mean', 'Fe_spread', 'fe_coverage']:
            v = np.array([r[k] for r in rr], dtype=float)
            print(f"  {k:18s}: {v.mean():.3f} +- {v.std():.3f}")
        if any('B_contact_frac' in r for r in rr):
            v = np.array([r.get('B_contact_frac', np.nan) for r in rr], dtype=float)
            print(f"  {'B_contact_frac':18s}: {np.nanmean(v):.3f} +- {np.nanstd(v):.3f}")

    print(f"\nWrote {len(rows)} rows to {args.out}")


if __name__ == '__main__':
    main()
