# Power BI Transformations
## Cyclistic Bike-Share Case Study

This file documents all data transformations and calculated columns implemented in Power BI using DAX. Each transformation includes the code and the reasoning behind key decisions.

---

## Calculated Columns

### Ride Distance (miles)
Calculates the straight-line distance between ride start and end coordinates using the Haversine formula.

**Why Haversine?**
The dataset provides only start and end coordinates, not actual routes. Haversine calculates straight-line distance between two points on Earth's surface and is the standard approach for this type of coordinate-based distance calculation.

**Why miles?**
This analysis is based in the United States where miles are the standard unit of measurement.

**Null handling:**
Rows with missing coordinates return BLANK() rather than 0 to avoid skewing distance averages with invalid data.

### Calculated Column — Ride Start Hour Label
Converts the 24-hour Ride Start Hour column into a 12-hour clock label (e.g. "9 AM", "3 PM") for use as a display axis in visuals. The column is intended to be used alongside Ride Start Hour — place Ride Start Hour Label on the visual axis and sort it by Ride Start Hour to maintain correct 24-hour chronological order.

**Null handling:** Inherits from Ride Start Hour — returns BLANK() implicitly if started_at is blank.

```dax
Ride Start Hour Label =
VAR Hour24 = Trips[Ride Start Hour]
VAR Hour12 = MOD(Hour24 - 1, 12) + 1
VAR Suffix = IF(Hour24 < 12 || Hour24 = 0, " AM", " PM")
VAR Midnight = Hour24 = 0
VAR Noon = Hour24 = 12
RETURN
    IF(Midnight, "12 AM",
        IF(Noon, "12 PM",
            FORMAT(Hour12, "0") & Suffix
        )
    )
```
```dax
Ride Distance (mi) =
IF(
    OR(
        OR(ISBLANK(rides[start_lat]), ISBLANK(rides[end_lat])),
        OR(ISBLANK(rides[start_lng]), ISBLANK(rides[end_lng]))
    ),
    BLANK(),
    VAR lat1 = RADIANS(rides[start_lat])
    VAR lat2 = RADIANS(rides[end_lat])
    VAR lon1 = RADIANS(rides[start_lng])
    VAR lon2 = RADIANS(rides[end_lng])
    VAR dlat = lat2 - lat1
    VAR dlon = lon2 - lon1
    VAR a =
        SIN(dlat / 2) ^ 2 +
        COS(lat1) * COS(lat2) * SIN(dlon / 2) ^ 2
    VAR c = 2 * ASIN(SQRT(a))
    VAR R = 3958.8
    RETURN
        R * c
)
```

---

### Ride Time (decimal minutes)
Calculates the duration of each ride in decimal minutes.

**Why decimal minutes?**
Decimal minutes preserve precision for aggregate measures and visual accuracy. Whole minute integers create distorted averages, unnatural histogram distributions, and stepped trend lines. Decimal values produce smoother, more accurate visuals and more reliable averages.

**Null handling:**
Rows with missing start or end timestamps return BLANK(). Negative values (where ended_at is earlier than started_at) also return BLANK() as these indicate data quality issues.
```dax
Ride Time (min) =
IF(
    OR(ISBLANK(rides[started_at]), ISBLANK(rides[ended_at])),
    BLANK(),
    VAR ride_seconds = DATEDIFF(rides[started_at], rides[ended_at], SECOND)
    RETURN
        IF(ride_seconds < 0, BLANK(), DIVIDE(ride_seconds, 60))
)
```

---

### Ride Start Date
Extracts the date portion from the started_at timestamp to create a relationship with the Date Table. Stripping the time component is necessary because Power BI requires matching data types and grain for table relationships.

**Null handling:**
If started_at is blank this column will also return blank, which is consistent with the ride time null handling approach.
```dax
Ride Start Date = DATE(
    YEAR(rides[started_at]),
    MONTH(rides[started_at]),
    DAY(rides[started_at])
)
```

---

## Tables

