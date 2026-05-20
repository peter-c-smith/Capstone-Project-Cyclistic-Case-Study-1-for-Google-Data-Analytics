"""
06_seasonal_breakdown.py
------------------------
How does ridership vary by season, and do casual riders show stronger
seasonal concentration than members?

Key finding: Casual ridership peaks at 42.7% of summer rides, drops to
19.6% in winter — far more seasonal than members, who ride year-round.

pandas notes:
  - .dt.month extracts the integer month; .dt.to_period('M') produces a
    Period object that formats cleanly as 'YYYY-MM' for the monthly table.
  - pd.cut() bins the month integers into seasons — a clean, readable
    alternative to a long if/elif chain or np.select().
  - pivot_table() reshapes the grouped data for the seasonal rollup,
    producing a member/casual cross-tab in one call.

Season definitions (Northern Hemisphere, matches SQL Server and DuckDB):
  Spring: March, April, May       (months 3, 4, 5)
  Summer: June, July, August      (months 6, 7, 8)
  Fall:   September, October, Nov (months 9, 10, 11)
  Winter: December, January, Feb  (months 12, 1, 2)

Expected output (matching SQL Server, DuckDB, and R):
  Summer casual %: ~42.7% | Winter casual %: ~19.6%
"""

import pandas as pd
from utils import load_trips

trips = load_trips()

# ---------------------------------------------------------------------------
# Month and season columns
# ---------------------------------------------------------------------------

trips["ride_month"] = trips["started_at"].dt.to_period("M").astype(str)
trips["month_int"]  = trips["started_at"].dt.month

# pd.cut() maps month integers to season labels.
# bins and labels must align: month 1-2 = Winter, 3-5 = Spring, etc.
# Month 12 needs special handling — it falls above the cut range, so we
# use np.where / map instead of cut for clarity.

season_map = {
    1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring",  5: "Spring",
    6: "Summer", 7: "Summer",  8: "Summer",
    9: "Fall",  10: "Fall",   11: "Fall",
   12: "Winter"
}
trips["season"] = trips["month_int"].map(season_map)

# ---------------------------------------------------------------------------
# Part 1: Monthly breakdown
# ---------------------------------------------------------------------------

monthly = (
    trips.groupby(["ride_month", "member_casual"])
    .size()
    .unstack(fill_value=0)
)
monthly["total"]      = monthly.sum(axis=1)
monthly["casual_pct"] = monthly["casual"] / monthly["total"] * 100

print("=" * 57)
print("  Monthly Breakdown")
print("=" * 57)
print(f"  {'Month':<10} {'Total':>9} {'Member':>9} {'Casual':>9} {'Casual%':>8}")
print(f"  {'-'*55}")
for month, row in monthly.sort_index().iterrows():
    print(f"  {month:<10} {row['total']:>9,.0f} {row['member']:>9,.0f} "
          f"{row['casual']:>9,.0f} {row['casual_pct']:>7.1f}%")

# ---------------------------------------------------------------------------
# Part 2: Seasonal rollup
# ---------------------------------------------------------------------------

season_order = ["Spring", "Summer", "Fall", "Winter"]

seasonal = (
    trips.groupby(["season", "member_casual"])
    .size()
    .unstack(fill_value=0)
)
seasonal["total"]      = seasonal.sum(axis=1)
seasonal["member_pct"] = seasonal["member"] / seasonal["total"] * 100
seasonal["casual_pct"] = seasonal["casual"] / seasonal["total"] * 100
seasonal = seasonal.reindex(season_order)

print()
print("=" * 57)
print("  Seasonal Rollup")
print("=" * 57)
print(f"  {'Season':<10} {'Total':>9} {'Member':>9} {'Casual':>9} {'Casual%':>8}")
print(f"  {'-'*55}")
for season, row in seasonal.iterrows():
    print(f"  {season:<10} {row['total']:>9,.0f} {row['member']:>9,.0f} "
          f"{row['casual']:>9,.0f} {row['casual_pct']:>7.1f}%")
print("=" * 57)
