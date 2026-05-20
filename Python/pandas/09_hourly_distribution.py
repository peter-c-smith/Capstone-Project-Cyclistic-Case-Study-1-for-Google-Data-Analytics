"""
09_hourly_distribution.py
-------------------------
At what hours of the day do members and casual riders most frequently
start rides?

Key finding: Members show a dual peak at ~8 AM and ~5 PM — a classic
commute pattern. Casual riders show a single broad afternoon peak
around 3–5 PM — consistent with leisure use.

pandas notes:
  - .dt.hour extracts the integer hour (0–23) from a datetime column.
    Equivalent to SQL's HOUR() / DATEPART(HOUR, ...).
  - groupby().agg() with a dict of named aggregations produces the hourly
    counts for both rider types in one pass.
  - Percentage of type: divide each hour's member/casual count by the
    total for that type — makes the two curves directly comparable
    regardless of the overall member/casual volume difference.
  - ASCII bar chart added to make the commute vs leisure pattern visible
    directly in the terminal, matching the DuckDB module output.

Expected output (matching SQL Server, DuckDB, and R):
  Member peaks at hours 8 and 17 (8 AM and 5 PM) — commute pattern
  Casual peak at hours 15–17 (3–5 PM) — leisure pattern
"""

import pandas as pd
from utils import load_trips

trips = load_trips()

# ---------------------------------------------------------------------------
# Extract hour and count by rider type
# ---------------------------------------------------------------------------

trips["hour_of_day"] = trips["started_at"].dt.hour

hourly = (
    trips.groupby(["hour_of_day", "member_casual"])
    .size()
    .unstack(fill_value=0)
)
hourly["total"] = hourly.sum(axis=1)

# Percentage of each rider type's total (makes curves comparable)
total_member = hourly["member"].sum()
total_casual = hourly["casual"].sum()

hourly["member_pct"] = hourly["member"] / total_member * 100
hourly["casual_pct"] = hourly["casual"] / total_casual * 100

# ---------------------------------------------------------------------------
# ASCII bar chart output
# ---------------------------------------------------------------------------

BAR_SCALE = 0.2  # 1 character per 0.2%

print("=" * 72)
print("  Hourly Ride Distribution  (% of each group's total rides)")
print("=" * 72)
print(f"  {'Hr':>5}  {'Member%':>7}  {'Casual%':>7}  {'Member bar':<25} {'Casual bar'}")
print(f"  {'-'*70}")

for hour, row in hourly.iterrows():
    mem_pct = row["member_pct"]
    cas_pct = row["casual_pct"]
    mem_bar = "█" * int(mem_pct / BAR_SCALE)
    cas_bar = "█" * int(cas_pct / BAR_SCALE)
    label   = f"{hour:02d}:00"
    print(f"  {label:>5}  {mem_pct:>7.2f}%  {cas_pct:>7.2f}%  {mem_bar:<25} {cas_bar}")

print("=" * 72)
print("  Members:  dual peaks at 08:00 and 17:00 → commute pattern")
print("  Casuals:  single broad peak at 15:00–17:00 → leisure pattern")
print("=" * 72)
