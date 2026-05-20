# 02_core_ride_counts.R
# Cyclistic Bike-Share Case Study — R Module
#
# Member vs casual ride distribution.
# Confirms: 64.1% member / 35.9% casual
#
# Introduces: group_by(), summarise(), ggplot2 bar chart

library(tidyverse)

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")
csv_files  <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)
trips      <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Summarise ride counts by rider type
# group_by() + summarise() is dplyr's equivalent of GROUP BY + COUNT in SQL
# ---------------------------------------------------------------------------

ride_counts <- trips |>
  group_by(member_casual) |>
  summarise(
    rides = n(),
    pct   = round(rides / nrow(trips) * 100, 1)
  )

cat("--- Core Ride Counts ---\n")
print(ride_counts)

# ---------------------------------------------------------------------------
# ggplot2 bar chart
#
# ggplot2 works in layers — you build a chart by adding (+) components:
#   ggplot()       sets up the canvas and maps columns to visual properties (aes)
#   geom_col()     draws the bars (heights = actual values, not counts)
#   geom_text()    adds labels on top of each bar
#   labs()         sets title, axis labels, caption
#   theme_minimal() applies a clean background
#   scale_y_continuous() formats the y-axis numbers with commas
# ---------------------------------------------------------------------------

ggplot(ride_counts, aes(x = member_casual, y = rides, fill = member_casual)) +
  geom_col(width = 0.5) +
  geom_text(
    aes(label = paste0(format(rides, big.mark = ","), "\n(", pct, "%)")),
    vjust = -0.3,
    size  = 4
  ) +
  scale_y_continuous(
    labels = scales::comma,
    limits = c(0, 4200000)
  ) +
  scale_fill_manual(values = c("casual" = "#F4A261", "member" = "#2A9D8F")) +
  labs(
    title   = "Members Take 64% of All Rides",
    subtitle = "April 2025 – March 2026  |  5,620,544 total rides",
    x       = NULL,
    y       = "Number of Rides",
    fill    = NULL,
    caption = "Source: Divvy Trip Data"
  ) +
  theme_minimal(base_size = 13) +
  theme(legend.position = "none")

ggsave(
  file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
            "Visuals", "R", "02_core_ride_counts.png"),
  width = 8, height = 6, dpi = 150
)
