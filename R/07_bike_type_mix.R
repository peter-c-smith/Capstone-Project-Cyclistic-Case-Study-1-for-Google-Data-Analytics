# 07_bike_type_mix.R
# Cyclistic Bike-Share Case Study — R Module
#
# Bike type preference by rider type.
# Null finding: members and casuals use electric bikes at nearly identical rates
# (~65% electric for both groups). Bike type is not a conversion lever.
#
# Introduces: geom_col with position="fill", scales::percent_format()

library(tidyverse)

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")
csv_files  <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)
trips      <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Summarise bike type mix by rider type
# ---------------------------------------------------------------------------

bike_summary <- trips |>
  group_by(member_casual, rideable_type) |>
  summarise(rides = n(), .groups = "drop") |>
  group_by(member_casual) |>
  mutate(
    pct         = round(rides / sum(rides) * 100, 1),
    grand_total = sum(rides)
  )

cat("--- Bike Type Mix ---\n")
print(bike_summary)

# ---------------------------------------------------------------------------
# Stacked 100% bar chart
#
# position = "fill" stacks bars and normalises them to 100% —
# useful when comparing proportions across groups of different sizes.
# scale_y_continuous with percent_format() formats the axis as percentages.
# ---------------------------------------------------------------------------

ggplot(bike_summary, aes(x = member_casual, y = rides, fill = rideable_type)) +
  geom_col(position = "fill", width = 0.5) +
  geom_text(
    aes(label = paste0(pct, "%")),
    position = position_fill(vjust = 0.5),
    size     = 4,
    color    = "white",
    fontface = "bold"
  ) +
  scale_fill_manual(
    values = c("electric_bike" = "#2A9D8F", "classic_bike" = "#E9C46A"),
    labels = c("electric_bike" = "Electric", "classic_bike" = "Classic")
  ) +
  scale_y_continuous(labels = scales::percent_format()) +
  labs(
    title    = "Bike Type Preference Is Nearly Identical for Both Groups",
    subtitle = "Null finding: ~65% electric for both members and casuals",
    x        = NULL,
    y        = "Share of Rides",
    fill     = "Bike Type",
    caption  = "Source: Divvy Trip Data"
  ) +
  theme_minimal(base_size = 13) +
  theme(legend.position = "top")

ggsave(
  file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
            "Visuals", "R", "07_bike_type_mix.png"),
  width = 8, height = 6, dpi = 150
)
