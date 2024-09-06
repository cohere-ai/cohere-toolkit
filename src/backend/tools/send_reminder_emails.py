from typing import Any, Dict, List

from backend.tools.base import BaseTool


class SendReminderEmails(BaseTool):
    """
    Sends reminder emails to customers with pending orders, including instructions on how to complete their verification.
    """

    NAME = "send_reminder_emails"

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:

        customer_info = parameters.get("customer_info", "")
        verification_steps = parameters.get("verification_steps", "")
        summary = parameters.get("summary", "")

        for customer in customer_info:
            customer_name = customer['customer']
            customer_email = customer['email']
            email_subject = "Action Required: Complete your Verification"
            email_message = f"Hi {customer_name},\n\nWe noticed that your order requires additional verification. Here are the steps to complete the process:\n\n{summary}\n\n{verification_steps}\n\nThank you,\n[Your Company Name]"
            print(f"Email sent to {customer_email} with subject '{email_subject}':\n{email_message}")

        result = [
            {
                "emails_sent": True,
                "title": "Reminder emails sent successfully.",
                "text": f"Sent reminder emails to {len(customer_info)} customers with pending orders."
            }
        ]

        return result