### Date Table
A calculated date table spanning the full dataset range of 4/1/2025 through 3/31/2026. Includes columns for time intelligence, visual formatting, and business analysis.


```dax
Date Table = 
VAR StartDate = DATE(2025, 4, 1)
VAR EndDate = DATE(2026, 3, 31)
RETURN
ADDCOLUMNS(
    CALENDAR(StartDate, EndDate),
    "Year", YEAR([Date]),
    "Month Number", MONTH([Date]),
    "Month Name", FORMAT([Date], "MMMM"),
    "Month Short", FORMAT([Date], "MMM"),
    "Quarter", "Q" & QUARTER([Date]),
    "Week Number", WEEKNUM([Date], 2),
    "Day Number", WEEKDAY([Date], 2),
    "Day Name", FORMAT([Date], "dddd"),
    "Day Short", FORMAT([Date], "ddd"),
    "Is Weekend", IF(WEEKDAY([Date], 2) >= 6, TRUE(), FALSE()),
    "Season", 
        SWITCH(
            TRUE(),
            MONTH([Date]) IN {3, 4, 5}, "Spring",
            MONTH([Date]) IN {6, 7, 8}, "Summer",
            MONTH([Date]) IN {9, 10, 11}, "Fall",
            "Winter"
        ),
    "Year-Month", FORMAT([Date], "YYYY-MM"),
    "Year-Quarter", YEAR([Date]) & " Q" & QUARTER([Date])
)

## Phase 1 — Core Measures

### Total Rides
Total Rides = COUNTROWS(Trips)
Counts all rows in the Trips table. Relies on upstream cleaning for invalid record removal.

### Member Rides
Member Rides = CALCULATE(COUNTROWS(Trips), Trips[member_casual] = "member")
Filters to member rides only.

### Casual Rides
Casual Rides = CALCULATE(COUNTROWS(Trips), Trips[member_casual] = "casual")
Filters to casual rides only.

### Member Ride %
Member Ride % = DIVIDE([Member Rides], [Total Rides], BLANK())
Returns the proportion of rides by members. BLANK() returned on divide-by-zero to stay consistent with null-handling convention.

### Avg Ride Duration (min)
Avg Ride Duration (min) = AVERAGEX(FILTER(Trips, Trips[Ride Time (min)] > 0), Trips[Ride Time (min)])
Averages decimal-minute ride durations. Filters out zero and blank values before averaging to avoid skewing the result.

### Avg Ride Distance (mi)
Avg Ride Distance (mi) = AVERAGEX(FILTER(Trips, Trips[Ride Distance (mi)] > 0), Trips[Ride Distance (mi)])
Averages Haversine-calculated ride distances in miles. Same filter logic as duration.

### Avg Ride Distance Member
```dax
Avg Ride Distance Member =
AVERAGEX(
    FILTER(Trips, Trips[member_casual] = "member" && Trips[Ride Distance (mi)] > 0),
    Trips[Ride Distance (mi)]
)
```
Average ride distance in miles for members only. Filters out zero and blank values before averaging, consistent with other average measures in this project. Companion measure to Avg Ride Distance Casual — both are used to feed the Distance Ratio Casual to Member measure in Phase 5.

### Avg Ride Distance Casual
```dax
Avg Ride Distance Casual =
AVERAGEX(
    FILTER(Trips, Trips[member_casual] = "casual" && Trips[Ride Distance (mi)] > 0),
    Trips[Ride Distance (mi)]
)
```
Average ride distance in miles for casual riders only. Filters out zero and blank values before averaging, consistent with other average measures in this project. Companion measure to Avg Ride Distance Member — both are used to feed the Distance Ratio Casual to Member measure in Phase 5.

## Phase 2 — Temporal & Usage Patterns

### Calculated Column — Ride Start Hour
Extracts the hour (0–23) from the ride start timestamp. Used as a visual axis to show ride distribution across hours of the day. Peak hour analysis is better surfaced through visuals than a single DAX measure, as the full hourly distribution is more informative than a single peak value.

**Null handling:** Returns BLANK() implicitly if started_at is blank, consistent with other calculated columns.

```dax
Ride Start Hour =
HOUR(Trips[started_at])
```

---

### Weekday Rides
```dax
Weekday Rides =
CALCULATE([Total Rides], 'Date'[Is Weekend] = FALSE())
```
Counts rides occurring on weekdays (Monday–Friday). Uses the Is Weekend column from the Date table.

### Weekend Rides
```dax
Weekend Rides =
CALCULATE([Total Rides], 'Date'[Is Weekend] = TRUE())
```
Counts rides occurring on weekends (Saturday–Sunday).

### Weekend Ride %
```dax
Weekend Ride % =
DIVIDE([Weekend Rides], [Total Rides], BLANK())
```
Proportion of all rides occurring on weekends. BLANK() returned on divide-by-zero consistent with null-handling convention.

---

### Avg Duration Member
```dax
Avg Duration Member =
AVERAGEX(
    FILTER(Trips, Trips[member_casual] = "member" && Trips[Ride Time (min)] > 0),
    Trips[Ride Time (min)]
)
```
Average ride duration in decimal minutes for members only. Filters out zero and blank values before averaging.

### Avg Duration Casual
```dax
Avg Duration Casual =
AVERAGEX(
    FILTER(Trips, Trips[member_casual] = "casual" && Trips[Ride Time (min)] > 0),
    Trips[Ride Time (min)]
)
```
Average ride duration in decimal minutes for casual riders only. Same filter logic as member duration.

---

### Spring Rides
```dax
Spring Rides =
CALCULATE([Total Rides], 'Date'[Season] = "Spring")
```

### Summer Rides
```dax
Summer Rides =
CALCULATE([Total Rides], 'Date'[Season] = "Summer")
```

### Fall Rides
```dax
Fall Rides =
CALCULATE([Total Rides], 'Date'[Season] = "Fall")
```

### Winter Rides
```dax
Winter Rides =
CALCULATE([Total Rides], 'Date'[Season] = "Winter")
```
Seasonal ride counts using the Season column from the Date table. Spring: March–May, Summer: June–August, Fall: September–November, Winter: December–February.

---

### Casual Weekend %
```dax
Casual Weekend % =
DIVIDE(
    CALCULATE([Casual Rides], 'Date'[Is Weekend] = TRUE()),
    [Casual Rides],
    BLANK()
)
```
Proportion of casual rides that occur on weekends. Expected to skew high — a key indicator that casual riders use the service recreationally rather than for commuting.

### Member Weekend %
```dax
Member Weekend % =
DIVIDE(
    CALCULATE([Member Rides], 'Date'[Is Weekend] = TRUE()),
    [Member Rides],
    BLANK()
)
```
Proportion of member rides that occur on weekends. Expected to be lower than casual weekend %, reflecting commuter usage patterns among members.

### Metric Group Measures

These measures work in conjunction with the Metric Groups calculated table to drive the clustered column chart on Page 2. They use SWITCH() to return the appropriate measure value based on the selected metric category, allowing a single clustered chart to display two different percentage metrics side by side with consistent member/casual color coding.

#### Metric Groups Table
```dax
Metric Groups = 
DATATABLE("Metric", STRING, {{"Weekend %"}, {"Round Trip %"}})
```
Calculated table containing two rows used as the X-axis category in the Page 2 clustered column chart. Created via Modeling → New Table in Power BI Desktop.

#### Member % by Metric
```dax
Member % by Metric =
SWITCH(
    SELECTEDVALUE('Metric Groups'[Metric]),
    "Weekend %", [Member Weekend %],
    "Round Trip %", [Round Trip % Member],
    BLANK()
)
```
Returns the appropriate member percentage measure based on the selected metric category from the Metric Groups table. Used as a Y-axis series in the Page 2 clustered column chart. Set color to #1F77B4 in the visual format pane.

#### Casual % by Metric
```dax
Casual % by Metric =
SWITCH(
    SELECTEDVALUE('Metric Groups'[Metric]),
    "Weekend %", [Casual Weekend %],
    "Round Trip %", [Round Trip % Casual],
    BLANK()
)
```
Returns the appropriate casual percentage measure based on the selected metric category from the Metric Groups table. Used as a Y-axis series in the Page 2 clustered column chart. Set color to #FF7F0E in the visual format pane.

## Phase 3 — Bike Type Analysis

Breaks down rideable type by member type to show preferences and usage patterns. Measures are written for classic and electric bike types, which are the only types present in the current dataset. Docked bike measures are included proactively — they will return BLANK() if the type is absent and will automatically populate if docked bikes are introduced in future data.

---

### Classic Bike Rides
```dax
Classic Bike Rides =
CALCULATE([Total Rides], Trips[rideable_type] = "classic_bike")
```
Total rides on classic bikes across all rider types.

```dax
Member Classic Rides =
CALCULATE([Member Rides], Trips[rideable_type] = "classic_bike")
```
Classic bike rides by members only.

```dax
Casual Classic Rides =
CALCULATE([Casual Rides], Trips[rideable_type] = "classic_bike")
```
Classic bike rides by casual riders only.

---

### Electric Bike Rides
```dax
Electric Bike Rides =
CALCULATE([Total Rides], Trips[rideable_type] = "electric_bike")
```
Total rides on electric bikes across all rider types.

```dax
Member Electric Rides =
CALCULATE([Member Rides], Trips[rideable_type] = "electric_bike")
```
Electric bike rides by members only.

```dax
Casual Electric Rides =
CALCULATE([Casual Rides], Trips[rideable_type] = "electric_bike")
```
Electric bike rides by casual riders only.

---

### Docked Bike Rides
```dax
Docked Bike Rides =
CALCULATE([Total Rides], Trips[rideable_type] = "docked_bike")
```
Total rides on docked bikes. Returns BLANK() with current dataset — included for forward compatibility.

```dax
Member Docked Rides =
CALCULATE([Member Rides], Trips[rideable_type] = "docked_bike")
```
Docked bike rides by members only. Returns BLANK() with current dataset.

```dax
Casual Docked Rides =
CALCULATE([Casual Rides], Trips[rideable_type] = "docked_bike")
```
Docked bike rides by casual riders only. Returns BLANK() with current dataset.

---

### Bike Type Mix %
```dax
Classic Bike % =
DIVIDE([Classic Bike Rides], [Total Rides], BLANK())
```
Proportion of all rides on classic bikes.

```dax
Electric Bike % =
DIVIDE([Electric Bike Rides], [Total Rides], BLANK())
```
Proportion of all rides on electric bikes.

```dax
Docked Bike % =
DIVIDE([Docked Bike Rides], [Total Rides], BLANK())
```
Proportion of all rides on docked bikes. Returns BLANK() with current dataset.

## Phase 4 — Station & Geographic Analysis

Analyzes ride origins and destinations to identify popular stations and geographic patterns by rider type. Most insights in this phase are surfaced through visuals (maps using coordinate fields, top station bar charts sliced by member/casual) rather than standalone measures. Note: missing station data is common in this dataset, particularly for electric bikes which can be docked at non-fixed locations.

---

### Station Activity
```dax
Rides with Start Station =
CALCULATE([Total Rides], Trips[start_station_name] <> BLANK())
```
Total rides where a start station name is recorded.

```dax
Rides with End Station =
CALCULATE([Total Rides], Trips[end_station_name] <> BLANK())
```
Total rides where an end station name is recorded.

```dax
Rides Missing Station Data =
[Total Rides] - [Rides with Start Station]
```
Quantifies rides with no start station recorded. Expected to be non-trivial, particularly for electric bike rides.

---

### Member vs Casual Station Usage
```dax
Member Rides with Start Station =
CALCULATE([Member Rides], Trips[start_station_name] <> BLANK())
```
Member rides where a start station name is recorded.

```dax
Casual Rides with Start Station =
CALCULATE([Casual Rides], Trips[start_station_name] <> BLANK())
```
Casual rides where a start station name is recorded.

---

### Round Trips
```dax
Round Trips =
CALCULATE(
    [Total Rides],
    Trips[start_station_name] = Trips[end_station_name]
)
```
Total rides where the start and end station are the same. Indicator of recreational usage.

```dax
Casual Round Trips =
CALCULATE(
    [Casual Rides],
    Trips[start_station_name] = Trips[end_station_name]
)
```
Round trips by casual riders. Expected to be proportionally higher than members, consistent with recreational usage patterns.

```dax
Member Round Trips =
CALCULATE(
    [Member Rides],
    Trips[start_station_name] = Trips[end_station_name]
)
```
Round trips by members. Expected to be proportionally lower, consistent with point-to-point commuter usage.

### Round Trip % Member
```dax
Round Trip % Member =
DIVIDE([Member Round Trips], [Member Rides], BLANK())
```
Proportion of member rides that are round trips. Used in Page 2 clustered bar chart for a fair comparison against casual round trip rate.

### Round Trip % Casual
```dax
Round Trip % Casual =
DIVIDE([Casual Round Trips], [Casual Rides], BLANK())
```
Proportion of casual rides that are round trips. Used in Page 2 clustered bar chart for a fair comparison against member round trip rate.

---

## Phase 5 — Summary KPIs & Final Viz Prep

Ties together behavioral insights from Phases 1–4 with a set of summary measures designed to directly answer the core analysis question: how do casual and member riders use Cyclistic bikes differently? Also includes an illustrative revenue proxy modeled after documented Divvy pricing. See `pricing_model_rationale.md` for full rationale and assumptions.

---

### Revenue Proxy Measures

> **These figures are entirely illustrative.** Cyclistic is a fictional company. Pricing assumptions are modeled after publicly documented Divvy rates. See `pricing_model_rationale.md` for details.

#### Estimated Casual Revenue per Ride
```dax
Estimated Casual Revenue per Ride =
VAR AvgDuration = [Avg Duration Casual]
VAR OverageMinutes = IF(AvgDuration > 30, AvgDuration - 30, 0)
RETURN
    3.30 + (OverageMinutes * 0.18)
