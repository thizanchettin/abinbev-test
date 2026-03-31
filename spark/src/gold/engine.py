from src.utils.client import fetch_breweries
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.spark import create_spark
from pyspark.sql import functions as F


def main():

    logger = get_logger("gold_engine")

    config = load_config()

    spark = create_spark("breweries-gold")

    logger.info("Starting transformations")
    logger.info(f"Writing to {config.gold.table}")

    df = spark.read.table(config.silver.table)

    df = (
        df.groupBy(
            "country",
            "state_province",
            "city",
            "brewery_type",
        )
        .agg(
            F.count("*").alias("brewery_count")
        )
    )

    (
        df.write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(config.gold.table)
    )

    logger.info("Finished transformations")

if __name__ == "__main__":
    main()
