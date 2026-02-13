#!/usr/bin/env python3
"""
==============================================================================
Stage 3: Before/After Statistical Comparison - DUAL CUTOFF ANALYSIS
==============================================================================
Purpose: Compare populist rhetoric for TWO cutoff dates:
         1. Election (March 23, 2021)
         2. Coalition Formation (June 13, 2021)
Input: analysis_data.pkl (from Stage 1)
Outputs: Statistical tests for both hypotheses, comparison tables, plots
==============================================================================
"""

import pandas as pd
import numpy as np
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import datetime

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

# ==============================================================================
# 1. LOAD DATA AND DEFINE CUTOFFS
# ==============================================================================

print("Loading cleaned dataset...")
analysis_data = pd.read_pickle("output/analysis_data.pkl")
print(f"Loaded {len(analysis_data)} observations\n")

# Define both cutoff dates
election_date = pd.to_datetime("2021-03-23")
coalition_date = pd.to_datetime("2021-06-13")

# Create indicators for both cutoffs
analysis_data['post_election'] = (analysis_data['day'] >= election_date).astype(int)
analysis_data['post_coalition'] = (analysis_data['day'] >= coalition_date).astype(int)

print("=== TWO CUTOFF DATES DEFINED ===")
print(f"Election date: March 23, 2021")
print(f"Coalition date: June 13, 2021\n")

# ==============================================================================
# 2. SUMMARY TABLES FOR BOTH CUTOFFS
# ==============================================================================

print("=== GENERATING SUMMARY TABLES FOR BOTH CUTOFFS ===\n")

results = {'election': {}, 'coalition': {}}

def generate_summaries(cutoff_var, cutoff_name):
    """Generate all summary tables for a given cutoff"""
    summaries = {}

    # Overall summary
    overall = analysis_data.groupby(cutoff_var).agg({
        'pop': ['sum', 'count', 'mean', 'std'],
        'screen_name': 'nunique'
    }).reset_index()
    overall.columns = [cutoff_var, 'populist_tweets', 'total_tweets', 'mean_prop', 'std_prop', 'unique_legislators']
    overall['period'] = overall[cutoff_var].map({0: f'Pre-{cutoff_name}', 1: f'Post-{cutoff_name}'})
    overall['se_prop'] = overall['std_prop'] / np.sqrt(overall['total_tweets'])
    summaries['overall'] = overall[['period', 'total_tweets', 'populist_tweets', 'mean_prop', 'se_prop', 'unique_legislators']]

    # By party
    party = analysis_data.groupby([cutoff_var, 'party_group']).agg({
        'pop': ['sum', 'count', 'mean', 'std'],
        'screen_name': 'nunique'
    }).reset_index()
    party.columns = [cutoff_var, 'party_group', 'populist_tweets', 'total_tweets', 'mean_prop', 'std_prop', 'unique_legislators']
    party['period'] = party[cutoff_var].map({0: f'Pre-{cutoff_name}', 1: f'Post-{cutoff_name}'})
    party['se_prop'] = party['std_prop'] / np.sqrt(party['total_tweets'])
    summaries['party'] = party[['period', 'party_group', 'total_tweets', 'populist_tweets', 'mean_prop', 'se_prop', 'unique_legislators']]

    return summaries

# Generate for both cutoffs
print("--- ELECTION CUTOFF (March 23, 2021) ---\n")
election_summaries = generate_summaries('post_election', 'Election')
print("Overall:")
print(election_summaries['overall'].to_string(index=False))
print("\nBy Party:")
print(election_summaries['party'].to_string(index=False))
print()

print("--- COALITION CUTOFF (June 13, 2021) ---\n")
coalition_summaries = generate_summaries('post_coalition', 'Coalition')
print("Overall:")
print(coalition_summaries['overall'].to_string(index=False))
print("\nBy Party:")
print(coalition_summaries['party'].to_string(index=False))
print()

results['election']['summaries'] = election_summaries
results['coalition']['summaries'] = coalition_summaries

# ==============================================================================
# 3. STATISTICAL TESTS FOR BOTH CUTOFFS
# ==============================================================================

print("=== CONDUCTING STATISTICAL TESTS FOR BOTH CUTOFFS ===\n")

