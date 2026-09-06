# INSTRUCTION.md — Owner-side How-To Playbook

This file holds **owner-executable instructions**: step-by-step, line-by-line,
command-by-command guides that let YOU (the project owner) do the work by hand
that the AI agent would otherwise do. The agent's job is to **instruct** — to
write the how-to — not to perform the task.

## Convention (governed by `AGENTS.md`)

- **Append-only.** When the owner asks the agent to *prepare an instruction*
  for a task, the agent **appends** a new self-contained block to the **end** of
  this file (newest last, oldest first — same convention as `LOG.md` /
  `PROMPTS.md`). It never reads back and rewrites or replaces prior blocks.
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

### Step 5 — Smoke test (tiny GPAW dipole acceptance run)

Run a reduced slab through a real GPAW calc with the same `poissonsolver` kwarg to
prove the option is accepted and a dipole correction is applied, **without** a full
100-iteration AGOX loop. Create `1_runs/0_femgo_dip/smoke_dipole.py`:

```python
"""Smoke: confirm poissonsolver={'dipolelayer':'xy'} is accepted + applied by GPAW 25.7."""
from ase.build import fcc111, add_adsorbate
from ase import Atoms
from gpaw import GPAW

# Tiny asymmetric slab carrying a net dipole along z (not periodic in z).
slab = fcc111('Pt', size=(1, 1, 3), a=3.975534, vacuum=8.0)
add_adsorbate(slab, 'O', height=1.6, position='ontop')
slab.center(vacuum=8.0, axis=2)
slab.pbc = [True, True, False]

calc = GPAW(mode={'name': 'lcao', 'basis': 'dzp'}, xc='PBE',
            kpts=(1, 1, 1), poissonsolver={'dipolelayer': 'xy'},
            txt='smoke_dipole.txt', maxiter=25, hund=True, spinpol=True)
slab.calc = calc
e_dip = slab.get_potential_energy()
print(f'energy(dipole ON)  = {e_dip:.6f} eV')

calc2 = GPAW(mode={'name': 'lcao', 'basis': 'dzp'}, xc='PBE',
             kpts=(1, 1, 1), txt='smoke_nodip.txt', maxiter=25,
             hund=True, spinpol=True)
slab2 = fcc111('Pt', size=(1, 1, 3), a=3.975534, vacuum=8.0)
add_adsorbate(slab2, 'O', height=1.6, position='ontop')
slab2.center(vacuum=8.0, axis=2); slab2.pbc = [True, True, False]
slab2.calc = calc2
e_nodip = slab2.get_potential_energy()
print(f'energy(dipole OFF) = {e_nodip:.6f} eV')
print('DIPOLE SMOKE OK' if e_dip != e_nodip else 'NO DIPOLE EFFECT (check config)')
```

Run it (a few tens of SCF steps on ~10 atoms — minutes):

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/1_runs/0_femgo_dip
$PY smoke_dipole.py
```

**Expected output:**
- SCF converges for both calculators (no `TypeError` / "unexpected keyword", no
  `ValueError: ... non-periodic perpendicular to dipole-layer`). Convergence of a
  single run to an error means the kwarg is wrong — re-check spelling `dipolelayer`
  and plane `'xy'`.
- `energy(dipole ON)` differs from `energy(dipole OFF)` (the correction shifts the
  slab total energy), and the last line prints `DIPOLE SMOKE OK`.

### Step 6 — Verify & clean up

- Confirm `grep dipolelayer 1_runs/0_femgo_dip/main.py` shows the kwarg once.
- Delete the throwaway `smoke_dipole.txt` / `smoke_nodip.txt` logs and
  `smoke_dipole.py` if you don't want to keep them; keep the real run dir data out
  of git (`seed_*/`, `*.db`, `*.out`, `gpaw_logs/` are ignored project-wide).
- Tracked additions for a commit: `main.py`, `j_5x5_dip.sh`, `scripts/*.py`.

**Pitfalls:** (1) spell it `dipolelayer`, not `dipole_layer`, and put it **inside**
`poissonsolver={...}`, not as a top-level GPAW kwarg; (2) keep `pbc` z non-periodic
or GPAW errors; (3) don't bump physical params while smoke-testing — the dipole
line must be the only diff vs `0_lcb_femgo`; (4) judge compile by `agox_v2`, never
the base-python LSP.

