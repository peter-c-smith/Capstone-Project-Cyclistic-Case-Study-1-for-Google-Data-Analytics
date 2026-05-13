# Power BI Measure Folder Structure

This document lists all DAX measures organized by their assigned display folder in the Power BI report. Folders are set in the Properties pane for each measure in Power BI Desktop.

---

---

## 📁 Annotations

Dynamic text measures that generate descriptive sentences for use in Card visuals alongside behavioral ratio cards. Values update automatically when slicers are adjusted.

| Measure | Description |
|---|---|
| Annotation Duration Ratio | Dynamic text describing the casual to member ride duration ratio |
| Annotation Weekend Skew | Dynamic text describing the casual to member weekend concentration ratio |
| Annotation Round Trip Ratio | Dynamic text describing the casual to member round trip ratio |
| Annotation Distance Ratio | Dynamic text describing the casual to member ride distance ratio |

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

---

## Calculated Columns

Calculated columns live in the `Trips` table and are not stored in measure folders.

| Column | Description |
|---|---|
| Ride Distance (mi) | Haversine formula distance in miles between start and end coordinates |
| Ride Time (min) | Ride duration in decimal minutes |
| Ride Start Date | Date portion of started_at for use with the Date table |
| Ride Start Hour | Hour (0–23) extracted from started_at for hourly distribution visuals |
| Ride Start Hour Label | 12-hour clock label (e.g. "9 AM", "3 PM") — sort by Ride Start Hour to maintain chronological order |