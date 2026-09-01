# QNA — Wang–Landau (c_landausampling)

1. How does the `mc steps` interact with the parallel walkers? I don't *quite understand* it. Write the *complete workflow*, with code snapshot.

---

**Short answer.** `--mc-steps N` is **per walker**, not total. In Mode A each of the `--n-walkers W` walkers independently runs a full `run(n_steps=N)` Wang–Landau loop; they all feed into **one shared histogram `H` / log-density `ln_g`** held by a `WangLandauSharedState` Ray actor. So the **total number of bin visits is `W × N`**, and flatness/refinement act on that combined visit count — that is exactly why N walkers reach flatness faster than one.

---

## The two clocks (this is the crux)

There are **two independent counters** that people confuse:

| Clock | Who owns it | Advances when | Role |
|---|---|---|---|
| `self.step` (walker-local) | each walker | +1 per MC step in its own `run()` loop (`wang_landau_sampler.py:360`) | drives the **acceptance test** and the walker's own progress prints |
| `shared.global_step` | the shared actor | `+= check_interval` each time a walker syncs (`parallel_wl.py:84`) | drives the **shared flatness check / refinement** (`parallel_wl.py:88`) |

Every walker advances its own `self.step` from 1 to `--mc-steps`. The shared actor's `global_step` is the sum of the per-walker steps, aggregated in `check_interval`-sized chunks at each sync.

---

## Complete workflow

Assume the launch line:
```bash
python main.py --dataset dataset --n-bins 100 --e-max 0.40 \
    --mc-steps 30000 --relax-steps 100 --perturb-symbols Fe \
    --n-walkers 500 --check-interval 5000 --rng 42
```
(`--n-walkers 500`, `--mc-steps 30000` → **15,000,000 total visits**.)

1. **Train ONE GPR** (root process, before any Ray). Every walker shares the same surrogate — it is serialised into each Ray actor (~35 MB copy each).
2. **`run_parallel_walkers`** (`parallel_wl.py:204`) creates:
   - one `WangLandauSharedState` actor (`:219`), holding `H`, `ln_g`, `ln_f`, `stage`, `switched_to_1_over_t`, `global_step` — all initialised to zero / the first stage;
   - `W = 500` `WangLandauWalkerActor`s (`:225`), walker *i* seeded `--rng + i` (42..541), each wrapping a `ParallelWangLandauWalker`.
3. Each walker **initialises** independently from the same DB global minimum (`initialize`, `wang_landau_sampler.py:316`).
4. **Each walker runs its own serial WL `run(n_steps=30000)`** (`parallel_wl.py:196` → `wang_landau_sampler.py:354`). Inside the loop (`:359-395`):
   - `_propose_move()` → (optional) basin-hopping `_relax` → `_energy_of` → bin;
   - **acceptance test** `wang_landau_sampler.py:382-389`: `log(r) < ln_g[cur] - ln_g[trial]`, using the walker's **local** `ln_g` snapshot;
   - **`_visit(bin)`** — *overridden in the parallel walker* to record into both the local snapshot and the local histogram buffer (`parallel_wl.py:146-152`);
   - **`_maybe_refine()`** is called every step (`:390`) but — overridden — returns early until the walker has gone `check_interval` (5000) of its *own* steps (`parallel_wl.py:159-161`).
5. **Periodic sync** — every 5000 local steps, the walker pushes to the shared actor (`parallel_wl.py:163-174`):
   ```python
   (self.ln_g, H, self.ln_f, self.stage,
    self.switched_to_1_over_t, reset) = ray.get(
       self.shared.sync.remote(self.H, self._ln_g_delta,
                               self.check_interval))
   self.ln_g = np.array(self.ln_g, copy=True)   # read-only -> copy
   self._ln_g_delta[:] = 0
   if reset:
       self.H[:] = 0
   ```
   It sends its local `H` (visits since last sync) plus its local `ln_g` delta (the `ln_f` it accumulated), and pulls back the **merged** `ln_g`, current `ln_f`, `stage`, and a `reset` flag. Then it zeroes its local `H` buffer.
6. **The shared actor merges + refines** (`parallel_wl.py:64-109`):
   ```python
   self.H        += local_H            # sum walkers' visits
   self.ln_g     += ln_g_delta         # sum walkers' ln_f contributions
   self.global_step += local_steps     # += check_interval
   if not switched_to_1_over_t:
       if self.global_step % check_interval == 0:
           if self._check_flatness():  # on the AGGREGATED H
               self.ln_f /= 2.0
               self.H[:] = 0
               self.stage += 1
               reset = True
       if self.stage >= n_stages_standard:
           switched_to_1_over_t = True
           ...
   else:
       self.ln_f = 1.0 / (global_step - step_at_switch)
   ```
   Flatness is judged only on the **summed** histogram across all 500 walkers (`_check_flatness`, `:118-124`). Because `local_steps == check_interval`, `global_step` is always a multiple of `check_interval`, so flatness is re-checked on every sync.
7. After `ray.get([a.run.remote(...) ...])` returns, the driver pulls the final **authoritative aggregate** snapshot (`parallel_wl.py:235`) and passes `(bin_centers, ln_g, H, ...)` to the same thermodynamics / plotting path as the serial run.

---

## Code snapshot — the one function you must read

```python
# parallel_wl.py:225-233 — the +N wall-clock concurrency
actors = [
    WangLandauWalkerActor.remote(
        gpr, shared, structures, energies,
        seed=args.rng + i, start_from_top=start_from_top,
        sampler_kwargs=sampler_kwargs)
    for i in range(n)
]
ray.get([a.run.remote(args.mc_steps, progress_every) for a in actors])
```
Here `args.mc_steps` is handed to **each** actor, so each walker does a full 30000-step WL walk; they run **concurrently** (one per Ray process), and only synchronise at the `check_interval` boundaries.

---

## Why periodic sync (not per-step)

If walkers pushed `H`/`ln_g` to the shared actor on **every** MC step, we'd pay one Ray call per step ~ 500 × 15M = 7.5 billion remote calls — wall-time dominated by overhead. So each walker keeps a **local snapshot** for the acceptance test and only syncs every 5000 steps (`parallel_wl.py:11-16`).

Trade-off: between syncs a walker uses a **slightly stale** `ln_g` (it doesn't see other walkers' contributions until the next sync). For a slowly-refining `ln_g` this is negligible and is the standard parallel-WL design — combined with the huge win of judging flatness on `W × N` visits.

---

## Concrete numbers (c1_parallel_w500)

- `--n-walkers 500`, `--mc-steps 30000` → **15,000,000 total bin visits** across 500 concurrent work processes.
- Each walker still does the "same" work as the serial c1 (30000 steps), but they run at ~64 cores on the node, so wall-time is far below 500 × the serial time.
- Flatness needs every bin in the **shared** `H` to have been visited ~equal times. 500 independent chains collectively fill all bins ~500× faster than 1 chain — that is the entire point of Mode A.
- Memory: 500 × ~135 MB ≈ 68 GB ≈ 73% of the 92.7 GB genkai limit (fits, tight headroom).