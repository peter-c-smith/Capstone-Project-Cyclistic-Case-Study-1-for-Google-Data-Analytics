"""
05_round_trips.py
-----------------
Do casual riders return to their starting station more often than members,
indicating recreational use?

Key finding: Casual riders take round trips at 1.63x the rate of members —
further evidence of leisure riding patterns.

pandas notes:
  - NaN semantics in pandas mirror SQL's three-valued logic: NaN == NaN
    evaluates to False, just like NULL = NULL → UNKNOWN in SQL. A naive
    comparison of start_station_name == end_station_name would silently
    exclude all e-bike rides where both station names are missing.
  - Fix: .fillna('') converts NaN to empty string first, so two missing
    station names compare as equal — matching Power BI DAX's behavior where
    BLANK() = BLANK() is TRUE.
  - This is the same fix applied in DuckDB (COALESCE) and SQL Server
    (ISNULL) — the pandas idiom just looks different.

Expected output (matching SQL Server, DuckDB, and R):
    Member round trip %:  ~11.1%
    Casual round trip %:  ~18.1%
    Round trip ratio (casual / member): 1.63x
"""

import pandas as pd
from utils import load_trips

trips = load_trips()

# ---------------------------------------------------------------------------
# Round trip flag
#
# fillna('') converts NaN → '' before comparison so that rides where both
# station names are missing (e-bikes at non-station racks) correctly count
# as round trips — matching the Power BI DAX BLANK() = BLANK() behavior.
# ---------------------------------------------------------------------------

trips["is_round_trip"] = (
    trips["start_station_name"].fillna("") == trips["end_station_name"].fillna("")
)

# ---------------------------------------------------------------------------
# Per-group round trip counts and percentages
# ---------------------------------------------------------------------------

group = trips.groupby("member_casual")["is_round_trip"].agg(
    total_rides="count",
    round_trips="sum"
)
group["round_trip_pct"] = group["round_trips"] / group["total_rides"] * 100

total_rt   = trips["is_round_trip"].sum()
member_pct = group.loc["member", "round_trip_pct"]
casual_pct = group.loc["casual", "round_trip_pct"]
member_rt  = group.loc["member", "round_trips"]
casual_rt  = group.loc["casual", "round_trips"]
ratio      = casual_pct / member_pct

print("=" * 55)
print("  Round Trip Analysis")
print("=" * 55)
print(f"  Total round trips:  {total_rt:,}")
print()
print(f"  {'':30s} {'Round Trip %':>12}")
print(f"  {'-'*48}")
print(f"  {'Members':30s} {member_pct:>11.1f}%  ({member_rt:,})")
print(f"  {'Casual riders':30s} {casual_pct:>11.1f}%  ({casual_rt:,})")
print(f"  {'-'*48}")
print(f"  Round trip ratio (casual/member): {ratio:.2f}x")
print("=" * 55)
print("  Note: NaN station names treated as equal (.fillna('')),")
print("  matching Power BI DAX BLANK() = BLANK() behavior.")
print("  e-bike rides ending at non-station racks count as")
print("  round trips when start and end locations both missing.")
print("=" * 55)
