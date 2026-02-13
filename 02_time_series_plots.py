#!/usr/bin/env python3
"""
==============================================================================
Stage 2: Time Series Visualizations
==============================================================================
Purpose: Create time series plots showing populist rhetoric trends over time
Input: analysis_data.pkl (from Stage 1)
Outputs: 3 PNG plots + markdown documentation
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
analysis_data = pd.read_pickle("analysis_data.pkl")
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

# 2.3 By new24 status
weekly_by_new24 = analysis_data.groupby(['week_from_cutoff', 'new24']).agg({
    'pop': ['sum', 'count', 'mean'],
    'day': 'min'
}).reset_index()
weekly_by_new24.columns = ['week_from_cutoff', 'new24', 'populist_tweets', 'total_tweets', 'prop_populist', 'week_start']
weekly_by_new24['legislator_type'] = weekly_by_new24['new24'].map({
    True: 'New Legislator',
    False: 'Continuing Legislator'
})
print(f"By new24: {len(weekly_by_new24)} legislator-type-week observations\n")

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

# Add vertical line at cutoff
ax.axvline(x=0, color=colors['cutoff'], linestyle='--', linewidth=2,
           label='Cutoff (June 13, 2021)')

# Add shaded regions for pre/post
ax.axvspan(weekly_overall['week_from_cutoff'].min(), 0, alpha=0.05, color='blue', label='Pre-cutoff')
ax.axvspan(0, weekly_overall['week_from_cutoff'].max(), alpha=0.05, color='red', label='Post-cutoff')

# Labels and formatting
ax.set_xlabel('Weeks from Cutoff (June 13, 2021)', fontweight='bold')
ax.set_ylabel('Proportion of Populist Tweets', fontweight='bold')
ax.set_title('Populist Rhetoric Over Time: Overall Trend', fontweight='bold', pad=20)
ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
ax.grid(True, alpha=0.3)

# Format y-axis as percentage
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

plt.tight_layout()
plt.savefig('plot1_overall_trend.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Plot 1 saved as 'plot1_overall_trend.png'\n")

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

# Add vertical line at cutoff
ax.axvline(x=0, color=colors['cutoff'], linestyle='--', linewidth=2,
           label='Cutoff (June 13, 2021)')

# Labels and formatting
ax.set_xlabel('Weeks from Cutoff (June 13, 2021)', fontweight='bold')
ax.set_ylabel('Proportion of Populist Tweets', fontweight='bold')
ax.set_title('Populist Rhetoric Over Time: By Party Group', fontweight='bold', pad=20)
ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
ax.grid(True, alpha=0.3)

# Format y-axis as percentage
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

plt.tight_layout()
plt.savefig('plot2_by_party.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Plot 2 saved as 'plot2_by_party.png'\n")

# ==============================================================================
# 5. PLOT 3: BY NEW24 STATUS
# ==============================================================================

print("Creating Plot 3: Trend by legislator type (New vs Continuing)...")

fig, ax = plt.subplots(figsize=(12, 6))

# Plot for each legislator type
for new24_val, leg_type, color_key in [(True, 'New Legislator', 'new'),
                                        (False, 'Continuing Legislator', 'continuing')]:
    type_data = weekly_by_new24[weekly_by_new24['new24'] == new24_val].sort_values('week_from_cutoff')

    # Scatter points
    ax.scatter(type_data['week_from_cutoff'],
               type_data['prop_populist'],
               alpha=0.3, s=20, color=colors[color_key])

    # Rolling average
    rolling_mean = type_data['prop_populist'].rolling(window=window, center=True).mean()
    ax.plot(type_data['week_from_cutoff'], rolling_mean,
            linewidth=2.5, color=colors[color_key], label=leg_type)

# Add vertical line at cutoff
ax.axvline(x=0, color=colors['cutoff'], linestyle='--', linewidth=2,
           label='Cutoff (June 13, 2021)')

# Labels and formatting
ax.set_xlabel('Weeks from Cutoff (June 13, 2021)', fontweight='bold')
ax.set_ylabel('Proportion of Populist Tweets', fontweight='bold')
ax.set_title('Populist Rhetoric Over Time: By Legislator Type', fontweight='bold', pad=20)
ax.legend(loc='best', frameon=True, fancybox=True, shadow=True)
ax.grid(True, alpha=0.3)

# Format y-axis as percentage
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))

plt.tight_layout()
plt.savefig('plot3_by_new24.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Plot 3 saved as 'plot3_by_new24.png'\n")

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

**Purpose:** Visualize trends in populist rhetoric over time around the government coalition change.

---

## Overview

This analysis examines temporal trends in populist tweets from Israeli legislators, focusing on the period before and after the government change on June 13, 2021.

### Key Findings

- **Pre-cutoff mean:** {pre_cutoff_mean:.2%} populist tweets
- **Post-cutoff mean:** {post_cutoff_mean:.2%} populist tweets
- **Change:** {change_pct:+.1f}% increase

---

## Visualizations

### Plot 1: Overall Trend

![Overall Trend](plot1_overall_trend.png)

**Description:** Shows the overall proportion of populist tweets over time with a {window}-week rolling average. The vertical dashed line marks June 13, 2021 (government change).

**Key observations:**
- Clear visual distinction between pre- and post-cutoff periods
- Smoothed trend line shows the general trajectory
- Weekly variation captured in scatter points

---

### Plot 2: By Party Group (Likud vs PRRPs)

![By Party Group](plot2_by_party.png)

**Description:** Compares populist rhetoric trends between Likud (the dominant party) and PRRPs (Populist Radical Right Parties).

**Key observations:**
- Separate trends for Likud and PRRPs coalition members
- Both groups show temporal patterns around the cutoff
- {window}-week rolling averages smooth out weekly volatility

---

### Plot 3: By Legislator Type (New vs Continuing)

![By Legislator Type](plot3_by_new24.png)

**Description:** Compares trends between new legislators (elected in 2021) and continuing legislators.

**Key observations:**
- Differential trends between new and continuing legislators
- New legislators may show different rhetorical patterns
- Both groups' trends are smoothed with {window}-week rolling averages

---

## Data Summary

- **Total observations:** {len(analysis_data):,}
- **Time span:** {len(weekly_overall)} weeks
- **Weeks before cutoff:** {(weekly_overall['week_from_cutoff'] < 0).sum()}
- **Weeks after cutoff:** {(weekly_overall['week_from_cutoff'] >= 0).sum()}
- **Smoothing method:** {window}-week rolling average (centered)

---

## Technical Details

**Visualization settings:**
- Resolution: 300 DPI
- Format: PNG
- Smoothing: {window}-week centered rolling average
- Cutoff marked at week 0 (June 13, 2021)

**Data aggregation:**
- Weekly aggregation by `week_from_cutoff`
- Proportion calculated as: populist_tweets / total_tweets
- Separate aggregations for overall, by party_group, and by legislator type

---

## Output Files

- **plot1_overall_trend.png**: Overall populist proportion trend
- **plot2_by_party.png**: Trend comparison by party group
- **plot3_by_new24.png**: Trend comparison by legislator type

---

## Next Steps

Proceed to Stage 3: Before/After Statistical Comparison
"""

with open("plots_stage2.md", "w") as f:
    f.write(md_content)

print("Documentation saved as 'plots_stage2.md'")

print("\n=== STAGE 2 COMPLETE ===")
print("All plots created successfully!")
print(f"- plot1_overall_trend.png")
print(f"- plot2_by_party.png")
print(f"- plot3_by_new24.png")
print(f"- plots_stage2.md")
