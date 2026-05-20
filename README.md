# Cyclistic Bike-Share Case Study
### Google Data Analytics Certification Capstone Project

This case study analyzes 5,620,544 rides from Cyclistic, a fictional Chicago bike-share company, to answer one business question: **how do annual members and casual riders use the bikes differently, and how can that difference be used to convert casual riders into members?**

The analysis is implemented across **five tools** — Power BI, SQL Server + SSIS, DuckDB, R, and Python (pandas + Polars) — with all results cross-validated to confirm consistency. AI assistance through Claude (Anthropic) is incorporated as part of the documented workflow, reflecting how modern analysts collaborate with AI tools in practice.

---

## What Makes This Project Different

Most Cyclistic capstone submissions run the standard analysis and report the expected numbers. This one goes further in three ways.

**1. Genuine discoveries — not just reported metrics.**
Several findings in this project emerged from the data itself rather than being assumed going in:

- **E-bikes have onboard GPS hardware** — inferred entirely from data structure. Classic bikes have 0% missing station names. Electric bikes have ~32% missing. But 100% of those e-bike rides without a station name still have GPS coordinates. The only way coordinates can exist without a station is if the bike itself is reporting location. This was not background knowledge — it was reasoned from the shape of the data.
- **Shedd Aquarium: 81.8% casual** — the single starkest example of the leisure-use pattern. Fewer than 1 in 5 rides from Shedd Aquarium are from members. Every station in the casual top 10 is a lakefront tourist or leisure destination; every station in the member top 10 is an urban transit hub. Zero overlap between the two lists.
- **DAX BLANK() vs SQL NULL semantics** — Power BI's DAX treats BLANK() = BLANK() as TRUE. SQL's three-valued logic treats NULL = NULL as UNKNOWN. This caused the round-trip metric to diverge between tools until the root cause was diagnosed, a targeted diagnostic query was written, and the SQL was corrected to replicate DAX behavior. This is the kind of cross-tool rigor that separates careful analysis from query output.
- **A retired bike type found in historical data** — `docked_bike` appeared in 2022–2023 Divvy data (3.1% of rides) but is completely absent from 2025–2026. The ETL was designed to handle unknown bike types for exactly this reason — and the DuckDB scooter experiment confirmed it.

**2. A sharper conversion recommendation.**
The standard recommendation is "convert casual riders to members." This analysis identifies *which* casual riders to target. Casual riders are not a monolith:

- **Leisure/tourist casuals** — riding from Shedd Aquarium and Navy Pier on weekend afternoons. Low conversion probability; annual membership makes no economic sense for occasional visitors.
- **Commuter-pattern casuals** — riding during weekday peak hours (7–9 AM, 4–6 PM) from stations that overlap with member corridors. Already using the bike as transportation. High conversion probability; they have a direct financial incentive to switch from pay-per-minute to annual flat rate.

A targeted campaign aimed at commuter-pattern casuals yields significantly higher revenue per marketing dollar than a broad casual-rider campaign.

**3. Tool breadth with purpose — including a real performance benchmark.**
Five tools isn't five ways to do the same thing. Each one has a specific reason to exist. The Python module runs the same 13 analyses in both pandas and Polars on the same 5.6M row dataset on the same hardware, producing a real, reproducible performance comparison:

| Metric | pandas | Polars | Speedup |
|--------|--------|--------|---------|
| Cold CSV load (5.6M rows) | ~24s | ~17s | **1.4×** |
| Full 13-script suite | 333s | 95s | **3.5×** |

*Test environment: AMD Ryzen 5 7520U (4-core, 2.80 GHz), 16 GB RAM, Samsung SSD, Windows 11*

---

## The Business Question

**How do annual members and casual riders use Cyclistic bikes differently?**

Understanding this behavioral distinction is the foundation for a targeted marketing strategy to convert casual riders into annual members — the goal identified by Cyclistic's director of marketing.

---

## Key Findings

| # | Finding | Evidence |
|---|---------|----------|
| 1 | Members commute; casuals leisure ride | Dual peaks at 8 AM / 5 PM for members; broad midday curve for casuals |
| 2 | Casual rides are 1.82× longer in duration | Only 1.03× farther in distance — leisurely pace, not longer routes |
| 3 | Casuals ride 1.61× more on weekends | Members are consistent across the week — integrated into daily routine |
| 4 | Zero overlap between top 10 station lists | Members: transit hubs. Casuals: lakefront tourism. Entirely different places. |
| 5 | Shedd Aquarium: 81.8% casual | Fewer than 1 in 5 rides there are from members — starkest single example |
| 6 | Casual ridership is highly seasonal | 42.7% of summer rides are casual; drops to 19.6% in winter |
| 7 | No bike-type preference difference (null finding) | ~65% electric for both groups — campaign should focus on behavior, not equipment |
| 8 | E-bikes have onboard GPS (inferred from data) | 100% of e-bikes missing station names still have GPS coordinates |
| 9 | Conversion opportunity: 5%–25% → \$12M–\$60M/yr | At \$119.88/yr × 2,015,499 casual riders |
| 10 | Targeted campaign outperforms broad campaign | Commuter-pattern casuals: higher probability, lower cost per conversion |
| 11 | Peak fleet: 1,199 simultaneous rides | Oct 12, 2025 at noon Sunday — minimum fleet size floor |
| 12 | Polars is 3.5× faster than pandas (same analysis) | Rust engine, parallel execution, lazy evaluation — quantified on real hardware |
| 13 | docked_bike retired between 2023 and 2025 | Found in historical DuckDB analysis — absent from current dataset entirely |