```
Calculates estimated per-ride revenue for a casual rider. Applies a $3.30 unlock fee plus $0.18/min for any minutes beyond the 30-minute included threshold.

#### Total Estimated Casual Revenue
```dax
SUMX(
    FILTER(Trips, Trips[member_casual] = "casual" && Trips[Ride Time (min)] > 0),
    VAR OverageMinutes = MAX(Trips[Ride Time (min)] - 30, 0)
    RETURN 3.30 + (OverageMinutes * 0.18)
)
```
Sums estimated casual revenue across all qualifying rides. Excludes rides with zero or blank duration. Overage calculated per ride before summing.

#### Total Estimated Member Overage Revenue
```dax
Total Estimated Member Overage Revenue =
SUMX(
    FILTER(Trips, Trips[member_casual] = "member" && Trips[Ride Time (min)] > 0),
    VAR OverageMinutes = MAX(Trips[Ride Time (min)] - 45, 0)
    RETURN OverageMinutes * 0.18
)
```
Captures variable overage revenue from member rides exceeding the 45-minute included threshold at $0.18/min. Does not include the annual membership fee, which is not amortized per ride in this model.

---

### Behavioral Summary Measures

These measures are designed to directly support the core analysis question and are intended for use in summary visuals and the final presentation.

#### Duration Ratio Casual to Member
```dax
Duration Ratio Casual to Member =
DIVIDE([Avg Duration Casual], [Avg Duration Member], BLANK())
```
Ratio of average casual ride duration to average member ride duration. Values above 1 indicate casual riders take longer rides on average. Expected to be meaningfully above 1, consistent with recreational usage patterns.

#### Distance Ratio Casual to Member
```dax
Distance Ratio Casual to Member =
DIVIDE([Avg Ride Distance Casual], [Avg Ride Distance Member], BLANK())
```
Ratio of average casual ride distance to average member ride distance. Compared alongside the duration ratio to assess whether casuals ride longer in time, distance, or both.

#### Weekend Skew Ratio
```dax
Weekend Skew Ratio =
DIVIDE([Casual Weekend %], [Member Weekend %], BLANK())
```
How much more concentrated casual rides are on weekends relative to members. A value of 2 indicates casuals are twice as likely to ride on weekends compared to members. A key indicator of recreational vs. commuter usage patterns.

#### Round Trip Ratio Casual to Member
```dax
Round Trip Ratio Casual to Member =
DIVIDE(
    DIVIDE([Casual Round Trips], [Casual Rides], BLANK()),
    DIVIDE([Member Round Trips], [Member Rides], BLANK()),
    BLANK()
)
```
Compares the proportion of round trips for casual riders vs. members. Expected to be significantly above 1, supporting the conclusion that casual riders use the service recreationally while members use it for point-to-point commuting.

### Fleet Utilization
True concurrent ride calculation (peak bikes in use simultaneously) requires interval overlap analysis that is computationally impractical in DAX. The Ride Start Hour column combined with day-of-week from the Date table serves as a proxy for peak demand periods in Power BI visuals. Full concurrency analysis is deferred to the R and Python phases of this project.

### Known Limitation — Unique Rider IDs
This dataset does not include unique rider identifiers. As a result the following analyses cannot be performed in this project:

- Total unique casual rider count
- Repeat ride frequency per rider
- Conversion rate modeling (estimating revenue impact of casual-to-member conversion)

A what-if analysis estimating revenue uplift from casual rider conversion would typically accompany the Phase 5 revenue measures. This has been intentionally omitted due to the methodological limitations described above. The omission is documented on the Revenue Opportunity report page. This analysis is flagged as a recommended next step should rider-level data become available.

---

*Phase 5 completes the DAX measure library for the Cyclistic Power BI analysis. Additional documentation for R and Python analysis phases will be maintained in separate files.*

### Annotation Measures

Dynamic text measures that generate descriptive sentences for use in Card visuals alongside behavioral ratio cards. Values update automatically when slicers are adjusted.

#### Annotation Duration Ratio
```dax
Annotation Duration Ratio =
VAR Ratio = [Duration Ratio Casual to Member]
RETURN
    "Casual riders take rides " & FORMAT(Ratio, "0.00") & "x longer on average than members"
