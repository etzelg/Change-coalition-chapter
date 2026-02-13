# Stage 1: Data Preparation & Exploration

**Date:** February 13, 2026

**Purpose:** Load, clean, and prepare the dataset for causal analysis of populist rhetoric change.

---

## Data Source

- **File:** `causal7_dat.csv`
- **Original size:** 170754 observations
- **Filtered size:** 69660 observations
- **Date range:** 2020-01-01 to 2022-07-15
- **Filters applied:**
  - Data from 2020-01-01 onwards
  - **Excluded party:** Israel Our Home

---

## Key Dates

| Metric | Value |
| --- | --- |
| Start Date | 2020-01-01 |
| End Date | 2022-07-15 |
| Cutoff Date | 2021-06-13 |
| Election Date | 2021-03-23 |
| Days Before Cutoff | 34053 |
| Days After Cutoff | 35607 |

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

| Metric | Count |
| --- | --- |
| Total Unique Legislators | 50 |

### Legislators by Party Group

| party_group | unique_legislators |
| --- | --- |
| Likud | 37 |
| PRRPs | 13 |

### Legislators by Type (New vs. Continuing)

| new24 | unique_legislators |
| --- | --- |
| Continuing Legislator | 46 |
| New Legislator | 4 |

### Crosstab: Party Group × Legislator Type

| party_group | Continuing Legislator | New Legislator |
| --- | --- | --- |
| Likud | 36 | 1 |
| PRRPs | 10 | 3 |

### Total Tweets by Period

| period | total_tweets |
| --- | --- |
| Pre-Cutoff | 34053 |
| Post-Cutoff | 35607 |

### Populist Tweets by Period

| period | total_tweets | populist_tweets | proportion_populist |
| --- | --- | --- | --- |
| Pre-Cutoff | 34053 | 1432 | 0.04205209526326609 |
| Post-Cutoff | 35607 | 2423 | 0.06804841744600781 |

### Weekly Tweet Summary

| Metric | Value |
| --- | --- |
| Total Weeks | 133.0 |
| Weeks Before Cutoff | 4864.0 |
| Weeks After Cutoff | 5086.0 |
| Min Weekly Tweets | 157.0 |
| Max Weekly Tweets | 1035.0 |
| Mean Weekly Tweets | 523.8 |

### Party Composition

| party | tweets | legislators | populist_tweets | prop_populist |
| --- | --- | --- | --- | --- |
| Likud | 34753 | 37 | 2127 | 0.06120334935113515 |
| Religious Zionism | 19151 | 6 | 1243 | 0.06490522688110281 |
| Rightwards | 11647 | 5 | 276 | 0.02369708937923929 |
| Jewish Home-National Union | 3786 | 4 | 199 | 0.05256207078711041 |
| Jewish Home | 323 | 1 | 10 | 0.030959752321981424 |

---

## Output Files

- **analysis_data.pkl**: Cleaned and transformed dataset ready for analysis (Python format)
- **analysis_data.rds**: Cleaned and transformed dataset ready for analysis (R format)
- **summary_stats_stage1.pkl**: Summary statistics object for reference

---

## Next Steps

Proceed to Stage 2: Time Series Visualizations
