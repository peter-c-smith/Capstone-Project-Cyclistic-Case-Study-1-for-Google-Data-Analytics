# Power BI Measure Folder Structure

This document lists all DAX measures organized by their assigned display folder in the Power BI report. Folders are set in the Properties pane for each measure in Power BI Desktop.

---

## 📁 Core

| Measure | Description |
|---|---|
| Total Rides | Total number of rides across all rider types |
| Member Rides | Total rides by annual members |
| Casual Rides | Total rides by casual riders |
| Member Ride % | Proportion of rides by members |
| Avg Ride Duration | Average ride duration in decimal minutes across all riders |
| Avg Ride Distance | Average ride distance in miles across all riders |
| Avg Ride Distance Member | Average ride distance in miles for members only |
| Avg Ride Distance Casual | Average ride distance in miles for casual riders only |

---

## 📁 Temporal

| Measure | Description |
|---|---|
| Weekday Rides | Total rides occurring Monday–Friday |
| Weekend Rides | Total rides occurring Saturday–Sunday |
| Weekend Ride % | Proportion of all rides occurring on weekends |
| Avg Duration Member | Average ride duration in decimal minutes for members |
| Avg Duration Casual | Average ride duration in decimal minutes for casual riders |
| Casual Weekend % | Proportion of casual rides occurring on weekends |
| Member Weekend % | Proportion of member rides occurring on weekends |
| Member Rides by Day Type | Returns member ride count for selected day type — used in Page 3 Weekday vs Weekend chart |
| Casual Rides by Day Type | Returns casual ride count for selected day type — used in Page 3 Weekday vs Weekend chart |
| Spring Rides | Total rides occurring March–May |
| Summer Rides | Total rides occurring June–August |
| Fall Rides | Total rides occurring September–November |
| Winter Rides | Total rides occurring December–February |

---

## 📁 Bike Type

| Measure | Description |
|---|---|
| Classic Bike Rides | Total rides on classic bikes |
| Member Classic Rides | Classic bike rides by members |
| Casual Classic Rides | Classic bike rides by casual riders |
| Electric Bike Rides | Total rides on electric bikes |
| Member Electric Rides | Electric bike rides by members |
| Casual Electric Rides | Electric bike rides by casual riders |
| Docked Bike Rides | Total rides on docked bikes (returns BLANK() with current dataset) |
| Member Docked Rides | Docked bike rides by members (returns BLANK() with current dataset) |
| Casual Docked Rides | Docked bike rides by casual riders (returns BLANK() with current dataset) |
| Classic Bike % | Proportion of all rides on classic bikes |
| Electric Bike % | Proportion of all rides on electric bikes |
| Docked Bike % | Proportion of all rides on docked bikes (returns BLANK() with current dataset) |

---

## 📁 Station

| Measure | Description |
|---|---|
| Rides with Start Station | Total rides where a start station name is recorded |
| Rides with End Station | Total rides where an end station name is recorded |
| Rides Missing Station Data | Total rides with no start station recorded |
| Member Rides with Start Station | Member rides where a start station name is recorded |
| Casual Rides with Start Station | Casual rides where a start station name is recorded |
| Round Trips | Total rides where start and end station are the same |
| Casual Round Trips | Round trips by casual riders |
| Member Round Trips | Round trips by members |
| Round Trip % Member | Proportion of member rides that are round trips |
| Round Trip % Casual | Proportion of casual rides that are round trips |

---

## 📁 Revenue (Illustrative)

> **All figures produced by these measures are illustrative.** Cyclistic is a fictional company. Pricing is modeled after publicly documented Divvy rates. See `pricing_model_rationale.md` for full details.

| Measure | Description |
|---|---|
| Estimated Casual Revenue per Ride | Per-ride revenue estimate for casual riders based on $3.30 unlock fee plus $0.18/min overage beyond 30 minutes |
| Total Estimated Casual Revenue | Sum of estimated casual revenue across all qualifying rides |
| Total Estimated Member Overage Revenue | Sum of overage revenue from member rides exceeding the 45-minute threshold |

---

## 📁 Behavioral Ratios

