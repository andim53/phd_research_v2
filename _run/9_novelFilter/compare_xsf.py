#!/usr/bin/env python3
"""
Copy the top-N structures (by rank) from every threshold output folder into a
single side-by-side directory for easy structural comparison.

For each rank 0..N-1 it makes a subfolder, and into it copies the
``novel_<rank>_E<e>.xsf`` file from EACH threshold folder, named so the
threshold is visible in the filename:

    side_by_side/
    ├── rank0/
    │   ├── thr_0.25_novel_0000_E-436.909.xsf
    │   ├── thr_0.50_novel_0000_E-436.909.xsf
    │   ├── thr_0.75_novel_0000_E-436.909.xsf
    │   ├── thr_1_novel_0000_E-436.909.xsf
    │   └── ...
    ├── rank1/
    │   └── ...
    └── ...

This lets you eyeball how the same structural rank changes as the filter
threshold varies.

Run with any Python (no AGOX needed; pure filesystem copy):
    python3 compare_xsf.py --outdir ./novel_output --n 5 --dest ./side_by_side

Options:
    --outdir   the run output dir containing thr_<v>/novel_structures/ (default ./novel_output)
    --n        how many top ranks to copy (default 5)
    --dest     where to write the side-by-side tree (default ./side_by_side)
"""

from __future__ import annotations

import argparse
import glob
import os
import shutil


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--outdir", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "novel_output"),
        help="Run output dir containing thr_<v>/ folders (default ./novel_output)")
    p.add_argument("--n", type=int, default=5,
                   help="Number of top ranks to copy per threshold (default 5)")
    p.add_argument("--dest", default="side_by_side",
                   help="Destination directory (default ./side_by_side)")
    args = p.parse_args()

    # Discover threshold folders: thr_<v>/novel_structures
    thr_dirs = sorted(
        d for d in os.listdir(args.outdir)
        if d.startswith("thr_") and os.path.isdir(os.path.join(args.outdir, d))
    )
    if not thr_dirs:
        raise SystemExit(f"No thr_<v>/ folders found under {args.outdir!r}")

    print(f"Found {len(thr_dirs)} threshold folders: {thr_dirs}")

    # Build rank -> {thr_label: src_path} map
    rank_files = {}   # rank -> list of (thr_label, abs_src)
    missing_any = False
    for d in thr_dirs:
        ns_dir = os.path.join(args.outdir, d, "novel_structures")
        for rank in range(args.n):
            glob_match = os.path.join(ns_dir, f"novel_{rank:04d}_*.xsf")
            hits = sorted(glob.glob(glob_match))
            rank_files.setdefault(rank, [])
            for src in hits:
                rank_files[rank].append((d, src))
            if not hits:
                # A rank may be absent at a strict (large) threshold (fewer kept
                # than N). Record so we can warn once at the end.
                rank_files.setdefault(rank, [])
                missing_any = True

    if missing_any:
        print("Note: some (threshold, rank) pairs have no file — those thresholds "
              "kept fewer than N structures.")

    os.makedirs(args.dest, exist_ok=True)
    total = 0
    for rank, items in sorted(rank_files.items()):
        rdir = os.path.join(args.dest, f"rank{rank}")
        os.makedirs(rdir, exist_ok=True)
        for thr_label, src in items:
            fname = f"{thr_label}_{os.path.basename(src)}"
            dst = os.path.join(rdir, fname)
            shutil.copy2(src, dst)
            total += 1
            print(f"  {thr_label}/rank{rank}: {os.path.basename(src)}")

    print(f"\nCopied {total} files into {args.dest}/")
    print("Compare: open the same-rank folder and cycle the thr_*_novel_<rank>_E<e>.xsf files.")


if __name__ == "__main__":
    main()