---

## Tools & Technologies

| Tool | Purpose | Status |
|------|---------|--------|
| **Power BI** | Data modeling, DAX calculations, and interactive dashboards | ✅ Complete |
| **SQL Server + SSIS** | Enterprise ETL pipeline and 14 T-SQL analytical queries | ✅ Complete |
| **DuckDB** | Lightweight SQL directly against CSV files — no database required | ✅ Complete |
| **R** | Statistical analysis, visualization, and Welch's t-test validation | ✅ Complete |
| **Python (pandas + Polars)** | 13 analyses × 2 libraries + performance benchmark + Jupyter notebook | ✅ Complete |
| **Claude (Anthropic)** | AI-assisted analysis and documentation throughout | Throughout |

---

## Data Source

12 months of Cyclistic (Divvy) historical trip data provided by Motivate International Inc. under the [Divvy Data License Agreement](https://divvybikes.com/data-license-agreement).

The full dataset is not included in this repository due to file size. A sample file and full source details are available in the `/Data` folder.

**Dataset period:** April 2025 – March 2026
**Total rides:** 5,620,544 (after ETL cleaning — 2,736 rows excluded from raw count of 5,623,280 due to missing critical fields)
**Fields:** ride_id, rideable_type, started_at, ended_at, start/end station names and IDs, start/end coordinates, member_casual

---

## Repository Structure

```
/
├── README.md
├── LICENSE
│
├── /Data
│   └── data_sources.md              — dataset description, source link, field definitions
│
├── /Docs
│   ├── transformations_powerbi.md   — all DAX measures and calculated columns
│   ├── report_design_brief.md       — Power BI report design decisions
│   └── pricing_model_rationale.md   — illustrative revenue model rationale
│
├── /PowerBI                         ✅ Complete
│   ├── README.md
│   ├── measure_folder_structure.md
│   └── CyclistCaseStudy.pbip
│
├── /SQLServer                       ✅ Complete
│   ├── README.md
│   ├── etl_process.md
│   ├── cross_validation.md          — authoritative cross-tool reference values
│   ├── schema.md
│   ├── query_runner.py
│   ├── /queries                     — 14 analytical T-SQL queries
│   ├── /schema                      — DDL scripts
│   └── /SSIS                        — LoadTrips.dtsx ETL package
│
├── /DuckDB                          ✅ Complete
│   ├── README.md
│   ├── 01_hello_duckdb.py through 11_revenue_proxy.py
│   └── 12_scooter_experiment.py     — discovered docked_bike in historical data
│
├── /R                               ✅ Complete
│   ├── README.md
│   ├── 00_run_all.R
│   ├── 01_hello_r.R through 11_revenue_proxy.R
│   └── 12_statistical_tests.R       — Welch's t-test + chi-square (R-exclusive)
│
├── /Python                          ✅ Complete
│   ├── /pandas
│   │   ├── utils.py                 — shared loader (DRY pattern)
│   │   ├── 00_run_all.py            — 12/12 pass, ~333s total
│   │   ├── 01_hello_pandas.py through 12_peak_concurrent_rides.py
│   │   ├── generate_notebook.py
│   │   ├── cyclistic_analysis.ipynb — Jupyter notebook with 10 charts
│   │   └── cyclistic_analysis.html  — standalone HTML export (no Jupyter needed)
│   └── /polars
│       ├── utils.py                 — lazy scan_csv loader
│       ├── 00_run_all.py            — 13/13 pass, ~95s total (3.5× faster than pandas)
│       ├── 01_hello_polars.py through 12_peak_concurrent_rides.py
│       └── 13_commuter_casual_segmentation.py  — unique: identifies high-conversion casual riders
│
└── /Visuals
    ├── /PowerBI                     — 5 dashboard page screenshots
    ├── /R                           — 10 ggplot2 chart exports
    └── /Python                      — 10 matplotlib chart exports (from Jupyter notebook)
```

---

## Power BI Report Pages

| Page | Title | Key Visual |
|------|-------|------------|
| 1 | Casual and Member Riders Use Cyclistic in Fundamentally Different Ways | Behavioral ratio cards with dynamic annotations |
| 2 | Casual Riders Take Longer, More Leisurely Rides Than Members | Duration and distance card pairs, weekend/round trip chart |
| 3 | Members Ride on Schedule — Casuals Ride for Leisure | Hour-of-day distribution chart showing commuter spikes |
| 4 | Members and Casuals Favor Different Bikes and Different Places | Map of ride start locations, top 10 station charts |
| 5 | Converting Casual Riders to Members Represents Significant Revenue Potential | Illustrative revenue chart and conversion sensitivity table |

---

## Important Notes

- **Cyclistic is a fictional company.** The underlying data is real Divvy trip data provided by Motivate International Inc.
- **Revenue figures are entirely illustrative.** Pricing is modeled after publicly documented Divvy rates (~2025). See `/Docs/pricing_model_rationale.md` for full rationale.
- **Unique rider IDs are not available** in this dataset — individual ride frequency cannot be determined and conversion rate modeling uses aggregate estimates only.
- **The 2,736 row difference** between raw CSV count (5,623,280) and SQL Server count (5,620,544) is intentional — ETL filtered rows missing critical fields. Power BI loaded raw CSVs directly; percentage metrics match exactly since proportions are unaffected.
- This project incorporates AI assistance (Claude by Anthropic) as part of the analytical workflow, reflecting how modern analysts collaborate with AI tools in practice.
