# ==============================================================================
# Stage 3: Before/After Statistical Analysis — Election Cutoff (R)
# ==============================================================================
# Comparison 1: ALL parties pre vs Likud + Religious Zionism post
#               ("Radicalized and Radical Populism")
# Comparison 2: Rightwards + Israel Our Home pre vs post
#               ("PRRPs in Change Coalition")
# 4 separate plots saved to output/
# ==============================================================================

library(tidyverse)
library(effsize)
options(scipen = 999)

cat("=== STAGE 3: BEFORE/AFTER ANALYSIS (R) ===\n\n")

data <- read_csv("output/analysis_data.csv", show_col_types = FALSE)
cat("Loaded", nrow(data), "rows\n\n")

PRR_PRE_NAMES  <- c("bezalelsm","michalwoldiger","ofir_sofer","oritstrock")
PRR_POST_NAMES <- c(PRR_PRE_NAMES, "rothmar","itamarbengvir")

COL_PRE  <- "#3498db"
COL_POST <- "#e74c3c"

# ── helpers ──────────────────────────────────────────────────────────────────

run_tests <- function(pre_vec, post_vec) {
  tt  <- t.test(pre_vec, post_vec)
  cd  <- cohen.d(pre_vec, post_vec)
  ct  <- table(c(rep(0,length(pre_vec)), rep(1,length(post_vec))),
               c(pre_vec, post_vec))
  ch  <- chisq.test(ct)
  n   <- sum(ct)
  v   <- sqrt(ch$statistic / (n * (min(dim(ct)) - 1)))

  list(t      = tt$statistic,
       t_p    = tt$p.value,
       pre_m  = mean(pre_vec),
       post_m = mean(post_vec),
       pct    = (mean(post_vec) - mean(pre_vec)) / mean(pre_vec) * 100,
       d      = cd$estimate,
       chi2   = ch$statistic,
       chi_p  = ch$p.value,
       v      = unname(v))
}

bar_two_plot <- function(labels, pre_m, post_m, pre_se, post_se,
                         title, stats_label) {
  df <- tibble(
    period = factor(c(labels[1], labels[2]), levels = c(labels[1], labels[2])),
    mean   = c(pre_m, post_m),
    se     = c(pre_se, post_se)
  )
  ggplot(df, aes(x = period, y = mean, fill = period)) +
    geom_col(color="black", linewidth=1.1, alpha=0.88, width=0.5) +
    geom_errorbar(aes(ymin=mean-1.96*se, ymax=mean+1.96*se),
                  width=0.12, linewidth=0.9) +
    geom_text(aes(label=scales::percent(mean, accuracy=0.01),
                  y=mean+1.96*se+0.003),
              fontface="bold", size=3.8, vjust=0) +
    scale_fill_manual(values=c(COL_PRE, COL_POST), guide="none") +
    scale_y_continuous(labels=scales::percent_format(accuracy=0.1),
                       expand=expansion(mult=c(0,0.18))) +
    labs(x=NULL, y="Proportion of Populist Tweets", title=title,
         caption=stats_label) +
    theme_minimal() +
    theme(plot.title   = element_text(face="bold", size=13),
          axis.title.y = element_text(face="bold"),
          axis.text.x  = element_text(size=10),
          panel.grid.major.x = element_blank(),
          plot.caption = element_text(size=8, color="#555", face="italic"))
}

