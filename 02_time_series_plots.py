#!/usr/bin/env python3
"""
==============================================================================
Stage 2: Time Series Visualizations
==============================================================================
Purpose: Create time series plots showing populist rhetoric trends over time
Input: analysis_data.pkl (from Stage 1)
Outputs: 2 PNG plots (overall + by party) + markdown documentation
Note: Shows both election (March 23) and coalition (June 13) dates
==============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 10

# Define color palette
colors = {
    'main': '#2E86AB',
    'Likud': '#E63946',
    'PRRPs': '#F77F00',
    'new': '#06A77D',
    'continuing': '#5E60CE',
    'cutoff': '#333333'
}

# ==============================================================================
# 1. LOAD DATA
# ==============================================================================

print("Loading cleaned dataset...")
analysis_data = pd.read_pickle("output/analysis_data.pkl")
print(f"Loaded {len(analysis_data)} observations\n")

# ==============================================================================
# 2. PREPARE AGGREGATED DATA
# ==============================================================================

print("Preparing aggregated data for visualization...")

# 2.1 Overall weekly aggregates
weekly_overall = analysis_data.groupby('week_from_cutoff').agg({
    'pop': ['sum', 'count', 'mean'],
    'day': 'min'
}).reset_index()
weekly_overall.columns = ['week_from_cutoff', 'populist_tweets', 'total_tweets', 'prop_populist', 'week_start']
print(f"Overall: {len(weekly_overall)} weeks")

# 2.2 By party_group
weekly_by_party = analysis_data.groupby(['week_from_cutoff', 'party_group']).agg({
    'pop': ['sum', 'count', 'mean'],
    'day': 'min'
}).reset_index()
weekly_by_party.columns = ['week_from_cutoff', 'party_group', 'populist_tweets', 'total_tweets', 'prop_populist', 'week_start']
print(f"By party: {len(weekly_by_party)} party-week observations")

# Calculate week numbers for election date (March 23, 2021)
election_date = pd.to_datetime("2021-03-23")
cutoff_date = pd.to_datetime("2021-06-13")
election_week = int((election_date - cutoff_date).days / 7)
print(f"Election date week: {election_week}")
print(f"Coalition date week: 0\n")

# ==============================================================================
# 3. PLOT 1: OVERALL TREND
# ==============================================================================

print("Creating Plot 1: Overall populist proportion trend...")

fig, ax = plt.subplots(figsize=(12, 6))

# Plot raw weekly proportions
ax.scatter(weekly_overall['week_from_cutoff'],
           weekly_overall['prop_populist'],
           alpha=0.3, s=20, color=colors['main'], label='Weekly values')

# Add smoothed trend (rolling average)
window = 4  # 4-week rolling average
weekly_overall_sorted = weekly_overall.sort_values('week_from_cutoff')
rolling_mean = weekly_overall_sorted['prop_populist'].rolling(window=window, center=True).mean()
ax.plot(weekly_overall_sorted['week_from_cutoff'], rolling_mean,
        linewidth=2.5, color=colors['main'], label=f'{window}-week rolling average')

# Add vertical lines for both dates
ax.axvline(x=election_week, color='#9B59B6', linestyle=':', linewidth=2.5,
           label='Election (March 23, 2021)', alpha=0.8)
ax.axvline(x=0, color=colors['cutoff'], linestyle='--', linewidth=2.5,
           label='Coalition (June 13, 2021)', alpha=0.8)

# Labels and formatting
ax.set_xlabel('Weeks from Cutoff (June 13, 2021)', fontweight='bold')
ax.set_ylabel('Proportion of Populist Tweets', fontweight='bold')
ax.set_title('Populist Rhetoric Over Time: Overall Trend', fontweight='bold', pad=20)
ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
ax.grid(True, alpha=0.3)

# Format y-axis as percentage
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

plt.tight_layout()
plt.savefig('output/plot1_overall_trend.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Plot 1 saved as 'output/plot1_overall_trend.png'\n")

# ==============================================================================
# 4. PLOT 2: BY PARTY GROUP
# ==============================================================================

print("Creating Plot 2: Trend by party group (Likud vs PRRPs)...")

fig, ax = plt.subplots(figsize=(12, 6))

# Plot for each party group
for party in ['Likud', 'PRRPs']:
    party_data = weekly_by_party[weekly_by_party['party_group'] == party].sort_values('week_from_cutoff')

    # Scatter points
    ax.scatter(party_data['week_from_cutoff'],
               party_data['prop_populist'],
               alpha=0.3, s=20, color=colors[party])

    # Rolling average
    rolling_mean = party_data['prop_populist'].rolling(window=window, center=True).mean()
    ax.plot(party_data['week_from_cutoff'], rolling_mean,
            linewidth=2.5, color=colors[party], label=party)

# Add vertical lines for both dates
ax.axvline(x=election_week, color='#9B59B6', linestyle=':', linewidth=2.5,
           label='Election (March 23)', alpha=0.8)
ax.axvline(x=0, color=colors['cutoff'], linestyle='--', linewidth=2.5,
           label='Coalition (June 13)', alpha=0.8)

# Labels and formatting
ax.set_xlabel('Weeks from Coalition Cutoff (June 13, 2021)', fontweight='bold')
ax.set_ylabel('Proportion of Populist Tweets', fontweight='bold')
ax.set_title('Populist Rhetoric Over Time: By Party Group', fontweight='bold', pad=20)
ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
ax.grid(True, alpha=0.3)

# Format y-axis as percentage
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

plt.tight_layout()
plt.savefig('output/plot2_by_party.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Plot 2 saved as 'output/plot2_by_party.png'\n")

# Plot 3 removed - focusing on overall and party trends only

# ==============================================================================
# 6. CREATE MARKDOWN DOCUMENTATION
# ==============================================================================

print("Creating markdown documentation...")

# Calculate some summary statistics for documentation
pre_cutoff_mean = weekly_overall[weekly_overall['week_from_cutoff'] < 0]['prop_populist'].mean()
post_cutoff_mean = weekly_overall[weekly_overall['week_from_cutoff'] >= 0]['prop_populist'].mean()
change_pct = ((post_cutoff_mean - pre_cutoff_mean) / pre_cutoff_mean) * 100

md_content = f"""# Stage 2: Time Series Visualizations

