# 09_hourly_distribution.R
# Cyclistic Bike-Share Case Study — R Module
#
# Ride volume by hour of day, split by rider type.
# Key finding: members show dual peaks at 8 AM and 5 PM (commute pattern).
#              Casuals show a single afternoon peak (leisure pattern).
#
# Introduces: lubridate::hour(), geom_area(), faceted area chart

library(tidyverse)

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")
csv_files  <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)
trips      <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Extract hour and summarise ride counts
#
# hour() from lubridate extracts the hour as an integer 0-23.
# Equivalent to DuckDB's HOUR() and SQL Server's DATEPART(HOUR, col).
# ---------------------------------------------------------------------------

hourly <- trips |>
  mutate(hour = hour(started_at)) |>
  group_by(member_casual, hour) |>
  summarise(rides = n(), .groups = "drop") |>
  group_by(member_casual) |>
  mutate(
    pct        = round(rides / sum(rides) * 100, 2),
    rider_label = recode(member_casual,
                         casual = "Casual Riders",
                         member = "Member Riders")
  )

cat("--- Peak Hours ---\n")
hourly |>
  group_by(member_casual) |>
  slice_max(rides, n = 3) |>
  arrange(member_casual, desc(rides)) |>
  select(member_casual, hour, rides, pct) |>
  print()

# ---------------------------------------------------------------------------
# Faceted area chart
#
# geom_area() fills the area under a line — more visually impactful than
# geom_line() alone for showing volume patterns.
#
# scale_x_continuous with breaks every 4 hours keeps the axis readable.
# annotate() adds text labels directly onto the plot — used here to call out
# the 8 AM and 5 PM commuter peaks on the member panel.
# ---------------------------------------------------------------------------

# Build annotation data for the commuter peaks (member panel only)
peak_annotations <- tibble(
  rider_label = "Member Riders",
  hour        = c(8, 17),
  label       = c("8 AM\ncommute", "5 PM\ncommute")
)

ggplot(hourly, aes(x = hour, y = rides, fill = member_casual)) +
  geom_area(alpha = 0.85) +
  geom_text(
    data     = peak_annotations,
    aes(x = hour, y = Inf, label = label),
    vjust    = 1.3,
    size     = 3.2,
    color    = "grey30",
    fontface = "italic",
    inherit.aes = FALSE
  ) +
  geom_vline(
    data        = peak_annotations,
    aes(xintercept = hour),
    linetype    = "dashed",
    color       = "grey50",
    linewidth   = 0.5,
    inherit.aes = FALSE
  ) +
  facet_wrap(~rider_label, ncol = 1, scales = "free_y") +
  scale_fill_manual(values = c("casual" = "#F4A261", "member" = "#2A9D8F")) +
  scale_x_continuous(
    breaks = seq(0, 23, by = 4),
    labels = c("12 AM","4 AM","8 AM","12 PM","4 PM","8 PM")
  ) +
  scale_y_continuous(labels = scales::comma) +
  labs(
    title    = "Members Ride on Schedule — Casuals Ride for Leisure",
    subtitle = "Member dual peaks at 8 AM and 5 PM reveal commuter usage;\ncasual single afternoon peak reveals recreational usage",
    x        = "Hour of Day",
    y        = "Number of Rides",
    fill     = NULL,
    caption  = "Source: Divvy Trip Data"
  ) +
  theme_minimal(base_size = 13) +
  theme(
    legend.position  = "none",
    strip.text       = element_text(face = "bold", size = 12),
    panel.spacing    = unit(1.5, "lines")
  )

ggsave(
  file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
            "Visuals", "R", "09_hourly_distribution.png"),
  width = 9, height = 8, dpi = 150
)
