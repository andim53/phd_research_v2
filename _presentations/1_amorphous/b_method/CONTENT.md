# B — Method

## 1. Why we need a fast relaxer

- To investigate the **disordering formation**, we need to perform **multiple rapid
  atomic relaxations**.
- Doing this with regular **ab-initio** calculations is **expensive**.

> **Speaker notes.** The method is driven by cost: many relaxations are needed, so
> ab-initio alone is too slow.

## 2. ML surrogate for relaxation

- We use **machine learning**, specifically tuned to **find the most relaxed atomic
  structure**.
- We **randomize the atom**, then **relax it with the GPR** surrogate.

> **Speaker notes.** The ML surrogate replaces the expensive ab-initio relaxer.

## 3. Sampling the low-energy basin

- We **gather the low-energy basin** of the structure.
- This lets us **investigate its stability**.

> **Speaker notes.** Collecting the low-energy basin is how we probe stability cheaply.
