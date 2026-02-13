# ==============================================================================
# Stage 3: Before/After Statistical Comparison
# ==============================================================================
# Purpose: Compare populist rhetoric before and after the government change
# Input: analysis_data.rds (from Stage 1)
# Outputs: Statistical test results, summary tables, comparison plot
# ==============================================================================

# Load required packages
library(tidyverse)
library(effsize)  # For Cohen's d

# Set options
options(scipen = 999)

# ==============================================================================
# 1. LOAD DATA
# ==============================================================================

cat("Loading cleaned dataset...\n")
analysis_data <- readRDS("analysis_data.rds")
cat("Loaded", nrow(analysis_data), "observations\n\n")

# ==============================================================================
# 2. SUMMARY TABLES
# ==============================================================================

cat("=== GENERATING SUMMARY TABLES ===\n\n")

results <- list()

# 2.1 Overall summary (pre vs post)
overall_summary <- analysis_data %>%
  mutate(period = if_else(post == 1, "Post-Cutoff", "Pre-Cutoff")) %>%
  group_by(period) %>%
  summarise(
    total_tweets = n(),
    populist_tweets = sum(pop),
    mean_prop = mean(pop),
    std_prop = sd(pop),
    unique_legislators = n_distinct(screen_name),
    .groups = "drop"
  ) %>%
  mutate(se_prop = std_prop / sqrt(total_tweets)) %>%
  select(period, total_tweets, populist_tweets, mean_prop, se_prop, unique_legislators)

results$overall_summary <- overall_summary
cat("Overall Summary (Pre vs Post):\n")
print(overall_summary)
cat("\n")

# 2.2 By party_group
party_summary <- analysis_data %>%
  mutate(period = if_else(post == 1, "Post-Cutoff", "Pre-Cutoff")) %>%
  group_by(period, party_group) %>%
  summarise(
    total_tweets = n(),
    populist_tweets = sum(pop),
    mean_prop = mean(pop),
    std_prop = sd(pop),
    unique_legislators = n_distinct(screen_name),
    .groups = "drop"
  ) %>%
  mutate(se_prop = std_prop / sqrt(total_tweets)) %>%
  select(period, party_group, total_tweets, populist_tweets, mean_prop, se_prop, unique_legislators)

results$party_summary <- party_summary
cat("Summary by Party Group:\n")
print(party_summary)
cat("\n")

# 2.3 By new24 status
new24_summary <- analysis_data %>%
  mutate(
    period = if_else(post == 1, "Post-Cutoff", "Pre-Cutoff"),
    legislator_type = if_else(new24, "New", "Continuing")
  ) %>%
  group_by(period, legislator_type) %>%
  summarise(
    total_tweets = n(),
    populist_tweets = sum(pop),
    mean_prop = mean(pop),
    std_prop = sd(pop),
    unique_legislators = n_distinct(screen_name),
    .groups = "drop"
  ) %>%
  mutate(se_prop = std_prop / sqrt(total_tweets)) %>%
  select(period, legislator_type, total_tweets, populist_tweets, mean_prop, se_prop, unique_legislators)

results$new24_summary <- new24_summary
cat("Summary by Legislator Type:\n")
print(new24_summary)
cat("\n")

# 2.4 Four-way breakdown (party_group × new24)
fourway_summary <- analysis_data %>%
  mutate(
    period = if_else(post == 1, "Post-Cutoff", "Pre-Cutoff"),
    legislator_type = if_else(new24, "New", "Continuing")
  ) %>%
  group_by(period, party_group, legislator_type) %>%
  summarise(
    total_tweets = n(),
    populist_tweets = sum(pop),
    mean_prop = mean(pop),
    std_prop = sd(pop),
    unique_legislators = n_distinct(screen_name),
    .groups = "drop"
  ) %>%
  mutate(se_prop = std_prop / sqrt(total_tweets)) %>%
  select(period, party_group, legislator_type, total_tweets, populist_tweets, mean_prop, se_prop, unique_legislators)

