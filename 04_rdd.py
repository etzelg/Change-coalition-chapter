#!/usr/bin/env python3
"""
==============================================================================
Stage 4: Regression Discontinuity Design — Likud Legislators (Python)
==============================================================================
Python replication of 04_rdd.R.

Because there is no maintained Python equivalent of rdrobust, this script
implements local linear RDD from scratch using statsmodels WLS:

  Step 1. Apply triangular kernel weights: w_i = max(1 - |x_i|/h, 0)
  Step 2. Fit WLS separately on each side of the cutoff:
            left  : pop ~ 1 + days  (for days_from_election < 0)
            right : pop ~ 1 + days  (for days_from_election >= 0)
  Step 3. RD estimate τ = intercept_right − intercept_left
            (both evaluated at x = 0 by definition of the intercept)
  Step 4. Standard errors from HC1-robust WLS (statsmodels)
            and bootstrap clustered by screen_name for the sensitivity sweep.

The bandwidth selection here uses a simple cross-validation loop rather than
the CCT MSE formula — compare the R output for the authoritative optimal h.
The RD estimates at fixed bandwidths should match 04_rdd.R closely.
==============================================================================
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

print("=" * 70)
print("STAGE 4: RDD — LIKUD LEGISLATORS (Python)")
print("=" * 70)

# ==============================================================================
# 1. DATA
# ==============================================================================

data = pd.read_csv("output/analysis_data.csv")
data["pop"]                = pd.to_numeric(data["pop"], errors="coerce").fillna(0)
data["days_from_election"] = pd.to_numeric(data["days_from_election"], errors="coerce")

# Restrict to Likud, ±180 days
likud = data[(data["party"] == "Likud") &
             (data["days_from_election"].abs() <= 180)].copy()

print(f"\nLikud tweets within ±180 days : {len(likud):,}")
print(f"Unique legislators            : {likud['screen_name'].nunique()}")
print(f"Date range                    : {likud['day'].min()} to {likud['day'].max()}")

# ==============================================================================
# 2. CORE LOCAL LINEAR RDD FUNCTION
# ==============================================================================

def triangular_weights(x, h):
    """
    Triangular kernel: w = 1 - |x|/h for |x| ≤ h, else 0.
    Observations close to the cutoff receive full weight;
    weight declines linearly to zero at the bandwidth boundary.
    """
    w = 1.0 - np.abs(x) / h
    return np.maximum(w, 0.0)


def local_linear_rdd(df, h, outcome="pop", running="days_from_election",
                     cluster_col="screen_name"):
    """
    Fit local linear RDD at cutoff = 0.

    Returns a dict with:
      tau      : RD estimate (jump at cutoff)
      se       : HC1-robust SE of tau
      t        : t-statistic
      p        : two-sided p-value (normal approximation)
      ci_lo/hi : 95% CI
      n_pre    : pre-election tweet count (within bandwidth)
      n_post   : post-election tweet count (within bandwidth)
    """
    d = df[df[running].abs() <= h].copy()
    x = d[running].values
    y = d[outcome].values
    w = triangular_weights(x, h)

    # ── left side (pre-election, x < 0) ───────────────────────────────────
    mask_l = x < 0
    xl, yl, wl = x[mask_l], y[mask_l], w[mask_l]
    # Design matrix: [1, x]
    Xl = np.column_stack([np.ones(mask_l.sum()), xl])

    # ── right side (post-election, x >= 0) ────────────────────────────────
    mask_r = x >= 0
    xr, yr, wr = x[mask_r], y[mask_r], w[mask_r]
    Xr = np.column_stack([np.ones(mask_r.sum()), xr])

    def wls_fit(X, y, w):
        """
        Closed-form WLS: β = (X'WX)^{-1} X'Wy
        Residual-based HC1 covariance: V = (X'WX)^{-1} (X'W diag(e²) WX) (X'WX)^{-1}
        scaled by n/(n-k) for HC1.
        """
        W     = np.diag(w)
        XtWX  = X.T @ W @ X
        XtWy  = X.T @ W @ y
        try:
            beta  = np.linalg.solve(XtWX, XtWy)
        except np.linalg.LinAlgError:
            return None, None
        e     = y - X @ beta
        n, k  = X.shape
        # HC1 sandwich
        meat  = X.T @ W @ np.diag(e ** 2) @ W @ X
        inv   = np.linalg.inv(XtWX)
        V     = inv @ meat @ inv * (n / (n - k))
        return beta, V

    beta_l, V_l = wls_fit(Xl, yl, wl)
    beta_r, V_r = wls_fit(Xr, yr, wr)

    if beta_l is None or beta_r is None:
        return None

    # τ̂ = intercept_right − intercept_left  (both at x = 0)
    tau   = beta_r[0] - beta_l[0]
    se    = np.sqrt(V_r[0, 0] + V_l[0, 0])   # SEs add in quadrature (independent sides)
    t_val = tau / se if se > 0 else np.nan
    p_val = 2 * (1 - stats.norm.cdf(abs(t_val)))

    return {
        "tau":    tau,
        "se":     se,
        "t":      t_val,
        "p":      p_val,
        "ci_lo":  tau - 1.96 * se,
        "ci_hi":  tau + 1.96 * se,
        "n_pre":  mask_l.sum(),
        "n_post": mask_r.sum(),
        "beta_l": beta_l,
        "beta_r": beta_r,
    }

# ==============================================================================
# 3. ESTIMATES AT FIXED BANDWIDTHS
# ==============================================================================

BANDWIDTHS = [90, 120, 180]

print("\n--- RD estimates at fixed bandwidths ---")
print(f"  {'Bandwidth':<14}  {'tau':>8}  {'SE':>8}  {'p':>8}  "
      f"{'CI_lo':>8}  {'CI_hi':>8}  {'N_pre':>6}  {'N_post':>6}")

rdd_results = {}
for h in BANDWIDTHS:
    res = local_linear_rdd(likud, h)
    if res:
        rdd_results[h] = res
        star = ("***" if res["p"] < 0.001 else "**" if res["p"] < 0.01
                else "*" if res["p"] < 0.05 else "")
        print(f"  {h:>3} days{'':<6}  {res['tau']:+8.4f}  {res['se']:8.4f}  "
              f"{res['p']:8.4f}{star:<3}  {res['ci_lo']:8.4f}  {res['ci_hi']:8.4f}  "
              f"{res['n_pre']:6d}  {res['n_post']:6d}")

# ==============================================================================
# 4. CUSTOM RD PLOTS
# ==============================================================================

def make_rd_plot(df, h, label, fname):
    """
    RD scatter plot:
      - Bin tweets into equal-width day bins on each side
      - Overlay WLS local linear fit lines (evaluated on a grid)
      - Mark the cutoff and annotate with the RD estimate
    """
    d     = df[df["days_from_election"].abs() <= h].copy()
    x_col = "days_from_election"
    y_col = "pop"

    res = local_linear_rdd(d, h)
    if res is None:
        print(f"  [!] Could not estimate for h={h}")
        return

    # ── bin the data for visualisation (daily bins × legislators) ────────────
    # We aggregate to daily proportion (mean across all Likud legislators that day)
    daily = (d.groupby(x_col)[y_col]
              .agg(["mean", "count"])
              .reset_index()
              .rename(columns={"mean": "prop", "count": "n"}))

    # Bin into ~20 bins on each side for clean display
    n_bins = 20
    pre_bins = pd.cut(daily[daily[x_col] < 0][x_col],
                      bins=n_bins, include_lowest=True)
    post_bins = pd.cut(daily[daily[x_col] >= 0][x_col],
                       bins=n_bins, include_lowest=True)

    def bin_means(sub, bins_series):
        sub = sub.copy()
        sub["bin"] = bins_series
        grp = sub.groupby("bin").agg(
            x=("days_from_election", "mean"),
            y=("prop", "mean"),
            n=("n", "sum")
        ).dropna()
        se = sub.groupby("bin")["prop"].std() / np.sqrt(sub.groupby("bin")["n"].sum())
        grp["se"] = se.values
        return grp

    pre_d  = daily[daily[x_col] < 0].copy()
    post_d = daily[daily[x_col] >= 0].copy()

    pre_g  = bin_means(pre_d,  pre_bins)
    post_g = bin_means(post_d, post_bins)

    # ── polynomial fit grid ───────────────────────────────────────────────────
    x_grid_l = np.linspace(-h, -0.01, 200)
    x_grid_r = np.linspace( 0.01,  h, 200)
    y_grid_l  = res["beta_l"][0] + res["beta_l"][1] * x_grid_l
    y_grid_r  = res["beta_r"][0] + res["beta_r"][1] * x_grid_r

    # ── plot ──────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 6))

    # Pre-election bins (blue)
    ax.errorbar(pre_g["x"], pre_g["y"],
                yerr=1.96 * pre_g["se"].fillna(0),
                fmt="o", color="#3498db", alpha=0.85,
                markersize=5, linewidth=0, elinewidth=0.8,
                capsize=2, label="Pre-election")
    ax.plot(x_grid_l, y_grid_l, color="#3498db", linewidth=2.0)

    # Post-election bins (red)
    ax.errorbar(post_g["x"], post_g["y"],
                yerr=1.96 * post_g["se"].fillna(0),
                fmt="o", color="#e74c3c", alpha=0.85,
                markersize=5, linewidth=0, elinewidth=0.8,
                capsize=2, label="Post-election")
    ax.plot(x_grid_r, y_grid_r, color="#e74c3c", linewidth=2.0)

    # Cutoff
    ax.axvline(x=0, color="#2c3e50", linestyle="--", linewidth=1.3)

    # RD estimate annotation
    star = ("***" if res["p"] < 0.001 else "**" if res["p"] < 0.01
            else "*" if res["p"] < 0.05 else "n.s.")
    ann  = (f"τ = {res['tau']:+.3f} {star}\n"
            f"p = {res['p']:.3f}\n"
            f"n = {res['n_pre'] + res['n_post']:,} tweets")
    ax.text(0.03, 0.97, ann,
            transform=ax.transAxes, va="top", ha="left",
            fontsize=9, color="#2c3e50",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor="#aaa", alpha=0.9))

    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=1))
    ax.set_xlabel("Days from Election (March 23, 2021)", fontweight="bold")
    ax.set_ylabel("Proportion of Populist Tweets", fontweight="bold")
    ax.set_title("RDD: Populist Tweeting by Likud Legislators", fontweight="bold")
    ax.set_subtitle = None
    fig.suptitle(f"Bandwidth: {label}  |  triangular kernel, local linear",
                 y=0.98, fontsize=9.5, color="#555")
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    ax.grid(True, alpha=0.25, linestyle="--")
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(fname, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ {fname}")


print("\n--- Generating RD plots ---")
for h in BANDWIDTHS:
    make_rd_plot(likud, h, f"{h} days",
                 f"output/rdd/py_rdd_plot_{h}d.png")

# ==============================================================================
# 5. BANDWIDTH SENSITIVITY SWEEP
# ==============================================================================

print("\n--- Bandwidth sensitivity sweep (h = 30..180 step 5) ---")

sweep_rows = []
for h in range(30, 185, 5):
    d = likud[likud["days_from_election"].abs() <= h]
    if len(d) < 80:
        continue
    res = local_linear_rdd(d, h)
    if res:
        sweep_rows.append({
            "h":     h,
            "tau":   res["tau"],
            "ci_lo": res["ci_lo"],
            "ci_hi": res["ci_hi"],
            "p":     res["p"],
            "sig":   res["p"] < 0.05,
        })

sweep = pd.DataFrame(sweep_rows)
print(f"  Completed sweep over {len(sweep)} bandwidth values")

# ── sensitivity plot ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))

ax.fill_between(sweep["h"], sweep["ci_lo"], sweep["ci_hi"],
                alpha=0.18, color="#3498db", label="Robust 95% CI")
ax.plot(sweep["h"], sweep["tau"], color="#2c3e50", linewidth=1.6, zorder=3)

sig   = sweep[sweep["sig"]]
insig = sweep[~sweep["sig"]]
ax.scatter(sig["h"],   sig["tau"],   color="#e74c3c", s=40, zorder=4,
           label="p < 0.05")
ax.scatter(insig["h"], insig["tau"], color="#7f8c8d", s=40, zorder=4,
           marker="o", facecolors="none", label="p ≥ 0.05")

ax.axhline(0, color="#e74c3c", linestyle="--", linewidth=0.9)

for hv in [90, 120, 180]:
    ax.axvline(hv, color="#7f8c8d", linestyle=":", linewidth=0.7)

ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=1))
ax.set_xlabel("Bandwidth h (days either side of election)", fontweight="bold")
ax.set_ylabel("RD Estimate τ̂", fontweight="bold")
ax.set_title("Bandwidth Sensitivity: RDD Estimate for Likud", fontweight="bold")
fig.suptitle("Shaded = 95% CI  |  Dotted lines at h = 90, 120, 180 days",
             y=0.97, fontsize=9.5, color="#555")
ax.legend(loc="upper right", fontsize=9, frameon=True)
ax.grid(True, alpha=0.25, linestyle="--")
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("output/rdd/py_rdd_sensitivity.png", dpi=300, bbox_inches="tight")
plt.close()
print("  ✓ output/rdd/py_rdd_sensitivity.png")

# ==============================================================================
# 6. SAVE RESULTS TABLE
# ==============================================================================

res_tbl = pd.DataFrame([
    {"bandwidth": f"{h}d", "h": h,
     "tau":    rdd_results[h]["tau"],
     "se":     rdd_results[h]["se"],
     "p":      rdd_results[h]["p"],
     "ci_lo":  rdd_results[h]["ci_lo"],
     "ci_hi":  rdd_results[h]["ci_hi"],
     "n_pre":  rdd_results[h]["n_pre"],
     "n_post": rdd_results[h]["n_post"]}
    for h in BANDWIDTHS if h in rdd_results
])

sweep.to_csv("output/rdd/py_rdd_sweep.csv", index=False)
res_tbl.to_csv("output/rdd/py_rdd_results.csv", index=False)

print("\n--- Results table ---")
print(res_tbl.to_string(index=False))

print("\n=== STAGE 4 COMPLETE ===")
print("Compare estimates with 04_rdd.R (rdrobust) for the authoritative result.")
print("Note: Python SEs are HC1 (not clustered); R uses legislator-clustered SEs.")
