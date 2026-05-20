# 03_avg_duration_distance.R
# Cyclistic Bike-Share Case Study — R Module
#
# Average ride duration and distance by rider type.
# Confirms: casual rides 1.82x longer, 1.03x farther than members.
#
# Introduces: mutate(), as.numeric(), difftime(), the Haversine formula in R,
#             side-by-side bar chart with facet_wrap()

library(tidyverse)

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")
csv_files  <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)
trips      <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Compute duration (minutes) and distance (miles) for each ride
#
# Duration: difftime() subtracts two datetime columns and returns a difftime
#           object. as.numeric(..., units="mins") converts it to a plain number.
#           This is the R equivalent of DuckDB's epoch(ended_at - started_at)/60
#
# Distance: same Haversine formula as DuckDB/SQL Server, expressed in R syntax.
#           Uses vectorised trig functions — no loop needed.
# ---------------------------------------------------------------------------

trips <- trips |>
  mutate(
    duration_min = as.numeric(difftime(ended_at, started_at, units = "mins")),
    distance_mi  = {
      lat1 <- start_lat * pi / 180
      lat2 <- end_lat   * pi / 180
      dlat <- (end_lat - start_lat) * pi / 180
      dlng <- (end_lng - start_lng) * pi / 180
      a    <- sin(dlat/2)^2 + cos(lat1) * cos(lat2) * sin(dlng/2)^2
      3958.8 * 2 * asin(sqrt(a))
    }
  ) |>
  filter(duration_min > 0)    # drop zero/negative durations only

# ---------------------------------------------------------------------------
# Data quality note: rides over 24 hours
# These almost certainly represent bikes that were not properly docked or
# trips where the rider forgot to end the session — not real rides.
# We include them here to match DuckDB and Power BI (which applied no cap),
# but flag them as a known data quality issue.
# ---------------------------------------------------------------------------

over_24hr <- trips |>
  filter(duration_min >= 1440) |>
  count(member_casual) |>
  mutate(pct_of_total = round(n / nrow(trips) * 100, 3))

cat("--- Rides Over 24 Hours (Data Quality Flag) ---\n")
cat("Total:", format(sum(over_24hr$n), big.mark = ","),
    "rides (", round(sum(over_24hr$n) / nrow(trips) * 100, 3), "% of all rides )\n")
print(over_24hr)
cat("Note: likely undocked/forgotten bikes — not genuine rides.\n\n")

# ---------------------------------------------------------------------------
# Summarise averages by rider type
# ---------------------------------------------------------------------------

summary_tbl <- trips |>
  group_by(member_casual) |>
  summarise(
    avg_duration_min = round(mean(duration_min, na.rm = TRUE), 1),
    avg_distance_mi  = round(mean(distance_mi,  na.rm = TRUE), 2)
  )

cat("--- Average Duration and Distance ---\n")
print(summary_tbl)

# Ratios (casual / member)
casual_dur  <- summary_tbl$avg_duration_min[summary_tbl$member_casual == "casual"]
member_dur  <- summary_tbl$avg_duration_min[summary_tbl$member_casual == "member"]
casual_dist <- summary_tbl$avg_distance_mi[summary_tbl$member_casual  == "casual"]
member_dist <- summary_tbl$avg_distance_mi[summary_tbl$member_casual  == "member"]

cat("\nDuration ratio (casual / member):", round(casual_dur  / member_dur,  2), "\n")
cat("Distance ratio (casual / member):", round(casual_dist / member_dist, 2), "\n")

# ---------------------------------------------------------------------------
# Side-by-side charts using facet_wrap()
#
# We reshape the data to "long" format first with pivot_longer() —
# this is the tidyverse way to go from wide (one column per metric)
# to long (one row per metric), which ggplot2 prefers.
# ---------------------------------------------------------------------------

plot_data <- summary_tbl |>
  pivot_longer(
    cols      = c(avg_duration_min, avg_distance_mi),
    names_to  = "metric",
    values_to = "value"
  ) |>
  mutate(
    metric = recode(metric,
                    avg_duration_min = "Avg Duration (min)",
                    avg_distance_mi  = "Avg Distance (mi)")
  )

ggplot(plot_data, aes(x = member_casual, y = value, fill = member_casual)) +
  geom_col(width = 0.5) +
  geom_text(aes(label = value), vjust = -0.4, size = 4) +
  facet_wrap(~metric, scales = "free_y") +
  scale_fill_manual(values = c("casual" = "#F4A261", "member" = "#2A9D8F")) +
  labs(
    title    = "Casual Riders Take Longer Rides — Not Longer Routes",
    subtitle = "82% longer duration, similar distance — round trips reduce casual's straight-line average",
    x        = NULL,
    y        = NULL,
    fill     = NULL,
    caption  = "Source: Divvy Trip Data"
  ) +
  theme_minimal(base_size = 13) +
  theme(legend.position = "none")

ggsave(
  file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
            "Visuals", "R", "03_avg_duration_distance.png"),
  width = 9, height = 6, dpi = 150
)
