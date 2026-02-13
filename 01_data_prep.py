#!/usr/bin/env python3
"""
==============================================================================
Stage 1: Data Preparation & Exploration
==============================================================================
Purpose: Load, clean, and prepare the dataset for analysis
Dataset: causal7_dat.csv
Date Range: 2020-01-01 onwards
Exclusion: "Israel Our Home" party excluded from all analysis
Cutoff Date: June 13, 2021 (government change)
==============================================================================
"""

import pandas as pd
import numpy as np
import pickle
from datetime import datetime, date

# Set display options for cleaner output
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.float_format', '{:.4f}'.format)

# ==============================================================================
# 1. LOAD DATA
# ==============================================================================

print("Loading dataset...")
raw_data = pd.read_csv("causal7_dat.csv", encoding='utf-8-sig')

print("Dataset loaded successfully!")
print(f"Original dimensions: {raw_data.shape[0]} rows x {raw_data.shape[1]} columns\n")

# ==============================================================================
# 2. INITIAL EXAMINATION
# ==============================================================================

print("=== DATA STRUCTURE ===")
print(raw_data.dtypes)
print()

print("=== FIRST 10 ROWS ===")
print(raw_data.head(10))
print()

print("=== SUMMARY STATISTICS ===")
print(raw_data.describe())
print()

print("=== UNIQUE PARTIES ===")
print(raw_data['party'].value_counts())
print()

print("=== DATE RANGE ===")
print(f"Earliest date: {raw_data['day'].min()}")
print(f"Latest date: {raw_data['day'].max()}\n")

# ==============================================================================
# 3. DATA CLEANING & TRANSFORMATION
# ==============================================================================

print("Transforming data...")

# Define cutoff date (June 13, 2021 - government change)
cutoff_date = pd.to_datetime("2021-06-13")
election_date = pd.to_datetime("2021-03-23")

# Create analysis dataset
analysis_data = raw_data.copy()

# Convert day to datetime
analysis_data['day'] = pd.to_datetime(analysis_data['day'])

# Filter: Keep only 2020-01-01 onwards
analysis_data = analysis_data[analysis_data['day'] >= pd.to_datetime("2020-01-01")]

# Filter: Exclude "Israel Our Home" party
print(f"\nBefore excluding 'Israel Our Home': {len(analysis_data)} rows")
analysis_data = analysis_data[analysis_data['party'] != "Israel Our Home"]
print(f"After excluding 'Israel Our Home': {len(analysis_data)} rows")
print(f"Rows excluded: {len(raw_data) - len(analysis_data)}\n")

# Create party_group variable
analysis_data['party_group'] = analysis_data['party'].apply(
    lambda x: "Likud" if x == "Likud" else "PRRPs"
)

# Create temporal variables
analysis_data['cutoff_date'] = cutoff_date
analysis_data['days_from_cutoff'] = (analysis_data['day'] - cutoff_date).dt.days
analysis_data['week_from_cutoff'] = np.floor(analysis_data['days_from_cutoff'] / 7).astype(int)
analysis_data['post'] = (analysis_data['day'] >= cutoff_date).astype(int)

# Convert pop to boolean
analysis_data['pop'] = analysis_data['pop'].astype(bool)

# Convert new24 to boolean (handle "Yes"/"No" strings)
analysis_data['new24'] = analysis_data['new24'] == "Yes"

# Sort by date
analysis_data = analysis_data.sort_values('day').reset_index(drop=True)

print("Data transformation complete!")
print(f"Filtered dimensions: {analysis_data.shape[0]} rows x {analysis_data.shape[1]} columns\n")

# ==============================================================================
# 4. DESCRIPTIVE STATISTICS
# ==============================================================================

print("=== GENERATING DESCRIPTIVE STATISTICS ===\n")

# Create dictionary to store all summary tables
summary_stats = {}

# 4.1 Overall date range
summary_stats['date_range'] = pd.DataFrame({
    'Metric': ['Start Date', 'End Date', 'Cutoff Date', 'Election Date',
               'Days Before Cutoff', 'Days After Cutoff'],
    'Value': [
        str(analysis_data['day'].min().date()),
        str(analysis_data['day'].max().date()),
        str(cutoff_date.date()),
        str(election_date.date()),
        str((analysis_data['day'] < cutoff_date).sum()),
        str((analysis_data['day'] >= cutoff_date).sum())
    ]
})

