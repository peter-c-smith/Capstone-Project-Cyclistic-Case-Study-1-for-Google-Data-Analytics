# 06_seasonal_breakdown.R
# Cyclistic Bike-Share Case Study — R Module
#
# Monthly and seasonal ride breakdown by rider type.
# Confirms: casual ridership peaks at 42.7% of summer rides, drops to 19.6% in winter.
#
# Introduces: lubridate::month(), floor_date(), ordered factors, line chart

library(tidyverse)

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")
csv_files  <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)
trips      <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Add month and season columns
#
# floor_date() rounds a datetime down to the nearest unit — here "month".
# This gives us a proper date (e.g. 2025-04-01) to sort and plot on an axis,
# unlike strftime() which gives a string.
#
# case_when() is dplyr's multi-condition ifelse — equivalent to a CASE WHEN
# in SQL. Each condition is evaluated in order; first TRUE wins.
# ---------------------------------------------------------------------------

trips <- trips |>
  mutate(
    ride_month = floor_date(started_at, "month"),
    month_num  = month(started_at),
    season     = case_when(
      month_num %in% c(12, 1, 2) ~ "Winter",
      month_num %in% c(3, 4, 5)  ~ "Spring",
      month_num %in% c(6, 7, 8)  ~ "Summer",
      month_num %in% c(9, 10, 11) ~ "Fall"
    )
  )

# ---------------------------------------------------------------------------
# Monthly summary — casual % of total rides each month
# ---------------------------------------------------------------------------

monthly <- trips |>
  group_by(ride_month, member_casual) |>
  summarise(rides = n(), .groups = "drop") |>
  group_by(ride_month) |>
  mutate(pct = round(rides / sum(rides) * 100, 1)) |>
  filter(member_casual == "casual")

cat("--- Monthly Casual Share ---\n")
print(monthly |> select(ride_month, rides, pct), n = 12)

# ---------------------------------------------------------------------------
# Seasonal summary
# ---------------------------------------------------------------------------

seasonal <- trips |>
  group_by(season, member_casual) |>
  summarise(rides = n(), .groups = "drop") |>
  group_by(season) |>
  mutate(pct = round(rides / sum(rides) * 100, 1)) |>
  filter(member_casual == "casual") |>
  mutate(season = factor(season, levels = c("Winter", "Spring", "Summer", "Fall"))) |>
  arrange(season)

cat("\n--- Seasonal Casual Share ---\n")
print(seasonal |> select(season, rides, pct))

# ---------------------------------------------------------------------------
# Line chart — casual % by month
#
# format(ride_month, "%b %Y") converts the date to a readable label like "Apr 2025"
# geom_line() connects points in order; geom_point() adds dots at each month.
# geom_hline() draws a horizontal reference line — here at 50% (equal split).
# ---------------------------------------------------------------------------

ggplot(monthly, aes(x = ride_month, y = pct)) +
  geom_line(color = "#F4A261", linewidth = 1.2) +
  geom_point(color = "#F4A261", size = 3) +
  geom_hline(yintercept = 50, linetype = "dashed", color = "grey50") +
  geom_text(
    aes(label = paste0(pct, "%")),
    vjust = -0.8,
    size  = 3.2
  ) +
  scale_x_date(date_labels = "%b %Y", date_breaks = "1 month") +
  scale_y_continuous(limits = c(0, 60), labels = scales::percent_format(scale = 1)) +
  labs(
    title    = "Casual Ridership Peaks in Summer, Collapses in Winter",
    subtitle = "Dashed line = 50% (equal member/casual split)",
    x        = NULL,
    y        = "Casual Share of Monthly Rides",
    caption  = "Source: Divvy Trip Data"
  ) +
  theme_minimal(base_size = 13) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave(
  file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
            "Visuals", "R", "06_seasonal_breakdown.png"),
  width = 10, height = 6, dpi = 150
)
