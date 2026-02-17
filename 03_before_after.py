#!/usr/bin/env python3
"""
==============================================================================
Stage 3: Before/After Statistical Analysis — Election Cutoff
==============================================================================
Comparison 1 (main):
  PRE  = ALL 7 parties
  POST = Likud + Religious Zionism  → "Radicalized and Radical Populism"

Comparison 2 (corollary):
  PRE & POST = Rightwards + Israel Our Home → "PRRPs in Change Coalition"

Plot 3a  – Comparison 1 overall bar
Plot 3b  – Comparison 1 detail: Likud | PRR legislators (named, expanding group)
Plot 3c  – Comparison 2 overall bar
Plot 3d  – Comparison 2 detail: Rightwards | Israel Our Home
==============================================================================
"""

import pandas as pd
import numpy as np
import pickle
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from scipy import stats
from datetime import datetime

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300

COL_PRE  = "#3498db"   # blue
COL_POST = "#e74c3c"   # red

print("=" * 70)
print("STAGE 3: BEFORE/AFTER STATISTICAL ANALYSIS")
print("=" * 70)

data = pd.read_pickle("output/analysis_data.pkl")
print(f"\nLoaded {len(data):,} rows")

# Named-legislator lists
PRR_PRE_NAMES  = ["bezalelsm", "michalwoldiger", "ofir_sofer", "oritstrock"]
PRR_POST_NAMES = ["bezalelsm", "michalwoldiger", "ofir_sofer", "oritstrock",
                  "rothmar", "itamarbengvir"]

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def summary_stats(series_pre, series_post, label_pre, label_post):
    """Return a one-row-per-period summary dataframe."""
    rows = []
    for label, s in [(label_pre, series_pre), (label_post, series_post)]:
        rows.append({"period": label,
                     "total_tweets":    len(s),
                     "populist_tweets": int(s.sum()),
                     "mean_prop":       s.mean(),
                     "se_prop":         s.std() / np.sqrt(len(s))})
    return pd.DataFrame(rows)

def run_tests(series_pre, series_post):
    """t-test, chi-square, Cohen's d, Cramér's V."""
    t_stat, t_p = stats.ttest_ind(series_pre, series_post)
    pre_m  = series_pre.mean()
    post_m = series_post.mean()
    pool   = np.sqrt(((len(series_pre)-1)*series_pre.std()**2 +
                      (len(series_post)-1)*series_post.std()**2) /
                     (len(series_pre)+len(series_post)-2))
    d = (post_m - pre_m) / pool if pool > 0 else 0.0
    pct = (post_m - pre_m) / pre_m * 100 if pre_m > 0 else float("nan")

    ct = np.array([[int((series_pre  == 0).sum()), int(series_pre.sum())],
                   [int((series_post == 0).sum()), int(series_post.sum())]])
    chi2, chi_p, dof, _ = stats.chi2_contingency(ct)
    n = ct.sum()
    v = np.sqrt(chi2 / (n * (min(ct.shape) - 1))) if n > 0 else 0.0

    return {"t": t_stat, "t_p": t_p,
            "pre_mean": pre_m, "post_mean": post_m,
            "diff": post_m - pre_m, "pct_change": pct,
            "cohens_d": d, "chi2": chi2, "chi_p": chi_p, "cramers_v": v}

def bar_two(ax, df, title, color_map=None):
    """Simple two-bar (pre vs post overall) plot."""
    periods = df["period"].tolist()
    vals    = df["mean_prop"].tolist()
    errs    = (1.96 * df["se_prop"]).tolist()
    colors  = [color_map.get(p, COL_PRE) if color_map else
               (COL_PRE if "Pre" in p else COL_POST) for p in periods]

    bars = ax.bar(periods, vals, yerr=errs, color=colors, edgecolor="black",
                  linewidth=1.4, alpha=0.88, capsize=6, width=0.5)
    for bar, v, e in zip(bars, vals, errs):
        ax.text(bar.get_x() + bar.get_width()/2,
                v + e + 0.003, f"{v:.2%}",
                ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=1))
    ax.set_ylabel("Proportion of Populist Tweets", fontweight="bold")
    ax.set_title(title, fontweight="bold", pad=10)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

