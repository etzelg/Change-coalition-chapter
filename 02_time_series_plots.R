# ==============================================================================
# Stage 2: Time Series Visualizations
# ==============================================================================
# Purpose: Create time series plots showing populist rhetoric trends over time
# Input: analysis_data.rds (from Stage 1)
# Outputs: 3 PNG plots + markdown documentation
# ==============================================================================

# Load required packages
library(tidyverse)
library(lubridate)

# Set plotting options
options(scipen = 999)

# Define color palette
colors <- list(
  main = "#2E86AB",
  Likud = "#E63946",
  PRRPs = "#F77F00",
  new = "#06A77D",
  continuing = "#5E60CE",
  cutoff = "#333333"
)

# ==============================================================================
# 1. LOAD DATA
# ==============================================================================

cat("Loading cleaned dataset...\n")
analysis_data <- readRDS("analysis_data.rds")
cat("Loaded", nrow(analysis_data), "observations\n\n")

# ==============================================================================
# 2. PREPARE AGGREGATED DATA
# ==============================================================================

cat("Preparing aggregated data for visualization...\n")

# 2.1 Overall weekly aggregates
weekly_overall <- analysis_data %>%
  group_by(week_from_cutoff) %>%
  summarise(
    populist_tweets = sum(pop),
    total_tweets = n(),
    prop_populist = mean(pop),
    week_start = min(day),
    .groups = "drop"
  )
cat("Overall:", nrow(weekly_overall), "weeks\n")

# 2.2 By party_group
weekly_by_party <- analysis_data %>%
  group_by(week_from_cutoff, party_group) %>%
  summarise(
    populist_tweets = sum(pop),
    total_tweets = n(),
    prop_populist = mean(pop),
    week_start = min(day),
    .groups = "drop"
  )
cat("By party:", nrow(weekly_by_party), "party-week observations\n")

# 2.3 By new24 status
weekly_by_new24 <- analysis_data %>%
  group_by(week_from_cutoff, new24) %>%
  summarise(
    populist_tweets = sum(pop),
    total_tweets = n(),
    prop_populist = mean(pop),
    week_start = min(day),
    .groups = "drop"
  ) %>%
  mutate(legislator_type = if_else(new24, "New Legislator", "Continuing Legislator"))
cat("By new24:", nrow(weekly_by_new24), "legislator-type-week observations\n\n")

# ==============================================================================
# 3. PLOT 1: OVERALL TREND
# ==============================================================================

cat("Creating Plot 1: Overall populist proportion trend...\n")

# Calculate rolling average
window_size <- 4
weekly_overall <- weekly_overall %>%
  arrange(week_from_cutoff) %>%
  mutate(rolling_mean = zoo::rollmean(prop_populist, k = window_size, fill = NA, align = "center"))

p1 <- ggplot(weekly_overall, aes(x = week_from_cutoff)) +
  # Scatter points
  geom_point(aes(y = prop_populist), alpha = 0.3, size = 2, color = colors$main) +
  # Rolling average line
  geom_line(aes(y = rolling_mean), linewidth = 1.2, color = colors$main) +
  # Cutoff line
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 1, color = colors$cutoff) +
  # Shaded regions
  annotate("rect", xmin = min(weekly_overall$week_from_cutoff), xmax = 0,
           ymin = -Inf, ymax = Inf, alpha = 0.05, fill = "blue") +
  annotate("rect", xmin = 0, xmax = max(weekly_overall$week_from_cutoff),
           ymin = -Inf, ymax = Inf, alpha = 0.05, fill = "red") +
  # Labels
  labs(
    title = "Populist Rhetoric Over Time: Overall Trend",
    x = "Weeks from Cutoff (June 13, 2021)",
    y = "Proportion of Populist Tweets"
  ) +
  scale_y_continuous(labels = scales::percent_format()) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 14, hjust = 0.5),
    axis.title = element_text(face = "bold", size = 12),
    panel.grid = element_line(alpha = 0.3)
  )

ggsave("plot1_overall_trend.png", plot = p1, width = 12, height = 6, dpi = 300)
cat("✓ Plot 1 saved as 'plot1_overall_trend.png'\n\n")

# ==============================================================================
# 4. PLOT 2: BY PARTY GROUP
# ==============================================================================

