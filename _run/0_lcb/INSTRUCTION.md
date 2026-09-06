# INSTRUCTION.md — Owner-side How-To Playbook

This file holds **owner-executable instructions**: step-by-step, line-by-line,
command-by-command guides that let YOU (the project owner) do the work by hand
that the AI agent would otherwise do. The agent's job is to **instruct** — to
write the how-to — not to perform the task.

## Convention (governed by `AGENTS.md`)

- **Append-only.** When the owner asks the agent to *prepare an instruction*
  for a task, the agent **appends** a new self-contained block **at the top of
  the instructions list** (newest first — the latest instruction is inserted
  immediately below the `---` divider above the oldest block). The agent never
  reads back and rewrites or replaces prior blocks; it only prepends the new one
  and moves the divider. (Convention updated 2026-09-06; earlier blocks were
  appended newest-last.)
- **Numbering.** Each block is headed `INSTR #N — <short title>` with a date.
  `N` increments with every append. The agent determines the next `N` by
  finding the highest existing `INSTR #N` header (a targeted header lookup,
  not a full re-read of prior content).
- **Voice.** Blocks are written in the second person, to the owner
  ("you run …", "edit `file.py:line` …"), covering: exact commands (with the
  right env python), where to edit and how, how to run the smoke test, and the
  expected output / how to verify.
- **Trigger.** The agent writes an instruction only on the owner's explicit
  request (e.g. "prepare an instruction for X"), after clarifying the specific
  task/approach when needed. It does not append one automatically for every task
  it executes.
- **Tracking.** The file is tracked and committed under the explicit `_run/0_lcb`
  pathspec; every append also gets an entry in `LOG.md`.

---

*(Owner-executable instructions begin below.)*

---

## INSTR #2 — Stand up Fe/MgO LCB runs with more MgO layers (`1_runs/2_femgo_3mgo`, `3_femgo_5mgo`, `4_femgo_10mgo`)

**Date:** 2026-09-06 · **Goal:** create three self-contained run dirs under
`1_runs/` that replicate the `0_lcb_femgo` system (Fe(001) overlayer on
MgO(001), **no B**, LCB/GPR AGOX search, **no dipole correction**) but with a
**thicker MgO substrate**: `mgo_layer_number = 3, 5, 10`, and a **vacuum grown
to keep the same clearance as the single-layer run**. Each dir gets a corrected
`main.py`, a job script, and a **stacking smoke test** that verifies the produced
MgO/Fe stacking on the generator structure. The heavy 100-iteration HPC run is
out of scope here.

**Source of truth:** copy from `2_analysist/0_lcb_femgo/` (its `main.py` +
`scripts/`). Env for all compile/run steps = **`agox_v2`**:
`/home/think/miniconda3/envs/agox_v2/bin/python`. Geometry (measured by importing
the real `build_*` scripts): each MgO monolayer in this builder is one **coplanar
Mg+O plane**, inter-plane spacing **2.106 Å** (`dist_mgo`, = `a_mgo/2`); after
the 5×5 repeat each plane holds 25 Mg + 25 O. `build_mgo_stack` auto-grows the
substrate cell with each added layer, so raising `vacuum` keeps the Fe-on-top
clearance constant.

---

### Step 1 — Create the three run dirs and copy the source files

```bash
cd /home/think/Desktop/research/_run/0_lcb
for d in 2_femgo_3mgo 3_femgo_5mgo 4_femgo_10mgo; do
  mkdir -p 1_runs/$d
  cp -r 2_analysist/0_lcb_femgo/scripts 1_runs/$d/scripts
  cp 2_analysist/0_lcb_femgo/main.py 1_runs/$d/main.py
  cp 2_analysist/0_lcb_femgo/job_5x5_9.sh 1_runs/$d/j_5x5.sh
done
ls 1_runs/2_femgo_3mgo 1_runs/3_femgo_5mgo 1_runs/4_femgo_10mgo
```

