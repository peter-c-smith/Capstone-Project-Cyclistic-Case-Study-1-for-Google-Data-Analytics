# 04_weekend_weekday.R
# Cyclistic Bike-Share Case Study — R Module
#
# Weekend vs weekday ride distribution by rider type.
# Confirms: casual riders 1.61x more likely to ride on weekends than members.
#
# Introduces: lubridate::wday(), if_else(), grouped bar chart

library(tidyverse)

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")
csv_files  <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)
trips      <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Classify each ride as weekend or weekday
#
# wday() is lubridate's day-of-week function.
# Default: 1 = Sunday, 7 = Saturday (same as SQL Server's DATEPART(WEEKDAY))
# DuckDB used DAYOFWEEK() where 0 = Sunday, 6 = Saturday — different numbering,
# same days. Always check the reference day when switching tools.
#
# if_else() is dplyr's vectorised ifelse — cleaner than base R's ifelse()
# for working inside mutate().
# ---------------------------------------------------------------------------

trips <- trips |>
  mutate(
    day_of_week = wday(started_at),                          # 1=Sun, 7=Sat
    is_weekend  = if_else(day_of_week %in% c(1, 7), "Weekend", "Weekday")
  )

# ---------------------------------------------------------------------------
# Summarise: rides by rider type and day type
# ---------------------------------------------------------------------------

day_summary <- trips |>
  group_by(member_casual, is_weekend) |>
  summarise(rides = n(), .groups = "drop") |>
  group_by(member_casual) |>
  mutate(pct = round(rides / sum(rides) * 100, 1))

cat("--- Weekend vs Weekday Breakdown ---\n")
print(day_summary)

# Weekend skew ratio (casual weekend % / member weekend %)
casual_wknd <- day_summary$pct[day_summary$member_casual == "casual"  & day_summary$is_weekend == "Weekend"]
member_wknd <- day_summary$pct[day_summary$member_casual == "member"  & day_summary$is_weekend == "Weekend"]

cat("\nCasual weekend share:", casual_wknd, "%\n")
cat("Member weekend share:", member_wknd, "%\n")
cat("Weekend skew ratio (casual / member):", round(casual_wknd / member_wknd, 2), "\n")

# ---------------------------------------------------------------------------
# Grouped bar chart
#
# position = "dodge" places bars side by side instead of stacked.
# ---------------------------------------------------------------------------

ggplot(day_summary, aes(x = is_weekend, y = pct, fill = member_casual)) +
  geom_col(position = "dodge", width = 0.6) +
  geom_text(
    aes(label = paste0(pct, "%")),
    position = position_dodge(width = 0.6),
    vjust    = -0.4,
    size     = 4
  ) +
  scale_fill_manual(
    values = c("casual" = "#F4A261", "member" = "#2A9D8F"),
    labels = c("Casual", "Member")
  ) +
  scale_y_continuous(limits = c(0, 85), labels = scales::percent_format(scale = 1)) +
  labs(
    title    = "Casual Riders Skew Heavily Toward Weekends",
    subtitle = "Casual riders are 1.61x more likely to ride on weekends than members",
    x        = NULL,
    y        = "Share of Rider Type's Trips",
    fill     = NULL,
    caption  = "Source: Divvy Trip Data"
  ) +
  theme_minimal(base_size = 13) +
  theme(legend.position = "top")

ggsave(
  file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
            "Visuals", "R", "04_weekend_weekday.png"),
  width = 8, height = 6, dpi = 150
)
