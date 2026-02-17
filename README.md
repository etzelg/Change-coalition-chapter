# Populist Rhetoric: Election Cutoff Analysis

**Branch:** `claude/election-cutoff-analysis-QqAoc`
**Cutoff:** Election — March 23, 2021

---

## Overview

Analyses whether the 2021 Israeli election produced differential changes in
populist rhetoric across two theoretically distinct blocs:

1. **Radicalized and Radical Populism** — Likud + Religious Zionism (Netanyahu bloc)
2. **PRRPs in Change Coalition** — Rightwards + Israel Our Home (anti-Netanyahu)

All 7 parties are included in the dataset (no exclusions).

---

## Key Findings

### Comparison 1 — All parties pre vs "Radicalized and Radical Populism" post

| | Proportion | N |
|---|---|---|
| Pre-election (all 7 parties) | 3.92% | 31,404 |
| Post-election (Likud + Religious Zionism) | 7.41% | 37,082 |
| **Change** | **+89.1%** | |

t = −19.52, p < 0.001, Cohen's d = 0.150

**Party detail:**
- Likud: +128.8% (3.63% → 8.31%)
- PRR legislators: +15.0% (5.66% → 6.51%)
  — Pre: bezalelsm, michalwoldiger, ofir_sofer, oritstrock
  — Post adds: rothmar, itamarbengvir

### Comparison 2 — PRRPs in Change Coalition pre vs post

| | Proportion | N |
|---|---|---|
| Pre-election | 3.80% | 10,480 |
| Post-election | 2.01% | 7,510 |
| **Change** | **−47.1%** | |

t = 6.88, p < 0.001, Cohen's d = −0.104

**Party detail:**
- Rightwards: −32.9% (2.77% → 1.86%)
- Israel Our Home: −57.9% (5.54% → 2.33%)

**Interpretation:** The Change Coalition parties *reduced* populist rhetoric
after the election, the inverse of the Netanyahu bloc — consistent with
government responsibility effects.

---

## Repository Structure

```
├── 01_data_prep.py             # Data preparation (Python)
├── 01_data_prep.R              # Data preparation (R)
├── 02_time_series_plots.py     # Time series plots (Python)
├── 02_time_series_plots.R      # Time series plots (R)
├── 03_before_after.py          # Before/after analysis (Python)
├── 03_before_after.R           # Before/after analysis (R)
├── causal7_dat.csv             # Raw data
└── output/
    ├── analysis_data.pkl/.csv       # Cleaned dataset
    ├── data_summary.md              # Stage 1 documentation
    ├── plot2a_radicalized_trend.png # Time series: all vs radicalized
    ├── plot2b_change_coalition_trend.png  # Time series: Rightwards vs IOH
    ├── plot3a_comp1_overall.png     # Bar: comparison 1 overall
    ├── plot3b_comp1_by_group.png    # Bar: Likud vs PRR legislators
    ├── plot3c_comp2_overall.png     # Bar: comparison 2 overall
    ├── plot3d_comp2_by_party.png    # Bar: Rightwards vs Israel Our Home
    ├── comparison_results.pkl       # Python results object
    └── before_after_results.md      # Full statistical tables
```

---

## Running the Analysis

```bash
python3 01_data_prep.py
python3 02_time_series_plots.py
python3 03_before_after.py
```

R scripts require: `tidyverse`, `effsize`, `zoo`
```r
Rscript 01_data_prep.R
Rscript 02_time_series_plots.R
Rscript 03_before_after.R
```
R input: `output/analysis_data.csv` (created by Python Stage 1)

---

## Party Groupings

| Group | Parties / Screen names |
|---|---|
| Radicalized and Radical Populism (post) | Likud, Religious Zionism |
| PRRPs in Change Coalition | Rightwards, Israel Our Home |
| PRR legislators (pre) | bezalelsm, michalwoldiger, ofir_sofer, oritstrock |
| PRR legislators (post) | above + rothmar, itamarbengvir |