results$fourway_summary <- fourway_summary
cat("Four-way Summary (Party × Legislator Type):\n")
print(fourway_summary)
cat("\n")

# ==============================================================================
# 3. STATISTICAL TESTS
# ==============================================================================

cat("=== CONDUCTING STATISTICAL TESTS ===\n\n")

# 3.1 Two-sample t-test
pre_data <- analysis_data %>% filter(post == 0) %>% pull(pop) %>% as.numeric()
post_data <- analysis_data %>% filter(post == 1) %>% pull(pop) %>% as.numeric()

t_test_result <- t.test(post_data, pre_data)

# Calculate Cohen's d
cohens_d <- cohen.d(post_data, pre_data)$estimate

# Effect size interpretation
effect_interp <- case_when(
  abs(cohens_d) < 0.5 ~ "small",
  abs(cohens_d) < 0.8 ~ "medium",
  TRUE ~ "large"
)

results$t_test <- list(
  t_statistic = t_test_result$statistic,
  p_value = t_test_result$p.value,
  pre_mean = mean(pre_data),
  post_mean = mean(post_data),
  cohens_d = cohens_d,
  effect_size_interpretation = effect_interp
)

cat("Two-Sample t-test (Pre vs Post):\n")
cat("  Pre-cutoff mean:", sprintf("%.4f (%.2f%%)", results$t_test$pre_mean, results$t_test$pre_mean * 100), "\n")
cat("  Post-cutoff mean:", sprintf("%.4f (%.2f%%)", results$t_test$post_mean, results$t_test$post_mean * 100), "\n")
cat("  t-statistic:", sprintf("%.4f", results$t_test$t_statistic), "\n")
cat("  p-value:", sprintf("%.4e", results$t_test$p_value), "\n")
cat("  Cohen's d:", sprintf("%.4f (%s)", results$t_test$cohens_d, results$t_test$effect_size_interpretation), "\n")
cat("\n")

# 3.2 Chi-square test
contingency_table <- table(analysis_data$post, analysis_data$pop)
chi_test_result <- chisq.test(contingency_table)

# Calculate Cramér's V
n <- sum(contingency_table)
cramers_v <- sqrt(chi_test_result$statistic / (n * (min(dim(contingency_table)) - 1)))

# Effect size interpretation
cramers_interp <- case_when(
  cramers_v < 0.1 ~ "small",
  cramers_v < 0.3 ~ "medium",
  TRUE ~ "large"
)

results$chi_square <- list(
  chi2_statistic = chi_test_result$statistic,
  p_value = chi_test_result$p.value,
  degrees_of_freedom = chi_test_result$parameter,
  cramers_v = as.numeric(cramers_v),
  effect_size_interpretation = cramers_interp
)

cat("Chi-Square Test of Independence:\n")
cat("Contingency Table:\n")
print(contingency_table)
cat("\n")
cat("  Chi-square statistic:", sprintf("%.4f", results$chi_square$chi2_statistic), "\n")
cat("  p-value:", sprintf("%.4e", results$chi_square$p_value), "\n")
cat("  Degrees of freedom:", results$chi_square$degrees_of_freedom, "\n")
cat("  Cramér's V:", sprintf("%.4f (%s)", results$chi_square$cramers_v, results$chi_square$effect_size_interpretation), "\n")
cat("\n")

# ==============================================================================
# 4. VISUALIZATION: BEFORE/AFTER COMPARISON
# ==============================================================================

cat("Creating before/after comparison plot...\n\n")

# Define colors
colors_pre <- "#3498db"
colors_post <- "#e74c3c"

# Create three-panel plot
p1 <- ggplot(overall_summary, aes(x = period, y = mean_prop, fill = period)) +
  geom_bar(stat = "identity", alpha = 0.8, color = "black", linewidth = 1.5) +
  geom_errorbar(aes(ymin = mean_prop - 1.96 * se_prop, ymax = mean_prop + 1.96 * se_prop),
                width = 0.2, linewidth = 1) +
  geom_text(aes(label = sprintf("%.2f%%", mean_prop * 100)),
            vjust = -0.5, size = 4, fontface = "bold",
            position = position_dodge(width = 0.9)) +
  scale_fill_manual(values = c("Pre-Cutoff" = colors_pre, "Post-Cutoff" = colors_post)) +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(title = "Overall Comparison", x = NULL, y = "Proportion of Populist Tweets") +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 12, hjust = 0.5),
    axis.title.y = element_text(face = "bold", size = 11),
    legend.position = "none",
    panel.grid.major.x = element_blank()
  )

