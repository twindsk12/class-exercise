import logging

logger = logging.getLogger(__name__)


class DataStorage:
    def __init__(self):
        self.datasets = {}
        self.counter = 0

    def save_data(self, df, filename):
        self.counter += 1
        dataset_id = self.counter

        self.datasets[dataset_id] = {
            "filename": filename,
            "data": df.copy()
        }

        logger.debug(f"Stored dataset: id={dataset_id}, rows={len(df)}")
        return dataset_id

    def get_data(self, dataset_id):
        item = self.datasets.get(dataset_id)

        if item is None:
            logger.debug(f"Dataset not found: id={dataset_id}")
            return None

        logger.debug(f"Retrieved dataset: id={dataset_id}")
        return item["data"].copy()