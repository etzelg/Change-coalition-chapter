#!/usr/bin/env python3
"""
==============================================================================
Stage 2: Time Series Plots
==============================================================================
Plot 2a: Netanyahu's bloc (Likud + Religious Zionism) — single trend line
         with election vertical line
Plot 2b: Rightwards vs Israel Our Home — election vertical line
Outputs: output/plot2a_radicalized_trend.png
         output/plot2b_change_coalition_trend.png
==============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300

WINDOW   = 4          # weeks rolling average
ELEC_WK  = 0          # election is week 0 by definition

print("=" * 70)
print("STAGE 2: TIME SERIES PLOTS")
print("=" * 70)

data = pd.read_pickle("output/analysis_data.pkl")
print(f"\nLoaded {len(data):,} rows")

# ── helper ───────────────────────────────────────────────────────────────────
def weekly_prop(df_subset):
    """Return weekly proportion of populist tweets."""
    return (df_subset.groupby("week_from_election")
                     .agg(pop_sum=("pop", "sum"), total=("pop", "count"))
                     .assign(prop=lambda x: x.pop_sum / x.total)
                     .reset_index())

def smooth(series, w=WINDOW):
    return series.rolling(window=w, center=True, min_periods=1).mean()

# ──────────────────────────────────────────────────────────────────────────────
# PLOT 2a — Netanyahu's bloc — single trend line, composition changes at cutoff
#   Pre-election : named PRR legislators (prr_leg_pre screen_names) + all Likud
#   Post-election: all Religious Zionism (party) + all Likud
# ──────────────────────────────────────────────────────────────────────────────
print("\nPlot 2a: Netanyahu's bloc trend (single line, correct pre/post composition)...")

bloc_mask = (
    ((data["post_election"] == 0) & (data["prr_leg_pre"] | (data["party"] == "Likud"))) |
    ((data["post_election"] == 1) & (data["radicalized_group"]))
)
rad_wk = weekly_prop(data[bloc_mask]).sort_values("week_from_election")

fig, ax = plt.subplots(figsize=(12, 6))

# scatter dots (faint)
ax.scatter(rad_wk["week_from_election"], rad_wk["prop"],
           alpha=0.18, s=14, color="#c0392b")

# single smoothed line
ax.plot(rad_wk["week_from_election"], smooth(rad_wk["prop"]),
        linewidth=2.5, color="#c0392b",
        label="Netanyahu's Bloc (Likud + Religious Zionism)")

# election line
ax.axvline(x=0, color="#2c3e50", linestyle="--", linewidth=2,
           label="Election — March 23, 2021")

ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=1))
ax.set_xlabel("Weeks from Election (March 23, 2021)", fontweight="bold")
ax.set_ylabel("Proportion of Populist Tweets", fontweight="bold")
ax.set_title("Populism in Netanyahu's Bloc Before and After 2021 Election",
             fontweight="bold", pad=14)
ax.legend(loc="upper left", frameon=True, fancybox=True, shadow=True, fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("output/plot2a_radicalized_trend.png", bbox_inches="tight")
plt.close()
print("✓ output/plot2a_radicalized_trend.png")

# ──────────────────────────────────────────────────────────────────────────────
# PLOT 2b — Rightwards vs Israel Our Home
# ──────────────────────────────────────────────────────────────────────────────
print("\nPlot 2b: Rightwards vs Israel Our Home trend...")

right_wk = weekly_prop(data[data["party"] == "Rightwards"]).sort_values("week_from_election")
ioh_wk   = weekly_prop(data[data["party"] == "Israel Our Home"]).sort_values("week_from_election")

fig, ax = plt.subplots(figsize=(12, 6))

ax.scatter(right_wk["week_from_election"], right_wk["prop"],
           alpha=0.18, s=14, color="#2980b9")
ax.scatter(ioh_wk["week_from_election"], ioh_wk["prop"],
           alpha=0.18, s=14, color="#27ae60")

ax.plot(right_wk["week_from_election"], smooth(right_wk["prop"]),
        linewidth=2.5, color="#2980b9", label="Rightwards")
ax.plot(ioh_wk["week_from_election"], smooth(ioh_wk["prop"]),
        linewidth=2.5, color="#27ae60", label="Israel Our Home")

ax.axvline(x=0, color="#2c3e50", linestyle="--", linewidth=2,
           label="Election — March 23, 2021")

ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=1))
ax.set_xlabel("Weeks from Election (March 23, 2021)", fontweight="bold")
ax.set_ylabel("Proportion of Populist Tweets", fontweight="bold")
ax.set_title("Populist Rhetoric Over Time:\nPRRPs in Change Coalition (Rightwards vs Israel Our Home)",
             fontweight="bold", pad=14)
ax.legend(loc="upper left", frameon=True, fancybox=True, shadow=True, fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("output/plot2b_change_coalition_trend.png", bbox_inches="tight")
plt.close()
print("✓ output/plot2b_change_coalition_trend.png")

print("\n=== STAGE 2 COMPLETE ===")
