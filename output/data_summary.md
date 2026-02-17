# Stage 1: Data Preparation Summary

**Date:** February 17, 2026
**Election cutoff:** March 23, 2021

## Dataset

- **Source:** causal7_dat.csv
- **Filter:** 2020-01-01 onwards, all 7 parties included
- **Total rows:** 76,003
- **Pre-election:** 31,404 tweets
- **Post-election:** 44,599 tweets

## Party Counts

                     party        period  total_tweets  populist_tweets  prop_pop
           Israel Our Home  Pre-election          3899              216  0.055399
           Israel Our Home Post-election          2444               57  0.023322
               Jewish Home  Pre-election           316               10  0.031646
               Jewish Home Post-election             7                0  0.000000
Jewish Home-National Union  Pre-election          3786              199  0.052562
                     Likud  Pre-election         16270              591  0.036325
                     Likud Post-election         18483             1536  0.083103
         Religious Zionism  Pre-election           552               32  0.057971
         Religious Zionism Post-election         18599             1211  0.065111
                Rightwards  Pre-election          6581              182  0.027655
                Rightwards Post-election          5066               94  0.018555

## Grouping Variables

| Variable | Definition |
|---|---|
| `radicalized_group` | party ∈ {Likud, Religious Zionism} |
| `change_coalition_group` | party ∈ {Rightwards, Israel Our Home} |
| `prr_leg_pre` | screen_name ∈ {bezalelsm, michalwoldiger, ofir_sofer, oritstrock} |
| `prr_leg_post` | prr_leg_pre ∪ {rothmar, itamarbengvir} |
