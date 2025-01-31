from typing import Any

import requests

from backend.schemas.tool import ToolCategory, ToolDefinition
from backend.tools.base import BaseTool


class ClinicalTrials(BaseTool):
    """
    Retrieves clinical studies from ClinicalTrials.gov.

    See: https://clinicaltrials.gov/data-api/api
    """

    ID = "clinical_trials"

    def __init__(self, url="https://clinicaltrials.gov/api/v2/studies"):
        self._url = url

    @classmethod
    def is_available(cls) -> bool:
        return True

    @classmethod
    def get_tool_definition(cls) -> ToolDefinition:
        return  ToolDefinition(
            name=cls.ID,
            display_name="Clinical Trials",
            implementation=cls,
            is_visible=False,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.Function,
            description="Retrieves clinical studies from ClinicalTrials.gov.",
            parameter_definitions={
                "condition": {
                    "description": "Filters clinical studies to a specified disease or condition",
                    "type": "str",
                    "required": False,
                },
                "location": {
                    "description": "Filters clinical studies to a specified city, state, or country.",
                    "type": "str",
                    "required": False,
                },
                "intervention": {
                    "description": "Filters clinical studies to a specified drug or treatment.",
                    "type": "str",
                    "required": False,
                },
                "is_recruiting": {
                    "description": "Filters clinical studies to those that are actively recruiting.",
                    "type": "bool",
                    "required": False,
                },
            },
        )

    async def call(
        self, parameters: dict[str, Any], **kwargs,
    ) -> list[dict[str, Any]]:
        query_params = {"sort": "LastUpdatePostDate"}
        if condition := parameters.get("condition", ""):
            query_params["query.cond"] = condition
        if location := parameters.get("location", ""):
            query_params["query.locn"] = location
        if intervention := parameters.get("intervention", ""):
            query_params["query.intr"] = intervention
        if parameters.get("is_recruiting"):
            query_params["filter.overallStatus"] = "RECRUITING"
        query_params["pageSize"] = kwargs.get("n_max_studies", 10)

        try:
            response = requests.get(self._url, params=query_params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return self.get_tool_error(details=str(e))

        results = self._parse_response(response, location, intervention)
        if not results:
            return self.get_no_results_error()

        return results

    def _parse_response(
        self, response: requests.Response, location: str, intervention: str
    ) -> list[dict[str, Any]]:
        data = response.json()
        return [
            self._parse_study(study, location, intervention)
            for study in data.get("studies", [])
        ]

    def _parse_study(
        self, study: dict[str, Any], location: str, intervention: str
    ) -> dict[str, Any]:
        """Parse individual study data."""
        id_module = study["protocolSection"].get("identificationModule", {})
        description_module = study["protocolSection"].get("descriptionModule", {})
        status_module = study["protocolSection"].get("statusModule", {})
        eligibility_module = study["protocolSection"].get("eligibilityModule", {})
        conditions_module = study["protocolSection"].get("conditionsModule", {})
        locations_module = study["protocolSection"].get("contactsLocationsModule", {})
        intervents_module = study["protocolSection"].get("armsInterventionsModule", {})

        return {
            "id": id_module.get("nctId"),
            "title": id_module["briefTitle"],
            "trial_summary": description_module.get("briefSummary"),
            "trial_status": status_module.get("overallStatus"),
            "eligibility_criteria": eligibility_module.get("eligibilityCriteria"),
            "last_updated": status_module.get("lastUpdateSubmitDate"),
            "url": f"https://www.clinicaltrials.gov/study/{id_module.get('nctId')}",
            "conditions": conditions_module.get("conditions", []),
            "locations": self._filter_results(
                locations_module.get("locations", []),
                location,
                ["city", "state", "country"],
            ),
            "interventions": self._filter_results(
                intervents_module.get("interventions", []),
                intervention,
                ["name", "type", "description"],
            ),
        }

    def _filter_results(
        self, results: list[dict[str, Any]], target: str, fields: list[str]
    ) -> list[dict[str, Any]]:
        """Keeps a result if any of the specified fields contain the target value. Only
        the specified fields are returned in the result. If the query does not specify a
        target value, all results are retained.
        """
        return [
            {k: v for k, v in res.items() if k in fields}
            for res in results
            if any(target in res.get(field, "") for field in fields)
        ]
