# Regression Discontinuity Design: Likud Populist Tweeting

**Scripts:** `04_rdd.R` (primary) · `04_rdd.py` (replication)
**Outputs:** `output/rdd/`

---

## 1. Research Question

Does losing an election — and the resulting transition from government to
opposition — cause an immediate *discontinuous* increase in populist rhetoric
among Likud legislators?

The before/after comparison (Stage 3) documents a large difference in populist
tweet rates pre- and post-election, but cannot rule out that this reflects a
longer time trend, anticipation effects during campaigning, or seasonal factors.
An RDD addresses these concerns by asking: is there a **sharp jump right at the
election date** that cannot be explained by the smooth time trend?

---

## 2. Why This Is an RDD

A Regression Discontinuity Design (RDD) is appropriate when:

1. An outcome of interest may change at a known threshold of a continuous
   **running variable**.
2. Units cannot perfectly manipulate the running variable to select treatment.

Here:

| RDD element | This study |
|---|---|
| Running variable | `days_from_election` — calendar days relative to March 23, 2021 (negative = before, positive = after) |
| Cutoff | 0 (the election date) |
| "Treatment" | Transition from governing party to opposition |
| Outcome | `pop` — binary indicator that a tweet contains populist rhetoric (0/1) |
| Sample | Likud legislators only |

Likud legislators had no control over when the election occurred or its outcome
on the day — Israel's 2021 election date was set by law and the result was
determined by the vote. The calendar is therefore an **exogenous cutoff**.

---

## 3. The Formal Model

Let $y_{it}$ be the populist tweet indicator for legislator $i$ on day $t$,
and let $x_t$ = `days_from_election` be the running variable. The sharp RDD
model is:

$$
y_{it} = \alpha + \tau \cdot \mathbf{1}[x_t \geq 0]
        + f_L(x_t) \cdot \mathbf{1}[x_t < 0]
        + f_R(x_t) \cdot \mathbf{1}[x_t \geq 0]
        + \varepsilon_{it}
$$

where $f_L$ and $f_R$ are smooth functions (here: linear, fitted separately on
each side) and $\tau$ is the **RD estimand** — the discontinuous jump in the
conditional mean of $y$ at $x = 0$.

In the **local linear** version used here:

$$
f_L(x) = \beta_{L0} + \beta_{L1} x, \qquad
f_R(x) = \beta_{R0} + \beta_{R1} x
$$

and $\tau = \beta_{R0} - \beta_{L0}$ — the difference in the two intercepts
(both evaluated at the cutoff $x = 0$).

---

## 4. Estimation Details

### Kernel

We use a **triangular kernel**:

$$
K(x, h) = \left(1 - \frac{|x|}{h}\right) \cdot \mathbf{1}[|x| \leq h]
$$

Observations close to the cutoff receive weight 1; weight declines linearly to
0 at the bandwidth boundary $\pm h$. The triangular kernel is optimal for
estimating boundary values (Cheng, Fan, and Marron 1997) and is the default
in `rdrobust`.

### Bandwidth

Two approaches are used in parallel:

**Optimal (R only):** The `rdrobust` package implements the MSE-optimal
bandwidth selector of Calonico, Cattaneo, and Titiunik (2014, CCT). This
selects $h$ to minimise the asymptotic mean-squared error of the RD estimator,
trading off variance (smaller $h$ = fewer observations = higher variance)
against bias (larger $h$ = more smoothing = potential bias from non-linearity).

**Fixed (both scripts):** Three pre-specified windows — 90, 120, and 180 days —
are reported to guard against the possibility that the CCT-optimal value
happens to favour the result.

### Standard Errors

**R script:** Standard errors are clustered at the legislator (`screen_name`)
level using `rdrobust`'s built-in cluster option. This accounts for the fact
that tweets from the same legislator are not independent — a legislator who
adopts a more populist tone will produce many correlated populist tweets. The
reported confidence intervals are **bias-corrected and robust** (the "robust"
row in rdrobust output).

**Python script:** HC1 heteroskedasticity-robust SEs are computed from the WLS
closed form. These are *not* legislator-clustered, so they will generally be
smaller (more optimistic) than the R estimates. Use the R output for inference;
the Python output is a consistency check on the point estimates.

### Unit of observation

Each row is a **single tweet**. Multiple tweets per legislator per day share the
same running-variable value $x_t$, which is valid — `rdrobust` handles repeated
values of the running variable gracefully (they are treated as tied). Clustering
by legislator accounts for the resulting intra-group correlation.

---

## 5. Identifying Assumption: Continuity