bar_grouped_plot <- function(parties, pre_v, post_v, pre_se, post_se,
                              title, pct_ch, footnote = NULL) {
  df <- tibble(
    party  = rep(parties, each=2),
    period = rep(c("Pre-election","Post-election"), length(parties)),
    mean   = c(rbind(pre_v, post_v)),
    se     = c(rbind(pre_se, post_se))
  ) %>%
    mutate(party  = factor(party,  levels=parties),
           period = factor(period, levels=c("Pre-election","Post-election")))

  p <- ggplot(df, aes(x=party, y=mean, fill=period)) +
    geom_col(position=position_dodge(0.8), color="black",
             linewidth=1.1, alpha=0.88, width=0.7) +
    geom_errorbar(aes(ymin=mean-1.96*se, ymax=mean+1.96*se),
                  position=position_dodge(0.8), width=0.18, linewidth=0.9) +
    geom_text(aes(label=scales::percent(mean, accuracy=0.01),
                  y=mean+1.96*se+0.003),
              position=position_dodge(0.8), fontface="bold", size=3.5, vjust=0) +
    scale_fill_manual(values=c("Pre-election"=COL_PRE,"Post-election"=COL_POST),
                      name=NULL) +
    scale_y_continuous(labels=scales::percent_format(accuracy=0.1),
                       expand=expansion(mult=c(0,0.22))) +
    labs(x=NULL, y="Proportion of Populist Tweets", title=title) +
    theme_minimal() +
    theme(plot.title   = element_text(face="bold", size=13),
          axis.title.y = element_text(face="bold"),
          axis.text.x  = element_text(size=11),
          legend.position = "top",
          panel.grid.major.x = element_blank())

  # % change annotations
  for (i in seq_along(parties)) {
    y_top <- max(c(pre_v[i] + 1.96*pre_se[i],
                   post_v[i] + 1.96*post_se[i])) + 0.032
    p <- p + annotate("label", x=i, y=y_top,
                       label=sprintf("Δ %+.1f%%", pct_ch[i]),
                       size=3.2, color="#333", fontface="italic",
                       fill="white", label.size=0.3)
  }
  if (!is.null(footnote))
    p <- p + labs(caption=footnote) +
      theme(plot.caption=element_text(size=7.5, color="#666", face="italic"))
  p
}

# ── se helper ────────────────────────────────────────────────────────────────
se <- function(x) sd(x)/sqrt(length(x))

# ==============================================================================
# COMPARISON 1
# ==============================================================================

cat("--- COMPARISON 1: All pre vs Radicalized post ---\n")

pre_all  <- data %>% filter(post_election==0) %>% pull(pop) %>% as.numeric()
post_rad <- data %>% filter(post_election==1, radicalized_group) %>%
              pull(pop) %>% as.numeric()

c1 <- run_tests(pre_all, post_rad)
cat(sprintf("  Pre %.4f  Post %.4f  Δ %+.2f%%\n",
            c1$pre_m, c1$post_m, c1$pct))
cat(sprintf("  t=%.4f  p=%.2e  d=%.4f  χ²=%.4f  p=%.2e  V=%.4f\n\n",
            c1$t, c1$t_p, c1$d, c1$chi2, c1$chi_p, c1$v))

p3a <- bar_two_plot(
  labels   = c("Pre-election\n(All parties)",
               "Post-election\nRadicalized & Radical Populism"),
  pre_m    = c1$pre_m,  post_m   = c1$post_m,
  pre_se   = se(pre_all), post_se = se(post_rad),
  title    = "Radicalized and Radical Populism:\nOverall Before vs After Election",
  stats_label = sprintf("Δ %+.1f%%  |  t=%.2f, p=%.2e  |  d=%.3f",
                         c1$pct, c1$t, c1$t_p, c1$d))
ggsave("output/plot3a_comp1_overall.png", p3a, width=7, height=6, dpi=300)
cat("✓ plot3a_comp1_overall.png\n")

# ==============================================================================
# COMPARISON 1b — Likud vs PRR legislators
# ==============================================================================

cat("--- COMPARISON 1b: Likud vs PRR legislators ---\n")

likud_pre  <- data %>% filter(post_election==0, party=="Likud") %>%
                pull(pop) %>% as.numeric()
likud_post <- data %>% filter(post_election==1, party=="Likud") %>%
                pull(pop) %>% as.numeric()
prr_pre    <- data %>% filter(post_election==0, prr_leg_pre)  %>%
                pull(pop) %>% as.numeric()
prr_post   <- data %>% filter(post_election==1, prr_leg_post) %>%
                pull(pop) %>% as.numeric()

likud_ch <- (mean(likud_post)-mean(likud_pre))/mean(likud_pre)*100
prr_ch   <- (mean(prr_post)  -mean(prr_pre))  /mean(prr_pre)  *100
prr_t    <- run_tests(prr_pre, prr_post)

cat(sprintf("  Likud  pre %.4f  post %.4f  Δ %+.2f%%\n",
            mean(likud_pre), mean(likud_post), likud_ch))
cat(sprintf("  PRR    pre %.4f  post %.4f  Δ %+.2f%%\n\n",
            mean(prr_pre), mean(prr_post), prr_ch))

