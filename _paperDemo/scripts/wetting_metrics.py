"""Wetting-metric analysis for Fe/MgO vs Fe-B/MgO structure-search databases.

Operationalizes 'wetting of Fe on MgO' from AGOX global-optimization candidates:

  For each candidate structure, per deposition-layer atom:
  - contact   : atom has >=1 O neighbor within d_cut (interfacial bonding)
  - z-height  : height of atom above the MgO substrate top plane (z0)
  Per-structure aggregates over Fe:
  - n_fe_contact      : number of Fe atoms bonded to the MgO interface
  - contact_fraction  : n_fe_contact / total Fe in deposition layer
  - film_roughness    : std of Fe z-positions (lower = flatter film = better wetting)
  - film_height_mean  : mean Fe z above interface
  - film_spread       : Fe z span (max - min)
  - coverage          : fraction of lateral (x,y) grid cells covered by low-lying Fe
                        (within 'film_window' of the lowest Fe) -- 2D wetting footprint
  Per-structure, for febmgo:
  - b_contact  : number of B atoms bonded to the MgO interface (O within d_cut)
  - b_z_mean   : mean B height above interface (interface-segregated vs in-film)

Output: per-structure CSV rows + aggregate summary (mean/std across seeds) per system.
Structures are windowed to a low-energy basin (rel_energy <= e_window eV above the
system's global minimum) to exclude relaxation artifacts / unphysical high-energy hits.

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/wetting_metrics.py
"""
import matplotlib; matplotlib.use('Agg')
import numpy as np, glob, os, csv, argparse
from agox.databases import Database

D_CUT = 2.6          # Angstrom; Fe-O / B-O bonding cutoff for interfacial contact
COVERAGE_DXY = 1.2   # Angstrom lateral bin for 2D coverage footprint
COVERAGE_WINDOW = 1.5  # Angstrom; Fe within this of the lowest-Fe plane counts as 'low'


def load_cands(dbp):
    db = Database(filename=dbp)
    db.restore_to_memory()
    return db.get_all_candidates()


def substrate_top_z(atoms, sym):
    """z0 = max z of substrate (Mg/O) atoms = interface plane."""
    mask = (sym == 'Mg') | (sym == 'O')
    return atoms.get_positions()[mask, 2].max()


def fe_distance_to_O(pos, opos):
    """min distance from each atom to any O atom (no PBC in z, in-plane PBC ignored
    for simplicity -- all relevant structures keep Fe within the lateral cell)."""
    d = np.linalg.norm(pos[:, None, :] - opos[None, :, :], axis=2)
    return d.min(axis=1)


def structure_metrics(atoms, is_feb):
    sym = np.array(atoms.get_chemical_symbols())
    pos = atoms.get_positions()
    z0 = substrate_top_z(atoms, sym)

    omask = sym == 'O'
    opos = pos[omask]
    result = {'z0': z0}

    for sp in ['Fe', 'B']:
        if sp not in sym:
            continue
        idx = np.where(sym == sp)[0]
        p = pos[idx]
        z = p[:, 2] - z0
        dO = fe_distance_to_O(p, opos)
        n_contact = int((dO < D_CUT).sum())
        result[f'{sp}_n'] = len(idx)
        result[f'{sp}_contact'] = n_contact
        result[f'{sp}_contact_frac'] = n_contact / len(idx) if len(idx) else np.nan
        result[f'{sp}_roughness'] = float(z.std()) if len(idx) > 1 else 0.0
        result[f'{sp}_height_mean'] = float(z.mean())
        result[f'{sp}_spread'] = float(z.max() - z.min()) if len(idx) else 0.0

    # lateral coverage of the Fe wetting footprint (2D)
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
            nx = int(np.ceil((xy[:, 0].max() - xmin) / COVERAGE_DXY))
            ny = int(np.ceil((xy[:, 1].max() - ymin) / COVERAGE_DXY))
            nx = max(nx, 1); ny = max(ny, 1)
            gx = ((xy[:, 0] - xmin) / COVERAGE_DXY).astype(int).clip(0, nx - 1)
            gy = ((xy[:, 1] - ymin) / COVERAGE_DXY).astype(int).clip(0, ny - 1)
            grid = np.zeros((nx, ny), dtype=bool)
            grid[gx, gy] = True
            result['fe_coverage'] = float(grid.sum() / (nx * ny))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--e-window', type=float, default=3.0,
                    help='keep structures within this eV of global min')
    ap.add_argument('--out', default='analysis/wetting_metrics.csv')
    args = ap.parse_args()

    os.makedirs('analysis', exist_ok=True)
    rows = []
    for system, is_feb in [('femgo', False), ('febmgo', True)]:
        dbs = sorted(glob.glob(f'data/{system}/seed_*/1_db/db_*.db'))
        # global min across all seeds in this system
        emins = []
        allc = []
        for dbp in dbs:
            for c in load_cands(dbp):
                emins.append(c.get_potential_energy())
                allc.append((c, dbp))
        gmin = min(emins)
        n_kept = 0
        for c, dbp in allc:
            rel = c.get_potential_energy() - gmin
            if rel > args.e_window:
                continue
            n_kept += 1
            m = structure_metrics(c, is_feb)
            m['system'] = system
            m['rel_energy'] = rel
            m['E_total'] = c.get_potential_energy()
            m['seed'] = os.path.basename(os.path.dirname(os.path.dirname(dbp)))
            rows.append(m)
        print(f"{system}: {len(allc)} cands, {n_kept} within {args.e_window} eV of gmin={gmin:.2f}")

    cols = ['system','seed','E_total','rel_energy','Fe_n','Fe_contact','Fe_contact_frac',
            'Fe_roughness','Fe_height_mean','Fe_spread','fe_coverage']
    if any('B_n' in r for r in rows):
        cols += ['B_n','B_contact','B_contact_frac','B_roughness','B_height_mean','B_spread']
    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # aggregate summary
    print("\n=== Aggregate (mean +- std across candidate structures) ===")
    for system in ['femgo','febmgo']:
        rr = [r for r in rows if r['system'] == system]
        if not rr:
            continue
        print(f"\n{system} (n={len(rr)})")
        for k in ['Fe_contact_frac','Fe_roughness','Fe_height_mean','Fe_spread','fe_coverage']:
            v = np.array([r[k] for r in rr], dtype=float)
            print(f"  {k:18s}: {v.mean():.3f} +- {v.std():.3f}")
        if any('B_contact_frac' in r for r in rr):
            v = np.array([r.get('B_contact_frac', np.nan) for r in rr], dtype=float)
            print(f"  {'B_contact_frac':18s}: {np.nanmean(v):.3f} +- {np.nanstd(v):.3f}")

    print(f"\nWrote {len(rows)} rows to {args.out}")


if __name__ == '__main__':
    main()
