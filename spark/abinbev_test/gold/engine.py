from pyspark.sql import functions as F

from abinbev_test.utils.config import load_config
from abinbev_test.utils.logger import get_logger
from abinbev_test.utils.spark import create_spark


def main():
    logger = get_logger("gold_engine")

    config = load_config()

    spark = create_spark("breweries-gold")

    logger.info("Starting transformations")
    logger.info(f"Writing to {config.gold.table}")

    df = spark.read.table(config.silver.table)

    df = df.groupBy(
        "country",
        "state_province",
        "city",
        "brewery_type",
    ).agg(F.count("*").alias("brewery_count"))

    (df.write.format("delta").mode("overwrite").saveAsTable(config.gold.table))

    logger.info("Finished transformations")


if __name__ == "__main__":
    main()
