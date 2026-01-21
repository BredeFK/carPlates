import json
import os
import requests
from dotenv import load_dotenv

from car import Car, Dimensions, parse_car_from_json

URL = "https://akfell-datautlevering.atlas.vegvesen.no/enkeltoppslag/kjoretoydata"

load_dotenv("carplates.env")
API_KEY = os.environ.get("STATENS_VEGVESEN_API_KEY", None)
if not API_KEY:
    raise ValueError("STATENS_VEGVESEN_API_KEY not set")


def fetch_car_details(plate: str) -> Car:
    response = requests.get(URL,
                            params={'kjennemerke': plate},
                            headers={'SVV-Authorization': f'Apikey {API_KEY}'})

    response_body = response.json()
    if response.status_code != 200:
        raise ValueError(f"Status code {response.status_code} not 200: {response_body}")

    return parse_car_from_json(response_body)