Expected: each dir holds `main.py`, `j_5x5.sh`, `scripts/` (with
`build_fe_stack.py`, `build_mgo_stack.py`, `build_heteroStruct.py`,
`hetero_struct_randomize.py`, `plot_structure.py`, …). **Do not** copy
`seed_*/`, `stop_16/`, `trash/`, or any run output — these dirs start empty of data.

### Step 2 — Edit each `main.py`: layer count + vacuum

In **all three** files the two edits are the two parameter assignments near the
top of `main.py` (in the copied `0_lcb_femgo` source these are the
`# ==== Slab Number of Layer` / `vacuum` block around lines 39–52). Set:

```python
# 2_femgo_3mgo:
mgo_layer_number = 3
vacuum = 24.2
```

```python
# 3_femgo_5mgo:
mgo_layer_number = 5
vacuum = 28.4
```

```python
# 4_femgo_10mgo:
mgo_layer_number = 10
vacuum = 39.0
```

**Why these `vacuum` values:** the single-layer `0_lcb_femgo` used `vacuum = 20`
and each extra MgO monolayer adds ~2.106 Å to the stack. To hold the Fe-on-top
clearance (~the same as the N=1 run) use `vacuum = 20 + 2.106*(N-1)` → N=3:
`24.2`; N=5: `28.4`; N=10: `39.0`. Measured result of the real builder with
these values (verified by importing `build_*`): O and Mg land **coplanar** in N
distinct planes spaced **2.106 Å**, Fe sits **0.50 Å** above the top MgO plane,
and the substrate cell leaves **27–42 Å** of vacuum above the Fe — plenty.

Do **not** change any other physical parameter (`a_mgo=4.212`, `a_fe=2.870190`,
`supercell=(5,5,1)`, `kpts=(1,1,1)`, `kappa=2`, `N_iterations=100`,
LCAO/dzp/PBE, spinpol, `ncores=24`). Keep `main.py` **dipole-free** (no
`poissonsolver` line) — these runs replicate plain `0_lcb_femgo`.

### Step 3 — Point each job script at its `main.py`

Each `j_5x5.sh` is a straight copy of `job_5x5_9.sh` (PJM headers, `gpaw_env`,
`python ./main.py`). Confirm it runs `main.py` from the dir's own cwd (it does —
the command is relative). Leave seed/iteration scope as-is unless you want a
narrower first run. Keep it a bare `#PJM` script; **never** add `pjsub -x`.

### Step 4 — Smoke test: compile gate

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb
for d in 2_femgo_3mgo 3_femgo_5mgo 4_femgo_10mgo; do
  $PY -m py_compile 1_runs/$d/main.py && echo "$d COMPILE OK"
done
```

Expected: three `COMPILE OK` lines. (LSP under base `python3` flags AGOX/ASE
imports — ignore it; judge by `agox_v2`'s `py_compile`.)

### Step 5 — Smoke test: stacking check on the produced generator structure

This verifies the **actual MgO/Fe stacking** the run would produce, per layer
count, by importing the real `build_*` scripts and building the heterostructure
the way `main.py` does (MgO substrate + Fe deposition, 5×5 repeat). It asserts:
(1) exactly N coplanar MgO planes, each with 25 Mg + 25 O; (2) inter-plane
spacing ≈ 2.106 Å; (3) Mg and O are coplanar per plane (rocksalt (001) registry —
no O/Mg on different heights within a plane); (4) Fe is a single plane **0.50 Å**
above the top MgO plane; (5) cell clearance above Fe ≥ 10 Å. Run it **inside each
run dir** (it imports that dir's own `scripts/`), passing N as an argument.

Create `1_runs/2_femgo_3mgo/smoke_stack.py` (then copy to the other two dirs and
edit `N` + `VAC` to 5/28.4 and 10/39.0):

```python
"""Stacking smoke: verify the Fe/MgO structure main.py would build has good MgO
stacking + correct Fe placement for the requested layer count.
Usage:  $PY smoke_stack.py    (edit N and VAC below per run dir)"""
import sys
import numpy as np
from ase.build import surface
sys.path.insert(0, 'scripts')
from build_mgo_stack import build_mgo_stack
from build_heteroStruct import build_heteroStruct
from build_fe_stack import build_fe_stack

