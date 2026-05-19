# Cyclistic Bike-Share Case Study
### Google Data Analytics Certification Capstone Project

This case study analyzes data for Cyclistic, a fictional bike-share company, as part of the Google Data Analytics Certification Capstone. Real-world tasks are performed and documented following Google's structured data analytics methodology: Ask, Prepare, Process, Analyze, Share, and Act.

As part of my workflow, I'm incorporating AI assistance through Claude (by Anthropic) to reflect how modern analysts collaborate with AI tools in practice.

---

## The Business Question

**How do annual members and casual riders use Cyclistic bikes differently?**

Understanding this behavioral distinction is the foundation for a targeted marketing strategy to convert casual riders into annual members — the goal identified by Cyclistic's director of marketing.

---

## Key Findings

- **Casual riders take 82% longer rides** than members on average, but cover only 3% more distance — suggesting a more leisurely pace rather than longer routes
- **Casual riders are 1.61x more likely to ride on weekends** than members, who concentrate usage on weekday commuter hours with clear spikes at 8 AM and 5 PM
- **Casual riders return to their starting station 1.63x more often** than members, consistent with recreational rather than point-to-point commuter usage
- **Casual ridership peaks at 42.7% of summer rides**, dropping to just 19.6% in winter — far more seasonal than members who ride year-round
- **Zero overlap** between the member and casual top 10 station lists — casuals concentrate at lakefront tourist destinations (Shedd Aquarium 81.8% casual, Navy Pier, Millennium Park) while members cluster near transit hubs
- **E-bikes have onboard GPS hardware** — inferred from data: 100% of the 1.2M rides missing a station name still have GPS coordinates, while classic bikes have zero missing station names
- **Bike type is not a differentiator** — members and casuals use electric bikes at nearly identical rates (65% vs 67%), confirming that conversion strategy should focus on when and where people ride, not what they ride
- **A retired bike type discovered in historical data** — `docked_bike` appeared in 2022–2023 Divvy data (3.1% of rides) but is absent from the 2025–2026 dataset, revealing fleet evolution not visible in the current data alone

---

## What Makes This Project Different

This capstone is implemented across **five tools** — Power BI, SQL Server + SSIS, DuckDB, R, and Python — allowing direct comparison of how the same analytical tasks are approached in each environment. This structure is intentional and designed to demonstrate tool flexibility relevant to real-world data analyst roles.

---

## Tools & Technologies

| Tool | Purpose | Status |
|------|---------|--------|
| **Power BI** | Data modeling, DAX calculations, and interactive dashboards | ✅ Complete |
| **SQL Server + SSIS** | Enterprise ETL pipeline and T-SQL analytical queries | ✅ Complete |
| **DuckDB** | Lightweight analytical SQL directly against CSV files | ✅ Complete |
| **R** | Statistical analysis, data profiling, and visualization | ⏳ Planned |
| **Python** | Data manipulation using Polars and pandas | ⏳ Planned |
| **Claude (Anthropic)** | AI-assisted analysis and documentation | Throughout |

---

## Data Source

The dataset consists of 12 months of Cyclistic (Divvy) historical trip data provided by Motivate International Inc. under the [Divvy Data License Agreement](https://divvybikes.com/data-license-agreement).

The full dataset is not included in this repository due to file size. A sample file and full source details are available in the `/Data` folder.

**Dataset period:** April 2025 – March 2026
**Total rides:** 5,620,544 (12 months loaded after ETL cleaning — 2,736 rows excluded from raw source count of 5,623,280 due to missing critical fields)
**Fields:** ride_id, rideable_type, started_at, ended_at, start/end station names and IDs, start/end coordinates, member_casual

---

## Repository Structure

```
/
├── README.md
├── LICENSE
├── Important Notes During Process.md
├── Transformation Process Notes.md
├── Original Google Requirement Case Study 1...md
│
├── /Data
│   ├── data_sources.md          — dataset description, source link, field definitions
│   └── sample_data.csv          — one month of data illustrating structure
│
├── /Docs
│   ├── transformations_powerbi.md    — all DAX measures and calculated columns with documentation
│   ├── report_design_brief.md        — Power BI report design decisions, page layouts, color conventions
│   └── pricing_model_rationale.md    — rationale for illustrative revenue model based on Divvy pricing
│
├── /PowerBI                          ✅ Complete
│   ├── measure_folder_structure.md   — all measures organized by display folder
│   └── CyclistCaseStudy.pbip         — Power BI project file
│
├── /SQLServer                        ✅ Complete
│   ├── README.md
│   ├── etl_process.md
│   ├── cross_validation.md
│   ├── schema.md
│   ├── query_runner.py
│   ├── /queries                      — 14 analytical queries (05–14)
│   ├── /schema                       — DDL scripts
│   └── /SSIS                         — LoadTrips.dtsx ETL package
│
├── /DuckDB                           ✅ Complete
│   ├── README.md
│   ├── 01_hello_duckdb.py
│   ├── 02_core_ride_counts.py
│   ├── 03_avg_duration_distance.py
│   ├── 04_weekend_weekday.py
│   ├── 05_round_trips.py
│   ├── 06_seasonal_breakdown.py
│   ├── 07_bike_type_mix.py
│   ├── 08_top_stations.py
│   ├── 09_hourly_distribution.py
│   ├── 10_missing_station_data.py
│   ├── 11_revenue_proxy.py
│   └── 12_scooter_experiment.py
│
├── /R                                ⏳ Planned
│   └── README.md
│
├── /Python                           ⏳ Planned
│   └── README.md
│
└── /Visuals
    └── /PowerBI
        ├── page1_executive_summary.png
        ├── page2_ride_behavior.png
        ├── page3_temporal_patterns.png
        ├── page4_bike_type_station.png
        └── page5_revenue_opportunity.png
```

---

## Power BI Report Pages

| Page | Title | Key Visual |
|------|-------|------------|
| 1 | Casual and Member Riders Use Cyclistic in Fundamentally Different Ways | Behavioral ratio cards with dynamic annotations |
| 2 | Casual Riders Take Longer, More Leisurely Rides Than Members | Duration and distance card pairs, weekend/round trip chart |
| 3 | Members Ride on Schedule — Casuals Ride for Leisure | Hour-of-day distribution chart showing commuter spikes |
| 4 | Members and Casuals Favor Different Bikes and Different Places | Map of ride start locations, top 10 station charts |
| 5 | Converting Casual Riders to Members Represents Significant Revenue Potential | Illustrative seasonal revenue chart and conversion narrative |

---

## Important Notes

- **Cyclistic is a fictional company.** The underlying data is real Divvy trip data provided by Motivate International Inc.
- **Revenue figures on Page 5 are entirely illustrative.** Pricing is modeled after publicly documented Divvy rates. See `/Docs/pricing_model_rationale.md` for full rationale.
- **Unique rider IDs are not available** in this dataset. Conversion rate modeling has been intentionally omitted — see `/Docs/transformations_powerbi.md` Phase 5 for discussion.
- This project uses AI assistance (Claude by Anthropic) as part of the analytical workflow, reflecting modern analyst practice.
