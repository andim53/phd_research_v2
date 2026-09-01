#!/usr/bin/env python3
"""Parallel / replica Wang-Landau (Mode A) via Ray actors.

Implements the README "Thing 2, Mode A" design: N walkers share a single
histogram ``H`` and log density of states ``ln_g`` (plus the shared refinement
state ``ln_f``/``stage``/1-t switch) held in one Ray actor, so the *combined*
histogram drives the flatness / refinement schedule. This lets N concurrent
walkers collectively reach flatness faster than any single walker, while using
the idle cores requested in the job scripts.

Synchronisation is **periodic** (not per-step): each walker keeps a local
``ln_g`` snapshot (for the acceptance test) and a local ``H`` buffer, and every
``check_interval`` steps pushes its local ``H`` + ``ln_g`` delta to the shared
actor. The shared actor merges them, judges flatness on the *aggregated* ``H``,
refines ``ln_f`` / broadcasts resets, and returns the fresh snapshot. This
avoids a Ray round-trip on every MC step (which would dominate wall-time).

State kept locally per walker (so ``run()`` / ``_visit`` / acceptance are
unchanged in spirit):

- ``self.ln_g``        : acceptance snapshot, refreshed from shared at each sync
- ``self.H``           : local histogram buffer since the last sync
- ``self._ln_g_delta`` : the ``ln_g`` this walker added since the last sync

The shared actor owns the authoritative ``H``, ``ln_g``, ``ln_f``, ``stage``,
``switched_to_1_over_t`` and ``global_step``.
"""

from __future__ import annotations

import numpy as np
import ray

from .wang_landau_sampler import WangLandauSampler


@ray.remote
class WangLandauSharedState:
    """Ray actor holding the shared histogram / ln_g / refinement state.

    All N walkers call ``sync`` every ``check_interval`` of their own steps;
    the actor merges each walker's local histogram, checks flatness on the
    aggregated ``H``, refines ``ln_f`` (and switches to the 1/t algorithm after
    ``n_stages_standard`` halvings), and returns a snapshot plus a ``reset``
    flag telling walkers to clear their local ``H`` buffers.
    """

    def __init__(self, n_bins, flatness_criterion=0.80,
                 check_interval=5000, n_stages_standard=14):
        self.n_bins = int(n_bins)
        self.H = np.zeros(self.n_bins, dtype=int)
        self.ln_g = np.zeros(self.n_bins)
        self.ln_f = 1.0
        self.stage = 0
        self.switched_to_1_over_t = False
        self.step_at_switch = 0
        self.global_step = 0
        self.flatness_criterion = float(flatness_criterion)
        self.check_interval = int(check_interval)
        self.n_stages_standard = int(n_stages_standard)

    # -- public actor API ----------------------------------------------------

    def sync(self, local_H, ln_g_delta, local_steps):
        """Merge one walker's local histogram + ln_g delta and refine.

        Parameters
        ----------
        local_H : np.ndarray (int), length n_bins
            The walker's histogram since its last sync.
        ln_g_delta : np.ndarray (float), length n_bins
            The ``ln_g`` this walker accumulated since its last sync.
        local_steps : int
            Number of MC steps the walker took since its last sync.

        Returns
        -------
        (ln_g, H, ln_f, stage, switched_to_1_over_t, reset) snapshot.
        ``reset`` is True when flatness was met (or the 1/t switch fired), so
        every walker must zero its local ``H`` buffer on the next sync.
        """
        self.H += np.asarray(local_H, dtype=int)
        self.ln_g += np.asarray(ln_g_delta, dtype=float)
        self.global_step += int(local_steps)

        reset = False
        if not self.switched_to_1_over_t:
            if self.global_step % self.check_interval == 0:
                if self._check_flatness():
                    self.ln_f /= 2.0
                    self.H[:] = 0
                    self.stage += 1
                    reset = True
                    print(f"  [shared] stage {self.stage}: ln_f = "
                          f"{self.ln_f:.6e} (flat at global step "
                          f"{self.global_step})")
            if self.stage >= self.n_stages_standard:
                self.switched_to_1_over_t = True
                self.step_at_switch = self.global_step
                self.H[:] = 0
                reset = True
                print(f"  [shared] switching to 1/t at global step "
                      f"{self.global_step} (after {self.stage} halvings)")
        else:
            # 1/t algorithm: ln_f = 1 / elapsed global steps since the switch
            self.ln_f = 1.0 / max(self.global_step - self.step_at_switch, 1)

        return (self.ln_g.copy(), self.H.copy(), self.ln_f, self.stage,
                self.switched_to_1_over_t, reset)

    def get_snapshot(self):
        """Return a full snapshot without modifying shared state."""
        return (self.ln_g.copy(), self.H.copy(), self.ln_f, self.stage,
                self.switched_to_1_over_t)

    # -- internals -----------------------------------------------------------

    def _check_flatness(self):
        visited = self.H > 0
        if not visited.any():
            return False
        mean_H = self.H[visited].mean()
        min_H = self.H[visited].min()
        return min_H > self.flatness_criterion * mean_H


