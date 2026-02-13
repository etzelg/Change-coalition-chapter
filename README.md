# Populist Rhetoric Analysis: Israeli Coalition Change 2021

## Overview

This repository contains a complete analysis of populist rhetoric changes among Israeli legislators around two critical dates in 2021:
- **Election**: March 23, 2021
- **Coalition Formation**: June 13, 2021

**Dataset**: Israeli legislator tweets from 2020-2022, excluding "Israel Our Home" party.

---

## Key Findings

### Dual Cutoff Analysis

**Election Cutoff (March 23, 2021):**
- Pre-election: 3.69% populist tweets
- Post-election: 6.74% populist tweets
- **Change: +82.8%** (Cohen's d = 0.134, p < 0.001)

**Coalition Cutoff (June 13, 2021):**
- Pre-coalition: 4.21% populist tweets
- Post-coalition: 6.80% populist tweets
- **Change: +61.8%** (Cohen's d = 0.114, p < 0.001)

**Conclusion**: The **election date shows a stronger effect**, suggesting populist rhetoric changes are driven more by electoral incentives than coalition formation.

---

## Repository Structure

```
├── 01_data_prep.py           # Python: Data preparation
├── 01_data_prep.R            # R: Data preparation (for reproducibility)
├── 02_time_series_plots.py   # Python: Time series visualizations
├── 02_time_series_plots.R    # R: Time series visualizations
├── 03_before_after.py        # Python: Dual cutoff statistical analysis
├── 03_before_after.R         # R: Dual cutoff analysis
├── causal7_dat.csv          # Raw data
├── output/                   # All analysis outputs
│   ├── analysis_data.pkl              # Cleaned dataset
│   ├── data_summary_stage1.md         # Stage 1 documentation
│   ├── summary_stats_stage1.pkl       # Stage 1 statistics
│   ├── plot1_overall_trend.png        # Overall time series (both dates)
│   ├── plot2_by_party.png             # By party time series (both dates)
│   ├── plots_stage2.md                # Stage 2 documentation
│   ├── plot_dual_cutoff_comparison.png # Four-panel comparison
│   ├── dual_cutoff_analysis.md        # Stage 3 documentation
│   └── dual_cutoff_results.pkl        # Complete statistical results
└── README.md                 # This file
```

---

## Analysis Pipeline

### Stage 1: Data Preparation
- Filters data from 2020-01-01 onwards
- **Excludes "Israel Our Home" party**
- Creates temporal variables for both cutoff dates
- Final dataset: 69,660 observations, 50 legislators

**Run**: `python3 01_data_prep.py` or `Rscript 01_data_prep.R`

### Stage 2: Time Series Visualizations
- Creates 2 plots showing populist rhetoric over time
- **Both election and coalition dates marked**
- 4-week rolling averages for smoothing

**Run**: `python3 02_time_series_plots.py` or `Rscript 02_time_series_plots.R`

### Stage 3: Dual Cutoff Statistical Analysis
- Runs t-tests and chi-square tests for **BOTH** cutoff dates
- Compares effect sizes to determine which hypothesis is supported
- Creates four-panel comparison visualization

**Run**: `python3 03_before_after.py` or `Rscript 03_before_after.R`

---

## Requirements

### Python
```bash
pip install pandas numpy scipy matplotlib seaborn
```

### R
```r
install.packages(c("tidyverse", "lubridate", "effsize", "gridExtra"))
```

---

## Reproducibility

Both Python (`.py`) and R (`.R`) scripts are provided for complete reproducibility:
- **Python scripts**: Run immediately, generate all outputs
- **R scripts**: Parallel implementation for publication/verification

All outputs are saved to the `output/` directory.

---

## Citation

If you use this analysis, please cite appropriately.

**Analysis completed**: February 13, 2026
**Session**: https://claude.ai/code/session_01NJkvGCZ7KeVPhtQ2uwBDFk