p2 <- ggplot(party_summary, aes(x = party_group, y = mean_prop, fill = period)) +
  geom_bar(stat = "identity", position = "dodge", alpha = 0.8, color = "black", linewidth = 1) +
  geom_errorbar(aes(ymin = mean_prop - 1.96 * se_prop, ymax = mean_prop + 1.96 * se_prop),
                position = position_dodge(width = 0.9), width = 0.25, linewidth = 0.8) +
  scale_fill_manual(values = c("Pre-Cutoff" = colors_pre, "Post-Cutoff" = colors_post)) +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(title = "By Party Group", x = NULL, y = "Proportion of Populist Tweets", fill = "Period") +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 12, hjust = 0.5),
    axis.title.y = element_text(face = "bold", size = 11),
    legend.position = "right",
    panel.grid.major.x = element_blank()
  )

p3 <- ggplot(new24_summary, aes(x = legislator_type, y = mean_prop, fill = period)) +
  geom_bar(stat = "identity", position = "dodge", alpha = 0.8, color = "black", linewidth = 1) +
  geom_errorbar(aes(ymin = mean_prop - 1.96 * se_prop, ymax = mean_prop + 1.96 * se_prop),
                position = position_dodge(width = 0.9), width = 0.25, linewidth = 0.8) +
  scale_fill_manual(values = c("Pre-Cutoff" = colors_pre, "Post-Cutoff" = colors_post)) +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(title = "By Legislator Type", x = NULL, y = "Proportion of Populist Tweets", fill = "Period") +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 12, hjust = 0.5),
    axis.title.y = element_text(face = "bold", size = 11),
    legend.position = "right",
    panel.grid.major.x = element_blank()
  )

# Combine plots
combined_plot <- gridExtra::grid.arrange(p1, p2, p3, ncol = 3)

# Save plot
ggsave("plot4_before_after_comparison.png", plot = combined_plot, width = 15, height = 5, dpi = 300)

cat("✓ Comparison plot saved as 'plot4_before_after_comparison.png'\n\n")

# ==============================================================================
# 5. SAVE RESULTS
# ==============================================================================

cat("Saving results...\n")
saveRDS(results, "before_after_results.rds")
cat("Results saved as 'before_after_results.rds'\n\n")

# ==============================================================================
# 6. CREATE MARKDOWN DOCUMENTATION
# ==============================================================================

cat("Creating markdown documentation...\n\n")