| Measure | Description |
|---|---|
| Duration Ratio Casual to Member | Ratio of average casual ride duration to average member ride duration |
| Distance Ratio Casual to Member | Ratio of average casual ride distance to average member ride distance |
| Weekend Skew Ratio | How much more concentrated casual rides are on weekends relative to members |
| Round Trip Ratio Casual to Member | Compares the round trip rate of casual riders vs members |
| Member % by Metric | Returns member weekend % or round trip % based on Metric Groups table context — used in Page 2 clustered column chart |
| Casual % by Metric | Returns casual weekend % or round trip % based on Metric Groups table context — used in Page 2 clustered column chart |

---

## 📁 Annotations

Dynamic text measures and display formatting measures used in Card visuals throughout the report. All ratio-based annotations update automatically when slicers are adjusted. Display measures wrap numeric measures in FORMAT() and append unit strings — the underlying numeric measures remain untouched and available for calculations. Place all measures in the Annotations display folder in Power BI Desktop. Style annotation cards as Segoe UI italic, 11pt, #666666, no border, no background unless otherwise noted.

| Measure | Description | Used On |
|---|---|---|
| Annotation Duration Ratio | Dynamic text describing the casual to member ride duration ratio | Page 1 |
| Annotation Weekend Skew | Dynamic text describing the casual to member weekend concentration ratio | Page 1 |
| Annotation Round Trip Ratio | Dynamic text describing the casual to member round trip ratio | Page 1 |
| Annotation Distance Ratio | Dynamic text describing the casual to member ride distance ratio | Page 1 |
| Annotation Pace Insight | Short dynamic callout connecting duration and distance ratios | Page 1 |
| Annotation Duration Card Callout | Dynamic text showing % difference in ride duration between casual and member | Page 2 |
| Annotation Distance Card Callout | Dynamic text showing % difference in ride distance between casual and member | Page 2 |
| Annotation Page 2 Pace Insight | Fuller dynamic callout connecting duration and distance ratios with interpretive conclusion | Page 2 |
| Annotation Page 3 Temporal Insight | Dynamic callout stating % of casual rides occurring in summer — ties together hour, season, and weekday visuals | Page 3 |
| Annotation Missing Station Data | Dynamic callout showing missing station count and % — uses ALL(Trips) to avoid cross-filter from station charts | Page 4 |
| Unit Duration | Displays "min" as unit label in Card visuals — drop into Category/Details field | Page 2 |
| Unit Distance | Displays "mi" as unit label in Card visuals — drop into Category/Details field | Page 2 |
| Avg Duration Member Display | Text-formatted version of Avg Duration Member with "min" suffix for Card visuals | Page 2 |
| Avg Duration Casual Display | Text-formatted version of Avg Duration Casual with "min" suffix for Card visuals | Page 2 |
| Avg Ride Distance Member Display | Text-formatted version of Avg Ride Distance Member with "mi" suffix for Card visuals | Page 2 |
| Avg Ride Distance Casual Display | Text-formatted version of Avg Ride Distance Casual with "mi" suffix for Card visuals | Page 2 |

---

## Calculated Columns

Calculated columns live in the `Trips` table unless otherwise noted. They are not stored in measure folders.

| Column | Table | Description |
|---|---|---|
| Ride Distance (mi) | Trips | Haversine formula distance in miles between start and end coordinates |
| Ride Time (min) | Trips | Ride duration in decimal minutes |
| Ride Start Date | Trips | Date portion of started_at for use with the Date table |
| Ride Start Hour | Trips | Hour (0–23) extracted from started_at for hourly distribution visuals |
| Ride Start Hour Label | Trips | 12-hour clock label (e.g. "9 AM", "3 PM") — sort by Ride Start Hour to maintain chronological order |
| Season Sort | Date | Numeric sort order (1–4) for Season column — based on month number to avoid circular dependency |

---

## Calculated Tables

Calculated tables are created via Modeling → New Table in Power BI Desktop.

| Table | Description |
|---|---|
| Metric Groups | Two-row table containing "Weekend %" and "Round Trip %" — used as X-axis category in the Page 2 clustered column chart via Member % by Metric and Casual % by Metric measures |
| Day Type Groups | Two-row table containing "Weekday" and "Weekend" — used as X-axis category in the Page 3 Weekday vs Weekend clustered column chart via Member Rides by Day Type and Casual Rides by Day Type measures |