p3b <- bar_grouped_plot(
  parties  = c("Likud", "PRR Legislators"),
  pre_v    = c(mean(likud_pre),  mean(prr_pre)),
  post_v   = c(mean(likud_post), mean(prr_post)),
  pre_se   = c(se(likud_pre),    se(prr_pre)),
  post_se  = c(se(likud_post),   se(prr_post)),
  title    = "Radicalized and Radical Populism: Likud vs PRR Legislators",
  pct_ch   = c(likud_ch, prr_ch),
  footnote = paste0("PRR legislators Pre: ", paste(PRR_PRE_NAMES, collapse=", "),
                    "\nPost adds: rothmar, itamarbengvir"))
ggsave("output/plot3b_comp1_by_group.png", p3b, width=9, height=6, dpi=300)
cat("✓ plot3b_comp1_by_group.png\n")

# ==============================================================================
# COMPARISON 2
# ==============================================================================

cat("--- COMPARISON 2: PRRPs in Change Coalition ---\n")

cc_pre  <- data %>% filter(post_election==0, change_coalition_group) %>%
             pull(pop) %>% as.numeric()
cc_post <- data %>% filter(post_election==1, change_coalition_group) %>%
             pull(pop) %>% as.numeric()

c2 <- run_tests(cc_pre, cc_post)
cat(sprintf("  Pre %.4f  Post %.4f  Δ %+.2f%%\n",
            c2$pre_m, c2$post_m, c2$pct))
cat(sprintf("  t=%.4f  p=%.2e  d=%.4f  χ²=%.4f  p=%.2e  V=%.4f\n\n",
            c2$t, c2$t_p, c2$d, c2$chi2, c2$chi_p, c2$v))

p3c <- bar_two_plot(
  labels    = c("Pre-election\nPRRPs in Change Coalition",
                "Post-election\nPRRPs in Change Coalition"),
  pre_m     = c2$pre_m,  post_m  = c2$post_m,
  pre_se    = se(cc_pre), post_se = se(cc_post),
  title     = "PRRPs in Change Coalition:\nOverall Before vs After Election",
  stats_label = sprintf("Δ %+.1f%%  |  t=%.2f, p=%.2e  |  d=%.3f",
                         c2$pct, c2$t, c2$t_p, c2$d))
ggsave("output/plot3c_comp2_overall.png", p3c, width=7, height=6, dpi=300)
cat("✓ plot3c_comp2_overall.png\n")

# ==============================================================================
# COMPARISON 2b — Rightwards vs Israel Our Home
# ==============================================================================

cat("--- COMPARISON 2b: Rightwards vs Israel Our Home ---\n")

right_pre  <- data %>% filter(post_election==0, party=="Rightwards")     %>% pull(pop) %>% as.numeric()
right_post <- data %>% filter(post_election==1, party=="Rightwards")     %>% pull(pop) %>% as.numeric()
ioh_pre    <- data %>% filter(post_election==0, party=="Israel Our Home") %>% pull(pop) %>% as.numeric()
ioh_post   <- data %>% filter(post_election==1, party=="Israel Our Home") %>% pull(pop) %>% as.numeric()

right_ch <- (mean(right_post)-mean(right_pre))/mean(right_pre)*100
ioh_ch   <- (mean(ioh_post)  -mean(ioh_pre))  /mean(ioh_pre)  *100

cat(sprintf("  Rightwards    pre %.4f  post %.4f  Δ %+.2f%%\n",
            mean(right_pre), mean(right_post), right_ch))
cat(sprintf("  Israel Our Home pre %.4f  post %.4f  Δ %+.2f%%\n\n",
            mean(ioh_pre), mean(ioh_post), ioh_ch))

p3d <- bar_grouped_plot(
  parties  = c("Rightwards", "Israel Our Home"),
  pre_v    = c(mean(right_pre),  mean(ioh_pre)),
  post_v   = c(mean(right_post), mean(ioh_post)),
  pre_se   = c(se(right_pre),    se(ioh_pre)),
  post_se  = c(se(right_post),   se(ioh_post)),
  title    = "PRRPs in Change Coalition: Rightwards vs Israel Our Home",
  pct_ch   = c(right_ch, ioh_ch))
ggsave("output/plot3d_comp2_by_party.png", p3d, width=9, height=6, dpi=300)
cat("✓ plot3d_comp2_by_party.png\n")

# Save results
saveRDS(list(c1=c1, c2=c2, prr=prr_t), "output/comparison_results.rds")
cat("\n✓ output/comparison_results.rds saved\n")
cat("\n=== STAGE 3 COMPLETE ===\n")