cat("Creating Plot 2: Trend by party group (Likud vs PRRPs)...\n")

# Calculate rolling average by party
weekly_by_party <- weekly_by_party %>%
  arrange(party_group, week_from_cutoff) %>%
  group_by(party_group) %>%
  mutate(rolling_mean = zoo::rollmean(prop_populist, k = window_size, fill = NA, align = "center")) %>%
  ungroup()

p2 <- ggplot(weekly_by_party, aes(x = week_from_cutoff, color = party_group, fill = party_group)) +
  # Scatter points
  geom_point(aes(y = prop_populist), alpha = 0.3, size = 2) +
  # Rolling average lines
  geom_line(aes(y = rolling_mean), linewidth = 1.2) +
  # Cutoff line
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 1, color = colors$cutoff) +
  # Colors
  scale_color_manual(values = c(Likud = colors$Likud, PRRPs = colors$PRRPs)) +
  scale_fill_manual(values = c(Likud = colors$Likud, PRRPs = colors$PRRPs)) +
  # Labels
  labs(
    title = "Populist Rhetoric Over Time: By Party Group",
    x = "Weeks from Cutoff (June 13, 2021)",
    y = "Proportion of Populist Tweets",
    color = "Party Group",
    fill = "Party Group"
  ) +
  scale_y_continuous(labels = scales::percent_format()) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 14, hjust = 0.5),
    axis.title = element_text(face = "bold", size = 12),
    panel.grid = element_line(alpha = 0.3),
    legend.position = "right"
  )

ggsave("plot2_by_party.png", plot = p2, width = 12, height = 6, dpi = 300)
cat("✓ Plot 2 saved as 'plot2_by_party.png'\n\n")

# ==============================================================================
# 5. PLOT 3: BY NEW24 STATUS
# ==============================================================================

cat("Creating Plot 3: Trend by legislator type (New vs Continuing)...\n")

# Calculate rolling average by legislator type
weekly_by_new24 <- weekly_by_new24 %>%
  arrange(legislator_type, week_from_cutoff) %>%
  group_by(legislator_type) %>%
  mutate(rolling_mean = zoo::rollmean(prop_populist, k = window_size, fill = NA, align = "center")) %>%
  ungroup()

p3 <- ggplot(weekly_by_new24, aes(x = week_from_cutoff, color = legislator_type, fill = legislator_type)) +
  # Scatter points
  geom_point(aes(y = prop_populist), alpha = 0.3, size = 2) +
  # Rolling average lines
  geom_line(aes(y = rolling_mean), linewidth = 1.2) +
  # Cutoff line
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 1, color = colors$cutoff) +
  # Colors
  scale_color_manual(values = c("New Legislator" = colors$new, "Continuing Legislator" = colors$continuing)) +
  scale_fill_manual(values = c("New Legislator" = colors$new, "Continuing Legislator" = colors$continuing)) +
  # Labels
  labs(
    title = "Populist Rhetoric Over Time: By Legislator Type",
    x = "Weeks from Cutoff (June 13, 2021)",
    y = "Proportion of Populist Tweets",
    color = "Legislator Type",
    fill = "Legislator Type"
  ) +
  scale_y_continuous(labels = scales::percent_format()) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = "bold", size = 14, hjust = 0.5),
    axis.title = element_text(face = "bold", size = 12),
    panel.grid = element_line(alpha = 0.3),
    legend.position = "right"
  )

ggsave("plot3_by_new24.png", plot = p3, width = 12, height = 6, dpi = 300)
cat("✓ Plot 3 saved as 'plot3_by_new24.png'\n\n")

# ==============================================================================
# 6. CREATE MARKDOWN DOCUMENTATION
# ==============================================================================

cat("Creating markdown documentation...\n")

# Calculate summary statistics
pre_cutoff_mean <- weekly_overall %>%
  filter(week_from_cutoff < 0) %>%
  pull(prop_populist) %>%
  mean()

post_cutoff_mean <- weekly_overall %>%
  filter(week_from_cutoff >= 0) %>%
  pull(prop_populist) %>%
  mean()

change_pct <- ((post_cutoff_mean - pre_cutoff_mean) / pre_cutoff_mean) * 100

