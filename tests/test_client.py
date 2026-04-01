from unittest.mock import MagicMock, patch

import pytest
from src.utils.client import fetch_breweries


def make_mock_response(data):
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status.return_value = None
    return mock


def test_fetch_breweries_yields_data():
    page1 = [{"id": "1", "name": "Brewery A"}]

    with patch("utils.client.requests.get") as mock_get, patch("utils.client.time.sleep"):
        mock_get.side_effect = [
            make_mock_response(page1),
            make_mock_response([]),
        ]

        results = list(fetch_breweries())

    assert len(results) == 1
    assert results[0] == (page1, 1)


def test_fetch_breweries_multiple_pages():
    page1 = [{"id": "1", "name": "Brewery A"}]
    page2 = [{"id": "2", "name": "Brewery B"}]

    with patch("utils.client.requests.get") as mock_get, patch("utils.client.time.sleep"):
        mock_get.side_effect = [
            make_mock_response(page1),
            make_mock_response(page2),
            make_mock_response([]),
        ]

        results = list(fetch_breweries())

    assert len(results) == 2
    assert results[0] == (page1, 1)
    assert results[1] == (page2, 2)


def test_fetch_breweries_raises_on_http_error():
    with patch("utils.client.requests.get") as mock_get:
        mock_get.return_value.raise_for_status.side_effect = Exception("HTTP Error")

        with pytest.raises(Exception, match="HTTP Error"):
            list(fetch_breweries())


def test_fetch_breweries_empty_first_page():
    with patch("utils.client.requests.get") as mock_get:
        mock_get.return_value = make_mock_response([])

        results = list(fetch_breweries())

    assert results == []
