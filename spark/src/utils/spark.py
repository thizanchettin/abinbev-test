from pyspark.sql import SparkSession

from src.utils.logger import get_logger


def create_spark(appName: str):
    logger = get_logger("create_spark")
    logger.info(f"Creating SparkSession: {appName}")

    return SparkSession.builder.appName(appName).getOrCreate()