```

#### Annotation Weekend Skew
```dax
Annotation Weekend Skew =
VAR Ratio = [Weekend Skew Ratio]
RETURN
    "Casual riders are " & FORMAT(Ratio, "0.00") & "x more likely to ride on weekends than members"
```

#### Annotation Round Trip Ratio
```dax
Annotation Round Trip Ratio =
VAR Ratio = [Round Trip Ratio Casual to Member]
RETURN
    "Casual riders return to their starting station " & FORMAT(Ratio, "0.00") & "x more often than members"
```

#### Annotation Distance Ratio
```dax
Annotation Distance Ratio =
VAR Ratio = [Distance Ratio Casual to Member]
RETURN
    "Casual riders cover " & FORMAT(Ratio, "0.00") & "x the distance per ride compared to members"
```

### Annotation Pace Insight
```dax
Annotation Pace Insight =
VAR DurationRatio = [Duration Ratio Casual to Member]
VAR DistanceRatio = [Distance Ratio Casual to Member]
VAR DurationPct = FORMAT((DurationRatio - 1) * 100, "0") & "%"
VAR DistancePct = FORMAT((DistanceRatio - 1) * 100, "0") & "%"
RETURN
    "Casual riders take " & DurationPct & " longer rides but cover only " & DistancePct & " more distance — suggesting a more leisurely pace than members. See the Ride Behavior page for more analysis."
