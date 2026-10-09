#!/usr/bin/env python3
"""Parallel 2D Wang-Landau: N independent walkers collected into a master DOS.

The "Thing 1" embarrassingly-parallel replica design (spec 202610091935): N
independent ``WangLandau2DSampler`` walkers, each walking its own Markov chain
toward its own flattening of the 2D ``g(E, dZ)`` histogram, then all N flattened
histograms are collected into one master density of states.

Design decisions (spec v7, all folded):
- **C1** — each walker's ``ln_g`` is known only up to an additive constant
  ``c_i``. Align all walkers to a common offset by matching the overlap region
  (cells accessible in ALL walkers): ``c_i`` chosen so
  ``mean(ln_g_i[accessible_common])`` equals a reference. Then
  ``master_ln_g = mean_i(ln_g_i - c_i)``, ``spread = std_i(ln_g_i - c_i)``.
  Never unit-integral-normalise a 2D DOS (changes shape, not offset).
- **C2(a)** — master ``<dZ(T)>`` = average of per-walker reweighted curves (each
  walker's own ensemble reweighted with its own offset-aligned ln_g), giving
  per-walker error bars on the observable. NOT a pooled-ensemble reweight.
- **M1** — workers inject the shared accessible map via
  ``WangLandau2DSampler.set_accessible`` and skip their own reference pass.
- **M3** — the shared map is produced once on the driver (fixed seed) and
  broadcast to all workers.
- **m2** — spread = std over the walkers that visited a cell; cells visited by
  <2 walkers get ``spread = NaN``.
- **m3** — all walkers included, but the master flags which reached the 1/t
  switch and warns on any that did not.

Run with the agox_v2 conda env. Ray is assumed present (never re-verify).
"""

from __future__ import annotations

__version__ = "1.0.0"

import json
import os
import tempfile
from pathlib import Path

import numpy as np
import ray

from .wang_landau_2d import WangLandau2DSampler


# -- Atomic writes (mirror of main.py's helpers, kept local so the worker is
#    self-contained for crash-resilient shard checkpointing) -----------------

def _atomic_write_bytes(path: Path, data: bytes):
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".",
                               suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _atomic_write_json(path: Path, obj):
    _atomic_write_bytes(path, json.dumps(obj, indent=2).encode("utf-8"))


def _atomic_write_traj(sampler, path: Path):
    """Write accepted geometries to an ASE trajectory atomically (geometry-only)."""
    from ase.io import write as ase_write
    structs = sampler.ensemble_structs
    if not structs:
        return
    clean = []
    for a in structs:
        c = a.copy()
        c.set_constraint()
        c.calc = None
        clean.append(c)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".",
                               suffix=".tmp")
    os.close(fd)
    try:
        ase_write(tmp, clean, format="traj")
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


# -- Shared-map production (M3) ----------------------------------------------

def build_shared_accessible(gpr, generator, sampler_kwargs, reference_steps,
                            rng_seed):
    """Run ONE reference pass on a driver-side sampler and return its accessible map.

    The accessible map is a property of generator + GPR, not the RNG seed, so a
    single pass (fixed ``rng_seed``) is valid for all walkers and reproducible.
    ``reference_steps`` overrides any value in ``sampler_kwargs``.
    """
    kw = dict(sampler_kwargs)
    kw["reference_steps"] = reference_steps
    probe = WangLandau2DSampler(
        gpr=gpr, generator=generator,
        rng=np.random.default_rng(rng_seed),
        **kw)
    probe._reference_pass()
    return probe.accessible.copy()


# -- Worker actor ------------------------------------------------------------

