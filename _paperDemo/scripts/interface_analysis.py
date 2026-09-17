"""Interface Fe analysis: (1) true-interface PDOS, (2) Fe-on-O registry.

Replaces the arbitrary bottom-8/top-8 split. Structure of the analysis:

  Interface Fe  := Fe with a nearest O within CONTACT_CUT (2.8 A) -> actually at the MgO.
  Non-interface := the remaining Fe (no O contact).
  Registry      := for each interface Fe, is its in-plane nearest substrate atom O or Mg,
                   and what is the in-plane offset (0 = directly atop)?

Data: femgo DOS (dos_seed_4 = FLAT monolayer, dos_seed_3 = ISLAND), matched Fe-dz2 / O-pz.

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/interface_analysis.py
"""
import matplotlib; matplotlib.use('Agg')
import numpy as np, csv, re, os
from ase.io import read

CONTACT_CUT = 2.8      # A; Fe-O contact cutoff defining "at the interface"
DBAND_WINDOW = (-5.0, 3.0)

CASES = {
    'FLAT':   dict(csv='data/dos_femgo_flatngs/dos_seed_4.csv', xsf='data/dos_femgo_flatngs/4.xsf'),
    'ISLAND': dict(csv='data/dos_femgo_flatngs/dos_seed_3.csv', xsf='data/dos_femgo_flatngs/3.xsf'),
}


def load_atom_pdos(path):
    rows = list(csv.DictReader(open(path)))
    E = np.array([float(r['energy']) for r in rows])
    fe = {}
    for c in rows[0]:
        m = re.match(r'^Fe(\d+)_dz2_(up|down)$', c)
        if m:
            fe.setdefault(int(m.group(1)), {})[m.group(2)] = np.array([float(r[c]) for r in rows])
    return E, fe


def analyze_structure(xsf):
    a = read(xsf); sym = np.array(a.get_chemical_symbols()); pos = a.get_positions()
    fe_idx = np.where(sym == 'Fe')[0]
    o_idx = np.where(sym == 'O')[0]
    mg_idx = np.where(sym == 'Mg')[0]
    opos, mgpos = pos[o_idx], pos[mg_idx]
    info = {}
    for i in fe_idx:
        p = pos[i]
        dO = np.linalg.norm(opos - p, axis=1).min()
        dMg = np.linalg.norm(mgpos - p, axis=1).min()
        # in-plane nearest substrate atom
        io = np.argmin(np.linalg.norm(opos[:, :2] - p[:2], axis=1))
        im = np.argmin(np.linalg.norm(mgpos[:, :2] - p[:2], axis=1))
        off_O = np.linalg.norm(opos[io, :2] - p[:2])
        off_Mg = np.linalg.norm(mgpos[im, :2] - p[:2])
        atop = 'O' if off_O < off_Mg else 'Mg'
        info[i] = dict(z=p[2], dO=dO, dMg=dMg, atop=atop,
                       offset=min(off_O, off_Mg), on_contact=dO < CONTACT_CUT)
    return info


def group_metrics(E, fe, indices):
    if not indices:
        return None
    up = sum(fe[i]['up'] for i in indices)
    dn = sum(fe[i]['down'] for i in indices)
    g = up + dn
    m = (E >= DBAND_WINDOW[0]) & (E <= DBAND_WINDOW[1])
    area = np.trapz(g[m], E[m])
    c = np.trapz(E[m] * g[m], E[m]) / area
    w = np.sqrt(np.trapz((E[m] - c) ** 2 * g[m], E[m]) / area)
    return c, w, area, up, dn


def main():
    os.makedirs('analysis', exist_ok=True)
    rows_out = []
    print(f"--- Interface definition: nearest-O < {CONTACT_CUT} A ---")
    for name, cfg in CASES.items():
        E, fe = load_atom_pdos(cfg['csv'])
        info = analyze_structure(cfg['xsf'])
        iface = [i for i in info if info[i]['on_contact']]
        non = [i for i in info if not info[i]['on_contact']]

        # --- registry ---
        n_on_O = sum(1 for i in iface if info[i]['atop'] == 'O')
        n_on_Mg = sum(1 for i in iface if info[i]['atop'] == 'Mg')
        offsets = [info[i]['offset'] for i in iface]
        dOs = [info[i]['dO'] for i in iface]
        print(f"\n=== {name} ===")
        print(f"  interface Fe (dO<{CONTACT_CUT}): {len(iface)} / {len(info)}")
        print(f"  of those, atop O: {n_on_O}, atop Mg: {n_on_Mg}")
        print(f"  mean in-plane offset: {np.mean(offsets):.3f} A (0 = directly atop)")
        print(f"  mean Fe-O distance: {np.mean(dOs):.3f} A")

        # --- PDOS by group ---
        for gname, idx in [('interface', iface), ('non-interface', non), ('all', list(info))]:
            r = group_metrics(E, fe, idx)
            if r is None:
                continue
            c, w, area, up, dn = r
            mdO = float(np.mean([info[i]['dO'] for i in idx]))
            moff = float(np.mean([info[i]['offset'] for i in idx]))
            print(f"    {gname:14s} n={len(idx):3d}  d-centre={c:+.3f} eV  width={w:.3f}  int={area:.2f}"
                  f"  d_Fe-O={mdO:.3f}  offset={moff:.3f}")
            rows_out.append([name, gname, len(idx), f"{c:.4f}", f"{w:.4f}", f"{area:.4f}",
                             f"{mdO:.4f}", f"{moff:.4f}"])
        rows_out.append([name, 'REGISTRY', len(iface), f"on_O={n_on_O}", f"on_Mg={n_on_Mg}",
                         f"mean_offset={np.mean(offsets):.3f}",
                         f"{np.mean(dOs):.4f}", f"{np.mean(offsets):.4f}"])

    with open('analysis/interface_analysis.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['case','group','n','d_band_centre_eV','d_band_width_eV','integral',
                    'mean_nearest_d_FeO_A','mean_inplane_offset_A'])
        w.writerows(rows_out)
    print('\nwrote analysis/interface_analysis.csv')


if __name__ == '__main__':
    main()
