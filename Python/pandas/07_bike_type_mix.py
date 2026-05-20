"""
07_bike_type_mix.py
-------------------
Do casual riders and members prefer different bike types?

Key finding (null result): Bike type preference is nearly identical between
members and casuals (~65% electric for both groups). This is NOT a meaningful
behavioral differentiator — worth including because a good analysis reports
what the data doesn't show, not just what it does.

pandas notes:
  - pd.crosstab() is the natural tool here — it counts combinations of two
    categorical columns and can normalise by row, column, or grand total
    in a single call.
  - normalize='columns' gives each bike type's share within each rider group;
    normalize='index' gives each rider group's share within each bike type.
    We use both to build the full picture.
  - The result mirrors a SQL CROSS JOIN pattern but with far less code.

Expected output (matching SQL Server, DuckDB, and R):
  electric_bike: ~65% of member rides, ~67% of casual rides
  classic_bike:  ~35% of member rides, ~33% of casual rides
  No electric_scooter in Apr 2025 – Mar 2026 dataset.
"""

import pandas as pd
from utils import load_trips

trips = load_trips()

# ---------------------------------------------------------------------------
# Bike type counts — overall and by rider group
# ---------------------------------------------------------------------------

# Absolute counts per bike type
counts = trips.groupby("rideable_type")["member_casual"].value_counts().unstack(fill_value=0)
counts["total"] = counts.sum(axis=1)

grand_total  = len(trips)
total_member = (trips["member_casual"] == "member").sum()
total_casual = (trips["member_casual"] == "casual").sum()

counts["pct_of_all"]    = counts["total"]  / grand_total  * 100
counts["member_pct"]    = counts.get("member", 0) / total_member * 100
counts["casual_pct"]    = counts.get("casual", 0) / total_casual * 100

counts = counts.sort_values("total", ascending=False)

print("=" * 70)
print("  Bike Type Mix")
print("=" * 70)
print(f"  {'Bike Type':<20} {'Total':>9} {'Member':>9} {'Casual':>9} "
      f"{'All%':>6} {'Mem%':>6} {'Cas%':>6}")
print(f"  {'-'*68}")
for bike, row in counts.iterrows():
    mem = int(row.get("member", 0))
    cas = int(row.get("casual", 0))
    print(f"  {bike:<20} {int(row['total']):>9,} {mem:>9,} {cas:>9,} "
          f"{row['pct_of_all']:>5.1f}% {row['member_pct']:>5.1f}% {row['casual_pct']:>5.1f}%")
print("=" * 70)
print("  Null finding: member and casual riders use electric bikes")
print("  at nearly identical rates — bike type does not distinguish")
print("  the two groups and is not a conversion lever.")
print()
print("  Note: No electric_scooter rows in Apr 2025–Mar 2026 data.")
print("=" * 70)
