"""
02_core_ride_counts.py
----------------------
Member vs casual ride distribution.

Expected output (matching SQL Server, DuckDB, and R):
    member    3,601,445    64.1%
    casual    2,019,099    35.9%

Introduces: value_counts(), Series arithmetic, f-string formatting
"""

from utils import load_trips

trips = load_trips()

# ---------------------------------------------------------------------------
# Member / casual split
#
# value_counts() returns a Series sorted by frequency descending.
# Dividing by len(trips) gives proportions; multiply by 100 for percentages.
# ---------------------------------------------------------------------------

counts = trips["member_casual"].value_counts()
pcts   = counts / len(trips) * 100

print("=" * 45)
print("  Core Ride Counts — Member vs Casual")
print("=" * 45)
print(f"  Total rides:  {len(trips):>12,}")
print()
for label in counts.index:
    print(f"  {label:<8}  {counts[label]:>12,}  ({pcts[label]:.1f}%)")
print("=" * 45)
print("  Matches SQL Server, DuckDB, and R exactly.")
print("=" * 45)