The RDD is valid if, in the absence of the election, the *expected* populist
tweet rate would have evolved **smoothly** through March 23, 2021. Any observed
jump is then attributed causally to the election outcome (losing → opposition).

This assumption would be violated by:

| Threat | Severity | Discussion |
|---|---|---|
| **Campaign contamination** | High | The 6-month pre-window includes active campaigning. Legislators may ramp up populist rhetoric *before* the election in anticipation of a loss, making the pre-cutoff trend non-smooth. A visual check of the RD plot is essential. |
| **Anticipation effects** | Medium | If legislators knew they would lose, they might begin shifting rhetoric before the cutoff. This would compress the estimated jump toward zero (attenuation). |
| **Concurrent events** | Low–Medium | Israel held its 4th election in 2 years in March 2021; external shocks (COVID waves, Gaza tensions) could coincide with the cutoff but are unlikely to align precisely with the election date. |
| **Running-variable manipulation** | None | Legislators cannot choose when the election falls or its result. The density continuity test (McCrary 2008) is unnecessary here — there is no meaningful way to "sort" around an election date. |

**Recommendation:** Inspect the RD plots (`output/rdd/`) carefully for
evidence of a pre-trend or a gradual (rather than sharp) change. If the fitted
line on the left side is already rising steeply as it approaches the cutoff,
campaign effects may be present and a shorter bandwidth (≤ 90 days, avoiding
most of the campaign period) is preferable.

---

## 6. What the Estimate Means

$\tau$ is the **Local Average Treatment Effect (LATE)** at the cutoff:

> The estimated immediate change in the probability that any given Likud
> tweet contains populist rhetoric, right at the moment of electoral defeat.

Because a tweet is a binary event ($y \in \{0, 1\}$), $\tau$ is expressed in
**percentage points** (e.g., $\tau = 0.02$ means a 2 pp increase in the
probability a tweet is populist, right at the cutoff).

This is a *local* effect — it applies specifically to the cutoff (the election
itself) and need not generalise to, say, a hypothetical election happening at a
different time or under different conditions.

---

## 7. Bandwidth Sensitivity

The sensitivity plot (`rdd_sensitivity.png`) shows the RD estimate and its
robust 95% CI across all bandwidths from 30 to 180 days in 5-day steps.

A **credible** RDD result is stable across a range of bandwidths:
- The sign of $\tau$ should not flip
- The magnitude should be roughly constant (some decrease as $h$ shrinks, due
  to variance, is expected)
- Significance need not hold at very small $h$ (too little data), but should
  appear consistently across the middle range

If the estimate is only significant at one specific bandwidth, this warrants
caution.

---

## 8. Interpreting the Python Results

The Python script estimates at fixed bandwidths (90, 120, 180 days):

| h | τ̂ | p (HC1) |
|---|---|---|
| 90d  | +0.006 | 0.55 (n.s.) |
| 120d | +0.012 | 0.20 (n.s.) |
| 180d | +0.015 | 0.06 (marginal) |

The positive direction is consistent across all bandwidths and matches the
before/after comparison, but significance depends on the window. The R output
with legislator-clustered SEs will give the authoritative inference. Note that
non-significance in the RDD does not contradict the before/after finding — it
means we cannot isolate a *sharp discontinuity at the exact cutoff*. The
before/after comparison captures the full post-election period, while the RDD
estimates only the *immediate jump*.

---

## 9. Why Likud Only (not PRR Legislators)

The 4 PRR legislators (`bezalelsm`, `michalwoldiger`, `ofir_sofer`,
`oritstrock`) changed party affiliation around the election — moving from
smaller parties into Religious Zionism. For them, the election cutoff coincides
with a **party change**, so it is impossible to separate the effect of the
electoral outcome from the effect of joining a new, more extreme party. This
violates the continuity assumption: the composition of the treated group itself
changes at the cutoff.

For Likud, the same legislators remain in the same party before and after —
only their government/opposition status changes. The RDD is therefore cleanly
interpretable for Likud.

---

## 10. Key References

- Calonico, S., Cattaneo, M. D., & Titiunik, R. (2014). Robust nonparametric
  confidence intervals for regression-discontinuity designs. *Econometrica*,
  82(6), 2295–2326.
- Cattaneo, M. D., Idrobo, N., & Titiunik, R. (2019). *A Practical Introduction
  to Regression Discontinuity Designs*. Cambridge University Press.
- Cheng, M.-C., Fan, J., & Marron, J. S. (1997). On automatic boundary
  corrections. *Annals of Statistics*, 25(4), 1691–1708.
- Imbens, G., & Lemieux, T. (2008). Regression discontinuity designs: A guide
  to practice. *Journal of Econometrics*, 142(2), 615–635.