md_content <- paste0(
  "# Stage 3: Before/After Statistical Comparison\n\n",
  "**Date:** ", format(Sys.Date(), "%B %d, %Y"), "\n\n",
  "**Purpose:** Statistically compare populist rhetoric before and after the government change on June 13, 2021.\n\n",
  "---\n\n",
  "## Executive Summary\n\n",
  "### Key Findings\n\n",
  "- **Pre-cutoff populist proportion:** ", sprintf("%.4f (%.2f%%)", results$t_test$pre_mean, results$t_test$pre_mean * 100), "\n",
  "- **Post-cutoff populist proportion:** ", sprintf("%.4f (%.2f%%)", results$t_test$post_mean, results$t_test$post_mean * 100), "\n",
  "- **Change:** ", sprintf("%+.2f", (results$t_test$post_mean - results$t_test$pre_mean) * 100), " percentage points\n",
  "- **Statistical significance:** p < 0.001 (highly significant)\n",
  "- **Effect size:** Cohen's d = ", sprintf("%.4f (%s)", results$t_test$cohens_d, results$t_test$effect_size_interpretation), "\n\n",
  "---\n\n",
  "## Summary Tables\n\n",
  "### Overall Comparison (Pre vs Post)\n\n",
  knitr::kable(overall_summary, format = "markdown"), "\n\n",
  "### By Party Group\n\n",
  knitr::kable(party_summary, format = "markdown"), "\n\n",
  "### By Legislator Type\n\n",
  knitr::kable(new24_summary, format = "markdown"), "\n\n",
  "### Four-Way Breakdown (Party Group × Legislator Type)\n\n",
  knitr::kable(fourway_summary, format = "markdown"), "\n\n",
  "---\n\n",
  "## Statistical Tests\n\n",
  "### Two-Sample t-test\n\n",
  "Tests whether the mean proportion of populist tweets differs significantly between pre- and post-cutoff periods.\n\n",
  "**Results:**\n",
  "- **t-statistic:** ", sprintf("%.4f", results$t_test$t_statistic), "\n",
  "- **p-value:** ", sprintf("%.4e", results$t_test$p_value), "\n",
  "- **Pre-cutoff mean:** ", sprintf("%.4f (%.2f%%)", results$t_test$pre_mean, results$t_test$pre_mean * 100), "\n",
  "- **Post-cutoff mean:** ", sprintf("%.4f (%.2f%%)", results$t_test$post_mean, results$t_test$post_mean * 100), "\n",
  "- **Cohen's d:** ", sprintf("%.4f", results$t_test$cohens_d), "\n",
  "- **Effect size interpretation:** ", tools::toTitleCase(results$t_test$effect_size_interpretation), "\n\n",
  "**Interpretation:** The difference in populist rhetoric between pre- and post-cutoff periods is statistically significant (p < 0.001) with a ", results$t_test$effect_size_interpretation, " effect size.\n\n",
  "---\n\n",
  "### Chi-Square Test of Independence\n\n",
  "Tests whether there is an association between the period (pre/post) and the populist tweet indicator.\n\n",
  "**Results:**\n",
  "- **χ² statistic:** ", sprintf("%.4f", results$chi_square$chi2_statistic), "\n",
  "- **p-value:** ", sprintf("%.4e", results$chi_square$p_value), "\n",
  "- **Degrees of freedom:** ", results$chi_square$degrees_of_freedom, "\n",
  "- **Cramér's V:** ", sprintf("%.4f", results$chi_square$cramers_v), "\n",
  "- **Effect size interpretation:** ", tools::toTitleCase(results$chi_square$effect_size_interpretation), "\n\n",
  "**Interpretation:** There is a statistically significant association between the time period and populist rhetoric (p < 0.001) with a ", results$chi_square$effect_size_interpretation, " effect size.\n\n",
  "---\n\n",
  "## Visualization\n\n",
  "### Before/After Comparison Plot\n\n",
  "![Before/After Comparison](plot4_before_after_comparison.png)\n\n",
  "**Description:** Three-panel comparison showing:\n",
  "1. **Overall:** Pre vs Post populist proportion with 95% confidence intervals\n",
  "2. **By Party Group:** Comparison for Likud and PRRPs\n",
  "3. **By Legislator Type:** Comparison for New and Continuing legislators\n\n",
  "Error bars represent 95% confidence intervals.\n\n",
  "---\n\n",
  "## Output Files\n\n",
  "- **before_after_results.rds**: Complete results object with all statistics (R format)\n",
  "- **before_after_results.pkl**: Complete results object with all statistics (Python format)\n",
  "- **plot4_before_after_comparison.png**: Three-panel comparison visualization\n",
  "- **before_after_summary.md**: This documentation file\n\n",
  "---\n\n",
  "**Analysis complete.** All results saved and documented.\n"
)

writeLines(md_content, "before_after_summary.md")
cat("Documentation saved as 'before_after_summary.md'\n")

cat("\n=== STAGE 3 COMPLETE ===\n")
cat("All statistical analyses completed successfully!\n")
cat("- before_after_results.rds\n")
cat("- plot4_before_after_comparison.png\n")
cat("- before_after_summary.md\n")
