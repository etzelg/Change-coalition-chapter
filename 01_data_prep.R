# ==============================================================================
# Stage 1: Data Preparation & Exploration
# ==============================================================================
# Purpose: Load, clean, and prepare the dataset for analysis
# Dataset: causal7_dat.csv
# Date Range: 2020-01-01 onwards
# Cutoff Date: June 13, 2021 (government change)
# ==============================================================================

# Load required packages
library(tidyverse)
library(lubridate)

# Set options for cleaner output
options(scipen = 999)  # Disable scientific notation

# ==============================================================================
# 1. LOAD DATA
# ==============================================================================

cat("Loading dataset...\n")
raw_data <- read_csv("causal7_dat.csv",
                     show_col_types = FALSE)

cat("Dataset loaded successfully!\n")
cat("Original dimensions:", nrow(raw_data), "rows x", ncol(raw_data), "columns\n\n")

# ==============================================================================
# 2. INITIAL EXAMINATION
# ==============================================================================

cat("=== DATA STRUCTURE ===\n")
str(raw_data)

cat("\n=== FIRST 10 ROWS ===\n")
print(head(raw_data, 10))

cat("\n=== SUMMARY STATISTICS ===\n")
summary(raw_data)

cat("\n=== UNIQUE PARTIES ===\n")
print(table(raw_data$party))

cat("\n=== DATE RANGE ===\n")
cat("Earliest date:", min(raw_data$day), "\n")
cat("Latest date:", max(raw_data$day), "\n\n")

# ==============================================================================
# 3. DATA CLEANING & TRANSFORMATION
# ==============================================================================

cat("Transforming data...\n")

# Define cutoff date (June 13, 2021 - government change)
cutoff_date <- as.Date("2021-06-13")
election_date <- as.Date("2021-03-23")

analysis_data <- raw_data %>%
  # Convert day to Date format
  mutate(day = as.Date(day)) %>%

  # Filter: Keep only 2020-01-01 onwards
  filter(day >= as.Date("2020-01-01")) %>%

  # Create party_group variable
  mutate(party_group = if_else(party == "Likud", "Likud", "PRRPs")) %>%

  # Create temporal variables
  mutate(
    cutoff_date = cutoff_date,
    days_from_cutoff = as.numeric(day - cutoff_date),
    week_from_cutoff = floor(days_from_cutoff / 7),
    post = if_else(day >= cutoff_date, 1, 0)
  ) %>%

  # Convert pop to logical (1 = populist tweet)
  mutate(pop = as.logical(pop)) %>%

  # Convert new24 to logical (handle "Yes"/"No" strings)
  mutate(new24 = case_when(
    new24 == "Yes" ~ TRUE,
    new24 == "No" ~ FALSE,
    TRUE ~ as.logical(new24)
  )) %>%

  # Arrange by date
  arrange(day)

cat("Data transformation complete!\n")
cat("Filtered dimensions:", nrow(analysis_data), "rows x", ncol(analysis_data), "columns\n\n")

# ==============================================================================
# 4. DESCRIPTIVE STATISTICS
# ==============================================================================

cat("=== GENERATING DESCRIPTIVE STATISTICS ===\n\n")

# Create list to store all summary tables
summary_stats <- list()

# 4.1 Overall date range
summary_stats$date_range <- tibble(
  Metric = c("Start Date", "End Date", "Cutoff Date", "Election Date",
             "Days Before Cutoff", "Days After Cutoff"),
  Value = c(
    as.character(min(analysis_data$day)),
    as.character(max(analysis_data$day)),
    as.character(cutoff_date),
    as.character(election_date),
    as.character(sum(analysis_data$day < cutoff_date)),
    as.character(sum(analysis_data$day >= cutoff_date))
  )
)

# 4.2 Total legislators
total_legislators <- analysis_data %>%
  summarise(
    total_unique_legislators = n_distinct(screen_name)
  )

summary_stats$legislators_overall <- tibble(
  Metric = "Total Unique Legislators",
  Count = total_legislators$total_unique_legislators
)

