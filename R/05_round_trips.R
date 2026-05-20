# 05_round_trips.R
# Cyclistic Bike-Share Case Study — R Module
#
# Round trip rate by rider type.
# Confirms: casual riders return to starting station 1.63x more often than members.
#
# Introduces: is.na(), coalesce(), case_when()

library(tidyverse)

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")
csv_files  <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)
trips      <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Classify round trips
#
# A round trip is where the start and end station are the same.
# Key NULL semantics issue — same as we solved in DuckDB and SQL Server:
#
#   NA == NA  evaluates to NA in R (not TRUE) — same as SQL's NULL = NULL
#
# To replicate Power BI's BLANK() = BLANK() = TRUE behavior, we replace
# NA with an empty string before comparing, using coalesce().
# coalesce() returns the first non-NA value — R's equivalent of SQL COALESCE()
# and DuckDB's COALESCE().
#
# This ensures e-bike rides with no station name (locked at non-station racks)
# are correctly counted as round trips when both ends are missing.
# ---------------------------------------------------------------------------

trips <- trips |>
  mutate(
    is_round_trip = coalesce(start_station_name, "") == coalesce(end_station_name, "")
  )

# ---------------------------------------------------------------------------
# Summarise round trip rates
# ---------------------------------------------------------------------------

round_trip_summary <- trips |>
  group_by(member_casual) |>
  summarise(
    total_rides     = n(),
    round_trips     = sum(is_round_trip),
    round_trip_pct  = round(round_trips / total_rides * 100, 1)
  )

cat("--- Round Trip Rates ---\n")
print(round_trip_summary)

casual_pct <- round_trip_summary$round_trip_pct[round_trip_summary$member_casual == "casual"]
member_pct <- round_trip_summary$round_trip_pct[round_trip_summary$member_casual == "member"]

cat("\nRound trip ratio (casual / member):", round(casual_pct / member_pct, 2), "\n")

# ---------------------------------------------------------------------------
# Bar chart
# ---------------------------------------------------------------------------

ggplot(round_trip_summary, aes(x = member_casual, y = round_trip_pct, fill = member_casual)) +
  geom_col(width = 0.5) +
  geom_text(
    aes(label = paste0(round_trip_pct, "%")),
    vjust = -0.4,
    size  = 4
  ) +
  scale_fill_manual(values = c("casual" = "#F4A261", "member" = "#2A9D8F")) +
  scale_y_continuous(limits = c(0, 25), labels = scales::percent_format(scale = 1)) +
  labs(
    title    = "Casual Riders Return to Their Starting Station Far More Often",
    subtitle = "Casual round trip rate is 1.63x higher — consistent with recreational riding",
    x        = NULL,
    y        = "Round Trip Rate",
    fill     = NULL,
    caption  = "Source: Divvy Trip Data"
  ) +
  theme_minimal(base_size = 13) +
  theme(legend.position = "none")

ggsave(
  file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
            "Visuals", "R", "05_round_trips.png"),
  width = 8, height = 6, dpi = 150
)
