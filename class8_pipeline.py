import logging
from pathlib import Path
from class8_src import load_netflix, require_columns

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

def main():
    input_path = Path("data/messy_netflix_titles.csv")

    try:
        df = load_netflix(input_path)
        require_columns(df, ["title", "type", "release_year"])
    except ValueError:
        logger.error("Pipeline failed")
        raise SystemExit(1)

    logger.info("Pipeline completed")


if __name__ == "__main__":
    main()