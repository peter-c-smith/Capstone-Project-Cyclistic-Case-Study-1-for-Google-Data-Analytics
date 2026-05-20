# R Analysis
## Cyclistic Bike-Share Case Study

This module demonstrates statistical analysis and visualization using R with the tidyverse ecosystem. All 11 core analytical queries replicate the SQL Server and DuckDB findings exactly, and a 12th script adds inferential statistics — formal hypothesis testing that no other tool in this portfolio performs.

**Status:** ✅ Complete

---

## Why R

R with the tidyverse occupies a different position in the analyst's toolkit than SQL Server or DuckDB. Where SQL excels at querying structured data and DuckDB at lightweight CSV exploration, R is purpose-built for statistical analysis and publication-quality visualization. Key differences demonstrated in this module:

| Capability | SQL Server | DuckDB | R |
|---|---|---|---|
| Setup | Server + SSMS | `pip install duckdb` | `install.packages("tidyverse")` |
| Data loading | Full ETL pipeline | `read_csv_auto('*.csv')` | `read_csv(list.files(...))` |
| Visualization | None (Power BI separate) | None | ggplot2 — full grammar of graphics |
| Statistical tests | None | None | t-tests, chi-square, and more |
| Best for | Production ETL, concurrent access | Ad-hoc CSV exploration | Statistical analysis, visualization |

All 11 core queries produced results consistent with SQL Server and DuckDB, confirming findings are robust across tools.

---

## Scripts

| Script | Description |
|---|---|
| `01_hello_r.R` | Sanity check — reads all 12 CSVs, confirms 5,620,544 rows match SQL Server and DuckDB |
| `02_core_ride_counts.R` | Member vs casual split (64.1% / 35.9%) — first ggplot2 bar chart |
| `03_avg_duration_distance.R` | Casual riders 1.82x longer duration, similar distance — faceted bar chart |
| `04_weekend_weekday.R` | Casual riders 1.61x more likely to ride on weekends — grouped bar chart |
| `05_round_trips.R` | Casual round trip rate 1.63x higher — NULL semantics handled with coalesce() |
| `06_seasonal_breakdown.R` | Casual ridership peaks at 43% in summer, drops to 18% in winter — line chart |
| `07_bike_type_mix.R` | Null finding: bike type preference nearly identical (~65% electric) — stacked 100% bar |
| `08_top_stations.R` | Zero overlap between member and casual top 10 station lists — horizontal faceted bar |
| `09_hourly_distribution.R` | Member dual peak at 8 AM / 5 PM vs casual single afternoon peak — faceted area chart |
| `10_missing_station_data.R` | E-bike GPS inference: 100% of missing-station e-bike rides still have coordinates |
| `11_revenue_proxy.R` | Illustrative revenue model + conversion sensitivity table (5%–25% scenarios) |
| `12_statistical_tests.R` | **R-exclusive** — Welch's t-test and chi-square tests validating all key findings |

---

## Statistical Validation (Script 12)

This is the R module's unique contribution to the portfolio. All three key behavioral findings were formally tested using hypothesis tests on the full 5,620,544-row dataset (t-test used a reproducible 100,000-row sample; chi-square tests used full data).

| Finding | Test | Result | Conclusion |
|---|---|---|---|
| Casual riders take longer rides | Welch's t-test | t = 22.06, p < 2.2e-16 | Significant — 95% CI: 9.1 to 10.8 min gap |
| Casual riders skew toward weekends | Chi-square | X² = 127,344, p < 2.2e-16 | Significant — not due to chance |
| Casual riders take more round trips | Chi-square | X² = 53,954, p < 2.2e-16 | Significant — not due to chance |

**All three findings are statistically significant at p < 0.001.** The behavioral differences between casual and member riders are real and consistent — not sampling artefacts.

---

## Key R Syntax Differences from SQL Server / DuckDB

