"""
04_weekend_weekday.py
---------------------
Do casual riders concentrate their usage on weekends more than members?

Key finding: Casual riders are 1.61x more likely to ride on weekends —
strong evidence of leisure use vs. member commuting patterns.

pandas notes:
  - .dt.dayofweek returns 0=Monday ... 6=Sunday (Python/pandas convention).
    This differs from DuckDB (0=Sunday) and SQL Server (1=Sunday) — a good
    reminder to always check the reference day when working across tools.
    Weekend = 5 (Saturday) or 6 (Sunday) in pandas.
  - groupby() + transform() broadcasts group-level totals back to each row,
    allowing per-group percentage calculations in one vectorised step.

Expected output (matching SQL Server, DuckDB, and R):
    Member weekend %:  ~23.3%
    Casual weekend %:  ~37.4%
    Weekend skew ratio (casual / member): 1.61x
"""

import pandas as pd
from utils import load_trips

trips = load_trips()

# ---------------------------------------------------------------------------
# Weekend flag
#
# .dt.dayofweek: 0=Monday, 1=Tuesday, ... 5=Saturday, 6=Sunday
# Note: pandas uses Monday=0, which differs from DuckDB (Sunday=0) and
# SQL Server (Sunday=1). Weekend logic is the same; only the numbers differ.
# ---------------------------------------------------------------------------

trips["is_weekend"] = trips["started_at"].dt.dayofweek.isin([5, 6])

# ---------------------------------------------------------------------------
# Overall weekend / weekday split
# ---------------------------------------------------------------------------

total        = len(trips)
weekend_tot  = trips["is_weekend"].sum()
weekday_tot  = total - weekend_tot

# ---------------------------------------------------------------------------
# Per-group weekend percentage
#
# groupby() + value_counts() on is_weekend gives counts per (member_casual,
# is_weekend) pair. We then compute each group's weekend % directly.
# ---------------------------------------------------------------------------

group_counts = (
    trips.groupby("member_casual")["is_weekend"]
    .agg(total_rides="count", weekend_rides="sum")
)
group_counts["weekend_pct"] = group_counts["weekend_rides"] / group_counts["total_rides"] * 100

member_pct = group_counts.loc["member", "weekend_pct"]
casual_pct = group_counts.loc["casual", "weekend_pct"]
skew_ratio = casual_pct / member_pct

print("=" * 50)
print("  Weekend vs Weekday Riding Patterns")
print("=" * 50)
print(f"  Weekend rides:   {weekend_tot:,}  ({weekend_tot/total*100:.1f}%)")
print(f"  Weekday rides:   {weekday_tot:,}  ({weekday_tot/total*100:.1f}%)")
print()
print(f"  {'':30s} {'Pct Weekend':>11}")
print(f"  {'-'*42}")
print(f"  {'Members':30s} {member_pct:>10.1f}%")
print(f"  {'Casual riders':30s} {casual_pct:>10.1f}%")
print(f"  {'-'*42}")
print(f"  Weekend skew ratio (casual/member): {skew_ratio:.2f}x")
print("=" * 50)
print(f"  Casual riders are {skew_ratio:.2f}x more likely to ride on")
print("  weekends — consistent with leisure, not commuting.")
print("=" * 50)