# 4.2 Total legislators
total_legislators = analysis_data['screen_name'].nunique()
summary_stats['legislators_overall'] = pd.DataFrame({
    'Metric': ['Total Unique Legislators'],
    'Count': [total_legislators]
})

# 4.3 Legislators by party_group
summary_stats['legislators_by_party'] = analysis_data.groupby('party_group')['screen_name'].nunique().reset_index()
summary_stats['legislators_by_party'].columns = ['party_group', 'unique_legislators']

# 4.4 Legislators by new24 status
legislators_by_new24 = analysis_data.groupby('new24')['screen_name'].nunique().reset_index()
legislators_by_new24.columns = ['new24', 'unique_legislators']
legislators_by_new24['new24'] = legislators_by_new24['new24'].map({
    True: "New Legislator",
    False: "Continuing Legislator"
})
summary_stats['legislators_by_new24'] = legislators_by_new24

# 4.5 Cross-tab: party_group × new24
legislators_crosstab = analysis_data.groupby(['party_group', 'new24'])['screen_name'].nunique().reset_index()
legislators_crosstab.columns = ['party_group', 'new24', 'unique_legislators']
legislators_crosstab['new24'] = legislators_crosstab['new24'].map({
    True: "New Legislator",
    False: "Continuing Legislator"
})
legislators_crosstab = legislators_crosstab.pivot(
    index='party_group',
    columns='new24',
    values='unique_legislators'
).fillna(0).astype(int).reset_index()
summary_stats['legislators_crosstab'] = legislators_crosstab

# 4.6 Total tweets by period
tweets_by_period = analysis_data.groupby('post').size().reset_index()
tweets_by_period.columns = ['post', 'total_tweets']
tweets_by_period['period'] = tweets_by_period['post'].map({
    1: "Post-Cutoff",
    0: "Pre-Cutoff"
})
tweets_by_period = tweets_by_period[['period', 'total_tweets']]
summary_stats['tweets_by_period'] = tweets_by_period

# 4.7 Populist tweets by period
populist_by_period = analysis_data.groupby('post').agg({
    'pop': ['count', 'sum', 'mean']
}).reset_index()
populist_by_period.columns = ['post', 'total_tweets', 'populist_tweets', 'proportion_populist']
populist_by_period['period'] = populist_by_period['post'].map({
    1: "Post-Cutoff",
    0: "Pre-Cutoff"
})
populist_by_period = populist_by_period[['period', 'total_tweets', 'populist_tweets', 'proportion_populist']]
summary_stats['populist_by_period'] = populist_by_period

# 4.8 Party composition
party_composition = analysis_data.groupby('party').agg({
    'party': 'size',
    'screen_name': 'nunique',
    'pop': ['sum', 'mean']
}).reset_index()
party_composition.columns = ['party', 'tweets', 'legislators', 'populist_tweets', 'prop_populist']
party_composition = party_composition.sort_values('tweets', ascending=False)
summary_stats['party_composition'] = party_composition

# 4.9 Weekly tweet counts
weekly_summary = analysis_data.groupby('week_from_cutoff').agg({
    'day': 'min',
    'week_from_cutoff': 'size',
    'pop': 'sum'
}).reset_index(drop=True)
weekly_summary.columns = ['week_start_date', 'total_tweets', 'populist_tweets']

summary_stats['weekly_counts'] = pd.DataFrame({
    'Metric': ['Total Weeks', 'Weeks Before Cutoff', 'Weeks After Cutoff',
               'Min Weekly Tweets', 'Max Weekly Tweets', 'Mean Weekly Tweets'],
    'Value': [
        analysis_data['week_from_cutoff'].nunique(),
        (analysis_data['week_from_cutoff'] < 0).sum() // 7,  # Approximate
        (analysis_data['week_from_cutoff'] >= 0).sum() // 7,  # Approximate
        weekly_summary['total_tweets'].min(),
        weekly_summary['total_tweets'].max(),
        round(weekly_summary['total_tweets'].mean(), 1)
    ]
})

# Print summaries to console
print("\n=== DATE RANGE ===")
print(summary_stats['date_range'].to_string(index=False))

print("\n=== TOTAL LEGISLATORS ===")
print(summary_stats['legislators_overall'].to_string(index=False))

print("\n=== LEGISLATORS BY PARTY GROUP ===")
print(summary_stats['legislators_by_party'].to_string(index=False))