| Feature | SQL Server | DuckDB | R (tidyverse) |
|---|---|---|---|
| Read CSV files | BULK INSERT / SSIS | `read_csv_auto('*.csv')` | `read_csv(list.files(...))` |
| Filter rows | `WHERE` | `WHERE` | `filter()` |
| Add columns | Calculated column / `SELECT col AS` | `SELECT col AS` | `mutate()` |
| Group & aggregate | `GROUP BY` + `COUNT/SUM` | same | `group_by()` + `summarise()` |
| Top N rows | `SELECT TOP 10` | `LIMIT 10` | `slice_max(col, n=10)` |
| NULL check | `IS NULL` | `IS NULL` | `is.na()` |
| NULL replacement | `ISNULL(col, '')` | `COALESCE(col, '')` | `coalesce(col, "")` |
| Day of week | `DATEPART(WEEKDAY, col)` 1=Sun | `DAYOFWEEK(col)` 0=Sun | `wday(col)` 1=Sun |
| Hour extraction | `DATEPART(HOUR, col)` | `HOUR(col)` | `hour(col)` |
| Duration in minutes | `DATEDIFF(minute, start, end)` | `epoch(end-start)/60` | `as.numeric(difftime(end, start, units="mins"))` |
| Conditional logic | `CASE WHEN` | `CASE WHEN` | `case_when()` or `if_else()` |
| Multi-condition filter | `IN (1, 7)` | `IN (0, 6)` | `%in% c(1, 7)` |

---

## Notable Findings and Data Quality Notes

### Rides Over 24 Hours
Script `03_avg_duration_distance.R` identified **5,779 rides (0.103%)** lasting more than 24 hours. These almost certainly represent bikes that were not properly docked or trips where the rider forgot to end the session. Notably, casual riders account for **4,771 of these (82.5%)** despite being only 35.9% of total riders — a strong signal that casual riders are far more likely to leave a bike checked out accidentally.

### Round Trip Distance Anomaly
Haversine distance (straight-line GPS) for round trips returns ~0 miles when a rider returns to the same station. Because casual riders complete round trips at 1.63x the rate of members, their average Haversine distance (1.34 mi) is slightly lower than members (1.39 mi). This is a methodology note, not a contradiction — the core finding (duration much longer, distance nearly the same) holds.

### E-Bike GPS Inference
Every one of the 1,194,952 e-bike rides missing a station name still has GPS coordinates (100%). Classic bikes have zero missing start station names. This confirms that e-bikes have onboard GPS hardware and report their location independently of any dock, while classic bikes are located only when physically docked at a station sensor.

### March 2025 Data Edge Case
The seasonal chart shows a small number of rides from March 2025, even though the dataset period is April 2025–March 2026. This is because a handful of rides that started in late March 2025 are included in the April 2025 Divvy CSV file. Analytically insignificant but worth noting.

---

## Running the Scripts

### Prerequisites
```r
install.packages(c("tidyverse", "skimr", "scales"))
```
R 4.1+ required (for the native pipe operator `|>`).

### Data
Scripts expect the 12 monthly Divvy CSV files in:
```
../Data/DATAfile_Consolidated/*.csv
```
Paths are resolved relative to the script file — scripts run correctly from any working directory when opened in RStudio.

### Execution
Open each script in RStudio and run with **Ctrl+Shift+Enter**. Charts are saved automatically to `../Visuals/R/`.

Scripts 01–11 complete in 20–60 seconds each. Script 12 may take 1–2 minutes (chi-square tests on 5.6M rows).

---

## Visuals

All charts saved to `/Visuals/R/`:

| File | Chart |
|---|---|
| `02_core_ride_counts.png` | Member vs casual ride counts |
| `03_avg_duration_distance.png` | Average duration and distance comparison |
| `04_weekend_weekday.png` | Weekend vs weekday split |
| `05_round_trips.png` | Round trip rates |
| `06_seasonal_breakdown.png` | Casual share by month (line chart) |
| `07_bike_type_mix.png` | Bike type preference (stacked 100%) |
| `08_top_stations.png` | Top 10 stations — member and casual |
| `09_hourly_distribution.png` | Hour-of-day distribution (area chart) |
| `10_missing_station_data.png` | Missing station % by bike type |
| `11_revenue_proxy.png` | Conversion sensitivity revenue chart |

---

## Cross-Tool Validation

All 11 core queries validated against SQL Server and DuckDB results. Results match, with the same `coalesce()`/`ISNULL()` NULL semantics handling required to replicate Power BI's `BLANK() = BLANK()` behavior in the round trip query.

---

*Data source: [Divvy Trip Data](https://divvybikes.com/system-data) provided by Motivate International Inc. under the [Divvy Data License Agreement](https://divvybikes.com/data-license-agreement).*
