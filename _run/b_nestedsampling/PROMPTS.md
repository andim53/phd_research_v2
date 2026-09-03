# PROMPTS — Project b_nestedsampling prompt log

This file logs every prompt the owner adds for future work, numbered simply `#1`,
`#2`, `#3`, ... (newest last). See `AGENTS.md` §3b for the rules.

#1
The DB is dominated at low energy by almost-duplicated structures, so the initial
live points might also include duplicates. To counter that, we can apply the
novelty+force filter here (/home/think/Desktop/research/_run/9_novelFilter) to the
dataset before the initial-live-point selection. Note this is NOT a filter for GPR
training: the GPR still uses the full dataset. Use this filter only when we are
about to choose the initial live points. What do you think? What are the pros and
cons?

#2
Much like in the gpr_accuracy.py code, update the nested-sampling codes to include
--e-max-per-atom (relative to the lowest energy). It will limit the dataset used
for the nested sampling and the GPR training data, and the initial structures for
the nested sampling.

#3
For all the DISCUSSION.md files, include the actual running script that produced
them.

#4
Add an additional analysis. I want to check the accuracy + uncertainty across
different delta Fe_z (the Fe island height: the distance between the highest Fe
z-axis height and the lowest Fe z-axis height).

#5
Include an analysis of different rattling distances versus GPR performance
(accuracy and uncertainty): take structures from the database, rattle them under
different ranges, then predict their energy. I want to check how much rattling
distance the kernel can handle (rattle only Fe by default; provide a way to choose
which atoms to rattle). Clarify each step.

#6
Include an uncertainty analysis showing the uncertainty across the energy levels.

#7
Make a new code for this project:
/home/think/Desktop/research/_run/b_nestedsampling/. It's the kernel GPR accuracy
analysis code. It will extract the performance of the GPR model under different
energy ranges. Specifically, I want to see the accuracy (using MAE, RMSE, R^2) of
the GPR model in predicting the energy of the structures, as a function of the
energy range.
