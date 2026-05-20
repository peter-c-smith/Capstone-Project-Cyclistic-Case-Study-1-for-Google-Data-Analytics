"""
07_bike_type_mix.py
-------------------
What is the bike type mix (classic vs electric) for members and casuals?
Is there a meaningful preference difference between the groups?

Expected output: No meaningful difference (~65% electric for both groups).
This is a null finding — the data does not support targeting by bike type.

Polars notes:
  - pivot() reshapes long → wide, equivalent to pandas .unstack().
  - Percentage within group: divide each count by the group total using
    a second with_columns() pass after computing row sums.
"""

import polars as pl
from utils import load_trips

trips = load_trips()

counts = (
    trips
    .group_by(["member_casual", "rideable_type"])
    .agg(pl.len().alias("rides"))
    .sort(["member_casual", "rideable_type"])
)

# Pivot to wide format
wide = (
    counts
    .pivot(on="rideable_type", index="member_casual", values="rides")
    .fill_null(0)
)

# Add total and percentages
bike_cols = [c for c in wide.columns if c != "member_casual"]
wide = wide.with_columns(
    pl.sum_horizontal(*[pl.col(c) for c in bike_cols]).alias("total")
)
for col in bike_cols:
    wide = wide.with_columns(
        (pl.col(col) / pl.col("total") * 100).alias(f"{col}_pct")
    )

print("=" * 65)
print("  Bike Type Mix by Rider Type")
print("=" * 65)
print(f"  {'Rider':<10}", end="")
for col in bike_cols:
    print(f"  {col.replace('_bike',''):>12}  {'%':>6}", end="")
print()
print(f"  {'-'*63}")
for row in wide.sort("member_casual").iter_rows(named=True):
    print(f"  {row['member_casual']:<10}", end="")
    for col in bike_cols:
        print(f"  {row[col]:>12,}  {row[col+'_pct']:>5.1f}%", end="")
    print()

print()
print("  Null finding: no meaningful bike-type preference difference")
print("  between members and casuals (~65% electric for both groups).")
print("  Campaign should focus on behavior, not equipment preference.")
print("=" * 65)
