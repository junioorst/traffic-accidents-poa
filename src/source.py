import os

import pendulum
import requests

CKAN_API = "https://dadosabertos.poa.br/api/3/action/package_show"


def get_csv_resource(dataset_id: str) -> dict:
    response = requests.get(CKAN_API, params={"id": dataset_id}, timeout=60)
    response.raise_for_status()

    resources = response.json()["result"]["resources"]
    csv = next(r for r in resources if r["format"].upper() == "CSV")

    return {
        "url": csv["url"],
        "last_modified": pendulum.parse(csv["last_modified"], tz="UTC"),
    }


def download_file(url: str, destination: str) -> None:
    temp_path = f"{destination}.tmp"

    with requests.get(url, stream=True, timeout=300) as response:
        response.raise_for_status()
        with open(temp_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                file.write(chunk)

    os.replace(temp_path, destination)
