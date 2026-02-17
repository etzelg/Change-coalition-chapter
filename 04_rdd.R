# ==============================================================================
# Stage 4: Regression Discontinuity Design — Likud Legislators
# ==============================================================================
#
# Research question:
#   Did losing the March 2021 election — and the resulting shift from government
#   to opposition — cause a sharp *immediate* increase in populist tweeting
#   among Likud legislators?
#
# Design:
#   Running variable : days_from_election (negative = pre, positive = post)
#   Outcome          : pop (binary 0/1, treated as local linear probability)
#   Cutoff           : 0  (March 23, 2021)
#   Sample           : party == "Likud" only
#   Clustering       : screen_name (tweets from same legislator are correlated)
#   Kernel           : triangular (down-weights observations far from the cutoff)
#   Polynomial order : 1 (local linear — the standard for RDD)
#
# Bandwidths:
#   (a) Optimal — chosen by the CCT (Calonico-Cattaneo-Titiunik 2014) MSE
#       criterion, computed automatically by rdrobust
#   (b) Fixed — 90, 120, 180 days, for robustness checks
#
# Outputs → output/rdd/
#   rdd_plot_optimal.png   — RD scatter + fit at optimal bandwidth
#   rdd_plot_90d.png       — same at h = 90 days
#   rdd_plot_120d.png      — same at h = 120 days
#   rdd_plot_180d.png      — same at h = 180 days
#   rdd_sensitivity.png    — RD estimate + CI swept across h = 30..180 days
#   rdd_results.rds        — all fitted objects for downstream use
# ==============================================================================

suppressPackageStartupMessages({
  library(tidyverse)
  library(rdrobust)   # install.packages("rdrobust") if missing
  library(scales)
})

options(scipen = 999)
dir.create("output/rdd", recursive = TRUE, showWarnings = FALSE)
cat("=== STAGE 4: RDD — LIKUD LEGISLATORS ===\n\n")

# ==============================================================================
# 1. DATA PREPARATION
# ==============================================================================
# We load the cleaned dataset produced by Stage 1. Each row is a single tweet.
# 'days_from_election' is already computed (negative = before, positive = after).
# We keep only Likud legislators and restrict to a maximum ±180-day window —
# the widest bandwidth we will ever test — to avoid loading unnecessary data.

data <- read_csv("output/analysis_data.csv", show_col_types = FALSE) %>%
  mutate(
    pop                = as.numeric(pop),
    days_from_election = as.numeric(days_from_election)
  )

# Full ±180-day Likud dataset (trimmed further inside each bandwidth run)
likud <- data %>%
  filter(party == "Likud",
         abs(days_from_election) <= 180)

n_legs <- n_distinct(likud$screen_name)
cat(sprintf("Likud tweets within ±180 days : %d\n",  nrow(likud)))
cat(sprintf("Unique legislators            : %d\n",  n_legs))
cat(sprintf("Date range                    : %s to %s\n\n",
            min(likud$day), max(likud$day)))

# ==============================================================================
# 2. OPTIMAL BANDWIDTH (Calonico-Cattaneo-Titiunik, 2014)
# ==============================================================================
# rdrobust selects h to minimise mean-squared error of the RD estimator.
# We pass cluster = screen_name so the bandwidth selector and variance estimator
# both account for within-legislator tweet correlation.
# The bias-correction bandwidth b is selected jointly.

cat("--- Optimal bandwidth (CCT MSE criterion) ---\n")

fit_opt <- rdrobust(
  y       = likud$pop,
  x       = likud$days_from_election,
  c       = 0,
  kernel  = "triangular",
  p       = 1,           # local linear (degree of polynomial fit)
  cluster = likud$screen_name
)

# Extract the symmetric bandwidth (left == right for triangular default)
h_opt <- round(fit_opt$bws["h", "left"])
b_opt <- round(fit_opt$bws["b", "left"])   # bias correction bandwidth

cat(sprintf("  Optimal h = %d days  (bias-correction b = %d days)\n", h_opt, b_opt))
cat(sprintf("  Conventional : τ = %+.4f  SE = %.4f  p = %.4f\n",
            fit_opt$coef["Conventional",    "Coeff"],
            fit_opt$se["Conventional",      "SE"],
            fit_opt$pv["Conventional",      "P-value"]))
