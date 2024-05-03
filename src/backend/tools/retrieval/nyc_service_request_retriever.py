import json
from typing import Any, Iterable, List, Dict
from elasticsearch import Elasticsearch
from backend.tools.retrieval.base import BaseRetrieval
import os
from half_json.core import JSONFixer

from backend.chat.custom.model_deployments.deployment import get_deployment
from backend.schemas.cohere_chat import CohereChatRequest
from backend.services.logger import get_logger

cohere_api_key = os.environ.get("COHERE_API_KEY")
logger = get_logger()


class NYCServiceRequestRetriever(BaseRetrieval):

    def __init__(self, host_url: str, index: str, deployment_name: str) -> None:
        self.index = index
        self.deployment_name = deployment_name
        self.client = Elasticsearch(host_url)
        self.cohere_api_key = os.environ.get("COHERE_API_KEY")

    @classmethod
    def is_available(cls) -> bool:
        return cohere_api_key is not None

    @classmethod
    def validate_and_parse_json(cls, json_string: str):
        try:
            # Try parsing the JSON string
            parsed_json = json.loads(json_string)
            return parsed_json, None
        except json.JSONDecodeError as e:
            # Attempt to fix the JSON if there is a parsing error
            fixer = JSONFixer()
            fix_result = fixer.fix(json_string)
            if fix_result.success:
                try:
                    # Try parsing the fixed JSON string
                    parsed_json = json.loads(fix_result.line)
                    return parsed_json, None
                except json.JSONDecodeError:
                    # Return error if the fixed JSON still fails to parse
                    return None, "Fixed JSON is still invalid."
            else:
                # Return the original error if fix was unsuccessful
                return None, str(e)

    def retrieve_first_document(self) -> Dict[str, Any]:
        response = self.client.search(index=self.index, query={"match_all": {}}, size=1)
        return response['hits']['hits'][0]['_source'] if response['hits']['hits'] else None

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        structure = self.retrieve_first_document()
        logger.info(f"--> The structure: {structure}")

        deployment_model = get_deployment(kwargs.get("deployment_name"))
        logger.info(f"Using deployment {deployment_model.__class__.__name__}")

        # TODO add more context to explain what the columns mean
        chat_request = CohereChatRequest(
            message=f"""
            1. Convert the query to a full executable ELASTICSEARCH query.
            2. The final results should be a VALID JSON STRING THAT CAN BE PARSED WITHOUT ERRORS.
            3. The output should only be a solution to the query.
            4. I WANT ONLY THE JSON STRING.
            5. DO NOT QUOTE THE EXPRESSION.
            6. DO NOT ADD ANYTHING APART FROM THE EXPRESSION!
            7. This data is about calls in the US about complaints.
            8. I REPEAT THE OUTPUT SHOULD BE A VALID JSON STRING.
            
            Query: {query}
            """,
            documents=[
                {
                    "title": "Structure of the ELASTICSEARCH data",
                    "content": json.dumps(structure, indent=2)
                }
            ]
        )

        results = deployment_model.invoke_chat(
            chat_request
        )

        logger.info(f"\n\n--> The results: {results.text}")

        transformed_query, error = self.validate_and_parse_json(results.text)

        logger.info(f"\n\n--> The results--> transformed_query: {transformed_query}")

        res = self.client.search(index=self.index, body=transformed_query)

        logger.info(f"\n\n--> Final Query The results: {res}")
        docs = []
        if 'hits' in res:
            for r in res['hits']['hits']:
                docs.append({
                    "text": json.dumps(r["_source"])
                })

        # TODO check for aggregations

        return docs