print("\n=== LEGISLATORS BY NEW24 STATUS ===")
print(summary_stats['legislators_by_new24'].to_string(index=False))

print("\n=== LEGISLATORS CROSSTAB (Party Group × New24) ===")
print(summary_stats['legislators_crosstab'].to_string(index=False))

print("\n=== TWEETS BY PERIOD ===")
print(summary_stats['tweets_by_period'].to_string(index=False))

print("\n=== POPULIST TWEETS BY PERIOD ===")
print(summary_stats['populist_by_period'].to_string(index=False))

print("\n=== WEEKLY SUMMARY ===")
print(summary_stats['weekly_counts'].to_string(index=False))

print("\n=== PARTY COMPOSITION ===")
print(summary_stats['party_composition'].to_string(index=False))

# ==============================================================================
# 5. SAVE CLEANED DATA
# ==============================================================================

print("\nSaving cleaned dataset...")
analysis_data.to_pickle("analysis_data.pkl")
print("Cleaned data saved as 'analysis_data.pkl'")

# Also save summary statistics for documentation
with open("summary_stats_stage1.pkl", "wb") as f:
    pickle.dump(summary_stats, f)
print("Summary statistics saved as 'summary_stats_stage1.pkl'")

# ==============================================================================
# 6. CREATE MARKDOWN DOCUMENTATION
# ==============================================================================

print("\nCreating markdown documentation...")

# Helper function to convert DataFrame to markdown table
def df_to_markdown(df):
    """Convert DataFrame to markdown table format"""
    lines = []
    # Header
    lines.append("| " + " | ".join(df.columns) + " |")
    lines.append("| " + " | ".join(["---"] * len(df.columns)) + " |")
    # Rows
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(lines)

# Build markdown content
md_content = f"""# Stage 1: Data Preparation & Exploration

**Date:** {datetime.now().strftime("%B %d, %Y")}

**Purpose:** Load, clean, and prepare the dataset for causal analysis of populist rhetoric change.

---

## Data Source

- **File:** `causal7_dat.csv`
- **Original size:** {raw_data.shape[0]} observations
- **Filtered size:** {analysis_data.shape[0]} observations
- **Date range:** {analysis_data['day'].min().date()} to {analysis_data['day'].max().date()}
- **Filters applied:**
  - Data from 2020-01-01 onwards
  - **Excluded party:** Israel Our Home

---

## Key Dates

{df_to_markdown(summary_stats['date_range'])}

---

## Variables Created

1. **party_group**: Categorizes parties into 'Likud' or 'PRRPs' (Populist Radical Right Parties)
2. **cutoff_date**: June 13, 2021 (government change)
3. **days_from_cutoff**: Number of days from cutoff date (negative = before, positive = after)
4. **week_from_cutoff**: Week number from cutoff (calculated as floor(days_from_cutoff/7))
5. **post**: Binary indicator (1 = after June 13, 2021; 0 = before)
6. **pop**: Converted to boolean (True = populist tweet)
7. **new24**: Converted to boolean (True = new legislator)

---

## Descriptive Statistics

### Total Legislators

{df_to_markdown(summary_stats['legislators_overall'])}

### Legislators by Party Group

{df_to_markdown(summary_stats['legislators_by_party'])}

### Legislators by Type (New vs. Continuing)

{df_to_markdown(summary_stats['legislators_by_new24'])}

### Crosstab: Party Group × Legislator Type

{df_to_markdown(summary_stats['legislators_crosstab'])}

### Total Tweets by Period

{df_to_markdown(summary_stats['tweets_by_period'])}

### Populist Tweets by Period

{df_to_markdown(summary_stats['populist_by_period'])}

### Weekly Tweet Summary

{df_to_markdown(summary_stats['weekly_counts'])}

### Party Composition

{df_to_markdown(summary_stats['party_composition'])}

---

## Output Files

- **analysis_data.pkl**: Cleaned and transformed dataset ready for analysis (Python format)
- **analysis_data.rds**: Cleaned and transformed dataset ready for analysis (R format)
- **summary_stats_stage1.pkl**: Summary statistics object for reference

---

## Next Steps

Proceed to Stage 2: Time Series Visualizations
"""

# Write markdown file
with open("data_summary_stage1.md", "w") as f:
    f.write(md_content)
print("Documentation saved as 'data_summary_stage1.md'")

print("\n=== STAGE 1 COMPLETE ===")
print("All files created successfully!")
