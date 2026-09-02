# A — Introduction

## 1. Why amorphous for SOT-MRAM?

- **Spin-orbit torque (SOT) MRAM** is a leading candidate for next-generation magnetic memory: fast, non-volatile, low power.
- The **heavy-metal / ferromagnet interface** is where the spin-orbit torque is generated — and the choice of the **underlayer material** dictatesthe efficiency.

  ![placeholder — SOT-MRAM schematic showing heavy-metal underlayer + ferromagnet](pngs/sot-mram-schematic.png)
- **Amorphous heavy metals** (e.g. W, Ta, Pt) offer a practically attractive route: they can be deposited as smooth, uniform underlayers at scale, unlike crystalline ones.

  ![placeholder — crystalline vs amorphous underlayer illustration](pngs/crystalline-vs-amorphous.png)

> **Speaker notes.** Frame the pitch: amorphous metals make the SOT-MRAM stack manufacturable — but computing their spintronics needs a handle on their structure-first.

## 2. Purpose of this work

Compute the **spintronics properties** (spin-Hall conductivity, SHC; spin-orbit torque efficiency) for **amorphous** systems, in a way that respects their **structural disorder**.

> **Speaker notes.** One sentence: "We want the spintronics of amorphous metals — computed correctly for an intrinsically disordered structure."

## 3. The structural problem

- To compute any electronic/spintronics property, we first need a **concrete structure** to run calculations on.
- **Amorphous = no lattice periodicity**→ the very definition of the structure is non-trivial.


  ![placeholder — amorphous structural disorder definition figure](pngs/amorph-disorder-def.png)
- **Melt-quench** is the standard way to build amorphous samples, but it is hard to know whether the quenched structure is truly **stable** (its exact thermodynamic stability is difficult to define positively).

> **Speaker notes.** This sets upthe tension: the difficulty is not the electronic structure problem, but the *structural-definition* problem that comes first.

## 4. Research question

> **One-line question this deck answers:** *Can we define stable, representative amorphous structures — and compute their spin-Hall conductivity as a well-defined statistical property?*