# 10_missing_station_data.R
# Cyclistic Bike-Share Case Study — R Module
#
# Missing station data analysis and e-bike GPS inference.
# Key finding: 100% of e-bike rides with missing station names still have
# GPS coordinates — proving e-bikes have onboard GPS hardware.
# Classic bikes have zero missing station names.
#
# Introduces: is.na(), across(), summarise with multiple columns

library(tidyverse)

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")
csv_files  <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)
trips      <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Part 1: Missing station data by bike type
#
# is.na() returns TRUE for NA values — R's equivalent of IS NULL in SQL.
# We use it inside summarise() to count missing values per group.
# ---------------------------------------------------------------------------

cat("--- Part 1: Missing Station Data by Bike Type ---\n")

missing_by_bike <- trips |>
  group_by(rideable_type) |>
  summarise(
    total_rides          = n(),
    missing_start_station = sum(is.na(start_station_name)),
    missing_end_station   = sum(is.na(end_station_name)),
    pct_missing_start    = round(missing_start_station / total_rides * 100, 1),
    pct_missing_end      = round(missing_end_station   / total_rides * 100, 1)
  )

print(missing_by_bike)

# ---------------------------------------------------------------------------
# Part 2: Missing station data by rider type
# ---------------------------------------------------------------------------

cat("\n--- Part 2: Missing Station Data by Rider Type ---\n")

missing_by_rider <- trips |>
  group_by(member_casual) |>
  summarise(
    total_rides           = n(),
    missing_start_station = sum(is.na(start_station_name)),
    pct_missing           = round(missing_start_station / total_rides * 100, 1)
  )

print(missing_by_rider)

# ---------------------------------------------------------------------------
# Part 3: GPS coverage on e-bike rides with missing station names
#
# The critical inference: if a ride has no station name but still has
# GPS coordinates, the bike itself must be reporting its location.
# Classic bikes are only "located" when docked at a station sensor.
# E-bikes know where they are independently of any dock.
# ---------------------------------------------------------------------------

cat("\n--- Part 3: GPS Coverage on Missing-Station E-Bike Rides ---\n")

ebike_missing <- trips |>
  filter(rideable_type == "electric_bike", is.na(start_station_name)) |>
  summarise(
    total_missing_station = n(),
    has_start_gps         = sum(!is.na(start_lat) & !is.na(start_lng)),
    has_end_gps           = sum(!is.na(end_lat)   & !is.na(end_lng)),
    pct_start_gps         = round(has_start_gps / total_missing_station * 100, 1),
    pct_end_gps           = round(has_end_gps   / total_missing_station * 100, 1)
  )

cat("E-bike rides with missing station name:", format(ebike_missing$total_missing_station, big.mark=","), "\n")
cat("Of those, rides with start GPS coordinates:", format(ebike_missing$has_start_gps, big.mark=","),
    paste0("(", ebike_missing$pct_start_gps, "%)"), "\n")
cat("Of those, rides with end GPS coordinates:  ", format(ebike_missing$has_end_gps, big.mark=","),
    paste0("(", ebike_missing$pct_end_gps, "%)"), "\n")
cat("\nConclusion: E-bikes have onboard GPS hardware — they report location\n")
cat("independently of any dock. Classic bikes have zero missing station names\n")
cat("because they are only located when physically docked at a station sensor.\n")

# ---------------------------------------------------------------------------
# Bar chart — missing station % by bike type
# ---------------------------------------------------------------------------

ggplot(missing_by_bike, aes(x = rideable_type, y = pct_missing_start, fill = rideable_type)) +
  geom_col(width = 0.5) +
  geom_text(
    aes(label = paste0(pct_missing_start, "%")),
    vjust = -0.4,
    size  = 4
  ) +
  scale_fill_manual(values = c("electric_bike" = "#2A9D8F", "classic_bike" = "#E9C46A")) +
  scale_x_discrete(labels = c("classic_bike" = "Classic Bike", "electric_bike" = "Electric Bike")) +
  scale_y_continuous(limits = c(0, 40), labels = scales::percent_format(scale = 1)) +
  labs(
    title    = "E-Bikes Have Onboard GPS — Classic Bikes Do Not",
    subtitle = "100% of missing-station e-bike rides still have GPS coordinates",
    x        = NULL,
    y        = "% of Rides Missing Start Station Name",
    fill     = NULL,
    caption  = "Source: Divvy Trip Data"
  ) +
  theme_minimal(base_size = 13) +
  theme(legend.position = "none")

ggsave(
  file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
            "Visuals", "R", "10_missing_station_data.png"),
  width = 8, height = 6, dpi = 150
)