@ray.remote(num_cpus=0)
class WangLandau2DWorker:
    """Owns a WangLandau2DSampler; runs it with a shared accessible map.

    Each worker: injects the shared map (M1), skips its own reference pass,
    resumes from its shard checkpoint if present (M2), runs the remaining steps
    writing its own shard checkpoint.json + ensemble.traj (crash-resilient), and
    returns its final state for the driver to collect.
    """

    def __init__(self, gpr, generator, sampler_kwargs, accessible_map,
                 rng_seed, shard_dir, mc_steps, checkpoint_interval):
        self.shard_dir = Path(shard_dir)
        self.shard_dir.mkdir(parents=True, exist_ok=True)
        self.mc_steps = int(mc_steps)
        self.checkpoint_interval = int(checkpoint_interval)

        self.sampler = WangLandau2DSampler(
            gpr=gpr, generator=generator,
            rng=np.random.default_rng(rng_seed),
            **sampler_kwargs)
        self.sampler.set_accessible(accessible_map)

        # Resume (M2): load shard checkpoint if present and valid.
        cp = self.shard_dir / "checkpoint.json"
        self.loaded_step = 0
        if cp.exists():
            try:
                with open(cp) as f:
                    ckpt = json.load(f)
                state = ckpt.get("state")
                if isinstance(state, dict):
                    self.sampler.load_state(state)
                    traj = self.shard_dir / "ensemble.traj"
                    if traj.exists():
                        from ase.io import read as ase_read
                        structs = list(ase_read(str(traj), index=":"))
                        n_rows = len(self.sampler.ensemble_rows)
                        if len(structs) > n_rows:
                            structs = structs[:n_rows]
                        self.sampler.ensemble_structs = structs
                    else:
                        self.sampler.ensemble_structs = []
                    self.loaded_step = self.sampler.step
                    print(f"[worker {rng_seed}] resumed at step {self.loaded_step}")
            except (OSError, ValueError) as e:
                print(f"[worker {rng_seed}] checkpoint unreadable ({e}); "
                      f"starting fresh")
                self.loaded_step = 0
        else:
            self.sampler.initialize()
            print(f"[worker {rng_seed}] initialized (shared map, no reference pass)")

    def _checkpoint_cb(self, sampler):
        # M1 two-file commit: traj before checkpoint.json.
        _atomic_write_traj(sampler, self.shard_dir / "ensemble.traj")
        _atomic_write_json(self.shard_dir / "checkpoint.json", {
            "config": {"n_e_bins": sampler.n_e_bins,
                       "n_dz_bins": sampler.n_dz_bins},
            "state": sampler.state_dict(),
        })

    def run(self):
        remaining = self.mc_steps - self.loaded_step
        if remaining < 0:
            raise SystemExit(
                f"[ABORT] --mc-steps {self.mc_steps} < checkpoint step "
                f"{self.loaded_step}. Refusing to run.")
        if remaining > 0:
            self.sampler.run(
                n_steps=remaining,
                checkpoint_interval=self.checkpoint_interval,
                checkpoint_callback=self._checkpoint_cb)
        # final checkpoint
        self._checkpoint_cb(self.sampler)
        return self.sampler.state_dict()

    def g_of_E_dZ(self):
        return self.sampler.g_of_E_dZ()


# -- Alignment + averaging (C1, m2) ------------------------------------------

def align_and_average(ln_g_list, accessible_list):
    """Offset-align N walkers' ln_g and return (master, spread, n_visited, aligned).

    C1: align each walker to a common offset via the overlap region (cells
    accessible in ALL walkers). m2: master at a cell = mean over walkers that
    visited it; spread = std over those same walkers; <2 visitors -> NaN.
    ``aligned`` is the list of per-walker offset-aligned ln_g (needed for the
    C2(a) per-walker reweight).
    """
    ln_g_list = [np.asarray(x, dtype=float) for x in ln_g_list]
    accessible_list = [np.asarray(a, dtype=bool) for a in accessible_list]
    N = len(ln_g_list)
    shape = ln_g_list[0].shape

    # overlap region = cells accessible in all walkers
    common = np.ones(shape, dtype=bool)
    for a in accessible_list:
        common &= a

    if not common.any():
        raise RuntimeError("No cell is accessible in ALL walkers; cannot align "
                           "offsets (C1). Increase --reference-steps or check "
                           "the accessible map.")

    # reference = mean over walker 0's ln_g on the common region
    ref = float(np.mean(ln_g_list[0][common]))
    aligned = []
    for ln_g in ln_g_list:
        c_i = float(np.mean(ln_g[common])) - ref
        aligned.append(ln_g - c_i)

    # master + spread over visiting walkers (m2)
    master = np.full(shape, np.nan)
    spread = np.full(shape, np.nan)
    n_visited = np.zeros(shape, dtype=int)
    for i in range(N):
        vis = accessible_list[i]
        n_visited[vis] += 1
    for i in range(N):
        vis = accessible_list[i]
        for i0, j0 in np.argwhere(vis):
            vals = [aligned[k][i0, j0] for k in range(N)
                    if accessible_list[k][i0, j0]]
            master[i0, j0] = float(np.mean(vals))
            if len(vals) >= 2:
                spread[i0, j0] = float(np.std(vals))
    return master, spread, n_visited, aligned


