# 08_top_stations.R
# Cyclistic Bike-Share Case Study — R Module
#
# Top 10 start stations by rider type.
# Key finding: zero overlap between member and casual top 10 lists.
# Casual stations = lakefront/tourist. Member stations = transit hubs.
# Shedd Aquarium: 81.8% casual — starkest example in the dataset.
#
# Introduces: slice_max(), fct_reorder(), coord_flip(), horizontal bar chart

library(tidyverse)

csv_folder <- file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
                        "Data", "DATAfile_Consolidated")
csv_files  <- list.files(csv_folder, pattern = "\\.csv$", full.names = TRUE)
trips      <- read_csv(csv_files, show_col_types = FALSE)

# ---------------------------------------------------------------------------
# Top 10 start stations for each rider type
#
# filter(!is.na(...)) removes rides with no station name (e-bikes at non-station racks)
# slice_max() selects the top N rows by a column — cleaner than arrange() + head()
# ---------------------------------------------------------------------------

top_stations <- trips |>
  filter(!is.na(start_station_name)) |>
  group_by(member_casual, start_station_name) |>
  summarise(rides = n(), .groups = "drop") |>
  group_by(member_casual) |>
  slice_max(rides, n = 10)

cat("--- Top 10 Stations: Casual ---\n")
top_stations |>
  filter(member_casual == "casual") |>
  arrange(desc(rides)) |>
  print(n = 10)

cat("\n--- Top 10 Stations: Member ---\n")
top_stations |>
  filter(member_casual == "member") |>
  arrange(desc(rides)) |>
  print(n = 10)

# Check for overlap
casual_stations <- top_stations$start_station_name[top_stations$member_casual == "casual"]
member_stations <- top_stations$start_station_name[top_stations$member_casual == "member"]
overlap         <- intersect(casual_stations, member_stations)

cat("\nStations appearing in both top 10 lists:", length(overlap), "\n")
if (length(overlap) == 0) cat("Zero overlap confirmed.\n")

# ---------------------------------------------------------------------------
# Shedd Aquarium casual %
# ---------------------------------------------------------------------------

shedd <- trips |>
  filter(start_station_name == "Shedd Aquarium") |>
  count(member_casual) |>
  mutate(pct = round(n / sum(n) * 100, 1))

cat("\n--- Shedd Aquarium Rider Mix ---\n")
print(shedd)

# ---------------------------------------------------------------------------
# Side-by-side horizontal bar charts
#
# fct_reorder() reorders a factor by another variable — here sorts stations
# by ride count so the longest bar is at the top.
# coord_flip() rotates the chart 90 degrees — standard for long station names.
# facet_wrap(scales="free") lets each panel have its own axis scale and labels.
# ---------------------------------------------------------------------------

plot_data <- top_stations |>
  mutate(
    start_station_name = fct_reorder(start_station_name, rides),
    member_casual      = recode(member_casual,
                                casual = "Casual Riders",
                                member = "Member Riders")
  )

ggplot(plot_data, aes(x = start_station_name, y = rides, fill = member_casual)) +
  geom_col(width = 0.7) +
  geom_text(
    aes(label = scales::comma(rides)),
    hjust = -0.1,
    size  = 3
  ) +
  coord_flip() +
  facet_wrap(~member_casual, scales = "free") +
  scale_fill_manual(values = c("Casual Riders" = "#F4A261", "Member Riders" = "#2A9D8F")) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.2)), labels = scales::comma) +
  labs(
    title   = "Zero Overlap Between Member and Casual Top 10 Stations",
    subtitle = "Casuals: lakefront/tourist destinations  |  Members: transit hubs",
    x       = NULL,
    y       = "Rides",
    fill    = NULL,
    caption = "Source: Divvy Trip Data"
  ) +
  theme_minimal(base_size = 11) +
  theme(legend.position = "none")

ggsave(
  file.path(dirname(dirname(rstudioapi::getSourceEditorContext()$path)),
            "Visuals", "R", "08_top_stations.png"),
  width = 12, height = 7, dpi = 150
)
