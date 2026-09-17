"""PDOS analysis: Fe flat reference vs Fe island (ground state) on MgO.

Explains the ORIGIN of the flat -> island transition from the electronic structure.

Data (both from the femgo DOS runs, same orbital projections -> directly comparable):
  data/dos_femgo_flatngs/dos_seed_4.csv  -> FLAT reference   (4.xsf, dZ = 0.000 A)
  data/dos_femgo_flatngs/dos_seed_3.csv  -> ISLAND ground st (3.xsf, dZ = 3.652 A)
Columns are per-atom: Fe*_dz2_{up,down} (l=2,m=2) and O*_pz_{up,down} (l=1,m=0).
Energies are Fermi-shifted (E_F = 0).

Metrics computed per structure:
  - total DOS up/down, DOS at E_F
  - Fe-dz2 (summed over Fe) up/down; d-band centre (1st moment) and width (2nd moment)
  - O-pz (summed over O) up/down
  - spin polarization  = integral(up) - integral(down)  (per channel)

Usage:
  /home/think/miniconda3/envs/agox_v2/bin/python scripts/pdos_flat_vs_island.py
"""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, csv, re, os

CASES = [
    ('FLAT',   'data/dos_femgo_flatngs/dos_seed_4.csv', '\u0394Z = 0.000 Å', '#1f6fd0'),
    ('ISLAND', 'data/dos_femgo_flatngs/dos_seed_3.csv', '\u0394Z = 3.652 Å', '#d62728'),
]
DBAND_WINDOW = (-5.0, 3.0)   # eV around E_F for d-band moments


def load(path):
    rows = list(csv.DictReader(open(path)))
    E = np.array([float(r['energy']) for r in rows])
    fe_cols = [c for c in rows[0] if re.match(r'^Fe\d+_dz2_(up|down)$', c)]
    o_cols = [c for c in rows[0] if re.match(r'^O\d+_pz_(up|down)$', c)]
    fe_up = sum(np.array([float(r[c]) for r in rows]) for c in fe_cols if c.endswith('_up'))
    fe_dn = sum(np.array([float(r[c]) for r in rows]) for c in fe_cols if c.endswith('_down'))
    o_up = sum(np.array([float(r[c]) for r in rows]) for c in o_cols if c.endswith('_up'))
    o_dn = sum(np.array([float(r[c]) for r in rows]) for c in o_cols if c.endswith('_down'))
    tot_up = np.array([float(r['total_dos_up']) for r in rows])
    tot_dn = np.array([float(r['total_dos_down']) for r in rows])
    return dict(E=E, fe_up=fe_up, fe_dn=fe_dn, o_up=o_up, o_dn=o_dn,
                tot_up=tot_up, tot_dn=tot_dn, n_fe=len(fe_cols)//2, n_o=len(o_cols)//2)


def moments(E, g, window=DBAND_WINDOW):
    m = (E >= window[0]) & (E <= window[1])
    Ew, gw = E[m], g[m]
    area = np.trapz(gw, Ew)
    if area <= 0:
        return np.nan, np.nan, 0.0
    c = np.trapz(Ew * gw, Ew) / area                 # 1st moment: d-band centre
    w = np.sqrt(np.trapz((Ew - c) ** 2 * gw, Ew) / area)  # 2nd moment: d-band width
    return c, w, area


def dos_at_ef(E, g):
    return float(np.interp(0.0, E, g))


def main():
    os.makedirs('analysis', exist_ok=True)
    data = {}
    print(f"{'case':8s} {'N_Fe':>5s} {'N_O':>4s} {'d-cent(eV)':>11s} {'d-width':>8s} "
          f"{'Fe-dz2 int':>10s} {'O-pz int':>9s} {'spinPol':>8s} {'DOS(E_F)':>9s}")
    for name, path, lab, col in CASES:
        d = load(path)
        fe_sum = d['fe_up'] + d['fe_dn']
        c, w, area = moments(d['E'], fe_sum)
        o_area = np.trapz(d['o_up'] + d['o_dn'], d['E'])
        spinpol = np.trapz(d['tot_up'] - d['tot_dn'], d['E'])
        d['dcentre'], d['dwidth'] = c, w
        d['fe_int'], d['o_int'], d['spinpol'] = area, o_area, spinpol
        d['dosEf'] = dos_at_ef(d['E'], d['tot_up'] + d['tot_dn'])
        data[name] = d
        print(f"{name:8s} {d['n_fe']:5d} {d['n_o']:4d} {c:11.3f} {w:8.3f} "
              f"{area:10.3f} {o_area:9.3f} {spinpol:8.3f} {d['dosEf']:9.3f}")

    # ---- write metrics CSV ----
    with open('analysis/pdos_metrics.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['case','dZ','d_band_centre_eV','d_band_width_eV','Fe_dz2_integral',
                    'O_pz_integral','spin_polarization','DOS_at_E_F'])
        for name, path, lab, col in CASES:
            d = data[name]
            w.writerow([name, lab, f"{d['dcentre']:.4f}", f"{d['dwidth']:.4f}",
                        f"{d['fe_int']:.4f}", f"{d['o_int']:.4f}",
                        f"{d['spinpol']:.4f}", f"{d['dosEf']:.4f}"])

    # ---- figure ----
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharex=True)
    panels = [('total DOS', 'tot_up', 'tot_dn'),
              ('Fe $d_{z^2}$ PDOS (summed)', 'fe_up', 'fe_dn'),
              ('O $p_z$ PDOS (summed)', 'o_up', 'o_dn')]
    for ax, (title, kup, kdn) in zip(axes, panels):
        for name, path, lab, col in CASES:
            d = data[name]
            up, dn = d[kup], d[kdn]
            ax.fill_between(d['E'], 0, up, color=col, alpha=0.35, lw=0)
            ax.fill_between(d['E'], 0, -dn, color=col, alpha=0.35, lw=0)
            ax.plot(d['E'], up, color=col, lw=1.8, label=f'{name} ({lab})')
            ax.plot(d['E'], -dn, color=col, lw=1.8)
        ax.axvline(0, color='0.4', ls='--', lw=1)
        ax.axhline(0, color='0.6', lw=0.6)
        ax.set_xlim(-8, 6)
        ax.set_title(title, fontweight='bold', fontsize=12)
        ax.set_xlabel('E - E$_F$ (eV)', fontsize=11)
        ax.grid(alpha=0.2, lw=0.5)
    axes[0].set_ylabel('DOS (states/eV)', fontsize=11)
    axes[0].legend(fontsize=9, loc='upper left')
    axes[1].annotate('spin up', xy=(0.03, 0.9), xycoords='axes fraction', fontsize=9, color='0.3')
    axes[1].annotate('spin down', xy=(0.03, 0.08), xycoords='axes fraction', fontsize=9, color='0.3')
    fig.tight_layout(rect=[0, 0, 1, 1])
    os.makedirs('figures', exist_ok=True)
    fig.savefig('figures/pdos_flat_vs_island.png', dpi=300, bbox_inches='tight')
    print('\nwrote figures/pdos_flat_vs_island.png')
    print('wrote analysis/pdos_metrics.csv')


if __name__ == '__main__':
    main()
