from typing import Any, Dict, List

from backend.tools.base import BaseTool


class SearchPendingOrders(BaseTool):
    """
    Searches the order management database for customers with pending verification.
    """

    NAME = "search_pending_orders"

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(
        self, parameters: dict, ctx: Any, **kwargs: Any
    ) -> List[Dict[str, Any]]:
        logger = ctx.get_logger()

        # Get the status parameter from the request
        status = parameters.get("status", "")

        # Mock database query, in a real scenario, this would connect to a database
        mock_database = [
            {'customer': 'Alice Johnson', 'email': 'alice@example.com', 'status': 'pending verification'},
            {'customer': 'Bob Smith', 'email': 'bob@example.com', 'status': 'completed'},
            {'customer': 'Carol Davis', 'email': 'carol@example.com', 'status': 'pending verification'},
            # ... more mock data ...
        ]

        # Filter the mock database for orders with the specified status
        filtered_orders = [order for order in mock_database if order['status'] == status]

        customers_info = []
        for order in filtered_orders:
            customer_info = {
                "customer": order['customer'],
                "email": order['email']
            }
            customers_info.append(customer_info)

        result = {
            "customers_with_pending_verification": customers_info
        }

        return [result]
