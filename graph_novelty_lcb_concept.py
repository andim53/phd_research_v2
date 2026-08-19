#!/usr/bin/env python3
"""
Conceptual visualization of the Novelty-LCB acquisition function.

Produces a 3-panel figure saved to novelty_lcb_concept.png, showing:
  Panel 1: 1D energy landscape + GPR mean/uncertainty + energy window + DB points
  Panel 2: Novelty(x) = min_i ||fingerprint(x) - fingerprint(x_i)||
  Panel 3: a(x) = sigma(x) + lambda * Novelty(x) with energy-window exclusion

This graphs the COMPLETE idea: how uncertainty alone would revisit local
minima, how novelty pushes the search outward, how the energy window
focuses on a target range, and how lambda balances the trade-off.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ── 0. Setup ────────────────────────────────────────────────────────────────
np.random.seed(42)
x = np.linspace(0, 10, 500)

# True "energy landscape" — a few Gaussian wells (the PES)
true_e = (
    -3.0 * np.exp(-0.5 * ((x - 2.0) / 0.6) ** 2)
    - 2.5 * np.exp(-0.5 * ((x - 5.5) / 0.8) ** 2)
    - 2.0 * np.exp(-0.5 * ((x - 8.0) / 0.5) ** 2)
    + 0.5 * np.sin(x) * 0.1
)

# ── 1. Simulated GPR predictions ────────────────────────────────────────────
# Simulated "database" — a few points already evaluated
db_positions = np.array([1.8, 2.2, 5.3, 5.7, 8.1])
db_energies = np.array([-2.8, -3.1, -2.3, -2.6, -1.9])

def gpr_mean(xp):
    """Simulated GPR mean: smooth interpolation of DB + bias."""
    mu = np.zeros_like(xp)
    for xi, ei in zip(db_positions, db_energies):
        mu += ei * np.exp(-0.5 * ((xp - xi) / 1.2) ** 2)
    kernel_sum = np.sum(np.exp(-0.5 * ((xp[:, None] - db_positions) / 1.2) ** 2), axis=1)
    mu = mu / np.maximum(kernel_sum, 0.3)
    mu += 0.2 * np.sin(xp * 0.5)
    return mu

def gpr_uncertainty(xp):
    """Uncertainty: low near DB points, high far from them."""
    dists = np.abs(xp[:, None] - db_positions)
    min_dist = np.min(dists, axis=1)
    sigma = 0.05 + 0.45 * (1.0 - np.exp(-min_dist / 1.5))
    return sigma

mu = gpr_mean(x)
sigma = gpr_uncertainty(x)

# ── 2. Energy window ────────────────────────────────────────────────────────
E_target = -2.5
delta_E = 0.4
window_lo = E_target - delta_E
window_hi = E_target + delta_E

# ── 3. Novelty = min distance to DB in "fingerprint space" ──────────────────
# In 1D we proxy fingerprint distance with |x - x_i| (Euclidean in 1D)
def novelty(xp):
    dists = np.abs(xp[:, None] - db_positions)
    return np.min(dists, axis=1)

nov = novelty(x)

# ── 4. Acquisition function a(x) = sigma(x) + lambda * Novelty(x) ──────────
lam = 0.6
a_raw = sigma + lam * nov

# Apply energy window: outside → -inf (excluded)
in_window = (mu >= window_lo) & (mu <= window_hi)
a = np.where(in_window, a_raw, -np.inf)

# ── 5. Select best candidate (max a(x) within window) ───────────────────────
finite_mask = np.isfinite(a)
if np.any(finite_mask):
    best_idx = np.argmax(a[finite_mask])
    finite_indices = np.where(finite_mask)[0]
    best_x = x[finite_indices[best_idx]]
    best_a = a[finite_indices[best_idx]]
else:
    best_x = None
    best_a = None

# ── 6. Plot ──────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(10, 11), sharex=True)

# --- Panel 1: Energy landscape + GPR + window + DB ---
ax1 = axes[0]
ax1.plot(x, true_e, "k--", lw=1.2, alpha=0.6, label="True PES (unknown to GPR)")
ax1.plot(x, mu, "b-", lw=2.0, label="GPR mean μ(x)")
ax1.fill_between(x, mu - sigma, mu + sigma, color="orange", alpha=0.20, label="GPR ±σ(x)")
ax1.plot(x, mu - sigma, "orange", lw=0.8, alpha=0.5)
ax1.plot(x, mu + sigma, "orange", lw=0.8, alpha=0.5)

ax1.axhspan(window_lo, window_hi, color="green", alpha=0.12, label="Energy window")
ax1.axhline(E_target, color="green", lw=1.0, ls=":", alpha=0.7)
ax1.axhline(window_lo, color="green", lw=0.8, ls="--", alpha=0.5)
ax1.axhline(window_hi, color="green", lw=0.8, ls="--", alpha=0.5)
ax1.text(x[-1] - 0.3, E_target, f"E_target = {E_target:.1f} eV",
         color="green", fontsize=9, va="center", ha="right")

ax1.scatter(db_positions, db_energies, color="red", s=60, zorder=5,
            edgecolors="black", linewidths=0.8, label="DB structures")
for xi, ei in zip(db_positions, db_energies):
    ax1.annotate(f"  DB@{xi:.1f}", (xi, ei), fontsize=7, color="red",
                 xytext=(4, 4), textcoords="offset points")

if best_x is not None:
    best_mu = gpr_mean(np.array([best_x]))[0]
    ax1.scatter([best_x], [best_mu], color="green", s=120, zorder=6,
                marker="*", edgecolors="black", linewidths=0.8,
                label=f"Selected candidate (x={best_x:.2f})")

ax1.set_ylabel("Energy [eV]", fontsize=11)
ax1.set_title("Panel 1 — Energy Landscape, GPR Prediction & Energy Window",
              fontsize=12, fontweight="bold")
ax1.legend(loc="upper right", fontsize=8, framealpha=0.9)
ax1.set_ylim(true_e.min() - 0.8, true_e.max() + 0.8)
ax1.grid(True, alpha=0.25)

# --- Panel 2: Novelty ---
ax2 = axes[1]
ax2.plot(x, nov, color="purple", lw=2.0, label="Novelty(x) = minᵢ d_fp(x, xᵢ)")
ax2.fill_between(x, nov, color="purple", alpha=0.12)
for xi in db_positions:
    ax2.axvline(xi, color="red", ls=":", alpha=0.15, label="_nolegend_")

ax2.set_ylabel("Novelty [a.u.]", fontsize=11)
ax2.set_title("Panel 2 — Structural Novelty (distance to nearest DB structure)",
              fontsize=12, fontweight="bold")
ax2.legend(loc="upper left", fontsize=8)
ax2.grid(True, alpha=0.25)

# --- Panel 3: Acquisition function ---
ax3 = axes[2]
plot_x = x[finite_mask]
plot_a = a[finite_mask]
ax3.plot(plot_x, plot_a, "g-", lw=2.2,
         label=f"a(x) = σ(x) + {lam}·Novelty(x)  [in window]")

excluded = ~finite_mask
if np.any(excluded):
    ax3.fill_between(x[excluded], -0.05, 0, color="red", alpha=0.15)
    ax3.scatter(x[excluded], np.full(np.sum(excluded), -0.02),
                color="red", s=3, alpha=0.5, marker="|")

ax3.text(0.02, 0.95, f"λ = {lam}", transform=ax3.transAxes,
         fontsize=10, va="top", bbox=dict(boxstyle="round", fc="white", alpha=0.8))

if best_x is not None:
    ax3.scatter([best_x], [best_a], color="green", s=150, zorder=6,
                marker="*", edgecolors="black", linewidths=0.8)
    ax3.annotate(
        f"  max a(x) = {best_a:.3f}\n  at x = {best_x:.2f}",
        (best_x, best_a),
        fontsize=8, color="darkgreen",
        xytext=(10, 10), textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color="darkgreen", lw=0.8),
    )

ax3.set_ylabel("a(x)  [higher = better]", fontsize=11)
ax3.set_xlabel("Position x  [structural coordinate]", fontsize=11)
ax3.set_title("Panel 3 — Acquisition Function a(x) = σ(x) + λ·Novelty(x)\n"
              "(out-of-window candidates excluded → a(x) = −∞)",
              fontsize=12, fontweight="bold")
ax3.legend(loc="upper left", fontsize=8)
ax3.grid(True, alpha=0.25)

plt.tight_layout()
outpath = "/home/think/Desktop/research/novelty_lcb_concept.png"
plt.savefig(outpath, dpi=150, bbox_inches="tight")
print(f"Saved concept figure: {outpath}")
print(f"  Best candidate: x={best_x:.3f}, a(x)={best_a:.4f}")
print(f"  Energy window: [{window_lo:.2f}, {window_hi:.2f}] eV")
print(f"  λ = {lam}")
plt.close()