md_content <- paste0(
  "# Stage 2: Time Series Visualizations\n\n",
  "**Date:** ", format(Sys.Date(), "%B %d, %Y"), "\n\n",
  "**Purpose:** Visualize trends in populist rhetoric over time around the government coalition change.\n\n",
  "---\n\n",
  "## Overview\n\n",
  "This analysis examines temporal trends in populist tweets from Israeli legislators, focusing on the period before and after the government change on June 13, 2021.\n\n",
  "### Key Findings\n\n",
  "- **Pre-cutoff mean:** ", sprintf("%.2f%%", pre_cutoff_mean * 100), " populist tweets\n",
  "- **Post-cutoff mean:** ", sprintf("%.2f%%", post_cutoff_mean * 100), " populist tweets\n",
  "- **Change:** ", sprintf("%+.1f%%", change_pct), " increase\n\n",
  "---\n\n",
  "## Visualizations\n\n",
  "### Plot 1: Overall Trend\n\n",
  "![Overall Trend](plot1_overall_trend.png)\n\n",
  "**Description:** Shows the overall proportion of populist tweets over time with a ", window_size, "-week rolling average. The vertical dashed line marks June 13, 2021 (government change).\n\n",
  "**Key observations:**\n",
  "- Clear visual distinction between pre- and post-cutoff periods\n",
  "- Smoothed trend line shows the general trajectory\n",
  "- Weekly variation captured in scatter points\n\n",
  "---\n\n",
  "### Plot 2: By Party Group (Likud vs PRRPs)\n\n",
  "![By Party Group](plot2_by_party.png)\n\n",
  "**Description:** Compares populist rhetoric trends between Likud (the dominant party) and PRRPs (Populist Radical Right Parties).\n\n",
  "**Key observations:**\n",
  "- Separate trends for Likud and PRRPs coalition members\n",
  "- Both groups show temporal patterns around the cutoff\n",
  "- ", window_size, "-week rolling averages smooth out weekly volatility\n\n",
  "---\n\n",
  "### Plot 3: By Legislator Type (New vs Continuing)\n\n",
  "![By Legislator Type](plot3_by_new24.png)\n\n",
  "**Description:** Compares trends between new legislators (elected in 2021) and continuing legislators.\n\n",
  "**Key observations:**\n",
  "- Differential trends between new and continuing legislators\n",
  "- New legislators may show different rhetorical patterns\n",
  "- Both groups' trends are smoothed with ", window_size, "-week rolling averages\n\n",
  "---\n\n",
  "## Data Summary\n\n",
  "- **Total observations:** ", format(nrow(analysis_data), big.mark = ","), "\n",
  "- **Time span:** ", nrow(weekly_overall), " weeks\n",
  "- **Weeks before cutoff:** ", sum(weekly_overall$week_from_cutoff < 0), "\n",
  "- **Weeks after cutoff:** ", sum(weekly_overall$week_from_cutoff >= 0), "\n",
  "- **Smoothing method:** ", window_size, "-week rolling average (centered)\n\n",
  "---\n\n",
  "## Technical Details\n\n",
  "**Visualization settings:**\n",
  "- Resolution: 300 DPI\n",
  "- Format: PNG\n",
  "- Smoothing: ", window_size, "-week centered rolling average\n",
  "- Cutoff marked at week 0 (June 13, 2021)\n\n",
  "**Data aggregation:**\n",
  "- Weekly aggregation by `week_from_cutoff`\n",
  "- Proportion calculated as: populist_tweets / total_tweets\n",
  "- Separate aggregations for overall, by party_group, and by legislator type\n\n",
  "---\n\n",
  "## Output Files\n\n",
  "- **plot1_overall_trend.png**: Overall populist proportion trend\n",
  "- **plot2_by_party.png**: Trend comparison by party group\n",
  "- **plot3_by_new24.png**: Trend comparison by legislator type\n\n",
  "---\n\n",
  "## Next Steps\n\n",
  "Proceed to Stage 3: Before/After Statistical Comparison\n"
)

writeLines(md_content, "plots_stage2.md")
cat("Documentation saved as 'plots_stage2.md'\n")

cat("\n=== STAGE 2 COMPLETE ===\n")
cat("All plots created successfully!\n")
cat("- plot1_overall_trend.png\n")
cat("- plot2_by_party.png\n")
cat("- plot3_by_new24.png\n")
cat("- plots_stage2.md\n")