# 4.3 Legislators by party_group
legislators_by_party <- analysis_data %>%
  group_by(party_group) %>%
  summarise(
    unique_legislators = n_distinct(screen_name),
    .groups = "drop"
  )

summary_stats$legislators_by_party <- legislators_by_party

# 4.4 Legislators by new24 status
legislators_by_new24 <- analysis_data %>%
  group_by(new24) %>%
  summarise(
    unique_legislators = n_distinct(screen_name),
    .groups = "drop"
  ) %>%
  mutate(new24 = if_else(new24, "New Legislator", "Continuing Legislator"))

summary_stats$legislators_by_new24 <- legislators_by_new24

# 4.5 Cross-tab: party_group × new24
legislators_crosstab <- analysis_data %>%
  group_by(party_group, new24) %>%
  summarise(
    unique_legislators = n_distinct(screen_name),
    .groups = "drop"
  ) %>%
  mutate(new24 = if_else(new24, "New Legislator", "Continuing Legislator")) %>%
  pivot_wider(names_from = new24, values_from = unique_legislators, values_fill = 0)

summary_stats$legislators_crosstab <- legislators_crosstab

# 4.6 Total tweets by period
tweets_by_period <- analysis_data %>%
  mutate(period = if_else(post == 1, "Post-Cutoff", "Pre-Cutoff")) %>%
  group_by(period) %>%
  summarise(
    total_tweets = n(),
    .groups = "drop"
  )

summary_stats$tweets_by_period <- tweets_by_period

# 4.7 Populist tweets by period
populist_by_period <- analysis_data %>%
  mutate(period = if_else(post == 1, "Post-Cutoff", "Pre-Cutoff")) %>%
  group_by(period) %>%
  summarise(
    total_tweets = n(),
    populist_tweets = sum(pop, na.rm = TRUE),
    proportion_populist = mean(pop, na.rm = TRUE),
    .groups = "drop"
  )

summary_stats$populist_by_period <- populist_by_period

