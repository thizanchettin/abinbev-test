from src.bronze.schema import get_brewery_schema
from src.utils.client import fetch_breweries
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.spark import create_spark


def main():

    logger = get_logger("bronze_engine")

    config = load_config()

    spark = create_spark("breweries-bronze")

    schema = get_brewery_schema()

    logger.info("Starting ingestion")
    logger.info(f"Writing to {config.bronze.table}")

    for batch, page in fetch_breweries():

        logger.info(f"Writing page {page}")

        df = spark.createDataFrame(batch, schema=schema)

        (
            df.write
            .format(config.bronze.format)
            .mode("append")
            .saveAsTable(config.bronze.table)
        )

    logger.info("Finished ingestion")

if __name__ == "__main__":
    main()
