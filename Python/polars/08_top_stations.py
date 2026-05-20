"""
08_top_stations.py
------------------
What are the top 10 start stations for members and casual riders?
Is there overlap between the two lists?

Expected output (matching SQL Server, DuckDB, R, and pandas):
  Top casual station: Streeter Dr & Grand Ave
  Top member station: Kingsbury St & Kinzie St
  Overlap between top 10 lists: 0

Key finding: Shedd Aquarium is 81.8% casual — starkest single example
of the leisure-use pattern. Zero overlap between the two top-10 lists
confirms members and casuals are going to entirely different places.

Polars notes:
  - filter() with is_not_null() + str.strip_chars() replaces pandas
    .notna() + .str.strip() compound boolean mask.
  - top_k() is more efficient than sort().head() for large DataFrames —
    it uses a partial sort (heap-based) rather than sorting all rows.
"""

import polars as pl
from utils import load_trips

trips = load_trips()

# Filter out missing station names
valid = trips.filter(
    pl.col("start_station_name").is_not_null() &
    (pl.col("start_station_name").str.strip_chars() != "")
)

station_counts = (
    valid
    .group_by(["start_station_name", "member_casual"])
    .agg(pl.len().alias("rides"))
    .pivot(on="member_casual", index="start_station_name", values="rides")
    .fill_null(0)
    .with_columns(
        (pl.col("casual") + pl.col("member")).alias("total"),
        (pl.col("casual") / (pl.col("casual") + pl.col("member")) * 100)
        .alias("casual_pct")
    )
)

top10_casual = station_counts.top_k(10, by="casual")
top10_member = station_counts.top_k(10, by="member")

print("=" * 70)
print("  Top 10 Start Stations — Casual Riders")
print("=" * 70)
print(f"  {'Station':<42} {'Casual':>8} {'Casual%':>8}")
print(f"  {'-'*62}")
for row in top10_casual.sort("casual", descending=True).iter_rows(named=True):
    name = row["start_station_name"][:40]
    print(f"  {name:<42} {row['casual']:>8,} {row['casual_pct']:>7.1f}%")

print()
print("=" * 70)
print("  Top 10 Start Stations — Members")
print("=" * 70)
print(f"  {'Station':<42} {'Member':>8} {'Member%':>8}")
print(f"  {'-'*62}")
for row in top10_member.sort("member", descending=True).iter_rows(named=True):
    name = row["start_station_name"][:40]
    member_pct = 100 - row["casual_pct"]
    print(f"  {name:<42} {row['member']:>8,} {member_pct:>7.1f}%")

# Overlap
casual_set = set(top10_casual["start_station_name"].to_list())
member_set  = set(top10_member["start_station_name"].to_list())
overlap     = casual_set & member_set

print(f"\n  Overlap between top 10 lists: {len(overlap)}")

# Shedd Aquarium highlight
shedd = station_counts.filter(
    pl.col("start_station_name").str.contains("Shedd")
)
if shedd.height > 0:
    row = shedd.row(0, named=True)
    print(f"\n  Shedd Aquarium casual %: {row['casual_pct']:.1f}%  "
          f"({'✓' if abs(row['casual_pct'] - 81.8) < 0.5 else '✗'})")

print(f"\n  Kingsbury St & Kinzie St check: "
      f"{'✓' if any('Kingsbury' in s for s in member_set) else '✗'}")
print(f"  DuSable Lake Shore Dr & Monroe St check: "
      f"{'✓' if any('Monroe' in s for s in casual_set) else '✗'}")
print("=" * 70)
