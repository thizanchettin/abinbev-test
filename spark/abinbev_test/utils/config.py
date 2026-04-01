import os
from dataclasses import dataclass


@dataclass
class LayerConfig:
    table: str
    format: str
    location: str | None = None


@dataclass
class PipelineConfig:
    bronze: LayerConfig
    silver: LayerConfig
    gold: LayerConfig


def load_config() -> PipelineConfig:
    catalog = os.getenv("UC_CATALOG", "workspace")
    schema = os.getenv("UC_SCHEMA", "data_lake")

    def table(name: str):
        return f"{catalog}.{schema}.{name}"

    return PipelineConfig(
        bronze=LayerConfig(
            table=table("bronze_breweries"),
            format=os.getenv("BRONZE_FORMAT", "delta"),
        ),
        silver=LayerConfig(
            table=table("silver_breweries"),
            format=os.getenv("SILVER_FORMAT", "delta"),
        ),
        gold=LayerConfig(
            table=table("gold_breweries"),
            format=os.getenv("GOLD_FORMAT", "delta"),
        ),
    )