cat(sprintf("  Bias-corrected robust: p = %.4f  CI = [%.4f, %.4f]\n\n",
            fit_opt$pv["Robust",            "P-value"],
            fit_opt$ci["Robust",            "CI Lower"],
            fit_opt$ci["Robust",            "CI Upper"]))

# ==============================================================================
# 3. RD ESTIMATES — FIXED BANDWIDTHS
# ==============================================================================
# We report three pre-specified bandwidths in addition to the optimal one.
# Using fixed bandwidths guards against the (unlikely) possibility that the CCT
# selector happens to choose a window that flatters the estimate.

BANDWIDTHS <- c(h_opt, 90, 120, 180)
LABELS     <- c(sprintf("Optimal (%dd)", h_opt), "90 days", "120 days", "180 days")

cat("--- RD estimates across bandwidths ---\n")
cat(sprintf("  %-20s  %+8s  %8s  %8s  %8s  %6s  %6s\n",
            "Bandwidth", "tau", "SE", "p_conv", "p_rob", "N_pre", "N_post"))

results <- list()
res_tbl <- tibble()

for (i in seq_along(BANDWIDTHS)) {
  h <- BANDWIDTHS[i]
  d <- likud %>% filter(abs(days_from_election) <= h)

  # tryCatch so the script doesn't crash if a tiny bandwidth fails
  fit <- tryCatch(
    rdrobust(y = d$pop, x = d$days_from_election, c = 0,
             h = h, kernel = "triangular", p = 1,
             cluster = d$screen_name),
    error = function(e) {
      message("  [!] rdrobust failed for h = ", h, ": ", e$message); NULL
    }
  )

  if (!is.null(fit)) {
    results[[LABELS[i]]] <- fit
    tau  <- fit$coef["Conventional", "Coeff"]
    se   <- fit$se  ["Conventional", "SE"]
    pc   <- fit$pv  ["Conventional", "P-value"]
    pr   <- fit$pv  ["Robust",       "P-value"]
    cilo <- fit$ci  ["Robust",       "CI Lower"]
    cihi <- fit$ci  ["Robust",       "CI Upper"]
    np   <- fit$N[1]; nq <- fit$N[2]

    cat(sprintf("  %-20s  %+8.4f  %8.4f  %8.4f  %8.4f  %6d  %6d\n",
                LABELS[i], tau, se, pc, pr, np, nq))

    res_tbl <- bind_rows(res_tbl, tibble(
      label = LABELS[i], h = h,
      tau   = tau, se = se, p_conv = pc, p_rob = pr,
      ci_lo = cilo, ci_hi = cihi,
      n_pre = np, n_post = nq
    ))
  }
}

# ==============================================================================
# 4. CUSTOM GGPLOT2 RD PLOTS
# ==============================================================================
# rdplot(..., plot = FALSE) returns two data frames:
#   vars_bins : binned sample means (one point per bin, with 95% CI bars)
#   vars_poly : smooth polynomial fit evaluated on a fine grid
# We reconstruct the plot in ggplot2 for publication-quality output.

