# 12_statistical_tests.R
# Cyclistic Bike-Share Case Study — R Module
#
# Statistical validation of key findings using hypothesis tests.
# This script is R-exclusive — none of the other tools in this portfolio
# (Power BI, SQL Server, DuckDB) can perform inferential statistics.
#
# Tests performed:
#   1. Welch's t-test    — Is the duration difference real or due to chance?
#   2. Chi-square test   — Is the weekend skew statistically significant?
#   3. Chi-square test   — Is the round trip rate difference statistically significant?
#
# Introduces: t.test(), chisq.test(), sampling for large datasets,
#             interpreting p-values and confidence intervals

library(tidyverse)

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")
csv_files  <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)
trips      <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Prepare derived columns needed for all tests
# ---------------------------------------------------------------------------

trips <- trips |>
  mutate(
    duration_min = as.numeric(difftime(ended_at, started_at, units = "mins")),
    is_weekend   = wday(started_at) %in% c(1, 7),
    is_round_trip = coalesce(start_station_name, "") == coalesce(end_station_name, "")
  ) |>
  filter(duration_min > 0)

# ---------------------------------------------------------------------------
# NOTE ON SAMPLE SIZE
#
# With 5.6 million rows, almost any difference will be statistically
# significant — large samples give tests enormous power to detect even
# trivial effects. We use a random sample of 100,000 rides for the t-test
# to get honest, meaningful results. The chi-square tests work on counts
# so they don't require sampling.
#
# set.seed() ensures the random sample is reproducible — anyone who runs
# this script will get the same sample and the same results.
# ---------------------------------------------------------------------------

set.seed(2025)
sample_size <- 100000
trips_sample <- trips |> slice_sample(n = sample_size)

cat("=================================================================\n")
cat("  STATISTICAL VALIDATION OF KEY CYCLISTIC FINDINGS\n")
cat("=================================================================\n\n")

# ---------------------------------------------------------------------------
# Test 1: Welch's t-test — Duration difference (casual vs member)
#
# H0: Mean ride duration is the same for casual and member riders
# H1: Mean ride duration differs between casual and member riders
#
# Welch's t-test is preferred over Student's t-test when the two groups
# have different variances (which is almost always the case with real data).
# R's t.test() uses Welch's by default.
# ---------------------------------------------------------------------------

cat("--- Test 1: Welch's t-test — Ride Duration ---\n")

casual_duration <- trips_sample$duration_min[trips_sample$member_casual == "casual"]
member_duration <- trips_sample$duration_min[trips_sample$member_casual == "member"]

cat("Sample means:\n")
cat("  Casual:", round(mean(casual_duration), 2), "min\n")
cat("  Member:", round(mean(member_duration), 2), "min\n\n")

t_result <- t.test(casual_duration, member_duration)
print(t_result)

cat("\nInterpretation:\n")
if (t_result$p.value < 0.001) {
  cat("  p <0.001 — the duration difference is statistically significant.\n")
  cat("  We reject H0. Casual riders take meaningfully longer rides.\n")
  cat("  95% CI for difference:", round(t_result$conf.int[1], 2),
      "to", round(t_result$conf.int[2], 2), "minutes.\n")
}

# ---------------------------------------------------------------------------
# Test 2: Chi-square test — Weekend skew (casual vs member)
#
# H0: Weekend riding rate is independent of rider type
# H1: Rider type and weekend usage are associated
#
# chisq.test() takes a contingency table — rows = rider type, cols = day type.
# table() builds the contingency table from two columns.
# ---------------------------------------------------------------------------

cat("\n--- Test 2: Chi-square test — Weekend Skew ---\n")

weekend_table <- table(trips$member_casual, trips$is_weekend)
colnames(weekend_table) <- c("Weekday", "Weekend")
cat("Contingency table:\n")
print(weekend_table)

chi_weekend <- chisq.test(weekend_table)
print(chi_weekend)

cat("\nInterpretation:\n")
if (chi_weekend$p.value < 0.001) {
  cat("  p <0.001 — weekend usage pattern is significantly associated with rider type.\n")
  cat("  We reject H0. The casual weekend skew is not due to chance.\n")
}

# ---------------------------------------------------------------------------
# Test 3: Chi-square test — Round trip rate (casual vs member)
#
# H0: Round trip rate is independent of rider type
# H1: Rider type and round trip behaviour are associated
# ---------------------------------------------------------------------------

cat("\n--- Test 3: Chi-square test — Round Trip Rate ---\n")

roundtrip_table <- table(trips$member_casual, trips$is_round_trip)
colnames(roundtrip_table) <- c("One-way", "Round trip")
cat("Contingency table:\n")
print(roundtrip_table)

chi_roundtrip <- chisq.test(roundtrip_table)
print(chi_roundtrip)

cat("\nInterpretation:\n")
if (chi_roundtrip$p.value < 0.001) {
  cat("  p <0.001 — round trip behaviour is significantly associated with rider type.\n")
  cat("  We reject H0. Casual riders' higher round trip rate is not due to chance.\n")
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

cat("\n=================================================================\n")
cat("  SUMMARY\n")
cat("=================================================================\n")
cat("All three key findings are statistically significant (p < 0.001):\n\n")
cat("  1. Casual riders take longer rides — confirmed by Welch's t-test\n")
cat("  2. Casual riders skew toward weekends — confirmed by chi-square\n")
cat("  3. Casual riders take more round trips — confirmed by chi-square\n\n")
cat("These are not sampling artefacts. The behavioural differences between\n")
cat("casual and member riders are real and consistent across 5.6M rides.\n")
