# ==============================================================================
# Stage 2: Time Series Plots (R)
# ==============================================================================
library(tidyverse)
library(zoo)   # rollmean
options(scipen = 999)

cat("=== STAGE 2: TIME SERIES PLOTS ===\n\n")

data <- read_csv("output/analysis_data.csv", show_col_types = FALSE)
WINDOW <- 4

weekly_prop <- function(df) {
  df %>%
    group_by(week_from_election) %>%
    summarise(prop = mean(pop), .groups = "drop") %>%
    arrange(week_from_election)
}

election_line <- geom_vline(xintercept = 0, linetype = "dashed",
                             color = "#2c3e50", linewidth = 1.2)
pct_fmt <- scales::percent_format(accuracy = 0.1)

# ── Plot 2a ──────────────────────────────────────────────────────────────────
# Single trend line; composition changes at election cutoff:
#   Pre-election : named PRR legislators (prr_leg_pre) + Likud
#   Post-election: all Religious Zionism (party) + Likud
cat("Plot 2a: Netanyahu's bloc trend (single line, correct pre/post composition)...\n")

bloc_data <- data %>%
  filter(
    (post_election == 0 & (prr_leg_pre | party == "Likud")) |
    (post_election == 1 & radicalized_group)
  )

rad_wk <- weekly_prop(bloc_data) %>%
  mutate(smooth = rollmean(prop, k = WINDOW, fill = NA, align = "center"))

p2a <- ggplot(rad_wk, aes(x = week_from_election)) +
  geom_point(aes(y = prop), alpha = 0.18, size = 1.2, color = "#c0392b") +
  geom_line(aes(y = smooth), linewidth = 1.8, color = "#c0392b", na.rm = TRUE) +
  election_line +
  scale_y_continuous(labels = pct_fmt) +
  labs(x = "Weeks from Election (March 23, 2021)",
       y = "Proportion of Populist Tweets",
       title = "Populism in Netanyahu's Bloc Before and After 2021 Election",
       caption = "Pre-election: bezalelsm, michalwoldiger, ofir_sofer, oritstrock + Likud\nPost-election: all Religious Zionism + Likud") +
  theme_minimal() +
  theme(plot.title    = element_text(face = "bold", size = 14),
        axis.title    = element_text(face = "bold"),
        legend.position = "none",
        plot.caption  = element_text(size = 8, color = "#666", face = "italic"),
        panel.grid.minor = element_blank())

ggsave("output/plot2a_radicalized_trend.png", p2a, width = 12, height = 6, dpi = 300)
cat("✓ output/plot2a_radicalized_trend.png\n")

# ── Plot 2b ──────────────────────────────────────────────────────────────────
cat("\nPlot 2b: Rightwards vs Israel Our Home...\n")

right_wk <- weekly_prop(data %>% filter(party == "Rightwards")) %>%
  mutate(smooth = rollmean(prop, k = WINDOW, fill = NA, align = "center"),
         group = "Rightwards")

ioh_wk <- weekly_prop(data %>% filter(party == "Israel Our Home")) %>%
  mutate(smooth = rollmean(prop, k = WINDOW, fill = NA, align = "center"),
         group = "Israel Our Home")

ts2b <- bind_rows(right_wk, ioh_wk)
colors2b <- c("Rightwards" = "#2980b9", "Israel Our Home" = "#27ae60")

p2b <- ggplot(ts2b, aes(x = week_from_election, color = group)) +
  geom_point(aes(y = prop), alpha = 0.18, size = 1.2) +
  geom_line(aes(y = smooth), linewidth = 1.8, na.rm = TRUE) +
  election_line +
  scale_color_manual(values = colors2b, name = NULL) +
  scale_y_continuous(labels = pct_fmt) +
  labs(x = "Weeks from Election (March 23, 2021)",
       y = "Proportion of Populist Tweets",
       title = "Populist Rhetoric Over Time:",
       subtitle = "PRRPs in Change Coalition (Rightwards vs Israel Our Home)") +
  theme_minimal() +
  theme(plot.title    = element_text(face = "bold", size = 14),
        plot.subtitle = element_text(size = 12),
        axis.title    = element_text(face = "bold"),
        legend.position = "top",
        panel.grid.minor = element_blank())

ggsave("output/plot2b_change_coalition_trend.png", p2b, width = 12, height = 6, dpi = 300)
cat("✓ output/plot2b_change_coalition_trend.png\n")

cat("\n=== STAGE 2 COMPLETE ===\n")