def bar_grouped(ax, parties, pre_vals, post_vals, pre_errs, post_errs,
                title, pct_changes):
    """Grouped bar plot (two bars per x-category)."""
    x     = np.arange(len(parties))
    w     = 0.35
    b_pre = ax.bar(x - w/2, pre_vals,  w, yerr=pre_errs,
                   label="Pre-election",  color=COL_PRE,  edgecolor="black",
                   linewidth=1.4, alpha=0.88, capsize=5)
    b_pos = ax.bar(x + w/2, post_vals, w, yerr=post_errs,
                   label="Post-election", color=COL_POST, edgecolor="black",
                   linewidth=1.4, alpha=0.88, capsize=5)

    for bar, v, e in zip(b_pre, pre_vals, pre_errs):
        ax.text(bar.get_x() + bar.get_width()/2,
                v + e + 0.003, f"{v:.2%}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")
    for bar, v, e in zip(b_pos, post_vals, post_errs):
        ax.text(bar.get_x() + bar.get_width()/2,
                v + e + 0.003, f"{v:.2%}",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    # % change annotation above each pair
    for i, (pv, ppv, pe, ppe, ch) in enumerate(zip(pre_vals, post_vals,
                                                     pre_errs, post_errs,
                                                     pct_changes)):
        y_top = max(pv+pe, ppv+ppe) + 0.025
        ax.text(i, y_top, f"Δ {ch:+.1f}%",
                ha="center", fontsize=9, style="italic",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor="#aaa", alpha=0.85))

    ax.set_xticks(x)
    ax.set_xticklabels(parties, fontsize=11)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=1))
    ax.set_ylabel("Proportion of Populist Tweets", fontweight="bold")
    ax.set_title(title, fontweight="bold", pad=10)
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

# ==============================================================================
# COMPARISON 1 — All pre vs Radicalized and Radical Populism post
# ==============================================================================

print("\n" + "─"*60)
print("COMPARISON 1: All parties pre vs Radicalized and Radical Populism post")
print("─"*60)

series_all_pre = data[data["post_election"] == 0]["pop"].astype(float)
series_rad_post = data[(data["post_election"] == 1) &
                       data["radicalized_group"]]["pop"].astype(float)

c1_stats = run_tests(series_all_pre, series_rad_post)
c1_summary = summary_stats(series_all_pre, series_rad_post,
                           "Pre-election\n(All parties)",
                           "Post-election\nRadicalized & Radical Populism")

print(f"  Pre  (all):      {c1_stats['pre_mean']:.4f}  n={len(series_all_pre):,}")
print(f"  Post (rad):      {c1_stats['post_mean']:.4f}  n={len(series_rad_post):,}")
print(f"  Change:          {c1_stats['pct_change']:+.2f}%")
print(f"  t={c1_stats['t']:.4f}  p={c1_stats['t_p']:.2e}  d={c1_stats['cohens_d']:.4f}")
print(f"  χ²={c1_stats['chi2']:.4f}  p={c1_stats['chi_p']:.2e}  V={c1_stats['cramers_v']:.4f}")

# ── Plot 3a ──────────────────────────────────────────────────────────────────
print("\nPlot 3a: Comparison 1 overall...")
fig, ax = plt.subplots(figsize=(7, 6))
bar_two(ax, c1_summary, "Radicalized and Radical Populism:\nOverall Before vs After Election")
# annotation
ax.text(0.5, -0.14,
        f"Δ {c1_stats['pct_change']:+.1f}%  |  t={c1_stats['t']:.2f}, p={c1_stats['t_p']:.2e}"
        f"  |  d={c1_stats['cohens_d']:.3f}",
        transform=ax.transAxes, ha="center", fontsize=9,
        style="italic", color="#555")
plt.tight_layout()
plt.savefig("output/plot3a_comp1_overall.png", bbox_inches="tight")
plt.close()
print("✓ output/plot3a_comp1_overall.png")

