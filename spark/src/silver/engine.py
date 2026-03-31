from src.bronze.schema import get_brewery_schema
from src.utils.client import fetch_breweries
from src.utils.config import load_config
from src.utils.logger import get_logger
from src.utils.spark import create_spark
from pyspark.sql.functions import trim, col
from pyspark.sql.types import StringType

def trim_string_columns(df):
    return df.select([
        trim(col(c)).alias(c) if isinstance(df.schema[c].dataType, StringType)
        else col(c)
        for c in df.columns
    ])

def main():

    logger = get_logger("silver_engine")

    config = load_config()

    spark = create_spark("breweries-silver")

    schema = get_brewery_schema()

    logger.info("Starting transformations")
    logger.info(f"Writing to {config.silver.table}")

    df = spark.read.schema(schema).table(config.bronze.table)

    df = df.drop("state", "street")

    df = df.dropDuplicates(["id"]).filter("id is not null").filter("name is not null")

    df = trim_string_columns(df)

    (
        df.write
        .format("delta")
        .mode("overwrite")
        .partitionBy("country","state_province","city")
        .saveAsTable(config.silver.table)
    )

    logger.info("Finished transformations")

if __name__ == "__main__":
    main()
