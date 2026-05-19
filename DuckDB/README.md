# DuckDB Analysis
## Cyclistic Bike-Share Case Study

This module demonstrates analytical SQL using DuckDB — a modern, lightweight in-process analytical database that queries CSV files directly without requiring a server, ETL pipeline, or data import step. All scripts run against the raw Divvy CSV files and produce results identical to the SQL Server module, demonstrating cross-tool consistency.

**Status:** ✅ Complete

---

## Why DuckDB

DuckDB occupies a different position in the analyst's toolkit than SQL Server. Where SQL Server is optimized for production workloads, concurrent access, and enterprise ETL, DuckDB is optimized for a single analyst running fast ad-hoc queries against flat files. Key differences demonstrated in this module:

| Capability | SQL Server | DuckDB |
|---|---|---|
| Setup required | Server install, SSMS, SSIS | `pip install duckdb` |
| Data loading | Full ETL pipeline (LoadTrips.dtsx) | None — reads CSVs directly |
| Query language | T-SQL | Standard SQL (very similar) |
| Best for | Production, concurrent access, ETL | Ad-hoc exploration, CSV analysis |
| Portability | Requires server connection | Runs anywhere Python runs |

Both tools produced identical analytical results across all 11 core queries — confirming the findings are robust and not artifacts of any one tool's implementation.

---

## Scripts

| Script | Description |
|---|---|
| `01_hello_duckdb.py` | Sanity check — reads all 12 CSVs at once, confirms row counts match SQL Server |
| `02_core_ride_counts.py` | Member vs casual ride distribution (64.1% / 35.9%) |
| `03_avg_duration_distance.py` | Casual riders take 1.82x longer rides, only 1.03x farther — leisure, not commuting |
| `04_weekend_weekday.py` | Casual riders 1.61x more likely to ride on weekends |
| `05_round_trips.py` | Casual round trip rate 1.63x higher than members |
| `06_seasonal_breakdown.py` | Casual ridership peaks at 42.7% in summer, drops to 19.6% in winter |
| `07_bike_type_mix.py` | Null finding: bike type preference nearly identical (~65% electric) for both groups |
| `08_top_stations.py` | Zero overlap between member and casual top 10 station lists |
| `09_hourly_distribution.py` | Member dual peak at 8 AM / 5 PM vs casual single afternoon peak (commute vs leisure) |
| `10_missing_station_data.py` | E-bike GPS inference: 100% of missing-station e-bike rides still have coordinates |
| `11_revenue_proxy.py` | Illustrative revenue model + conversion sensitivity table (5%–25% scenarios) |
| `12_scooter_experiment.py` | Ad-hoc cross-year exploration — discovered `docked_bike` type retired between 2023–2025 |

---

## Key DuckDB Syntax Differences from SQL Server

| Feature | SQL Server | DuckDB |
|---|---|---|
| Read CSV files | `BULK INSERT` / SSIS | `read_csv_auto('*.csv')` |
| Conditional count | `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` | `COUNT(*) FILTER (WHERE ...)` |
| Top N rows | `SELECT TOP 10` | `LIMIT 10` |
| Hour extraction | `DATEPART(HOUR, col)` | `HOUR(col)` |
| Day of week | `DATEPART(WEEKDAY, col)` 1=Sun, 7=Sat | `DAYOFWEEK(col)` 0=Sun, 6=Sat |
| Timestamp duration | `DATEDIFF(minute, start, end)` | `epoch(end - start) / 60.0` |
| Timestamp format | `FORMAT(col, 'yyyy-MM')` | `strftime(col, '%Y-%m')` |
| NULL replacement | `ISNULL(col, '')` | `COALESCE(col, '')` |

---

## Notable Findings from This Module

### The docked_bike Discovery
Script `12_scooter_experiment.py` was written to search for `electric_scooter` in older Divvy data. Scooters were not found — but a third bike type, `docked_bike`, appeared in 2022 (3.1% of rides) and 2023 (1.5% of rides) before disappearing entirely from the 2025–2026 dataset. This confirms the ETL's design to handle unknown bike types beyond classic and electric was warranted, and illustrates how DuckDB enables rapid discovery across datasets that have never been loaded into a database.

### E-Bike GPS Inference
Every one of the 1,194,952 e-bike rides missing a station name still has GPS coordinates (100.0%). Classic bikes have zero missing station names. This data structure reveals that e-bikes have onboard GPS hardware and report location independently of any dock — classic bikes are located only when physically docked at a station sensor.

### The Null Finding on Bike Type
Members and casual riders use electric bikes at nearly identical rates (64.7% vs 66.8%). A two-percentage-point difference across 5.6 million rides is not a behavioral signal. Bike type does not distinguish the two groups and is not a marketing conversion lever. Reporting this null finding honestly is as important as reporting the significant findings.

---

## Running the Scripts

### Prerequisites
```
pip install duckdb
```
Python 3.8+ required. No other dependencies.

### Data
Scripts expect the 12 monthly Divvy CSV files in:
```
../Data/DATAfile_Consolidated/*.csv
```
All paths are resolved relative to the script file location — scripts run correctly from any terminal directory.

### Execution
```
python 01_hello_duckdb.py
python 02_core_ride_counts.py
# ... and so on
```
Scripts 01–11 run against local CSVs and complete in seconds. Script 12 downloads ~400MB of external data and requires an internet connection — allow 2–3 minutes.

---

## Cross-Tool Validation

All 11 core queries were validated against SQL Server results. Results match exactly, with the same deliberate handling of the `COALESCE`/`ISNULL` NULL semantics required to replicate Power BI's `BLANK() = BLANK()` behavior in the round trip query. See `SQLServer/cross_validation.md` for full validation documentation.

---

*Data source: [Divvy Trip Data](https://divvybikes.com/system-data) provided by Motivate International Inc. under the [Divvy Data License Agreement](https://divvybikes.com/data-license-agreement).*