N   = 3                     # EDIT per dir: 3 | 5 | 10
VAC = 24.2                  # EDIT per dir: 24.2 | 28.4 | 39.0
a_mgo, a_fe = 4.212, 2.870190
dist_z_fe2o, SC = 0.5, (5, 5, 1)

slab_fe_base = surface('Fe', (0, 0, 1), layers=1, vacuum=VAC)
sm = build_mgo_stack(slab_fe_base, num_layers=N, vacuum=VAC)
mgo = sm[[a.symbol != 'Fe' for a in sm]].repeat(SC)          # MgO substrate
fe  = build_fe_stack(slab_fe_base, num_layers=1, vacuum=VAC).repeat(SC)
het = build_heteroStruct(mgo.copy(), fe.copy(), dist_inter=dist_z_fe2o, vacuum=VAC)

ok = True
def chk(msg, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + msg)
    ok = ok and cond

o   = het[[a.symbol == 'O'  for a in het]]
mg  = het[[a.symbol == 'Mg' for a in het]]
fea = het[[a.symbol == 'Fe' for a in het]]
oz  = np.sort(np.unique(np.round(o.positions[:, 2], 3)))
mz  = np.sort(np.unique(np.round(mg.positions[:, 2], 3)))
fz  = np.sort(np.unique(np.round(fea.positions[:, 2], 3)))
cz  = mgo.cell[2, 2]; zmax = het.positions[:, 2].max()

chk(f'{N} MgO layers (O planes={len(oz)})', len(oz) == N)
chk(f'{N} MgO layers (Mg planes={len(mz)})', len(mz) == N)
chk('O and Mg coplanar per plane', np.allclose(oz, mz, atol=0.01))
chk('plane spacing ~ 2.106 A', np.allclose(np.diff(oz), 2.106, atol=0.01))
chk('25 Mg + 25 O per plane (5x5)', len(o) == 25*N and len(mg) == 25*N)
chk('single Fe plane (25)', len(fea) == 25 and len(fz) == 1)
chk(f'Fe sits 0.50 A above top MgO (gap {fz.min()-oz.max():.2f})',
    np.isclose(fz.min() - oz.max(), dist_z_fe2o, atol=0.02))
chk(f'cell clearance above Fe >= 10 A (={cz-zmax:.1f})', cz - zmax >= 10.0)
chk('no atom below cell bottom / above cell top', zmax < cz - 1.0)

