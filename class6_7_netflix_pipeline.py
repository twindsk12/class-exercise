import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from class6_7_netflix_utils import (
    clean_text,
    drop_missing_rows,
    remove_duplicates,
    remove_iqr_outliers,
    show_overview,
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Explore Netflix titles"
    )
    parser.add_argument(
        "--input",
        default="data/messy_netflix_titles.csv",
        help="Path to the Netflix CSV file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show debug messages"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S"
    )
    # TODO 4:
    # Create a Path object from args.input.
    # Inside a try block, load that path using pd.read_csv().
    # Catch FileNotFoundError, log an ERROR message,
    # and exit with sys.exit(1).
    # Log an INFO message.
    input_path = Path(args.input)

    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_path}")
        sys.exit(1)

    logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")

    df_original = df.copy()


    # TODO 5:
    # Call show_overview().
    # Log an INFO message.
    show_overview(df)
    logger.info("Displayed DataFrame overview")

    # TODO 6:
    # Call remove_duplicates().
    # Call drop_missing_rows().
    # Log an INFO message after each step that
    # includes the number of rows removed.
    before = len(df)
    df = remove_duplicates(df)
    removed = before - len(df)

    logger.info(f"Removed {removed} duplicate row(s)")

    before = len(df)
    df = drop_missing_rows(df)
    removed = before - len(df)

    logger.info(f"Dropped {removed} rows with missing values")

    # TODO 3:
    # Inside a try block, remove runtime_minutes outliers
    # using remove_iqr_outliers() with a threshold of 1.5.
    # Catch ValueError and exit with sys.exit(1).# Log an INFO message.

    try:
        df = remove_iqr_outliers(df, "runtime_minutes", 1.5)
    except ValueError:
        sys.exit(1)

    logger.info("Removed runtime_minutes outlier(s)")

    # TODO 4:
    # Apply clean_text() to title, type, and country.
    # Log an INFO message.

    for column in ["title", "type", "country"]:
        df[column] = df[column].apply(clean_text)
        logger.info(f"Cleaned text column: {column}")

    # TODO 5:
    # Create a report (dictionary) containing rows_before, rows_after, rows_removed, and columns.
    # Log an INFO message reporting: rows_before, rows_after, rows_removed, and columns.

    rows_before = len(df_original)
    rows_after = len(df)
    rows_removed = rows_before - rows_after

    report = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_removed,
        "columns": len(df.columns),
    }

    logger.info(f"Cleaning complete: {report}")

if __name__ == "__main__":
    main()
