from pyspark.sql.types import DoubleType, StringType, StructType
from src.bronze.schema import get_brewery_schema


def test_get_brewery_schema_returns_struct_type():
    schema = get_brewery_schema()
    assert isinstance(schema, StructType)


def test_get_brewery_schema_field_count():
    schema = get_brewery_schema()
    assert len(schema.fields) == 16


def test_get_brewery_schema_required_fields():
    schema = get_brewery_schema()
    field_names = [f.name for f in schema.fields]

    assert "id" in field_names
    assert "name" in field_names
    assert "brewery_type" in field_names
    assert "country" in field_names


def test_get_brewery_schema_coordinate_types():
    schema = get_brewery_schema()
    fields = {f.name: f.dataType for f in schema.fields}

    assert isinstance(fields["latitude"], DoubleType)
    assert isinstance(fields["longitude"], DoubleType)


def test_get_brewery_schema_string_fields_nullable():
    schema = get_brewery_schema()
    string_fields = [f for f in schema.fields if isinstance(f.dataType, StringType)]

    assert all(f.nullable for f in string_fields)
