# DISCUSSION — c3_parallel_w500

Two distinct problems have been found in this run directory. Problem 1 is the
500-walker deployment crash (`.6667338.out`). Problem 2 is the completed-but-empty
run (`.6667777.out`) — the subject of this section.

---

## Problem 1 — crash: `pthread_create: Resource temporarily unavailable`

Run: `_runs/c3_parallel_w500/` — Mode A parallel WL, `--n-walkers 500`.
Error report: `jc3_parallel_w500.sh.6667338.out`.

## 1. What happened

The job **aborted (SIGABRT) during Ray actor creation**, before any walker ran a
single MC step. The GPR trained fine (1297 structures, 720-dim descriptor,
`Neg. log marginal likelihood = 876.35`), then the process died while building
the 500 `WangLandauWalkerActor`s.

Key error lines (verbatim from the `.out`):

```
logging.cc:117: Unhandled exception: St12system_error. what(): Resource temporarily unavailable
(WangLandauWalkerActor pid=21441) ... thread: Resource temporarily unavailable [system:11]
(WangLandauWalkerActor pid=19658) E0901 ... pthread_create failed: Resource temporarily unavailable
*** SIGABRT received at time=1788245271 on cpu 111 ***
```

The Python stack trace pins the crash site:

```
ray/actor.py:1719 in _remote
parallel_wl.py:226 in <listcomp>      <- creating the 500 actors
parallel_wl.py:225 in run_parallel_walkers
main.py:185 in main
```

and the C++ frame just before the abort is `ray::parallel_memcopy()` →
`Pickle5Writer_write_to` → `create_actor` — i.e. the failure is inside the
**serialization / dispatch of the actor constructor arguments** (the GPR object
being pickled to each of the 500 actors).

## 2. Why it happened

`pthread_create: Resource temporarily unavailable` is **EAGAIN** — the OS refused
to create another thread. Two independent causes, both present here:

### (a) 500 actors = 500 processes + a thread spike, on a small node

Each Ray actor is a **separate OS process**, and each process spawns several
threads (Ray's core-worker threads + the actor's own + the memcopy threads used
to ship the serialized GPR). Creating **500 actors at once** makes Ray fire a
burst of `parallel_memcopy` threads to copy the ~35 MB GPR object into every
actor. That burst, on top of 500 processes, blows past the **per-user
process/thread limit** (`RLIMIT_NPROC`, `ulimit -u`) and/or the memory available
for thread stacks → `pthread_create` returns EAGAIN → Ray's C++ handler aborts.

### (b) The node is far smaller than the memory model assumed

The Ray resource line in the `.out` is the smoking gun:

```
object_store_memory = 12000000000.0   (12 GB)
CPU                = 24.0
memory             = 48000000000.0    (48 GB)
node:172.16.11.23  = 1.0
```

