"""
09_hourly_distribution.py
-------------------------
At what hours of the day do members and casual riders most frequently
start rides?

Key finding: Members show a dual peak at ~8 AM and ~5 PM — a classic
commute pattern. Casual riders show a single broad afternoon peak
around 3–5 PM — consistent with leisure use.

DuckDB notes:
  - HOUR() extracts the hour from a timestamp (0–23).
    SQL Server used DATEPART(HOUR, started_at) — identical result.
  - CROSS JOIN totals pattern used again (same as 07_bike_type_mix.py)
    to calculate each hour's rides as a % of that rider type's total.
    This makes the two curves directly comparable regardless of the
    overall member/casual volume difference.
  - The output adds a simple ASCII bar chart to make the commute vs
    leisure pattern visible directly in the terminal.

Validates against SQL Server query 09_hourly_distribution.sql
  Expected: member peaks at hours 8 and 17 | casual peak at ~15-17
"""

import duckdb
from pathlib import Path

CSV_PATH = str(Path(__file__).parent.parent / "Data" / "DATAfile_Consolidated" / "*.csv")

con = duckdb.connect()

rows = con.execute(f"""
    WITH HourlyAgg AS (
        SELECT
            HOUR(started_at)                                    AS hour_of_day,
            COUNT(*)                                            AS total_rides,
            COUNT(*) FILTER (WHERE member_casual = 'member')   AS member_rides,
            COUNT(*) FILTER (WHERE member_casual = 'casual')   AS casual_rides
        FROM read_csv_auto('{CSV_PATH}')
        GROUP BY hour_of_day
    ),
    TypeTotals AS (
        SELECT
            SUM(member_rides) AS total_member,
            SUM(casual_rides) AS total_casual
        FROM HourlyAgg
    )
    SELECT
        h.hour_of_day,
        h.total_rides,
        h.member_rides,
        h.casual_rides,
        ROUND(100.0 * h.member_rides / t.total_member, 2) AS member_pct_of_type,
        ROUND(100.0 * h.casual_rides / t.total_casual, 2) AS casual_pct_of_type
    FROM HourlyAgg h
    CROSS JOIN TypeTotals t
    ORDER BY h.hour_of_day
""").fetchall()

# Scale factor for ASCII bars (1 char per 0.2%)
BAR_SCALE = 0.2

print("=" * 72)
print("  Hourly Ride Distribution  (% of each group's total rides)")
print("=" * 72)
print(f"  {'Hr':>3}  {'Member%':>7}  {'Casual%':>7}  {'Member bar':<25} {'Casual bar'}")
print(f"  {'-'*70}")
for row in rows:
    hour, total, member, casual, mem_pct, cas_pct = row
    mem_bar = '█' * int(mem_pct / BAR_SCALE)
    cas_bar = '█' * int(cas_pct / BAR_SCALE)
    label = f"{hour:02d}:00"
    print(f"  {label:>5}  {mem_pct:>7.2f}%  {cas_pct:>7.2f}%  {mem_bar:<25} {cas_bar}")

print("=" * 72)
print("  Members:  dual peaks at 08:00 and 17:00 → commute pattern")
print("  Casuals:  single broad peak at 15:00–17:00 → leisure pattern")
print("=" * 72)
