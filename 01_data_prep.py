#!/usr/bin/env python3
"""
==============================================================================
Stage 1: Data Preparation
==============================================================================
Purpose: Load raw data, apply filters, create grouping variables for
         the election-cutoff focused analysis.
Input:   causal7_dat.csv
Outputs: output/analysis_data.pkl, output/analysis_data.csv,
         output/data_summary.md
==============================================================================
"""

import pandas as pd
import numpy as np
import pickle
from datetime import datetime

print("=" * 70)
print("STAGE 1: DATA PREPARATION")
print("=" * 70)

# ==============================================================================
# 1. LOAD RAW DATA
# ==============================================================================

print("\nLoading raw data...")
df = pd.read_csv("causal7_dat.csv", encoding="utf-8-sig")
df["day"] = pd.to_datetime(df["day"])
print(f"Loaded {len(df):,} rows | date range: {df['day'].min().date()} to {df['day'].max().date()}")
print(f"Parties: {sorted(df['party'].unique())}")

# ==============================================================================
# 2. FILTER: 2020-01-01 ONWARDS — ALL 7 PARTIES KEPT
# ==============================================================================

analysis_data = df[df["day"] >= pd.to_datetime("2020-01-01")].copy()
print(f"\nAfter 2020+ filter: {len(analysis_data):,} rows")
print(f"Party counts:\n{analysis_data['party'].value_counts().to_string()}")

# ==============================================================================
# 3. ELECTION CUTOFF VARIABLES
# ==============================================================================

election_date = pd.to_datetime("2021-03-23")
analysis_data["post_election"] = (analysis_data["day"] >= election_date).astype(int)
analysis_data["days_from_election"] = (analysis_data["day"] - election_date).dt.days
analysis_data["week_from_election"] = (analysis_data["days_from_election"] / 7).apply(np.floor).astype(int)

pre_n  = (analysis_data["post_election"] == 0).sum()
post_n = (analysis_data["post_election"] == 1).sum()
print(f"\nElection cutoff: {election_date.date()}")
print(f"  Pre-election tweets:  {pre_n:,}")
print(f"  Post-election tweets: {post_n:,}")

# ==============================================================================
# 4. GROUPING VARIABLES
# ==============================================================================

# Comparison 1: "Radicalized and Radical Populism" — Likud + Religious Zionism
analysis_data["radicalized_group"] = analysis_data["party"].isin(["Likud", "Religious Zionism"])

# Comparison 2: "PRRPs in Change Coalition" — Rightwards + Israel Our Home
analysis_data["change_coalition_group"] = analysis_data["party"].isin(["Rightwards", "Israel Our Home"])

# PRR legislators (by screen_name — composition differs pre/post)
PRR_PRE  = {"bezalelsm", "michalwoldiger", "ofir_sofer", "oritstrock"}
PRR_POST = {"bezalelsm", "michalwoldiger", "ofir_sofer", "oritstrock", "rothmar", "itamarbengvir"}

analysis_data["prr_leg_pre"]  = analysis_data["screen_name"].isin(PRR_PRE)
analysis_data["prr_leg_post"] = analysis_data["screen_name"].isin(PRR_POST)

print("\nGrouping variable counts:")
print(f"  radicalized_group (Likud + Religious Zionism): {analysis_data['radicalized_group'].sum():,}")
print(f"  change_coalition_group (Rightwards + IOH):     {analysis_data['change_coalition_group'].sum():,}")
print(f"  prr_leg_pre  (4 named legislators):            {analysis_data['prr_leg_pre'].sum():,}")
print(f"  prr_leg_post (6 named legislators):            {analysis_data['prr_leg_post'].sum():,}")

# ==============================================================================
# 5. POP AS NUMERIC
# ==============================================================================

analysis_data["pop"] = pd.to_numeric(analysis_data["pop"], errors="coerce").fillna(0).astype(int)
overall_pop_rate = analysis_data["pop"].mean()
print(f"\nOverall populist rate: {overall_pop_rate:.4f} ({overall_pop_rate*100:.2f}%)")

# ==============================================================================
# 6. SAVE
# ==============================================================================

analysis_data.to_pickle("output/analysis_data.pkl")
analysis_data.to_csv("output/analysis_data.csv", index=False)
print(f"\nSaved {len(analysis_data):,} rows → output/analysis_data.pkl + .csv")

# ==============================================================================
# 7. SUMMARY STATS + DOCUMENTATION
# ==============================================================================

pre  = analysis_data[analysis_data["post_election"] == 0]
post = analysis_data[analysis_data["post_election"] == 1]

by_party = analysis_data.groupby(["party", "post_election"])["pop"].agg(["sum", "count", "mean"]).reset_index()
by_party.columns = ["party", "post_election", "populist_tweets", "total_tweets", "prop_pop"]
by_party["period"] = by_party["post_election"].map({0: "Pre-election", 1: "Post-election"})

print("\nSummary by party and period:")
print(by_party[["party", "period", "total_tweets", "populist_tweets", "prop_pop"]].to_string(index=False))

md = f"""# Stage 1: Data Preparation Summary

**Date:** {datetime.now().strftime("%B %d, %Y")}
**Election cutoff:** March 23, 2021

## Dataset

- **Source:** causal7_dat.csv
- **Filter:** 2020-01-01 onwards, all 7 parties included
- **Total rows:** {len(analysis_data):,}
- **Pre-election:** {pre_n:,} tweets
- **Post-election:** {post_n:,} tweets

## Party Counts

{by_party[["party","period","total_tweets","populist_tweets","prop_pop"]].to_string(index=False)}

## Grouping Variables

| Variable | Definition |
|---|---|
| `radicalized_group` | party ∈ {{Likud, Religious Zionism}} |
| `change_coalition_group` | party ∈ {{Rightwards, Israel Our Home}} |
| `prr_leg_pre` | screen_name ∈ {{bezalelsm, michalwoldiger, ofir_sofer, oritstrock}} |
| `prr_leg_post` | prr_leg_pre ∪ {{rothmar, itamarbengvir}} |
"""

with open("output/data_summary.md", "w") as f:
    f.write(md)

print("\n✓ output/data_summary.md saved")
print("\n=== STAGE 1 COMPLETE ===")
