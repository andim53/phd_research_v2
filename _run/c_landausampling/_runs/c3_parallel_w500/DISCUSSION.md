# DISCUSSION — c3_parallel_w500 crash: `pthread_create: Resource temporarily unavailable`

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