**Date:** {datetime.now().strftime("%B %d, %Y")}

**Purpose:** Visualize trends in populist rhetoric over time, showing both critical dates.

---

## Overview

This analysis examines temporal trends in populist tweets from Israeli legislators, showing **two critical dates**:
- **March 23, 2021**: Election date (dotted purple line)
- **June 13, 2021**: Coalition formation (dashed black line)

Visual inspection helps determine which event marks the true discontinuity in populist rhetoric.

### Key Findings (Coalition Cutoff)

- **Pre-coalition mean:** {pre_cutoff_mean:.2%} populist tweets
- **Post-coalition mean:** {post_cutoff_mean:.2%} populist tweets
- **Change:** {change_pct:+.1f}% increase

---

## Visualizations

### Plot 1: Overall Trend

![Overall Trend](plot1_overall_trend.png)

**Description:** Overall proportion of populist tweets over time with a {window}-week rolling average.
- **Purple dotted line**: Election (March 23, 2021)
- **Black dashed line**: Coalition formation (June 13, 2021)

**Key observations:**
- Visual inspection reveals timing of the change
- Smoothed trend line shows the general trajectory
- Both critical dates marked for comparison

---

### Plot 2: By Party Group (Likud vs PRRPs)

![By Party Group](plot2_by_party.png)

**Description:** Compares populist rhetoric trends between Likud and PRRPs (Populist Radical Right Parties).

**Key observations:**
- Differential timing of changes between party groups possible
- Both critical dates shown for each group
- {window}-week rolling averages smooth out weekly volatility

---

## Data Summary

- **Total observations:** {len(analysis_data):,}
- **Time span:** {len(weekly_overall)} weeks
- **Election week:** {election_week} (March 23, 2021)
- **Coalition week:** 0 (June 13, 2021)
- **Smoothing method:** {window}-week rolling average (centered)

---

## Technical Details

**Critical dates:**
- **Election**: March 23, 2021 (week {election_week})
- **Coalition**: June 13, 2021 (week 0, reference point)

**Visualization settings:**
- Resolution: 300 DPI
- Format: PNG
- Smoothing: {window}-week centered rolling average
- Two vertical lines mark both critical dates

**Data aggregation:**
- Weekly aggregation by `week_from_cutoff` (relative to coalition date)
- Proportion calculated as: populist_tweets / total_tweets

---

## Output Files

- **plot1_overall_trend.png**: Overall populist proportion trend
- **plot2_by_party.png**: Trend comparison by party group

---

## Next Steps

Proceed to Stage 3: Statistical tests for **both** cutoff dates to determine which hypothesis is supported.
"""

with open("output/plots_stage2.md", "w") as f:
    f.write(md_content)

print("Documentation saved as 'output/plots_stage2.md'")

print("\n=== STAGE 2 COMPLETE ===")
print("All plots created successfully!")
print(f"- plot1_overall_trend.png (shows both election + coalition dates)")
print(f"- plot2_by_party.png (shows both election + coalition dates)")
print(f"- plots_stage2.md")
print(f"\nBoth critical dates visualized:")
print(f"  - Election: March 23, 2021 (week {election_week}, purple dotted)")
print(f"  - Coalition: June 13, 2021 (week 0, black dashed)")