# ==============================================================================
# COMPARISON 1b — Likud vs PRR legislators (named, expanding group)
# ==============================================================================

print("\n" + "─"*60)
print("COMPARISON 1b: Likud  vs  PRR legislators (by screen_name)")
print("─"*60)

# Likud (party-based)
likud_pre  = data[(data["post_election"] == 0) & (data["party"] == "Likud")]["pop"].astype(float)
likud_post = data[(data["post_election"] == 1) & (data["party"] == "Likud")]["pop"].astype(float)

# PRR legislators — DIFFERENT COMPOSITION pre vs post
prr_pre  = data[(data["post_election"] == 0) & data["prr_leg_pre"]]["pop"].astype(float)
prr_post = data[(data["post_election"] == 1) & data["prr_leg_post"]]["pop"].astype(float)

likud_ch = (likud_post.mean() - likud_pre.mean()) / likud_pre.mean() * 100
prr_ch   = (prr_post.mean()   - prr_pre.mean())   / prr_pre.mean()   * 100

prr_tests = run_tests(prr_pre, prr_post)

print(f"  Likud  pre: {likud_pre.mean():.4f}  post: {likud_post.mean():.4f}  Δ {likud_ch:+.2f}%")
print(f"  PRR    pre: {prr_pre.mean():.4f}  post: {prr_post.mean():.4f}  Δ {prr_ch:+.2f}%")
print(f"  PRR t={prr_tests['t']:.4f}  p={prr_tests['t_p']:.2e}  d={prr_tests['cohens_d']:.4f}")
print(f"  (PRR pre n={len(prr_pre):,} [{', '.join(PRR_PRE_NAMES)}])")
print(f"  (PRR post n={len(prr_post):,} [{', '.join(PRR_POST_NAMES)}])")

# ── Plot 3b ──────────────────────────────────────────────────────────────────
print("\nPlot 3b: Likud vs PRR legislators...")
fig, ax = plt.subplots(figsize=(9, 6))
bar_grouped(ax,
            parties=["Likud", "PRR Legislators"],
            pre_vals =[likud_pre.mean(),  prr_pre.mean()],
            post_vals=[likud_post.mean(), prr_post.mean()],
            pre_errs =[1.96*likud_pre.std()/np.sqrt(len(likud_pre)),
                       1.96*prr_pre.std()/np.sqrt(len(prr_pre))],
            post_errs=[1.96*likud_post.std()/np.sqrt(len(likud_post)),
                       1.96*prr_post.std()/np.sqrt(len(prr_post))],
            title="Radicalized and Radical Populism: Likud vs PRR Legislators",
            pct_changes=[likud_ch, prr_ch])

# footnote explaining the changing group
fig.text(0.5, 0.01,
         f"PRR legislators — Pre: {', '.join(PRR_PRE_NAMES)}\n"
         f"Post adds: rothmar, itamarbengvir",
         ha="center", fontsize=7.5, color="#666",
         style="italic")
plt.subplots_adjust(bottom=0.12)
plt.savefig("output/plot3b_comp1_by_group.png", bbox_inches="tight")
plt.close()
print("✓ output/plot3b_comp1_by_group.png")

# ==============================================================================
# COMPARISON 2 — PRRPs in Change Coalition (Rightwards + Israel Our Home)
# ==============================================================================

print("\n" + "─"*60)
print("COMPARISON 2: PRRPs in Change Coalition — pre vs post election")
print("─"*60)

cc = data[data["change_coalition_group"]]
cc_pre  = cc[cc["post_election"] == 0]["pop"].astype(float)
cc_post = cc[cc["post_election"] == 1]["pop"].astype(float)

c2_stats = run_tests(cc_pre, cc_post)
c2_summary = summary_stats(cc_pre, cc_post,
                           "Pre-election\nPRRPs in Change Coalition",
                           "Post-election\nPRRPs in Change Coalition")

