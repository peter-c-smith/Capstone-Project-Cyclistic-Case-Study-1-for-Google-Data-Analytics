"""
09_hourly_distribution.py
-------------------------
How does ride volume vary by hour of day for members vs casual riders?

Expected output (matching SQL Server, DuckDB, R, and pandas):
  Member peaks: 08:00 and 17:00 (commute pattern)
  Casual peak:  broad midday curve (leisure pattern)

Polars notes:
  - .dt.hour() extracts the hour as an integer (0-23) — same as pandas.
  - After group_by + pivot, percentage within group requires dividing
    each hour's count by the column sum, done with a second with_columns()
    pass using pl.col() / pl.col().sum().
"""

import polars as pl
from utils import load_trips

trips = load_trips()

trips = trips.with_columns(
    pl.col("started_at").dt.hour().alias("hour")
)

hourly = (
    trips
    .group_by(["hour", "member_casual"])
    .agg(pl.len().alias("rides"))
    .pivot(on="member_casual", index="hour", values="rides")
    .fill_null(0)
    .with_columns(
        (pl.col("member") / pl.col("member").sum() * 100).alias("member_pct"),
        (pl.col("casual") / pl.col("casual").sum() * 100).alias("casual_pct"),
    )
    .sort("hour")
)

print("=" * 70)
print("  Hourly Ride Distribution  (% of each group's total rides)")
print("=" * 70)
print(f"  {'Hr':>4}  {'Member%':>8}  {'Casual%':>8}  "
      f"{'Member bar':<20}  {'Casual bar'}")
print(f"  {'-'*68}")

max_m = hourly["member_pct"].max()
max_c = hourly["casual_pct"].max()

for row in hourly.iter_rows(named=True):
    m_bar = "█" * int(row["member_pct"] / max_m * 20)
    c_bar = "█" * int(row["casual_pct"] / max_c * 20)
    print(f"  {row['hour']:02d}:00  {row['member_pct']:>8.1f}%  "
          f"{row['casual_pct']:>8.1f}%  {m_bar:<20}  {c_bar}")

# Validate peaks
member_peak = hourly.sort("member_pct", descending=True).row(0, named=True)
casual_peak = hourly.sort("casual_pct", descending=True).row(0, named=True)

print()
print(f"  Member peak hour:  {member_peak['hour']:02d}:00  "
      f"({'✓' if member_peak['hour'] == 17 else '~'})")
print(f"  Casual peak hour:  {casual_peak['hour']:02d}:00")
print(f"  commute pattern confirmed: "
      f"{'✓' if member_peak['hour'] in [8, 17] else '✗'}")
print("=" * 70)
