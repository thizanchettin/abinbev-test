import time

import requests


def fetch_breweries(
    url="https://api.openbrewerydb.org/v1/breweries",
    page=1,
    per_page=200,
):
    while True:
        response = requests.get(
            url,
            params={"page": page, "per_page": per_page},
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            break

        yield (data, page)

        page += 1
        time.sleep(0.2)
