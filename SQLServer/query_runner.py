"""
query_runner.py
Cyclistic Bike-Share Case Study — SQL Server Query Runner

Connects to the CyclisticCaseStudy SQL Server database and runs one or more
.sql files from the /queries folder, writing results to /query_results as
timestamped CSV files.

Usage:
    python query_runner.py                  # runs all .sql files in /queries
    python query_runner.py 01_ride_counts   # runs a specific query by name (with or without .sql)

Configuration:
    Copy .env.example to .env and fill in your connection details.
    The .env file is git-ignored and never committed.

Requirements:
    pip install pymssql python-dotenv
"""

import sys
import os
import csv
import datetime
import pymssql
from dotenv import load_dotenv
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────

BASE_DIR     = Path(__file__).parent
QUERIES_DIR  = BASE_DIR / "queries"
RESULTS_DIR  = BASE_DIR / "query_results"
ENV_FILE     = BASE_DIR / ".env"

# ── Config ───────────────────────────────────────────────────────────────────

load_dotenv(ENV_FILE)

SERVER   = os.getenv("SQL_SERVER",   "localhost")
PORT     = int(os.getenv("SQL_PORT", "1433"))
DATABASE = os.getenv("SQL_DATABASE", "CyclisticCaseStudy")
USERNAME = os.getenv("SQL_USERNAME", "claude")
PASSWORD = os.getenv("SQL_PASSWORD", "")


# ── Helpers ──────────────────────────────────────────────────────────────────

def connect():
    """Open and return a pymssql connection."""
    return pymssql.connect(
        server=SERVER,
        port=PORT,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE,
        as_dict=False,
    )


def split_batches(sql: str) -> list[str]:
    """
    Split a SQL script on GO batch separators (case-insensitive,
    GO must appear on its own line). pymssql does not understand GO —
    it is an SSMS/sqlcmd directive, not valid T-SQL.
    Returns a list of non-empty batch strings.
    """
    import re
    batches = re.split(r'^\s*GO\s*$', sql, flags=re.IGNORECASE | re.MULTILINE)
    return [b.strip() for b in batches if b.strip()]


def run_query(conn, sql: str) -> tuple[list, list]:
    """
    Execute a SQL script, splitting on GO batch separators.
    Returns (columns, rows) from the last batch that produced a result set.
    Earlier result sets are captured and returned if no later batch
    produces one — useful for scripts with multiple SELECT statements.
    """
    columns, rows = [], []

    for batch in split_batches(sql):
        cursor = conn.cursor()
        cursor.execute(batch)
        while True:
            if cursor.description:
                columns = [d[0] for d in cursor.description]
                rows    = cursor.fetchall()
            if not cursor.nextset():
                break

    return columns, rows


def save_results(query_name: str, columns: list, rows: list) -> Path:
    """Write results to a timestamped CSV in /query_results."""
    RESULTS_DIR.mkdir(exist_ok=True)
    ts        = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path  = RESULTS_DIR / f"{query_name}__{ts}.csv"

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    return out_path


def run_file(conn, sql_path: Path):
    """Run a single .sql file and print a summary."""
    print(f"\n{'─' * 60}")
    print(f"  Query : {sql_path.name}")
    print(f"{'─' * 60}")

    sql = sql_path.read_text(encoding="utf-8")

    try:
        columns, rows = run_query(conn, sql)
    except Exception as e:
        print(f"  ERROR : {e}")
        return

    if not columns:
        print("  Result: no result set returned (DDL or row-count statement)")
        return

    row_count = len(rows)
    print(f"  Rows  : {row_count:,}")
    print(f"  Cols  : {', '.join(columns)}")

    # Print preview (first 10 rows) to console
    print()
    col_widths = [max(len(str(c)), max((len(str(r[i])) for r in rows[:10]), default=0))
                  for i, c in enumerate(columns)]
    header = "  " + "  ".join(str(c).ljust(col_widths[i]) for i, c in enumerate(columns))
    print(header)
    print("  " + "  ".join("─" * w for w in col_widths))
    for row in rows[:10]:
        print("  " + "  ".join(str(v).ljust(col_widths[i]) for i, v in enumerate(row)))
    if row_count > 10:
        print(f"  ... ({row_count - 10:,} more rows)")

    # Save full results to CSV
    out_path = save_results(sql_path.stem, columns, rows)
    print(f"\n  Saved : {out_path.relative_to(BASE_DIR)}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Determine which files to run
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if not target.endswith(".sql"):
            target += ".sql"
        sql_files = [QUERIES_DIR / target]
        missing = [f for f in sql_files if not f.exists()]
        if missing:
            print(f"ERROR: query file not found: {missing[0]}")
            sys.exit(1)
    else:
        sql_files = sorted(QUERIES_DIR.glob("*.sql"))
        if not sql_files:
            print(f"No .sql files found in {QUERIES_DIR}")
            sys.exit(0)

    # Connect
    print(f"\nConnecting to {SERVER} / {DATABASE} as {USERNAME} ...")
    try:
        conn = connect()
        print("Connected.\n")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    # Run each file
    for sql_path in sql_files:
        run_file(conn, sql_path)

    conn.close()
    print(f"\n{'─' * 60}")
    print("  Done.")
    print(f"{'─' * 60}\n")


if __name__ == "__main__":
    main()
