# 00_run_all.R
# Cyclistic Bike-Share Case Study — R Module
#
# Runs all analysis scripts in order. Each script reads the data,
# performs analysis, prints results to the console, and saves its
# chart to Visuals/R/.
#
# Note: each script re-reads the CSVs independently.
# Total run time: approximately 15-20 minutes.
#
# Usage: open this file in RStudio and run with Ctrl+Shift+Enter.

script_dir <- dirname(rstudioapi::getSourceEditorContext()$path)

scripts <- c(
  "01_hello_r.R",
  "02_core_ride_counts.R",
  "03_avg_duration_distance.R",
  "04_weekend_weekday.R",
  "05_round_trips.R",
  "06_seasonal_breakdown.R",
  "07_bike_type_mix.R",
  "08_top_stations.R",
  "09_hourly_distribution.R",
  "10_missing_station_data.R",
  "11_revenue_proxy.R",
  "12_statistical_tests.R"
)

for (s in scripts) {
  cat("\n", strrep("=", 60), "\n")
  cat(" Running:", s, "\n")
  cat(strrep("=", 60), "\n\n")
  source(file.path(script_dir, s), echo = FALSE)
}

cat("\n", strrep("=", 60), "\n")
cat(" All scripts complete.\n")
cat(" Charts saved to Visuals/R/\n")
cat(strrep("=", 60), "\n")
