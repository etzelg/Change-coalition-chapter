# ==============================================================================
# Stage 1: Data Preparation (R)
# ==============================================================================
library(tidyverse)
options(scipen = 999)

cat("=== STAGE 1: DATA PREPARATION ===\n\n")

# Load
df <- read_csv("causal7_dat.csv", locale = locale(encoding = "UTF-8"), show_col_types = FALSE)
df <- df %>% mutate(day = as.Date(day))
cat("Loaded", nrow(df), "rows\n")

# Filter 2020+
analysis_data <- df %>% filter(day >= as.Date("2020-01-01"))
cat("After 2020+ filter:", nrow(analysis_data), "rows\n")

# Election cutoff variables
election_date <- as.Date("2021-03-23")
analysis_data <- analysis_data %>%
  mutate(
    post_election        = as.integer(day >= election_date),
    days_from_election   = as.integer(day - election_date),
    week_from_election   = floor(days_from_election / 7)
  )

# Grouping variables
PRR_PRE  <- c("bezalelsm", "michalwoldiger", "ofir_sofer", "oritstrock")
PRR_POST <- c(PRR_PRE, "rothmar", "itamarbengvir")

analysis_data <- analysis_data %>%
  mutate(
    radicalized_group      = party %in% c("Likud", "Religious Zionism"),
    change_coalition_group = party %in% c("Rightwards", "Israel Our Home"),
    prr_leg_pre            = screen_name %in% PRR_PRE,
    prr_leg_post           = screen_name %in% PRR_POST,
    pop                    = as.integer(pop)
  )

cat("radicalized_group:", sum(analysis_data$radicalized_group), "\n")
cat("change_coalition_group:", sum(analysis_data$change_coalition_group), "\n")

# Save
write_csv(analysis_data, "output/analysis_data.csv")
saveRDS(analysis_data, "output/analysis_data.rds")
cat("\n✓ Saved output/analysis_data.csv and .rds\n")
cat("\n=== STAGE 1 COMPLETE ===\n")
