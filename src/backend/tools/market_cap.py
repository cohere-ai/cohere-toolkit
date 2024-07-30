from typing import Any
import requests
import os


from typing import List, Dict

from backend.tools.base import BaseTool

class MarketCapTool(BaseTool):
    """
    Function Tool that retrieves the market cap of a ticker.
    """

    NAME = "Market_Cap"


    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(self, parameters, **kwargs: Any):       

        ticker = parameters.get('ticker')

        url = f"https://financialmodelingprep.com/api/v3/market-capitalization/{ticker}?apikey={os.environ['MARKET_CAP_API']}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                market_cap = data[0].get('marketCap', 'No market cap data available')
                result = {"result": f'Market cap for {ticker}: ${market_cap}'}
            else:
                result = {"result": "No data available for the specified ticker."}
        else:
            result = {"result": "Failed to retrieve data from the API."}
        return result