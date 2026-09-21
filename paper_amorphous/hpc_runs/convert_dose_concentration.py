"""convert_dose_concentration.py — map the reference's ion-dose metric <=> at% P.

The reference paper (Shashank 2025, NPG Asia Materials 17:15) reports P content as an
ion-IMPLANTATION DOSE (10-30 keV, 2.5-10e16 ions/cm^2) with SRIM depth profiles (their
SI S3). OUR amorphous Pt(P) is parametrized by explicit at% P (20P=P27Pt108 ~20 at%,
30P=P46Pt108 ~30 at%). To place both XRD and SHC on a common P-concentration axis we
convert (dose, keV) <-> at% P.

Model (per ion implantation): the P areal density maps to a mean atomic fraction
over a Pt layer of thickness t:
    C (at%) = Dose [ions/cm^2] / ( rho_Pt_atomic [atoms/cm^3] * t [cm] ) * 100
where rho_Pt_atomic = rho_Pt * N_A / M (fcc Pt density, 21.45 g/cm^3 => ~
6.62e22 atoms/cm^3). This is the peak/mean-of-box approximation; SRIM gives the
actual depth profile. Parameters are adjustable flags because the SI's SRIM figures
S3a-c publish the profile shape, not a single at% number.

Usage:
  python convert_dose_concentration.py --dose 7.5e16 30  # dose+keV -> at% (box model)
  python convert_dose_concentration.py --at 20           # our at% -> implied dose
Prints conversions for the reference's dose set and our compositions.
"""
from __future__ import annotations

__version__ = "1.0.0"

import argparse

# Pt atomic density (fcc, rho 21.45 g/cm^3, M 195.084, N_A 6.022e23)
RHO_PT_A = 6.62e22  # atoms / cm^3
# SRIM projected range ~ t for P in Pt at energy (nm); values flagged as estimates to
# be replaced by the SI S3 SRIM profiles.
RANGE_NM_BY_KEV = {10: 8.0, 20: 13.0, 30: 17.0}
DEFAULT_KEV = 30
# Reference dose set (ions/cm^2) from the paper
REF_DOSES = [2.5e16, 4.0e16, 7.5e16, 9.0e16, 10.0e16]
# Our compositions (at% P)
OUR_AT = [20.0, 30.0]


def dose_to_atpct(dose, kev):
    rng_cm = RANGE_NM_BY_KEV.get(kev, RANGE_NM_BY_KEV[DEFAULT_KEV]) * 1e-7  # nm -> cm
    volume_cm3 = rng_cm  # 1 cm^2 area * thickness
    n_host = RHO_PT_A * volume_cm3
    C = (dose / n_host) * 100.0
    return C, rng_cm


def atpct_to_dose(at, kev):
    rng_cm = RANGE_NM_BY_KEV.get(kev, RANGE_NM_BY_KEV[DEFAULT_KEV]) * 1e-7
    n_host = RHO_PT_A * rng_cm
    return (at / 100.0) * n_host


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dose", type=float, default=None, help="ions/cm^2")
    ap.add_argument("--kev", type=float, default=DEFAULT_KEV)
    ap.add_argument("--at", type=float, default=None, help="at% P to invert to dose")
    ap.add_argument("--all", action="store_true", help="print the full reference table")
    args = ap.parse_args()

    print(f"Using Pt range model: rho={RHO_PT_A:.3g} atoms/cm^3, "
          f"range_nm_by_kev={RANGE_NM_BY_KEV} (replace with SI S3 SRIM profiles)")
    if args.dose is not None:
        C, rng = dose_to_atpct(args.dose, args.kev)
        print(f"dose {args.dose:.2g} ions/cm^2 @ {args.kev:.0f} keV -> ~{C:.2f} at% P "
              f"(range ~{rng*1e7:.1f} nm)")
    if args.at is not None:
        d = atpct_to_dose(args.at, args.kev)
        print(f"our {args.at:.1f} at% P @ {args.kev:.0f} keV -> implied dose "
              f"{d:.2e} ions/cm^2")
    if args.all or (args.dose is None and args.at is None):
        print("\nReference dose -> at% P table (30 keV box model):")
        for d in REF_DOSES:
            C, rng = dose_to_atpct(d, 30)
            print(f"  {d:.2e} ions/cm^2 -> ~{C:5.2f} at% P")
        print("\nOur compositions -> implied dose (30 keV):")
        for a in OUR_AT:
            print(f"  {a:5.1f} at% P -> ~{atpct_to_dose(a,30):.2e} ions/cm^2")


if __name__ == "__main__":
    main()