make_rd_plot <- function(d, h, label) {

  # rdplot bins the data and fits the polynomial — we only want the data
  rp <- rdplot(
    y      = d$pop,
    x      = d$days_from_election,
    c      = 0,
    h      = h,
    nbins  = c(25, 25),        # bins on each side
    kernel = "triangular",
    p      = 1,
    plot   = FALSE             # suppress base-R plot
  )

  bins <- as.data.frame(rp$vars_bins) %>%
    mutate(side = if_else(rdplot_mean_x < 0, "Pre-election", "Post-election"),
           side = factor(side, levels = c("Pre-election", "Post-election")))

  poly <- as.data.frame(rp$vars_poly) %>%
    mutate(side = if_else(rdplot_x < 0, "Pre-election", "Post-election"),
           side = factor(side, levels = c("Pre-election", "Post-election")))

  # Fetch the estimate at *this* bandwidth for the annotation
  fit_h <- tryCatch(
    rdrobust(y = d$pop, x = d$days_from_election, c = 0,
             h = h, kernel = "triangular", p = 1,
             cluster = d$screen_name),
    error = function(e) NULL
  )

  ann <- if (!is.null(fit_h)) {
    tau  <- fit_h$coef["Conventional", "Coeff"]
    pr   <- fit_h$pv  ["Robust",       "P-value"]
    star <- case_when(pr < 0.001 ~ "***", pr < 0.01 ~ "**",
                      pr < 0.05  ~ "*",   TRUE ~ "n.s.")
    sprintf("τ = %+.3f %s\n(robust p = %.3f)\nn = %d tweets",
            tau, star, pr, nrow(d))
  } else "estimate unavailable"

  y_ann <- max(bins$rdplot_ci_r, na.rm = TRUE)

  ggplot() +
    # Binned means with 95% CI error bars
    geom_errorbar(data  = bins,
                  aes(x = rdplot_mean_x,
                      ymin = rdplot_ci_l, ymax = rdplot_ci_r,
                      color = side),
                  width = 0, linewidth = 0.5, alpha = 0.55) +
    geom_point(data = bins,
               aes(x = rdplot_mean_x, y = rdplot_mean_bin, color = side),
               size = 2.2, alpha = 0.9) +
    # Polynomial fit lines (one per side)
    geom_line(data = poly,
              aes(x = rdplot_x, y = rdplot_y, color = side),
              linewidth = 1.4) +
    # Cutoff
    geom_vline(xintercept = 0, linetype = "dashed",
               color = "#2c3e50", linewidth = 1) +
    # RD estimate annotation
    annotate("label",
             x     = -h * 0.65,
             y     = y_ann * 0.97,
             label = ann,
             size  = 3.1, color = "#2c3e50",
             fill  = "white", label.size = 0.3,
             hjust = 0, vjust = 1) +
    scale_color_manual(
      values = c("Pre-election" = "#3498db", "Post-election" = "#e74c3c"),
      name = NULL
    ) +
    scale_y_continuous(labels = percent_format(accuracy = 0.1)) +
    labs(
      x        = "Days from Election (March 23, 2021)",
      y        = "Proportion of Populist Tweets",
      title    = "RDD: Populist Tweeting by Likud Legislators",
      subtitle = paste0("Bandwidth: ", label,
                        "  |  triangular kernel, local linear, SE clustered by legislator"),
      caption  = paste0("Points = binned daily means with 95% CI.  ",
                        "Lines = local linear fit on each side of cutoff.")
    ) +
    theme_minimal(base_size = 11) +
    theme(
      plot.title       = element_text(face = "bold", size = 13),
      plot.subtitle    = element_text(size = 9.5, color = "#555"),
      plot.caption     = element_text(size = 7.5, color = "#777", face = "italic"),
      axis.title       = element_text(face = "bold"),
      legend.position  = "top",
      panel.grid.minor = element_blank()
    )
}

cat("\n--- Generating RD plots ---\n")

plot_specs <- list(
  list(h = h_opt, label = sprintf("optimal (%d days)", h_opt), fname = "rdd_plot_optimal.png"),
  list(h = 90,    label = "90 days",                           fname = "rdd_plot_90d.png"),
  list(h = 120,   label = "120 days",                          fname = "rdd_plot_120d.png"),
  list(h = 180,   label = "180 days",                          fname = "rdd_plot_180d.png")
)

for (spec in plot_specs) {
  d <- likud %>% filter(abs(days_from_election) <= spec$h)
  p <- make_rd_plot(d, spec$h, spec$label)
  ggsave(paste0("output/rdd/", spec$fname), p,
         width = 10, height = 6, dpi = 300)
  cat(sprintf("  ✓ output/rdd/%s\n", spec$fname))
}

# ==============================================================================
# 5. BANDWIDTH SENSITIVITY SWEEP
# ==============================================================================
# A trustworthy RDD result is stable across a range of bandwidths.
# We loop h from 30 to 180 in steps of 5 and store the RD estimate and its
# robust bias-corrected 95% CI at each value.
# If the estimate only appears at one particular bandwidth, that is suspicious.

cat("\n--- Bandwidth sensitivity sweep (h = 30 to 180 in steps of 5) ---\n")

sweep <- tibble()