print(f"  Pre:    {c2_stats['pre_mean']:.4f}  n={len(cc_pre):,}")
print(f"  Post:   {c2_stats['post_mean']:.4f}  n={len(cc_post):,}")
print(f"  Change: {c2_stats['pct_change']:+.2f}%")
print(f"  t={c2_stats['t']:.4f}  p={c2_stats['t_p']:.2e}  d={c2_stats['cohens_d']:.4f}")
print(f"  χ²={c2_stats['chi2']:.4f}  p={c2_stats['chi_p']:.2e}  V={c2_stats['cramers_v']:.4f}")

# ── Plot 3c ──────────────────────────────────────────────────────────────────
print("\nPlot 3c: Comparison 2 overall...")
fig, ax = plt.subplots(figsize=(7, 6))
bar_two(ax, c2_summary, "PRRPs in Change Coalition:\nOverall Before vs After Election")
ax.text(0.5, -0.14,
        f"Δ {c2_stats['pct_change']:+.1f}%  |  t={c2_stats['t']:.2f}, p={c2_stats['t_p']:.2e}"
        f"  |  d={c2_stats['cohens_d']:.3f}",
        transform=ax.transAxes, ha="center", fontsize=9,
        style="italic", color="#555")
plt.tight_layout()
plt.savefig("output/plot3c_comp2_overall.png", bbox_inches="tight")
plt.close()
print("✓ output/plot3c_comp2_overall.png")

# ==============================================================================
# COMPARISON 2b — Rightwards vs Israel Our Home
# ==============================================================================

print("\n" + "─"*60)
print("COMPARISON 2b: Rightwards vs Israel Our Home (party detail)")
print("─"*60)

right_pre  = data[(data["post_election"] == 0) & (data["party"] == "Rightwards")]["pop"].astype(float)
right_post = data[(data["post_election"] == 1) & (data["party"] == "Rightwards")]["pop"].astype(float)
ioh_pre    = data[(data["post_election"] == 0) & (data["party"] == "Israel Our Home")]["pop"].astype(float)
ioh_post   = data[(data["post_election"] == 1) & (data["party"] == "Israel Our Home")]["pop"].astype(float)

right_ch = (right_post.mean() - right_pre.mean()) / right_pre.mean() * 100
ioh_ch   = (ioh_post.mean()   - ioh_pre.mean())   / ioh_pre.mean()   * 100

print(f"  Rightwards    pre: {right_pre.mean():.4f}  post: {right_post.mean():.4f}  Δ {right_ch:+.2f}%")
print(f"  Israel Our Home pre: {ioh_pre.mean():.4f}  post: {ioh_post.mean():.4f}  Δ {ioh_ch:+.2f}%")

# ── Plot 3d ──────────────────────────────────────────────────────────────────
print("\nPlot 3d: Rightwards vs Israel Our Home...")
fig, ax = plt.subplots(figsize=(9, 6))
bar_grouped(ax,
            parties=["Rightwards", "Israel Our Home"],
            pre_vals =[right_pre.mean(),  ioh_pre.mean()],
            post_vals=[right_post.mean(), ioh_post.mean()],
            pre_errs =[1.96*right_pre.std()/np.sqrt(len(right_pre)),
                       1.96*ioh_pre.std()/np.sqrt(len(ioh_pre))],
            post_errs=[1.96*right_post.std()/np.sqrt(len(right_post)),
                       1.96*ioh_post.std()/np.sqrt(len(ioh_post))],
            title="PRRPs in Change Coalition: Rightwards vs Israel Our Home",
            pct_changes=[right_ch, ioh_ch])
plt.tight_layout()
plt.savefig("output/plot3d_comp2_by_party.png", bbox_inches="tight")
plt.close()
print("✓ output/plot3d_comp2_by_party.png")

# ==============================================================================
# SAVE RESULTS + DOCUMENTATION
# ==============================================================================

results = {
    "comparison1":    {"stats": c1_stats,   "summary": c1_summary},
    "comparison1b":   {"stats": prr_tests,
                       "likud_pre": likud_pre.mean(), "likud_post": likud_post.mean(),
                       "prr_pre": prr_pre.mean(),     "prr_post":  prr_post.mean()},
    "comparison2":    {"stats": c2_stats,   "summary": c2_summary},
    "right_ioh":      {"right_pre": right_pre.mean(), "right_post": right_post.mean(),
                       "ioh_pre":   ioh_pre.mean(),   "ioh_post":   ioh_post.mean()},
}
with open("output/comparison_results.pkl", "wb") as f:
    pickle.dump(results, f)