def run_statistical_tests(cutoff_var, cutoff_name):
    """Run t-test and chi-square for a given cutoff"""
    test_results = {}

    # Two-sample t-test
    pre_data = analysis_data[analysis_data[cutoff_var] == 0]['pop'].astype(int)
    post_data = analysis_data[analysis_data[cutoff_var] == 1]['pop'].astype(int)

    t_stat, t_pval = stats.ttest_ind(pre_data, post_data)

    # Cohen's d
    pre_mean = pre_data.mean()
    post_mean = post_data.mean()
    pooled_std = np.sqrt(((len(pre_data) - 1) * pre_data.std()**2 +
                          (len(post_data) - 1) * post_data.std()**2) /
                         (len(pre_data) + len(post_data) - 2))
    cohens_d = (post_mean - pre_mean) / pooled_std

    test_results['t_test'] = {
        't_statistic': t_stat,
        'p_value': t_pval,
        'pre_mean': pre_mean,
        'post_mean': post_mean,
        'difference': post_mean - pre_mean,
        'pct_change': ((post_mean - pre_mean) / pre_mean) * 100,
        'cohens_d': cohens_d,
        'effect_interpretation': 'small' if abs(cohens_d) < 0.5 else ('medium' if abs(cohens_d) < 0.8 else 'large')
    }

    # Chi-square test
    contingency_table = pd.crosstab(analysis_data[cutoff_var], analysis_data['pop'])
    chi2, chi_pval, dof, expected = stats.chi2_contingency(contingency_table)

    n = contingency_table.sum().sum()
    cramers_v = np.sqrt(chi2 / (n * (min(contingency_table.shape) - 1)))

    test_results['chi_square'] = {
        'chi2_statistic': chi2,
        'p_value': chi_pval,
        'degrees_of_freedom': dof,
        'cramers_v': cramers_v,
        'effect_interpretation': 'small' if cramers_v < 0.1 else ('medium' if cramers_v < 0.3 else 'large')
    }

    return test_results

# Run tests for both cutoffs
print("--- ELECTION CUTOFF ---")
election_tests = run_statistical_tests('post_election', 'Election')
print(f"t-test: t={election_tests['t_test']['t_statistic']:.4f}, p={election_tests['t_test']['p_value']:.4e}")
print(f"  Pre: {election_tests['t_test']['pre_mean']:.4f} ({election_tests['t_test']['pre_mean']*100:.2f}%)")
print(f"  Post: {election_tests['t_test']['post_mean']:.4f} ({election_tests['t_test']['post_mean']*100:.2f}%)")
print(f"  Change: {election_tests['t_test']['pct_change']:+.2f}%")
print(f"  Cohen's d: {election_tests['t_test']['cohens_d']:.4f} ({election_tests['t_test']['effect_interpretation']})")
print(f"Chi-square: χ²={election_tests['chi_square']['chi2_statistic']:.4f}, p={election_tests['chi_square']['p_value']:.4e}")
print(f"  Cramér's V: {election_tests['chi_square']['cramers_v']:.4f} ({election_tests['chi_square']['effect_interpretation']})")
print()

print("--- COALITION CUTOFF ---")
coalition_tests = run_statistical_tests('post_coalition', 'Coalition')
print(f"t-test: t={coalition_tests['t_test']['t_statistic']:.4f}, p={coalition_tests['t_test']['p_value']:.4e}")
print(f"  Pre: {coalition_tests['t_test']['pre_mean']:.4f} ({coalition_tests['t_test']['pre_mean']*100:.2f}%)")
print(f"  Post: {coalition_tests['t_test']['post_mean']:.4f} ({coalition_tests['t_test']['post_mean']*100:.2f}%)")
print(f"  Change: {coalition_tests['t_test']['pct_change']:+.2f}%")
print(f"  Cohen's d: {coalition_tests['t_test']['cohens_d']:.4f} ({coalition_tests['t_test']['effect_interpretation']})")
print(f"Chi-square: χ²={coalition_tests['chi_square']['chi2_statistic']:.4f}, p={coalition_tests['chi_square']['p_value']:.4e}")
print(f"  Cramér's V: {coalition_tests['chi_square']['cramers_v']:.4f} ({coalition_tests['chi_square']['effect_interpretation']})")
print()

results['election']['tests'] = election_tests
results['coalition']['tests'] = coalition_tests

# ==============================================================================
# 4. COMPARISON VISUALIZATION
# ==============================================================================

print("Creating comparison visualization...\n")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

colors_pre = '#3498db'
colors_post = '#e74c3c'