for (h in seq(30, 180, by = 5)) {
  d <- likud %>% filter(abs(days_from_election) <= h)
  if (nrow(d) < 80) next                      # skip if too few tweets

  fit <- tryCatch(
    rdrobust(y = d$pop, x = d$days_from_election, c = 0,
             h = h, kernel = "triangular", p = 1,
             cluster = d$screen_name),
    error = function(e) NULL
  )

  if (!is.null(fit)) {
    sweep <- bind_rows(sweep, tibble(
      h      = h,
      tau    = fit$coef["Conventional",  "Coeff"],
      ci_lo  = fit$ci  ["Robust",        "CI Lower"],
      ci_hi  = fit$ci  ["Robust",        "CI Upper"],
      p_rob  = fit$pv  ["Robust",        "P-value"],
      sig    = fit$pv  ["Robust",        "P-value"] < 0.05
    ))
  }
}

cat(sprintf("  Completed sweep over %d bandwidth values\n", nrow(sweep)))

# Build sensitivity plot
p_sens <- ggplot(sweep, aes(x = h, y = tau)) +
  # Robust 95% CI band
  geom_ribbon(aes(ymin = ci_lo, ymax = ci_hi),
              alpha = 0.18, fill = "#3498db") +
  # Point estimate line
  geom_line(linewidth = 1.3, color = "#2c3e50") +
  # Points coloured by significance
  geom_point(aes(color = sig, shape = sig), size = 2.8) +
  # Null reference
  geom_hline(yintercept = 0, linetype = "dashed",
             color = "#e74c3c", linewidth = 0.8) +
  # Vertical lines at the reported bandwidths
  geom_vline(xintercept = c(90, 120, 180),
             linetype = "dotted", color = "#7f8c8d", linewidth = 0.6) +
  geom_vline(xintercept = h_opt,
             linetype = "dotted", color = "#e67e22", linewidth = 1) +
  annotate("text",
           x = h_opt + 2,
           y = min(sweep$ci_lo, na.rm = TRUE) * 0.85,
           label = sprintf("CCT optimal\n(%dd)", h_opt),
           size = 2.8, color = "#e67e22", hjust = 0) +
  scale_color_manual(
    values = c("TRUE" = "#e74c3c", "FALSE" = "#7f8c8d"),
    labels = c("TRUE" = "p < 0.05", "FALSE" = "p ≥ 0.05"),
    name   = NULL
  ) +
  scale_shape_manual(
    values = c("TRUE" = 19, "FALSE" = 1),
    labels = c("TRUE" = "p < 0.05", "FALSE" = "p ≥ 0.05"),
    name   = NULL
  ) +
  scale_y_continuous(labels = percent_format(accuracy = 0.1)) +
  labs(
    x        = "Bandwidth h (days either side of election cutoff)",
    y        = "RD Estimate τ̂ (jump in populist tweet probability)",
    title    = "Bandwidth Sensitivity: RDD Estimate for Likud",
    subtitle = "Shaded band = robust bias-corrected 95% CI  |  Filled = p < 0.05",
    caption  = "Dotted lines at h = 90, 120, 180 days (pre-specified) and CCT optimal (orange)."
  ) +
  theme_minimal(base_size = 11) +
  theme(
    plot.title       = element_text(face = "bold", size = 13),
    plot.subtitle    = element_text(size = 9.5, color = "#555"),
    plot.caption     = element_text(size = 7.5, color = "#777", face = "italic"),
    axis.title       = element_text(face = "bold"),
    legend.position  = "top",
    panel.grid.minor = element_blank()
  )

ggsave("output/rdd/rdd_sensitivity.png", p_sens,
       width = 10, height = 6, dpi = 300)
cat("  ✓ output/rdd/rdd_sensitivity.png\n")

# ==============================================================================
# 6. SAVE ALL RESULTS
# ==============================================================================

saveRDS(
  list(fit_opt = fit_opt, results = results, res_tbl = res_tbl,
       sweep = sweep, h_opt = h_opt),
  "output/rdd/rdd_results.rds"
)

cat("\n--- Summary table ---\n")
print(res_tbl %>%
        select(label, h, tau, se, p_conv, p_rob, ci_lo, ci_hi, n_pre, n_post),
      n = 10)

cat("\n=== STAGE 4 COMPLETE ===\n")
cat("Run Rscript 04_rdd.R from the repo root.\n")