print('--- per-MgO-plane z (O and Mg coincide):', oz)
print('STACKING SMOKE ' + ('PASS' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
```

Run it in each dir (each time with the matching `N`/`VAC`):

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/1_runs/2_femgo_3mgo
$PY smoke_stack.py
# repeat in 3_femgo_5mgo (N=5, VAC=28.4) and 4_femgo_10mgo (N=10, VAC=39.0)
```

**Expected output (N=3):**
```
PASS 3 MgO layers (O planes=3)
PASS 3 MgO layers (Mg planes=3)
PASS O and Mg coplanar per plane
PASS plane spacing ~ 2.106 A
PASS 25 Mg + 25 O per plane (5x5)
PASS single Fe plane (25)
PASS Fe sits 0.50 A above top MgO (gap 0.50)
PASS cell clearance above Fe >= 10 A (=27.4)
PASS no atom below cell bottom / above cell top
--- per-MgO-plane z (O and Mg coincide): [24.2  26.306 28.412]
STACKING SMOKE PASS
```
(Verified with the real `build_*` scripts. N=5/VAC=28.4: planes
`[28.4 30.506 32.612 34.718 36.824]`, clearance 31.6. N=10/VAC=39.0: 10 planes
`[39. 41.106 43.212 ... 57.954]`, clearance 42.2.)

**Failures to watch for:**
- A **FAIL on layer count / spacing** → `mgo_layer_number` or `vacuum` edit didn't
  land, or the wrong `N`/`VAC` was set in the smoke for that dir.
- **FAIL "Fe sits 0.50 A above top MgO"** → the substrate/deposition gap changed
  (`dist_z_fe2o`); it should be 0.5. Revert it.
- **FAIL "cell clearance < 10 A"** → `vacuum` too small; use the `20+2.106*(N-1)`
  rule. Clearance is not a stacking fault per se, but a cramped cell lets the slab
  interact with its periodic image.

### Step 6 — Verify & clean up

- Confirm each `main.py` has the right `mgo_layer_number`/`vacuum`:
  `grep -nE 'mgo_layer_number|^vacuum' 1_runs/2_femgo_3mgo/main.py 1_runs/3_femgo_5mgo/main.py 1_runs/4_femgo_10mgo/main.py`.
- Confirm **no** `poissonsolver`/`dipolelayer` line in any of the three (these are
  plain runs): `grep -L dipolelayer 1_runs/*/main.py`.
- Delete throwaway smoke logs if any; keep real run data out of git (`seed_*/`,
  `*.db`, `*.out`, `gpaw_logs/` are ignored project-wide). Keep `smoke_stack.py`
  if you want to re-verify.
- Tracked additions for a commit: `main.py`, `j_5x5.sh`, `scripts/*.py` per dir.

**Pitfalls:** (1) three dirs, three distinct `N`/`vacuum` — don't mix them up; the
smoke must be run with the value matching the dir; (2) `vacuum` grows only the
clearance — it does not change the 2.106 Å inter-layer spacing or the 0.50 Å
Fe–MgO gap, so don't "fix" those; (3) keep the runs dipole-free (plain
`0_lcb_femgo`); (4) judge compile by `agox_v2`, never the base-python LSP; (5) the
heavy 100-iteration HPC runs are deferred — this instruction stops at the passing
stacking smoke.

---

## INSTR #1 — Stand up a Fe/MgO LCB run with a dipole correction (`1_runs/0_femgo_dip`)

**Date:** 2026-09-06 · **Goal:** create a self-contained run dir under `1_runs/` that
replicates the `0_lcb_femgo` system (Fe(001) overlayer on MgO(001), **no B**,
LCB/GPR AGOX search) and adds a **dipole correction on the vacuum axis (z)** to
the GPAW calculator. You do this by hand; follow the steps in order. When done you
have a compile-clean `main.py` wired with `poissonsolver={'dipolelayer': 'xy'}`,
a matching job script, and a passing smoke test. The heavy 100-iteration HPC run is
out of scope here.

**Source of truth:** copy from
`2_analysist/0_lcb_femgo/` (its `main.py` + `scripts/`). Env for all compile/run
steps below = **`agox_v2`**: `/home/think/miniconda3/envs/agox_v2/bin/python`.
GPAW here is **25.7.0**; in this version the dipole layer is spelled
`dipolelayer` inside a `poissonsolver` dict (verified against
`site-packages/gpaw/test/test_dipole.py`). `SubprocessGPAW` forwards every
`**kwargs` verbatim into the GPAW constructor (`agox/helpers/gpaw_subprocess.py`
→ `gpaw_process`), so adding a `poissonsolver` kwarg is all you need.

---

### Step 1 — Create the run dir and copy the source files

```bash
cd /home/think/Desktop/research/_run/0_lcb
mkdir -p 1_runs/0_femgo_dip
cp -r 2_analysist/0_lcb_femgo/scripts 1_runs/0_femgo_dip/scripts
cp 2_analysist/0_lcb_femgo/main.py 1_runs/0_femgo_dip/main.py
# job script (name it to fit the 1_runs j_*.sh convention; adjust as you like)
cp 2_analysist/0_lcb_femgo/job_5x5_9.sh 1_runs/0_femgo_dip/j_5x5_dip.sh
ls 1_runs/0_femgo_dip 1_runs/0_femgo_dip/scripts | head
```

Expected: the dir holds `main.py`, `j_5x5_dip.sh`, `scripts/` (with
`build_fe_stack.py`, `build_mgo_stack.py`, `build_heteroStruct.py`,
`hetero_struct_randomize.py`, `plot_structure.py`, …). **Do not** copy the
`seed_*/`, `stop_16/`, `trash/`, or any run output — this dir starts empty of data.

### Step 2 — Edit `main.py`: add the dipole correction

Open `1_runs/0_femgo_dip/main.py`. Find the `SubprocessGPAW(...)` call (in the
copied `0_lcb_femgo` source it is the `calc = SubprocessGPAW(` block, roughly
lines 156–171). It currently opens:

```python
    calc = SubprocessGPAW(
        ncores=ncores,
        mode={"name": "lcao"},
        basis="dzp",
        xc="PBE",
        ...
        spinpol=True
    )
```

Add **one line** to the keyword list. Insert immediately after `ncores=ncores,`
(and update the script docstring/comment to note the dipole correction):

```python
    calc = SubprocessGPAW(
        ncores=ncores,
        poissonsolver={"dipolelayer": "xy"},
        mode={"name": "lcao"},
        ...
    )
```

**Why `'xy'`:** the dipole layer is the plane perpendicular to the non-periodic
(vacuum) axis. Here `pbc = [True, True, False]`, so the vacuum/relaxed direction is
**z** and the correction plane is **xy**. `dipolelayer` (no second underscore)
must match the non-periodic axis or GPAW raises `ValueError: System must be
non-periodic perpendicular to dipole-layer`.

That is the only code change required. Do **not** change the physical parameters
(`a_mgo=4.212`, `a_fe=2.870190`, `supercell=(5,5,1)`, `kpts=(1,1,1)`, `kappa=2`,
`N_iterations=100`, LCAO/dzp/PBE, spinpol, `ncores=24`).

### Step 3 — Point the job script at the new `main.py`

`j_5x5_dip.sh` is a straight copy of `job_5x5_9.sh` (PJM headers, `gpaw_env`,
`python ./main.py`). Confirm it still runs `main.py` **from the new dir's cwd**
(it does — `python ./main.py` is relative). Edit the seed/iteration scope only if
you want a narrower first run; otherwise leave as-is. Keep it a bare `#PJM` script;
**never** add `pjsub -x`.

### Step 4 — Smoke test (compile gate first)

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb
$PY -m py_compile 1_runs/0_femgo_dip/main.py && echo "COMPILE OK"
```

Expected: `COMPILE OK`. (The LSP under base `python3` will flag AGOX/ASE imports —
ignore it; judge by `agox_v2`'s `py_compile`.)

### Step 5 — Smoke test (GPAW dipole acceptance run)

Run a reduced slab through a real GPAW calc with the same `poissonsolver` kwarg to
prove the option is **accepted** (config errors surface at initialization, before
the SCF loop) **without** a full 100-iteration AGOX loop. Create
`1_runs/0_femgo_dip/smoke_dipole.py`:

```python
"""Smoke: prove poissonsolver={'dipolelayer':'xy'} is ACCEPTED by GPAW 25.7
(basis must be a top-level kwarg, not inside mode). Full SCF convergence is NOT
required — reaching the SCF loop without a config error is the pass condition."""
import sys
from ase.build import fcc111, add_adsorbate
from gpaw import GPAW, KohnShamConvergenceError

# Tiny asymmetric slab carrying a net dipole along z; not periodic in z.
slab = fcc111('Pt', size=(1, 1, 3), a=3.975534, vacuum=8.0)
add_adsorbate(slab, 'O', height=1.6, position='ontop')
slab.center(vacuum=8.0, axis=2)
slab.pbc = [True, True, False]

# NOTE: 'basis' is a TOP-LEVEL GPAW kwarg, NOT a key inside mode={...}.
calc = GPAW(mode={'name': 'lcao'}, basis='dzp', xc='PBE',
            kpts=(1, 1, 1), poissonsolver={'dipolelayer': 'xy'},
            txt='smoke_dipole.txt', maxiter=8, hund=True, spinpol=True)
slab.calc = calc

try:
    e = slab.get_potential_energy()
    print(f'converged (unexpected): E={e:.4f} eV')
except KohnShamConvergenceError:
    # Reached the SCF loop and ran iterations — dipole kwarg accepted,
    # no config error fired. That is the smoke pass.
    print('SCF loop reached (dipole kwarg accepted, not converged) -> DIPOLE KWARG ACCEPTED')
except Exception as ex:
    print(f'FAIL {type(ex).__name__}: {ex}')
    sys.exit(1)
```

Run it:

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/1_runs/0_femgo_dip
$PY smoke_dipole.py
```

**Expected output:** a line `SCF loop reached (dipole kwarg accepted, not converged)
-> DIPOLE KWARG ACCEPTED`, process exit code 0. (It need **not** fully converge —
an O/Pt metallic slab is slow and may not reach the default tolerance in a handful
of SCF steps; that is expected and acceptable here. A real `ConvergenceError`
means the kwarg was accepted, which is what we are testing.)

#### If Step 5 errored: `LCAO.__init__() got an unexpected keyword argument 'basis'`

**Why:** the earlier (original) smoke script put `basis='dzp'` **inside** the
`mode` dict (`mode={'name': 'lcao', 'basis': 'dzp'}`). In GPAW 25.7 the `mode`
dict's keys are passed straight to the wave-function mode constructor
(`gpaw.wavefunctions.mode.create_wave_function_mode` → `LCAO(...)`), and
`LCAO.__init__` accepts only `atomic_correction`, `interpolation`,
`force_complex_dtype` — **not** `basis`. So `basis` must be a **top-level** GPAW
kwarg, exactly as your real `main.py` already writes it
(`mode={"name": "lcao"}, basis="dzp"` as two separate kwargs). The two `calc`
lines in the earlier smoke had this bug; the corrected script above fixes it
(`mode={'name': 'lcao'}, basis='dzp'`). The error is a `TypeError` raised at
calculator initialization — it has nothing to do with the dipole correction
(which is spelled correctly), so do not "fix" the `dipolelayer` line.

**Fix:** apply the smoke script exactly as written above (move `basis='dzp'` out
of the `mode={...}` dict to a top-level kwarg) and re-run. When it prints
`DIPOLE KWARG ACCEPTED`, Step 5 passes.

### Step 6 — Verify & clean up

- Confirm `grep dipolelayer 1_runs/0_femgo_dip/main.py` shows the kwarg once.
- Delete the throwaway `smoke_dipole.txt` log (and `smoke_dipole.py` if you don't
  want to keep it); keep the real run dir data out of git (`seed_*/`, `*.db`,
  `*.out`, `gpaw_logs/` are ignored project-wide).
- Tracked additions for a commit: `main.py`, `j_5x5_dip.sh`, `scripts/*.py`.

**Pitfalls:** (1) spell it `dipolelayer`, not `dipole_layer`, and put it **inside**
`poissonsolver={...}`, not as a top-level GPAW kwarg; (2) `basis` is a **top-level**
GPAW kwarg — do **not** nest it inside `mode={...}` (that raises
`LCAO.__init__() got an unexpected keyword argument 'basis'`); (3) keep `pbc` z
non-periodic or GPAW errors; (4) don't bump physical params while smoke-testing —
the dipole line must be the only diff vs `0_lcb_femgo`; (5) judge compile by
`agox_v2`, never the base-python LSP.

