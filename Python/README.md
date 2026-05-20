# Python Analysis
## Cyclistic Bike-Share Case Study

**Status:** ✅ Complete  
**Dataset:** 5,620,544 rides · Apr 2025 – Mar 2026  
**Hardware:** AMD Ryzen 5 7520U (4-core, 2.80 GHz) · 16 GB RAM · Samsung SSD · Windows 11

This module implements the full Cyclistic analysis twice — once in **pandas** and once in **Polars** — on the identical 5.6M row dataset, then benchmarks them head-to-head. The result is a real, reproducible performance comparison, not a synthetic benchmark.

---

## Performance Benchmark

| Metric | pandas | Polars | Speedup |
|--------|--------|--------|---------|
| Cold CSV load (5.6M rows) | ~24s | ~17s | **1.4×** |
| Full script suite (all analyses) | ~333s | ~95s | **3.5×** |

Polars is faster because it uses a Rust execution engine, parallel multi-core processing, lazy query evaluation, and the Apache Arrow columnar memory format. pandas runs mostly single-threaded on Python's slower runtime.

The warm-cache runs (all scripts after the first) amplify the gap — disk I/O is eliminated, leaving only computation, where Polars' Rust engine outperforms pandas' NumPy stack by a wider margin.

---

## pandas Module — `/pandas`

12 analysis scripts + a Jupyter notebook with 9 inline charts.

### Scripts

| Script | Analysis |
|--------|----------|
| `01_hello_pandas.py` | Sanity check — row count, schema, load timer |
| `02_core_ride_counts.py` | Member vs casual split (64.1% / 35.9%) |
| `03_avg_duration_distance.py` | Duration 1.82× longer, distance only 1.03× farther |
| `04_weekend_weekday.py` | Casuals 1.61× more weekend-heavy than members |
| `05_round_trips.py` | Casuals 1.63× more likely to return to start station |
| `06_seasonal_breakdown.py` | Casual share: 42.7% summer → 19.6% winter |
| `07_bike_type_mix.py` | Null finding — ~65% electric for both groups |
| `08_top_stations.py` | Zero overlap between top-10 member and casual station lists |
| `09_hourly_distribution.py` | Dual commute peaks (8 AM / 5 PM) for members; broad midday for casuals |
| `10_missing_station_data.py` | E-bikes have onboard GPS — 100% of missing-station e-bikes have coordinates |
| `11_revenue_proxy.py` | 5%–25% conversion = \$12M–\$60M annual upside |
| `12_peak_concurrent_rides.py` | Peak fleet utilization: 1,199 simultaneous rides (sweep line algorithm) |

### Jupyter Notebook

`cyclistic_analysis.ipynb` — all 12 analyses with narrative commentary and 10 matplotlib charts, including the casual rider segmentation (Script 13 insight).

`cyclistic_analysis.html` — standalone export; opens in any browser, no Jupyter required.

**Charts saved to `/Visuals/Python/`:**

| File | Chart |
|------|-------|
| `01_rider_split.png` | Pie chart — member/casual proportions |
| `02_duration_distance.png` | Bar pair — avg duration and distance by rider type |
| `03_hourly_distribution.png` | Line chart — hourly ride distribution, commuter peaks annotated |
| `04_weekend_weekday.png` | Grouped bar — weekend vs weekday volume |
| `05_seasonal.png` | Grouped bar — seasonal ride volume with casual % annotations |
| `06_bike_type_mix.png` | Grouped bar — bike type mix (null finding) |
| `07_top_casual_stations.png` | Horizontal bar — top 10 casual start stations |
| `08_revenue_sensitivity.png` | Bar chart — revenue upside at 5%–25% conversion rates |
| `09_peak_concurrent.png` | Dual bar — peak concurrent rides by hour and by day of week |
| `10_casual_segmentation.png` | Pie + grouped bar — commuter vs leisure profile, targeted vs broad revenue |

### Key Technical Notes

- **`utils.py`** — shared CSV loader (DRY pattern). All 12 scripts import `load_trips()` from one place. Change the loader once, all scripts benefit.
- **Vectorized Haversine** — GPS distance computed with NumPy across all 5.6M rows simultaneously. A Python loop would take minutes; the NumPy version takes seconds.
- **Sweep line algorithm** — peak concurrent rides uses +1 / −1 events sorted by timestamp and cumsum'd. Handles 11.2M events efficiently with vectorized pandas operations.
- **`PYTHONIOENCODING=utf-8`** — `00_run_all.py` sets this in the child process environment. Required on Windows to prevent `UnicodeEncodeError` when scripts print `✓` and `█` characters through subprocess capture.

---

## Polars Module — `/polars`

13 analysis scripts — the same 12 as pandas, plus a unique 13th script.

### Scripts

