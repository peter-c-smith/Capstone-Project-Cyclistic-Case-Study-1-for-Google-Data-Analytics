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

*Additional transformations will be added as the analysis progresses.*