# -- Driver ------------------------------------------------------------------

def reweight_per_walker(states, aligned_ln_g, e_centers, dz_centers,
                        e_min, e_width, dz_min, dz_width, n_atoms, temperatures):
    """C2(a): reweight each walker's own ensemble with its own aligned ln_g.

    Returns (rows, per_walker_rows) where ``rows`` is the master <dZ(T)> = mean
    of the per-walker reweighted curves, and ``per_walker_rows`` is the list of
    per-walker row dicts (for error bars / diagnostics).
    """
    from .thermodynamics import reweight_2d
    per_walker_rows = []
    for state, ln_g in zip(states, aligned_ln_g):
        rows = reweight_2d(
            state["ensemble_rows"], ln_g, e_centers, dz_centers,
            e_min, e_width, dz_min, dz_width, n_atoms, temperatures)
        per_walker_rows.append(rows)
    # master = mean of per-walker curves (C2(a))
    n = len(per_walker_rows)
    master = []
    for t_idx in range(len(temperatures)):
        master.append({
            "T_K": float(temperatures[t_idx]),
            "mean_dZ_A": float(np.mean([r[t_idx]["mean_dZ_A"]
                                        for r in per_walker_rows])),
            "std_dZ_A": float(np.mean([r[t_idx]["std_dZ_A"]
                                       for r in per_walker_rows])),
            "effN": float(np.mean([r[t_idx]["effN"]
                                   for r in per_walker_rows])),
        })
    return master, per_walker_rows


def run_parallel_walkers_2d(gpr, generator, sampler_kwargs, accessible_map,
                             n_walkers, rng_base, mc_steps, checkpoint_interval,
                             output_dir):
    """Spawn N independent walkers, collect, align+average, return results.

    Returns a dict with the master DOS (ln_g, spread, n_visited), the per-walker
    states, and per-walker g_of_E_dZ for the driver to emit.
    """
    import ray
    if not ray.is_initialized():
        ray.init(ignore_reinit_error=True)

    # G2: size to the real node, not the PJM header.
    try:
        res = ray.cluster_resources()
        mem = res.get("memory", float("inf"))
        cpus = res.get("CPU", 1)
        est_gb = 0.26 + n_walkers * 0.135
        if mem != float("inf") and est_gb * 1e9 > mem:
            print(f"[WARN] estimated {est_gb:.1f} GB > node memory "
                  f"{mem/1e9:.1f} GB; reduce --n-walkers (G2).")
        if n_walkers > cpus:
            print(f"[WARN] --n-walkers {n_walkers} > {cpus} cores; wall-time "
                  f"benefit saturates at ~#cores (G2).")
    except Exception as e:
        print(f"[WARN] could not read Ray resources ({e}); skipping G2 check.")

    workers = [
        WangLandau2DWorker.remote(
            gpr, generator, sampler_kwargs, accessible_map,
            rng_base + i, str(Path(output_dir) / f"shard{i}"),
            mc_steps, checkpoint_interval)
        for i in range(n_walkers)
    ]
    states = ray.get([w.run.remote() for w in workers])
    gs = ray.get([w.g_of_E_dZ.remote() for w in workers])

    ln_g_list = [g[2] for g in gs]
    accessible_list = [g[4] for g in gs]
    master_ln_g, spread, n_visited, aligned = align_and_average(
        ln_g_list, accessible_list)

    return {
        "master_ln_g": master_ln_g,
        "spread": spread,
        "n_visited": n_visited,
        "aligned_ln_g": aligned,
        "per_walker_states": states,
        "per_walker_g": gs,
        "n_walkers": n_walkers,
    }