```
### Annotation Duration Card Callout
```dax
Annotation Duration Card Callout =
VAR DurationRatio = [Duration Ratio Casual to Member]
VAR DurationPct = FORMAT((DurationRatio - 1) * 100, "0")
RETURN
    "Casual riders average " & DurationPct & "% longer rides than members"
```
Dynamic text callout displayed beneath the duration card pair on Page 2. Updates automatically when slicers are adjusted.

### Annotation Distance Card Callout
```dax
Annotation Distance Card Callout =
VAR DistanceRatio = [Distance Ratio Casual to Member]
VAR DistancePct = FORMAT((DistanceRatio - 1) * 100, "0")
RETURN
    IF(
        DistanceRatio >= 1,
        "Casual riders cover " & DistancePct & "% more distance per ride than members",
        "Casual riders cover " & FORMAT((1 - DistanceRatio) * 100, "0") & "% less distance per ride than members"
    )
```
Dynamic text callout displayed beneath the distance card pair on Page 2. Handles both directions — if casual riders cover more distance it says "more", if less it says "less". Updates automatically when slicers are adjusted.

### Annotation Page 2 Pace Insight
```dax
Annotation Page 2 Pace Insight =
VAR DurationRatio = [Duration Ratio Casual to Member]
VAR DistanceRatio = [Distance Ratio Casual to Member]
VAR DurationPct = FORMAT((DurationRatio - 1) * 100, "0")
VAR DistancePct = FORMAT(ABS(DistanceRatio - 1) * 100, "0")
VAR DistanceDirection = IF(DistanceRatio >= 1, "more", "less")
RETURN
    "Casual riders take " & DurationPct & "% longer rides but cover only " & DistancePct & "% " & DistanceDirection & " distance than members. This suggests casual riders move at a more leisurely pace — prioritizing the experience of riding over reaching a destination efficiently."