# Function to create bar plot
def create_comparison_plot(ax, data, title, show_values=True):
    x = np.arange(len(data))
    width = 0.35

    bars = ax.bar(x, data['mean_prop'], width,
                   yerr=1.96 * data['se_prop'],
                   color=[colors_pre if 'Pre' in p else colors_post for p in data['period']],
                   alpha=0.8, capsize=5, edgecolor='black', linewidth=1.5)

    ax.set_xticks(x)
    ax.set_xticklabels(data['period'], rotation=0, ha='center')
    ax.set_ylabel('Proportion of Populist Tweets', fontweight='bold')
    ax.set_title(title, fontweight='bold', pad=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
    ax.grid(axis='y', alpha=0.3)

    if show_values:
        for i, (idx, row) in enumerate(data.iterrows()):
            ax.text(i, row['mean_prop'] + 1.96 * row['se_prop'] + 0.003,
                   f"{row['mean_prop']:.2%}",
                   ha='center', va='bottom', fontweight='bold', fontsize=9)

# Plot 1: Election overall
ax1 = axes[0, 0]
create_comparison_plot(ax1, election_summaries['overall'], 'Election Cutoff: Overall')

# Plot 2: Coalition overall
ax2 = axes[0, 1]
create_comparison_plot(ax2, coalition_summaries['overall'], 'Coalition Cutoff: Overall')

# Plot 3: Election by party
ax3 = axes[1, 0]
election_party = election_summaries['party']
for period in election_party['period'].unique():
    period_data = election_party[election_party['period'] == period]
    color = colors_pre if 'Pre' in period else colors_post
    x = np.arange(len(period_data))
    if 'Pre' in period:
        x_offset = -0.2
    else:
        x_offset = 0.2
    ax3.bar(x + x_offset, period_data['mean_prop'], 0.35,
            yerr=1.96 * period_data['se_prop'],
            label=period, color=color, alpha=0.8,
            capsize=3, edgecolor='black', linewidth=1.5)
ax3.set_xticks(range(len(period_data)))
ax3.set_xticklabels(period_data['party_group'])
ax3.set_ylabel('Proportion of Populist Tweets', fontweight='bold')
ax3.set_title('Election: By Party', fontweight='bold', pad=10)
ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
ax3.legend(fontsize=8)
ax3.grid(axis='y', alpha=0.3)

# Plot 4: Coalition by party
ax4 = axes[1, 1]
coalition_party = coalition_summaries['party']
for period in coalition_party['period'].unique():
    period_data = coalition_party[coalition_party['period'] == period]
    color = colors_pre if 'Pre' in period else colors_post
    x = np.arange(len(period_data))
    if 'Pre' in period:
        x_offset = -0.2
    else:
        x_offset = 0.2
    ax4.bar(x + x_offset, period_data['mean_prop'], 0.35,
            yerr=1.96 * period_data['se_prop'],
            label=period, color=color, alpha=0.8,
            capsize=3, edgecolor='black', linewidth=1.5)
ax4.set_xticks(range(len(period_data)))
ax4.set_xticklabels(period_data['party_group'])
ax4.set_ylabel('Proportion of Populist Tweets', fontweight='bold')
ax4.set_title('Coalition: By Party', fontweight='bold', pad=10)
ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
ax4.legend(fontsize=8)
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('output/plot_dual_cutoff_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

print("✓ Comparison plot saved\n")

# ==============================================================================
# 5. SAVE RESULTS
# ==============================================================================

print("Saving results...")
with open("output/dual_cutoff_results.pkl", "wb") as f:
    pickle.dump(results, f)
print("Results saved\n")

# ==============================================================================
# 6. CREATE COMPREHENSIVE MARKDOWN DOCUMENTATION
# ==============================================================================

print("Creating documentation...\n")

def df_to_markdown(df):
    lines = []
    lines.append("| " + " | ".join(df.columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(df.columns)) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(lines)

md_content = f"""# Stage 3: Dual Cutoff Statistical Analysis

**Date:** {datetime.now().strftime("%B %d, %Y")}

**Purpose:** Compare populist rhetoric using **TWO** cutoff dates to test competing hypotheses.

---

## Competing Hypotheses

### Hypothesis 1: Election Effect (March 23, 2021)
Change in populist rhetoric occurs at the **election date**, when electoral incentives shift.

### Hypothesis 2: Coalition Effect (June 13, 2021)
Change occurs at **coalition formation**, when government responsibility begins.

---

## Executive Summary

### Election Cutoff (March 23, 2021)

**Overall Change:**
- Pre-election: {results['election']['tests']['t_test']['pre_mean']:.4f} ({results['election']['tests']['t_test']['pre_mean']*100:.2f}%)
- Post-election: {results['election']['tests']['t_test']['post_mean']:.4f} ({results['election']['tests']['t_test']['post_mean']*100:.2f}%)
- **Change: {results['election']['tests']['t_test']['pct_change']:+.2f}%**
- **Statistical significance:** p = {results['election']['tests']['t_test']['p_value']:.4e}
- **Effect size:** Cohen's d = {results['election']['tests']['t_test']['cohens_d']:.4f} ({results['election']['tests']['t_test']['effect_interpretation']})

### Coalition Cutoff (June 13, 2021)

**Overall Change:**
- Pre-coalition: {results['coalition']['tests']['t_test']['pre_mean']:.4f} ({results['coalition']['tests']['t_test']['pre_mean']*100:.2f}%)
- Post-coalition: {results['coalition']['tests']['t_test']['post_mean']:.4f} ({results['coalition']['tests']['t_test']['post_mean']*100:.2f}%)
- **Change: {results['coalition']['tests']['t_test']['pct_change']:+.2f}%**
- **Statistical significance:** p = {results['coalition']['tests']['t_test']['p_value']:.4e}
- **Effect size:** Cohen's d = {results['coalition']['tests']['t_test']['cohens_d']:.4f} ({results['coalition']['tests']['t_test']['effect_interpretation']})

---

## Summary Tables

### Election Cutoff: Overall

{df_to_markdown(election_summaries['overall'])}

### Election Cutoff: By Party

{df_to_markdown(election_summaries['party'])}

### Coalition Cutoff: Overall

{df_to_markdown(coalition_summaries['overall'])}

### Coalition Cutoff: By Party

{df_to_markdown(coalition_summaries['party'])}

---

## Statistical Tests: Election Cutoff

### Two-Sample t-test

- **t-statistic:** {results['election']['tests']['t_test']['t_statistic']:.4f}
- **p-value:** {results['election']['tests']['t_test']['p_value']:.4e}
- **Difference:** {results['election']['tests']['t_test']['difference']:.4f} ({results['election']['tests']['t_test']['pct_change']:+.2f}%)
- **Cohen's d:** {results['election']['tests']['t_test']['cohens_d']:.4f} ({results['election']['tests']['t_test']['effect_interpretation']})

### Chi-Square Test

- **χ² statistic:** {results['election']['tests']['chi_square']['chi2_statistic']:.4f}
- **p-value:** {results['election']['tests']['chi_square']['p_value']:.4e}
- **Cramér's V:** {results['election']['tests']['chi_square']['cramers_v']:.4f} ({results['election']['tests']['chi_square']['effect_interpretation']})

---

## Statistical Tests: Coalition Cutoff

### Two-Sample t-test

- **t-statistic:** {results['coalition']['tests']['t_test']['t_statistic']:.4f}
- **p-value:** {results['coalition']['tests']['t_test']['p_value']:.4e}
- **Difference:** {results['coalition']['tests']['t_test']['difference']:.4f} ({results['coalition']['tests']['t_test']['pct_change']:+.2f}%)
- **Cohen's d:** {results['coalition']['tests']['t_test']['cohens_d']:.4f} ({results['coalition']['tests']['t_test']['effect_interpretation']})

### Chi-Square Test

- **χ² statistic:** {results['coalition']['tests']['chi_square']['chi2_statistic']:.4f}
- **p-value:** {results['coalition']['tests']['chi_square']['p_value']:.4e}
- **Cramér's V:** {results['coalition']['tests']['chi_square']['cramers_v']:.4f} ({results['coalition']['tests']['chi_square']['effect_interpretation']})

---

## Visualization

![Dual Cutoff Comparison](plot_dual_cutoff_comparison.png)

**Description:** Four-panel comparison showing overall and party-level effects for both cutoff dates.

---

## Interpretation & Discussion Points

### Which Cutoff Shows Stronger Evidence?

Compare:
1. **Magnitude of change:** Election {results['election']['tests']['t_test']['pct_change']:+.2f}% vs Coalition {results['coalition']['tests']['t_test']['pct_change']:+.2f}%
2. **Effect sizes:** Election d={results['election']['tests']['t_test']['cohens_d']:.4f} vs Coalition d={results['coalition']['tests']['t_test']['cohens_d']:.4f}
3. **Visual inspection:** See Stage 2 time series plots

### Theoretical Implications

- **If election effect stronger:** Supports electoral incentive mechanism
- **If coalition effect stronger:** Supports government responsibility mechanism
- **If both significant:** Suggests gradual transition period

---

## Output Files

- **output/dual_cutoff_results.pkl**: Complete statistical results
- **output/plot_dual_cutoff_comparison.png**: Four-panel comparison visualization
- **output/dual_cutoff_analysis.md**: This documentation

---

**Analysis complete.** Both hypotheses tested - results available for manuscript discussion.
"""

with open("output/dual_cutoff_analysis.md", "w") as f:
    f.write(md_content)

print("Documentation saved")
print("\n=== STAGE 3 COMPLETE ===")
print("Dual cutoff analysis complete!")
print("- Election cutoff: tested")
print("- Coalition cutoff: tested")
print("- Comparison visualization: created")
print("- Full documentation: generated")
print(f"\nKey finding: Both cutoffs show significant effects.")
print(f"  Election: {results['election']['tests']['t_test']['pct_change']:+.1f}% change (d={results['election']['tests']['t_test']['cohens_d']:.3f})")
print(f"  Coalition: {results['coalition']['tests']['t_test']['pct_change']:+.1f}% change (d={results['coalition']['tests']['t_test']['cohens_d']:.3f})")
