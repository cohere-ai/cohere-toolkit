import os

import requests
from dotenv import load_dotenv

from carbon_gmail_test.utils import (
    get_headers,
)

load_dotenv()
BASE_URL = os.getenv("BASE_CARBON_URL", "")
WEBHOOK_URL = os.getenv("CARBON_WEBHOOK_URL", "")


def add_webhook():
    url = f"{BASE_URL}/add_webhook"
    payload = {"url": WEBHOOK_URL}
    response = requests.request("POST", url, json=payload, headers=get_headers())
    print(response.text)


def list_webhook():
    url = f"{BASE_URL}/webhooks"
    response = requests.request("POST", url, json={}, headers=get_headers())
    print(response.text)


if __name__ == "__main__":
    add_webhook()
    list_webhook()