```
Fuller pace insight callout displayed at the bottom of Page 2 spanning the full canvas width. Connects the duration and distance findings into a single interpretive conclusion. Updates automatically when slicers are adjusted. Style as Segoe UI italic, 11pt, #666666, no border, no background.

### Display Unit Measures

Simple text measures used as Category/Details field in Card visuals to display unit labels alongside numeric values. Keeps underlying measures numeric and available for calculations while providing unit context in the visual. Place in the Annotations display folder in Power BI Desktop.

#### Unit Duration
```dax
Unit Duration = "min"
```
Displays "min" as the unit label in card visuals showing ride duration measures. Drop into the Category or Details field of the Avg Duration Member and Avg Duration Casual card visuals.

#### Unit Distance
```dax
Unit Distance = "mi"
```
Displays "mi" as the unit label in card visuals showing ride distance measures. Drop into the Category or Details field of the Avg Ride Distance Member and Avg Ride Distance Casual card visuals.

### Display Measures — Card Visuals

Text-formatted versions of numeric measures for use in Card visuals on Page 2. Each wraps the underlying numeric measure in a FORMAT() call and appends the appropriate unit string. The original numeric measures remain untouched and available for calculations. Place all four in the Annotations display folder in Power BI Desktop.

#### Avg Duration Member Display
```dax
Avg Duration Member Display =
FORMAT([Avg Duration Member], "0.0") & " min"
```
Text-formatted version of Avg Duration Member for use in the Page 2 duration card pair. Displays to one decimal place with "min" unit suffix.

#### Avg Duration Casual Display
```dax
Avg Duration Casual Display =
FORMAT([Avg Duration Casual], "0.0") & " min"
```
Text-formatted version of Avg Duration Casual for use in the Page 2 duration card pair. Displays to one decimal place with "min" unit suffix.

#### Avg Ride Distance Member Display
```dax
Avg Ride Distance Member Display =
FORMAT([Avg Ride Distance Member], "0.00") & " mi"
```
Text-formatted version of Avg Ride Distance Member for use in the Page 2 distance card pair. Displays to two decimal places with "mi" unit suffix.

#### Avg Ride Distance Casual Display
```dax
Avg Ride Distance Casual Display =
FORMAT([Avg Ride Distance Casual], "0.00") & " mi"
```
Text-formatted version of Avg Ride Distance Casual for use in the Page 2 distance card pair. Displays to two decimal places with "mi" unit suffix.

*Place these measures in the Annotations display folder in Power BI Desktop.*