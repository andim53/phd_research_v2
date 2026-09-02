# B — Method

## 1. Idea: sample configurational space, focus on the low-energy basin

- To resolve the stability problem, we do NOT pin a single melt-quenched snapshot, we perform a **configurational-space sampling** focused on the **low-energy configurations**.
- **Why the low-energy basin?** It is where the **most stable structures** live.



> **Speaker notes.** "Instead of betting on one quench, we sample the low-energy part of structure space — the stable region."

## 2. From sampled minima → a statistical property

- Locating the **multiple low-energy snapshot** amorphous structures within the low-energy basin
- Then define the **spin-Hall conductivity (SHC) as a statistical property** averaged over those low-energy structures.



> **Speaker notes.** The disorder is not a bug to average away — it is the object; SHC becomes a distribution over the stable-amorphous ensemble.

## 3. Active-learning ML method (Inherent Structure approach)

- Incorporate an **active-learning machine-learning model** to **locate the local minima** and derive their **preliminary local-minimum configurations** — the **Inherent Structure** picture.
- **Generation step:** use **dual-scale randomization** to propose new structures (small local moves + large barrier-crossing moves).
- **Relaxation step:** use the **ML surrogate** to **relax each proposed structure into the low-energy basin**.
- The **relaxed structure** becomes the **cumulated local minimum** — a structure resident within the low-energy state / basin.



> **Speaker notes.** Map the two roles clearly: randomization explores, surrogate relaxation descends to the basin, and each relaxed minimum is collected into the stable ensemble..

  ![placeholder — method workflow: dual-scale randomization -> ML relaxation -> relaxed local minima (basin)](pngs/method-workflow.png]

  ![placeholder — active-learning loop schematic (generate -> relax -> select/train (repeat](pngs/method-active-learning.png)

## 4. Key parameters / choices

- **Move set:** dual-scale randomization (small = local refinement, large = basin hopping.
- **Energy model:** ML surrogate (cheap enough to relax many candidates into the basin)
- **Sampling window:** focused on the low-energy region (not the full landscape)



> **Speaker notes.** Eich choice exists to make the relax-to-basin cheap and the sampling stay near stabilitywhere THE thermodynamics lives.> **Placeholder — figures to supply (will be added to pngs/):** `method-workflow.png`, `method-active-learning.png`.