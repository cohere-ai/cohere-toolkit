from typing import Any, Dict, List

from backend.tools.base import BaseTool


class ExtractVerificationSteps(BaseTool):
    """
    Extracts and summarizes the steps required for user account verification from the user onboarding documentation..
    """

    NAME = "extract_verification_steps"

    def __init__(self):
        # Mock database query, in a real scenario, this would connect to a database
        self.mock_documentation = """
            Welcome to our platform! To complete your account verification, please follow these steps:
            1. Click on the 'Profile' tab in the main menu.
            2. Navigate to the 'Verification' section.
            3. Upload a clear photo of your government-issued ID.
            4. Wait for our team to review your submission.
            5. Once approved, you will receive an email confirmation.
        """
        self.summary = "To complete verification, upload your ID in the 'Verification' section of your profile. Our team will review and confirm via email."

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:

        # Extract and summarize the steps
        steps = self.mock_documentation.split("\n")[2:]

        result = {
            "verification_steps": steps,
            "summary": self.summary
        }

        return result
