# 01_hello_r.R
# Cyclistic Bike-Share Case Study — R Module
#
# Sanity check: read all 12 monthly CSV files, confirm total row count
# matches SQL Server (5,620,544) and DuckDB.
#
# Introduces: readr, tibbles, the tidyverse, glimpse()

library(tidyverse)

# ---------------------------------------------------------------------------
# Path to the consolidated CSV folder
# Here we use list.files() to get all CSV paths, then read_csv() to load them.
# This is the R equivalent of DuckDB's read_csv_auto('*.csv').
# ---------------------------------------------------------------------------

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")

csv_files <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)

cat("CSV files found:", length(csv_files), "\n")

# ---------------------------------------------------------------------------
# Read all files into a single tibble
# read_csv() is readr's version of read.csv() — faster, smarter type detection,
# and returns a tibble instead of a plain data.frame.
# ---------------------------------------------------------------------------

trips <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Basic confirmation
# ---------------------------------------------------------------------------

cat("\n--- Row & Column Count ---\n")
cat("Total rows:   ", format(nrow(trips), big.mark = ","), "\n")
cat("Total columns:", ncol(trips), "\n")

cat("\n--- Member / Casual Split ---\n")
trips |>
  count(member_casual) |>
  mutate(pct = round(n / sum(n) * 100, 1)) |>
  print()

cat("\n--- Data Structure (first look) ---\n")
glimpse(trips)
