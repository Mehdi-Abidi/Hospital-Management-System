from __future__ import annotations

import argparse
from pathlib import Path

from database import DB_PATH, init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize or reset the hospital database.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the existing database file before re-initializing.",
    )
    args = parser.parse_args()

    if args.reset and DB_PATH.exists():
        DB_PATH.unlink()
        print("Existing database removed.")

    init_db(seed=True)
    print(f"Database ready at {Path(DB_PATH).resolve()}")


if __name__ == "__main__":
    main()