This node has **24 CPUs and 48 GB RAM** — **not** the 64-core / 92.7 GB (92760 MB)
genkai node the memory model was built on. The earlier estimate ("500 walkers ≈
68 GB ≈ 73% of 92.7 GB") assumed the big node. On this 48 GB node:

- **Memory alone would already be exceeded**: 500 × ~135 MB ≈ **68 GB > 48 GB**.
- **Oversubscription is ~21×**: 500 walkers on 24 cores (500/24 ≈ 21) — far past
  the point where more walkers buys anything.

So the crash is the OS refusing to create threads because the node simply cannot
host 500 concurrent actor processes.

### Why the memory model was wrong for this run

The model's premise was the genkai 92.7 GB node. The job actually landed on a
24-core / 48 GB node (different resource group / smaller allocation than the
`vnode-core=64` header requested, or Ray detected a cgroup subset). The takeaway:
**the walker count must be sized to the node that is actually allocated, not to
the largest node in the system.**

## 3. How to fix it

### Fix 1 (primary): size `--n-walkers` to the real node

On a 24-core / 48 GB node, use **~24–48 walkers**, not 500. Rule of thumb:
`n_walkers ≈ 1–2 × CPU count`, and check `n_walkers × ~135 MB` fits the node's
RAM. 500 walkers only make sense on a node with ≥ 500 cores and ≥ 68 GB.

### Fix 2: request / confirm the right node

If you genuinely want ~500 walkers, the job must land on a node with enough
cores **and** memory (the 64-core / 92.7 GB genkai node). Verify the actual
allocation from the `.out` Ray resource line before trusting the header.

### Fix 3: raise the per-user process/thread limit

Add to the job script (if the scheduler permits):
```sh
ulimit -u unlimited      # max user processes (RLIMIT_NPROC)
ulimit -s 65536          # thread stack size (KB) — smaller stacks = more threads
```
This directly addresses the `pthread_create: Resource temporarily unavailable`
EAGAIN.

### Fix 4: constrain Ray so it doesn't over-claim

Tell Ray the real budget and stop it treating each walker as a full CPU slot:
```python
ray.init(num_cpus=24, memory=48_000_000_000, object_store_memory=12_000_000_000)
```
and mark the walker actors as not owning a CPU slot so many can share cores:
```python
@ray.remote(num_cpus=0)
class WangLandauWalkerActor: ...
```
(They are I/O-bound MC walkers; `num_cpus=0` lets Ray schedule them densely on
the available cores instead of demanding 500 CPU slots.)

### Fix 5: stagger actor creation

Create the actors in batches (e.g. 50 at a time) instead of all 500 in one list
comprehension, so the `parallel_memcopy` thread burst stays under the limit:
```python
actors = []
for i in range(0, n, 50):
    actors += [WangLandauWalkerActor.remote(...) for _ in range(50)]
    time.sleep(1)   # let the OS reclaim threads between batches
```

### Fix 6 (design): reconsider whether 500 walkers is even useful

On 24 cores you get **no wall-time benefit beyond ~24 walkers** — the extra
walkers only add statistical aggregation (faster flatness in total steps), not
speed. If the goal is wall-clock, add cores; if it is statistical, a few hundred
walkers on a big node is fine, but 500 on a 24-core node is pure oversubscription.

## 4. Recommended next step

1. Confirm which node the job actually gets (read the Ray resource line in the
   `.out`).
2. For a quick smoke test on this node: `--n-walkers 24 --mc-steps 1000
   --relax-steps 10` (matches 24 cores, ~3.2 GB — trivially fits 48 GB).
3. Only scale to ~500 on a node with ≥ 500 cores / ≥ 68 GB, and add the
   `ulimit` + `ray.init` + `num_cpus=0` guards above.

## 5. Bottom line

The code is not wrong — the **deployment is**. 500 Ray actors (500 processes +
a serialization thread burst) cannot be created on a 24-core / 48 GB node; the
OS refuses with `pthread_create: Resource temporarily unavailable` and Ray
aborts. Size `--n-walkers` to the node actually allocated, raise the process
limit, and constrain Ray's resource claims. The memory model was correct for the
92.7 GB genkai node but does **not** apply to the smaller node this job landed on.

---

## Problem 2 — the run completes but produces empty (all-zero) results

Run: `_runs/c3_parallel_w500/`, error/report file `jc3_parallel_w500.sh.6667777.out`.
Outputs: `wl_output_c1_parallel_w500/`.

### 1. What happened

The job **ran to completion without crashing** — the 500-walker deployment fix
(Problem 1, reduce to 24 walkers on the 24-core node) worked. The log shows all
24 `WangLandauWalkerActor`s started, each ran its `--mc-steps 1000` walk
(`Total MC steps = 1000, stages reached = 0`, 24×), and the driver printed a
final state. **But the shared result is empty:**

```
[Mode A] All 24 walkers done. Shared final state: stage=0, ln_f=1.000e+00, switched_to_1/t=False, H nonzero=0/100
```

`H nonzero = 0/100` — the **aggregate histogram `H` is entirely zero**, even
though 24 walkers × 1000 steps = 24,000 bin visits happened. Consequently:

- `g_of_E.csv` — every row has `ln_g = 0.0` and `H = 0.0` (all 100 bins).
- `thermodynamics.csv` — `Z = inf`, `logZ ≈ 50679`, and the free energy `F ≈ -436.7 eV` is the same flat value at every temperature (i.e. a constant, physically meaningless offset).
- `heat_capacity.csv` — `C_V = 0.0000` at all temperatures (a flat/empty `ln g(E)` yields zero heat capacity).

### 2. Why it happened (root cause)

This is a **logic bug in Mode A's periodic-sync design**, not a resource crash.

The parallel walker only flushes its local histogram to the shared actor after
`check_interval` of **its own** MC steps. The gating is in
`wang_landau/parallel_wl.py:159-161`:

```python
def _maybe_refine(self):
    self._steps_since_sync += 1
    if self._steps_since_sync < self.check_interval:
        return          # <-- returns early until check_interval local steps
    self._steps_since_sync = 0
    (self.ln_g, H, ...) = ray.get(self.shared.sync.remote(self.H, ...))
```

`check_interval` defaults to **5000** (`main.py:92`), but this run used
`--mc-steps 1000`. So each walker took only 1000 steps — **fewer than the 5000
needed to trigger a single sync**. `_steps_since_sync` never reaches
`check_interval`, `sync.remote()` is never called, and the walker's local `H` /
`ln_g_delta` are **never pushed** to the shared actor.

At the end, the driver reads the shared actor's snapshot (`parallel_wl.py:235`):

```python
ln_g, H, ln_f, stage, switched = ray.get(shared.get_snapshot.remote())
```

Since nothing was ever merged in, the shared `H`/`ln_g` are still their initial
all-zero arrays → `H nonzero = 0/100`. The **walker-local** histograms (which did
record the 24,000 visits) are simply discarded — the driver only uses the shared
snapshot, not each walker's `get_result()`.

So the run "worked" (no crash, correct concurrency) but produced a physically
empty result: **`mc-steps (1000) < check_interval (5000)` ⇒ zero synchronisations
⇒ empty aggregate.**

### 3. How to fix it

There are two fixes — a config fix (immediate) and a code fix (the real cure).

#### Config fix (immediate, for this smoke test)

Make `--mc-steps` a **multiple of `--check-interval`**, and larger than it, so at
least one sync fires. For the same smoke test:

```bash
--n-walkers 24 --mc-steps 5000 --check-interval 5000    # exactly 1 sync per walker
# or better, give it headroom:
--n-walkers 24 --mc-steps 10000 --check-interval 5000   # 2 syncs per walker
```

For the real production run you want many syncs anyway, so `--mc-steps 30000`
(or higher) with the default `--check-interval 5000` is fine (6 syncs per walker).

#### Code fix (the real cure) — flush local state at the end

Even with the config fix, any run whose `mc-steps % check_interval != 0` leaves
the **tail** visits stuck in walker-local buffers that are never merged. The
robust fix is to force a **final flush** of each walker's remaining local `H` /
`ln_g_delta` into the shared actor after `run()` completes, before reading the
snapshot. In `run_parallel_walkers` (`parallel_wl.py:233-235`), add a final sync:

```python
ray.get([a.run.remote(args.mc_steps, progress_every) for a in actors])
# final flush: merge any local steps not yet synced (mc_steps % check_interval)
for a in actors:
    a.flush.remote()          # -> calls shared.sync(local_H, local_delta, steps)
ln_g, H, ln_f, stage, switched = ray.get(shared.get_snapshot.remote())
```

where `WangLandauWalkerActor.flush()` calls `sync.remote` with whatever remains
in `self.walker.H` / `self.walker._ln_g_delta` and the residual `_steps_since_sync`.
This guarantees the shared aggregate always contains **all** walker visits, so
`mc-steps` no longer needs to be a multiple of `check_interval`.

### 4. Correctness note (not a bug, but important)

Even with a flush, a 1000-step / 24-walker run is **not converged** (stage 0,
`ln_f` still 1.0, no flatness reached) — that is expected and fine for a smoke
test. The empty output is purely the sync-gating bug above, not a statement
about convergence. A real run needs `--mc-steps` large enough to advance the
standard-scheme halvings.

### 5. Bottom line

Problem 2 is **not a deployment issue** (the 24-walker run on 24 cores ran fine)
but a **code bug in the periodic-sync design**: when `mc-steps < check_interval`,
walkers never flush, and the driver reads an empty shared snapshot. Fix by (a)
setting `mc-steps` ≥ a multiple of `check_interval`, and (b) adding a final flush
of walker-local state so the aggregate is never silently empty.