# 4.8 Party composition
party_composition <- analysis_data %>%
  group_by(party) %>%
  summarise(
    tweets = n(),
    legislators = n_distinct(screen_name),
    populist_tweets = sum(pop, na.rm = TRUE),
    prop_populist = mean(pop, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(desc(tweets))

summary_stats$party_composition <- party_composition

# 4.9 Weekly tweet counts
weekly_summary <- analysis_data %>%
  group_by(week_from_cutoff) %>%
  summarise(
    week_start_date = min(day),
    total_tweets = n(),
    populist_tweets = sum(pop, na.rm = TRUE),
    .groups = "drop"
  )

summary_stats$weekly_counts <- tibble(
  Metric = c("Total Weeks", "Weeks Before Cutoff", "Weeks After Cutoff",
             "Min Weekly Tweets", "Max Weekly Tweets", "Mean Weekly Tweets"),
  Value = c(
    n_distinct(analysis_data$week_from_cutoff),
    sum(weekly_summary$week_from_cutoff < 0),
    sum(weekly_summary$week_from_cutoff >= 0),
    min(weekly_summary$total_tweets),
    max(weekly_summary$total_tweets),
    round(mean(weekly_summary$total_tweets), 1)
  )
)

# Print summaries to console
cat("\n=== DATE RANGE ===\n")
print(summary_stats$date_range)

cat("\n=== TOTAL LEGISLATORS ===\n")
print(summary_stats$legislators_overall)

cat("\n=== LEGISLATORS BY PARTY GROUP ===\n")
print(summary_stats$legislators_by_party)

cat("\n=== LEGISLATORS BY NEW24 STATUS ===\n")
print(summary_stats$legislators_by_new24)

cat("\n=== LEGISLATORS CROSSTAB (Party Group × New24) ===\n")
print(summary_stats$legislators_crosstab)

cat("\n=== TWEETS BY PERIOD ===\n")
print(summary_stats$tweets_by_period)

cat("\n=== POPULIST TWEETS BY PERIOD ===\n")
print(summary_stats$populist_by_period)

cat("\n=== WEEKLY SUMMARY ===\n")
print(summary_stats$weekly_counts)

cat("\n=== PARTY COMPOSITION ===\n")
print(summary_stats$party_composition)

# ==============================================================================
# 5. SAVE CLEANED DATA
# ==============================================================================

cat("\nSaving cleaned dataset...\n")
saveRDS(analysis_data, "analysis_data.rds")
cat("Cleaned data saved as 'analysis_data.rds'\n")

# Also save summary statistics for documentation
saveRDS(summary_stats, "summary_stats_stage1.rds")
cat("Summary statistics saved as 'summary_stats_stage1.rds'\n")

# ==============================================================================
# 6. CREATE MARKDOWN DOCUMENTATION
# ==============================================================================

cat("\nCreating markdown documentation...\n")

# Build markdown content
md_content <- c(
  "# Stage 1: Data Preparation & Exploration",
  "",
  "**Date:** ", format(Sys.Date(), "%B %d, %Y"),
  "",
  "**Purpose:** Load, clean, and prepare the dataset for causal analysis of populist rhetoric change.",
  "",
  "---",
  "",
  "## Data Source",
  "",
  "- **File:** `causal7_dat.csv`",
  paste0("- **Original size:** ", nrow(raw_data), " observations"),
  paste0("- **Filtered size:** ", nrow(analysis_data), " observations"),
  paste0("- **Date range:** ", min(analysis_data$day), " to ", max(analysis_data$day)),
  "- **Filter applied:** Data from 2020-01-01 onwards",
  "",
  "---",
  "",
  "## Key Dates",
  "",
  knitr::kable(summary_stats$date_range, format = "markdown"),
  "",
  "---",
  "",
  "## Variables Created",
  "",
  "1. **party_group**: Categorizes parties into 'Likud' or 'PRRPs' (Populist Radical Right Parties)",
  "2. **cutoff_date**: June 13, 2021 (government change)",
  "3. **days_from_cutoff**: Number of days from cutoff date (negative = before, positive = after)",
  "4. **week_from_cutoff**: Week number from cutoff (calculated as floor(days_from_cutoff/7))",
  "5. **post**: Binary indicator (1 = after June 13, 2021; 0 = before)",
  "6. **pop**: Converted to logical (TRUE = populist tweet)",
  "7. **new24**: Converted to logical (TRUE = new legislator)",
  "",
  "---",
  "",
  "## Descriptive Statistics",
  "",
  "### Total Legislators",
  "",
  knitr::kable(summary_stats$legislators_overall, format = "markdown"),
  "",
  "### Legislators by Party Group",
  "",
  knitr::kable(summary_stats$legislators_by_party, format = "markdown"),
  "",
  "### Legislators by Type (New vs. Continuing)",
  "",
  knitr::kable(summary_stats$legislators_by_new24, format = "markdown"),
  "",
  "### Crosstab: Party Group × Legislator Type",
  "",
  knitr::kable(summary_stats$legislators_crosstab, format = "markdown"),
  "",
  "### Total Tweets by Period",
  "",
  knitr::kable(summary_stats$tweets_by_period, format = "markdown"),
  "",
  "### Populist Tweets by Period",
  "",
  knitr::kable(summary_stats$populist_by_period, format = "markdown"),
  "",
  "### Weekly Tweet Summary",
  "",
  knitr::kable(summary_stats$weekly_counts, format = "markdown"),
  "",
  "### Party Composition",
  "",
  knitr::kable(summary_stats$party_composition, format = "markdown"),
  "",
  "---",
  "",
  "## Output Files",
  "",
  "- **analysis_data.rds**: Cleaned and transformed dataset ready for analysis",
  "- **summary_stats_stage1.rds**: Summary statistics object for reference",
  "",
  "---",
  "",
  "## Next Steps",
  "",
  "Proceed to Stage 2: Time Series Visualizations",
  ""
)

# Write markdown file
writeLines(md_content, "data_summary_stage1.md")
cat("Documentation saved as 'data_summary_stage1.md'\n")

cat("\n=== STAGE 1 COMPLETE ===\n")
cat("All files created successfully!\n")
