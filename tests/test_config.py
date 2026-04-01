from src.utils.config import LayerConfig, PipelineConfig, load_config


def test_load_config_defaults():
    config = load_config()

    assert isinstance(config, PipelineConfig)
    assert isinstance(config.bronze, LayerConfig)
    assert isinstance(config.silver, LayerConfig)
    assert isinstance(config.gold, LayerConfig)


def test_load_config_default_table_names():
    config = load_config()

    assert config.bronze.table == "workspace.data_lake.bronze_breweries"
    assert config.silver.table == "workspace.data_lake.silver_breweries"
    assert config.gold.table == "workspace.data_lake.gold_breweries"


def test_load_config_default_formats():
    config = load_config()

    assert config.bronze.format == "delta"
    assert config.silver.format == "delta"
    assert config.gold.format == "delta"


def test_load_config_custom_catalog_and_schema(monkeypatch):
    monkeypatch.setenv("UC_CATALOG", "my_catalog")
    monkeypatch.setenv("UC_SCHEMA", "my_schema")

    config = load_config()

    assert config.bronze.table == "my_catalog.my_schema.bronze_breweries"
    assert config.silver.table == "my_catalog.my_schema.silver_breweries"
    assert config.gold.table == "my_catalog.my_schema.gold_breweries"


def test_load_config_custom_formats(monkeypatch):
    monkeypatch.setenv("BRONZE_FORMAT", "parquet")
    monkeypatch.setenv("SILVER_FORMAT", "parquet")
    monkeypatch.setenv("GOLD_FORMAT", "parquet")

    config = load_config()

    assert config.bronze.format == "parquet"
    assert config.silver.format == "parquet"
    assert config.gold.format == "parquet"