md = f"""# Stage 3: Before/After Analysis — Election Cutoff

**Date:** {datetime.now().strftime("%B %d, %Y")}
**Election cutoff:** March 23, 2021

---

## Comparison 1: All Parties Pre vs Radicalized and Radical Populism Post

| Period | Tweets | Populist | Proportion |
|---|---|---|---|
| Pre-election (all parties) | {len(series_all_pre):,} | {int(series_all_pre.sum()):,} | {c1_stats['pre_mean']:.4f} ({c1_stats['pre_mean']*100:.2f}%) |
| Post-election (Likud + Religious Zionism) | {len(series_rad_post):,} | {int(series_rad_post.sum()):,} | {c1_stats['post_mean']:.4f} ({c1_stats['post_mean']*100:.2f}%) |

**Change: {c1_stats['pct_change']:+.2f}%**
- t = {c1_stats['t']:.4f}, p = {c1_stats['t_p']:.2e}
- Cohen's d = {c1_stats['cohens_d']:.4f}
- χ² = {c1_stats['chi2']:.4f}, p = {c1_stats['chi_p']:.2e}, Cramér's V = {c1_stats['cramers_v']:.4f}

---

## Comparison 1b: Likud vs PRR Legislators (by screen_name)

| Group | Period | Legislators | Proportion | Change |
|---|---|---|---|---|
| Likud | Pre | (all Likud) | {likud_pre.mean():.4f} | — |
| Likud | Post | (all Likud) | {likud_post.mean():.4f} | {likud_ch:+.2f}% |
| PRR legislators | Pre | bezalelsm, michalwoldiger, ofir_sofer, oritstrock | {prr_pre.mean():.4f} | — |
| PRR legislators | Post | + rothmar, itamarbengvir | {prr_post.mean():.4f} | {prr_ch:+.2f}% |

PRR t = {prr_tests['t']:.4f}, p = {prr_tests['t_p']:.2e}, d = {prr_tests['cohens_d']:.4f}

---

## Comparison 2: PRRPs in Change Coalition

| Period | Tweets | Populist | Proportion |
|---|---|---|---|
| Pre-election | {len(cc_pre):,} | {int(cc_pre.sum()):,} | {c2_stats['pre_mean']:.4f} ({c2_stats['pre_mean']*100:.2f}%) |
| Post-election | {len(cc_post):,} | {int(cc_post.sum()):,} | {c2_stats['post_mean']:.4f} ({c2_stats['post_mean']*100:.2f}%) |

**Change: {c2_stats['pct_change']:+.2f}%**
- t = {c2_stats['t']:.4f}, p = {c2_stats['t_p']:.2e}
- Cohen's d = {c2_stats['cohens_d']:.4f}
- χ² = {c2_stats['chi2']:.4f}, p = {c2_stats['chi_p']:.2e}, Cramér's V = {c2_stats['cramers_v']:.4f}

| Party | Pre | Post | Change |
|---|---|---|---|
| Rightwards | {right_pre.mean():.4f} | {right_post.mean():.4f} | {right_ch:+.2f}% |
| Israel Our Home | {ioh_pre.mean():.4f} | {ioh_post.mean():.4f} | {ioh_ch:+.2f}% |

---

## Output Plots

| File | Content |
|---|---|
| plot3a_comp1_overall.png | Comparison 1 — overall bar |
| plot3b_comp1_by_group.png | Comparison 1 — Likud vs PRR legislators |
| plot3c_comp2_overall.png | Comparison 2 — overall bar |
| plot3d_comp2_by_party.png | Comparison 2 — Rightwards vs Israel Our Home |
"""

with open("output/before_after_results.md", "w") as f:
    f.write(md)

print("\n✓ output/comparison_results.pkl saved")
print("✓ output/before_after_results.md saved")
print("\n=== STAGE 3 COMPLETE ===")
