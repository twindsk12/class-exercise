import logging
import pandas as pd

logger = logging.getLogger(__name__)

def load_netflix(filepath):
    """Load the Netflix CSV file."""
    df = pd.read_csv(filepath)
    logger.info("Data loaded")
    return df