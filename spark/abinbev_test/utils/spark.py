from pyspark.sql import SparkSession

from abinbev_test.utils.logger import get_logger


def create_spark(appName: str):
    logger = get_logger("create_spark")
    logger.info(f"Creating SparkSession: {appName}")

    try:
        return (
            SparkSession.getActiveSession() or SparkSession.builder.appName(appName).getOrCreate()
        )
    except Exception:
        return SparkSession.builder.getOrCreate()