class ParallelWangLandauWalker(WangLandauSampler):
    """A Wang-Landau walker whose histogram / ln_g live in a shared actor.

    Subclass of ``WangLandauSampler``. ``run()`` / ``_visit`` / the acceptance
    test are inherited unchanged; we only override ``_visit`` to also record
    into a local ``ln_g`` delta buffer, and override ``_maybe_refine`` to push
    the local histogram to the shared actor every ``check_interval`` steps.
    """

    def __init__(self, shared, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shared = shared
        self._ln_g_delta = np.zeros(self.n_bins)
        self._steps_since_sync = 0
        # pull the initial shared snapshot (all zeros at start); copy because
        # Ray object-store arrays are read-only
        ln_g, _, _, _, _ = ray.get(self.shared.get_snapshot.remote())
        self.ln_g = np.array(ln_g, copy=True)

    def _visit(self, b: int):
        # local snapshot update (for the acceptance test between syncs)
        self.ln_g[b] += self.ln_f
        # local histogram buffer
        self.H[b] += 1
        # ln_g contribution to be pushed at the next sync
        self._ln_g_delta[b] += self.ln_f

    def _maybe_refine(self):
        # Push local contributions to the shared actor every check_interval
        # steps, pull the refreshed snapshot, and reset local H if a global
        # reset was broadcast. Flatness / ln_f refinement happen inside the
        # shared actor on the aggregated histogram.
        self._steps_since_sync += 1
        if self._steps_since_sync < self.check_interval:
            return
        self._steps_since_sync = 0

        (self.ln_g, H, self.ln_f, self.stage,
         self.switched_to_1_over_t, reset) = ray.get(
            self.shared.sync.remote(self.H, self._ln_g_delta,
                                    self.check_interval))
        # copy: Ray object-store arrays are read-only
        self.ln_g = np.array(self.ln_g, copy=True)
        self._ln_g_delta[:] = 0
        if reset:
            self.H[:] = 0
            print(f"  [walker] global reset received; local H cleared at "
                  f"step {self.step}")


@ray.remote
class WangLandauWalkerActor:
    """Thin Ray-actor wrapper that owns one parallel walker and runs it.

    ``gpr`` is passed directly (Ray serialises one copy into each actor's
    process). Note: Ray copies composite Python objects per actor; the object
    store's zero-copy only applies to raw numpy arrays, so each walker holds its
    own GPR copy. The measured per-copy footprint is tiny (~35 MB), so N=24
    costs ~0.8 GB — negligible against the genkai 92.7 GB node limit.
    """

    def __init__(self, gpr, shared_ref, db_structures, db_energies,
                 seed, start_from_top, sampler_kwargs):
        self.walker = ParallelWangLandauWalker(
            shared_ref, gpr=gpr, db_structures=db_structures,
            db_energies=db_energies, rng=np.random.default_rng(seed),
            **sampler_kwargs)
        self.walker.initialize(start_from_top=start_from_top)

    def run(self, n_steps, progress_every):
        self.walker.run(n_steps=n_steps, progress_every=progress_every)

    def flush(self):
        """Merge any residual local steps into the shared actor.

        A walker only auto-syncs every ``check_interval`` of its own steps, so
        the last ``mc_steps % check_interval`` visits sit in the local ``H`` /
        ``_ln_g_delta`` buffers and would otherwise be lost. Calling this after
        ``run()`` guarantees the shared aggregate contains ALL walker visits,
        even when ``mc_steps`` is not a multiple of ``check_interval`` (and even
        when ``mc_steps < check_interval``, the empty-output bug). No-op when
        nothing is pending. The residual step count (< check_interval) will not
        spuriously trigger flatness/refinement in ``sync``.
        """
        steps = self.walker._steps_since_sync
        if steps > 0:
            ray.get(self.walker.shared.sync.remote(
                self.walker.H, self.walker._ln_g_delta, steps))
            self.walker._steps_since_sync = 0
            self.walker.H[:] = 0
            self.walker._ln_g_delta[:] = 0

    def get_result(self):
        centers, ln_g = self.walker.g_of_E()
        return centers, ln_g, self.walker.bin_current


def run_parallel_walkers(args, gpr, structures, energies, sampler_kwargs,
                         start_from_top):
    """Launch ``args.n_walkers`` concurrent walkers sharing H/ln_g via Ray.

    Returns ``(bin_centers_rel, ln_g, H, ln_f, stage)`` taken from the shared
    actor after all walkers finish (the authoritative aggregate result).
    """
    import ray

    n = int(args.n_walkers)
    print(f"\n[Mode A] Starting {n} parallel walkers sharing one H/ln_g "
          f"via Ray (seeds {args.rng}..{args.rng + n - 1}).")

    if not ray.is_initialized():
        ray.init(log_to_driver=False)
    shared = WangLandauSharedState.remote(
        n_bins=args.n_bins,
        flatness_criterion=args.flatness_criterion,
        check_interval=args.check_interval,
        n_stages_standard=args.n_stages_standard)

    actors = [
        WangLandauWalkerActor.remote(
            gpr, shared, structures, energies,
            seed=args.rng + i, start_from_top=start_from_top,
            sampler_kwargs=sampler_kwargs)
        for i in range(n)
    ]
    progress_every = max(args.check_interval, 1)
    ray.get([a.run.remote(args.mc_steps, progress_every) for a in actors])

    # final flush: merge each walker's residual local visits (mc_steps %
    # check_interval, including the mc_steps < check_interval empty-output
    # case) into the shared actor so the aggregate is never silently incomplete.
    ray.get([a.flush.remote() for a in actors])

    ln_g, H, ln_f, stage, switched = ray.get(shared.get_snapshot.remote())
    bin_centers = args.e_min + (args.e_max - args.e_min) / args.n_bins * (
        np.arange(args.n_bins) + 0.5)

    # re-derive E_ref / n_atoms for thermodynamics downstream
    E_ref = float(energies.min())
    n_atoms = len(structures[0])

    print(f"\n[Mode A] All {n} walkers done. Shared final state: "
          f"stage={stage}, ln_f={ln_f:.3e}, switched_to_1/t="
          f"{switched}, H nonzero={int((H > 0).sum())}/{args.n_bins}")

    # return the aggregate result plus what the thermodynamics post-processing
    # needs
    return (bin_centers, ln_g, H, ln_f, stage, E_ref, n_atoms)
