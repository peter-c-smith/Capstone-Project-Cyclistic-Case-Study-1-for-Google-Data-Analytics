"""
10_missing_station_data.py
--------------------------
How prevalent is missing station data, and what does it reveal about
how electric bikes track location differently from classic bikes?

Key inference (derived entirely from the data, not assumed from outside
knowledge): Classic bikes have 0% missing station data. Electric bikes
have ~32% missing — but those rides still have start_lat/start_lng and
end_lat/end_lng populated. The only way GPS coordinates can exist without
a station name is if the bike itself is reporting its location. This means
e-bikes almost certainly have onboard GPS and wireless communication
hardware. Classic bikes are "located" only when physically docked; the
station sensor reports occupancy. E-bikes know where they are
independently of any dock.

pandas notes:
  - .isna() detects NaN values; .str.strip() handles empty strings.
    Combining both covers all representations of "missing" in the CSVs.
  - Boolean Series arithmetic: True counts as 1, so .sum() gives the
    count of missing values — a clean pandas idiom replacing SQL's
    COUNT(*) FILTER (WHERE ...) pattern.
  - Compound boolean masks (&, |) apply multiple conditions at once,
    directly equivalent to SQL's AND / OR in WHERE / FILTER clauses.

Expected output (matching SQL Server, DuckDB, and R):
  classic_bike: ~0% missing station data
  electric_bike: ~32% missing station data
  100% of missing-station e-bike rides still have GPS coordinates
"""

import pandas as pd
from utils import load_trips

trips = load_trips()

# ---------------------------------------------------------------------------
# Missing station flags — NaN or empty string
# ---------------------------------------------------------------------------

def is_missing(col):
    """True where a station name column is NaN or blank."""
    return col.isna() | (col.str.strip() == "")

trips["missing_start"] = is_missing(trips["start_station_name"])
trips["missing_end"]   = is_missing(trips["end_station_name"])
trips["missing_both"]  = trips["missing_start"] & trips["missing_end"]

# ---------------------------------------------------------------------------
# Part 1: Overall missing station summary
# ---------------------------------------------------------------------------

total = len(trips)

print("=" * 55)
print("  Part 1: Overall Missing Station Data")
print("=" * 55)
for label, col in [("Missing start station", "missing_start"),
                    ("Missing end station",   "missing_end"),
                    ("Missing both",          "missing_both")]:
    n   = trips[col].sum()
    pct = n / total * 100
    print(f"  {label}: {n:>9,}  ({pct:.1f}%)")

# ---------------------------------------------------------------------------
# Part 2: Missing by rider type and bike type
# ---------------------------------------------------------------------------

by_type = (
    trips.groupby(["member_casual", "rideable_type"])
    .agg(
        total_rides   = ("ride_id",        "count"),
        missing_start = ("missing_start",  "sum")
    )
    .reset_index()
)
by_type["missing_pct"] = by_type["missing_start"] / by_type["total_rides"] * 100
by_type = by_type.sort_values(["member_casual", "rideable_type"])

print()
print("=" * 55)
print("  Part 2: Missing Start Station by Rider & Bike Type")
print("=" * 55)
print(f"  {'Rider':<10} {'Bike Type':<16} {'Total':>9} {'Missing':>9} {'Miss%':>7}")
print(f"  {'-'*53}")
for _, row in by_type.iterrows():
    print(f"  {row['member_casual']:<10} {row['rideable_type']:<16} "
          f"{int(row['total_rides']):>9,} {int(row['missing_start']):>9,} "
          f"{row['missing_pct']:>6.1f}%")

# ---------------------------------------------------------------------------
# Part 3: GPS inference — missing station name BUT coordinates present
# ---------------------------------------------------------------------------

has_gps = (
    trips["start_lat"].notna() &
    trips["start_lng"].notna()
)

gps_check = (
    trips[trips["missing_start"]]
    .groupby("rideable_type")
    .agg(
        total_missing          = ("ride_id",  "count"),
        missing_but_has_gps    = ("ride_id",  lambda x: has_gps.loc[x.index].sum())
    )
)
gps_check["gps_pct"] = gps_check["missing_but_has_gps"] / gps_check["total_missing"] * 100

print()
print("=" * 55)
print("  Part 3: Missing Station — But GPS Coordinates Present?")
print("=" * 55)
print(f"  {'Bike Type':<16} {'Missing Stn':>12} {'Has GPS':>10} {'GPS%':>7}")
print(f"  {'-'*48}")
for bike, row in gps_check.iterrows():
    print(f"  {bike:<16} {int(row['total_missing']):>12,} "
          f"{int(row['missing_but_has_gps']):>10,} {row['gps_pct']:>6.1f}%")

print()
print("=" * 55)
print("  Inference: E-bikes missing station names still have GPS")
print("  coordinates — the bike itself is reporting its location.")
print("  E-bikes have onboard GPS hardware. Classic bikes are")
print("  located only when docked at a station sensor.")
print("  Missing e-bike station data is NOT a data quality gap —")
print("  coordinates are present and fully usable for geo analysis.")
print("=" * 55)