| Script | Analysis |
|--------|----------|
| `01_hello_polars.py` | Sanity check — load timer (cold: ~17s vs pandas ~24s) |
| `02_core_ride_counts.py` | Member vs casual split — cross-validates pandas |
| `03_avg_duration_distance.py` | Duration / distance ratios |
| `04_weekend_weekday.py` | Weekend vs weekday pattern |
| `05_round_trips.py` | Round-trip rate using `fill_null("")` to replicate DAX BLANK() behavior |
| `06_seasonal_breakdown.py` | Seasonal breakdown with `pl.when().then()` chain |
| `07_bike_type_mix.py` | Bike type null finding |
| `08_top_stations.py` | Top stations — zero overlap confirmed |
| `09_hourly_distribution.py` | Hourly distribution — commuter peaks |
| `10_missing_station_data.py` | E-bike onboard GPS inference |
| `11_revenue_proxy.py` | Revenue proxy using vectorized `pl.when().then().otherwise()` |
| `12_peak_concurrent_rides.py` | Sweep line in Polars — parallel sort + `cum_sum()` |
| **`13_commuter_casual_segmentation.py`** | **Unique: identifies high-conversion casual riders** |

### Script 13 — The Unique Analysis

Script 13 is not a port of a pandas script. It originated from an insight that emerged during this project:

**Casual riders are not a monolith.** The standard Cyclistic recommendation is "convert casual riders to members." But the data shows two very different casual rider profiles with very different conversion probabilities:

- **Leisure/tourist casuals** — weekend afternoons at Navy Pier and Shedd Aquarium. Low conversion probability; annual membership makes no economic sense for occasional or tourist riders.
- **Commuter-pattern casuals** — weekday peak hours (7–9 AM, 4–6 PM) from stations in member commuter corridors. Already using the bike as transportation. High conversion probability; they have a direct financial incentive.

**Definition used:** A casual ride meeting all three conditions simultaneously:
1. Weekday (Monday–Friday)
2. Peak hour (7–9 AM or 4–6 PM)
3. Start station in the member top-10 list

This is a conservative floor — many commuter casuals start from non-top-10 stations. The true commuter pool is likely larger.

**Business implication:** A targeted campaign aimed at commuter-pattern casuals achieves a higher conversion rate per marketing dollar than a broad casual campaign — and costs less to reach a smaller, higher-intent audience.

### Key Technical Notes

- **`utils.py`** — uses `pl.scan_csv()` (lazy evaluation) + `try_parse_dates=True`. Polars builds a query plan before executing, allowing the optimizer to push down filters and projections.
- **`pl.when().then().otherwise()`** — replaces pandas `.apply(lambda row: ...)`. Fully vectorized in Rust; no Python loop overhead on 5.6M rows.
- **`.dt.weekday()` numbering** — Polars uses ISO 8601: 1=Monday, 7=Sunday. Different from pandas (0=Monday, 6=Sunday) and DuckDB (0=Sunday, 6=Saturday). Weekend filter: `>= 6`.
- **`replace()` type safety** — Polars enforces type consistency. Integer columns must be cast to `String` before replacing with string labels: `.cast(pl.String).replace({str(k): v ...})`.
- **`is_in()` for list membership** — replaces pandas `.isin()`. Fully vectorized; used in Script 13 to filter rides starting at member top-10 stations.

---

## Cross-Validation

All metrics produced by both modules match the reference values in `/SQLServer/cross_validation.md`. The cross-validation document is the authoritative source of truth for all numerical results.

Key values confirmed across all five tools (Power BI, SQL Server, DuckDB, R, Python):

| Metric | Value |
|--------|-------|
| Total rides | 5,620,544 |
| Member share | 64.1% |
| Casual share | 35.9% |
| Avg casual duration / member | 1.82× |
| Avg casual distance / member | 1.03× |
| Casual weekend/weekday ratio | 1.61× |
| Summer casual share | 42.7% |
| Winter casual share | 19.6% |
| Top casual station casual % | 81.8% (Shedd Aquarium) |
| Station list overlap | 0 (zero) |
| Peak concurrent rides | 1,199 |

---

## Running the Code

**Prerequisites**
```
pip install pandas polars numpy matplotlib nbformat
```

**pandas — run all 12 scripts**
```
cd Python/pandas
python 00_run_all.py
```
Expected: 12/12 pass · ~333s total

**Polars — run all 13 scripts**
```
cd Python/polars
python 00_run_all.py
```
Expected: 13/13 pass · ~95s total · ~3.5× speedup reported

**Regenerate the Jupyter notebook**
```
cd Python/pandas
python generate_notebook.py
jupyter notebook cyclistic_analysis.ipynb
```
Run all cells, then export HTML via File → Download as → HTML.

---

*Analysis by Peter | Cyclistic Capstone | Google Data Analytics Certificate*  
*Python 3.13 · pandas 2.3 · Polars 1.40 · matplotlib · NumPy*
