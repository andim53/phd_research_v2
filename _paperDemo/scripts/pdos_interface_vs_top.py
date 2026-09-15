"""Per-Fe-site PDOS: interface Fe vs top-layer Fe, and vs the flat monolayer.

Tests the interpretation that island formation reduces Fe-O hybridisation:
if correct, the ISLAND's interface Fe (in contact with MgO) should look more
"flat-like" (lower d-band centre, more O-p coupling), while the ISLAND's top Fe
should look more bulk-like (higher d-band centre).

Data: femgo DOS (dos_seed_4 = FLAT monolayer, dos_seed_3 = ISLAND), matched Fe-dz2 / O-pz.
Fe groups defined by z from the corresponding XSF.

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/pdos_interface_vs_top.py
"""
import matplotlib; matplotlib.use('Agg')
import numpy as np, csv, re, os
from ase.io import read

DBAND_WINDOW = (-5.0, 3.0)
NSPLIT = 8      # bottom/top N Fe by z

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


def fe_z(xsf):
    a = read(xsf); sym = np.array(a.get_chemical_symbols()); z = a.get_positions()[:, 2]
    return {i: z[i] for i in np.where(sym == 'Fe')[0]}


def sites_metrics(E, fe, indices):
    up = sum(fe[i]['up'] for i in indices)
    dn = sum(fe[i]['down'] for i in indices)
    g = up + dn
    m = (E >= DBAND_WINDOW[0]) & (E <= DBAND_WINDOW[1])
    Ew, gw = E[m], g[m]
    area = np.trapz(gw, Ew)
    c = np.trapz(Ew * gw, Ew) / area
    w = np.sqrt(np.trapz((Ew - c) ** 2 * gw, Ew) / area)
    spin = np.trapz(up - dn, E)
    return c, w, area, spin, up, dn


def main():
    print(f"{'case/group':22s} {'nFe':>4s} {'d-cent(eV)':>11s} {'d-width':>8s} {'int':>7s} {'spinPol':>8s}")
    out = []
    curves = {}
    for name, cfg in CASES.items():
        E, fe = load_atom_pdos(cfg['csv'])
        zmap = fe_z(cfg['xsf'])
        idx_sorted = sorted(zmap, key=lambda i: zmap[i])
        groups = {'all': idx_sorted}
        if name == 'ISLAND':
            groups = {'interface (bottom)': idx_sorted[:NSPLIT],
                      'top': idx_sorted[-NSPLIT:],
                      'all': idx_sorted}
        for gname, idx in groups.items():
            c, w, area, spin, up, dn = sites_metrics(E, fe, idx)
            label = f"{name}:{gname}"
            print(f"{label:22s} {len(idx):4d} {c:11.3f} {w:8.3f} {area:7.2f} {spin:8.3f}")
            out.append([name, gname, len(idx), f"{c:.4f}", f"{w:.4f}", f"{area:.4f}", f"{spin:.4f}"])
            curves[label] = (E, up, dn)
        if name == 'FLAT':
            # flat monolayer = single interface-like layer; record as its own group too
            pass

    with open('analysis/pdos_site_metrics.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['case','group','n_Fe','d_band_centre_eV','d_band_width_eV','integral','spin_polarization'])
        w.writerows(out)
    print('\nwrote analysis/pdos_site_metrics.csv')

    # quick figure: Fe-dz2 PDOS for the three site groups
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for label, (E, up, dn) in curves.items():
        if 'all' in label and 'ISLAND' in label:
            continue
        ax.plot(E, up, lw=1.9, label=label)
        ax.plot(E, -dn, lw=1.9, ls='--')
    ax.axvline(0, color='0.4', ls=':', lw=1)
    ax.axhline(0, color='0.6', lw=0.6)
    ax.set_xlim(-6, 4); ax.set_xlabel('E - E$_F$ (eV)'); ax.set_ylabel('Fe-d$_{z^2}$ PDOS (summed)')
    ax.set_title('Fe site-resolved PDOS: flat monolayer vs island interface/top', fontweight='bold')
    ax.legend(fontsize=9); ax.grid(alpha=0.2, lw=0.5)
    fig.tight_layout(); fig.savefig('figures/pdos_sites.png', dpi=300, bbox_inches='tight')
    print('wrote figures/pdos_sites.png')


if __name__ == '__main__':
    main()
