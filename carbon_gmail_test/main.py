import os

import requests
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "https://api.carbon.ai"
CUSTOMER_ID = "tanzim_test_gmail"
API_KEY = os.getenv("CARBON_API_KEY")


def auth():
    url = f"{BASE_URL}/integrations/oauth_url"
    payload = {"service": "GOOGLE_DRIVE"}
    headers = {
        "authorization": "Bearer " + API_KEY,
        "customer-id": CUSTOMER_ID,
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)


auth()
