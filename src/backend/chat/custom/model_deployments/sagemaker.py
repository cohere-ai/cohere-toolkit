import io
import json
import os
from typing import Any, Dict, Generator, List

import boto3
from cohere.types import StreamedChatResponse

from backend.chat.custom.model_deployments.base import BaseDeployment
from backend.schemas.cohere_chat import CohereChatRequest


class SageMakerDeployment(BaseDeployment):
    """
    SageMaker Deployment.
    How to setup SageMaker with Cohere:
    https://docs.cohere.com/docs/amazon-sagemaker-setup-guide
    """

    DEFAULT_MODELS = ["sagemaker-command"]
    profile_name = os.environ.get("SAGE_MAKER_PROFILE_NAME")
    region_name = os.environ.get("SAGE_MAKER_REGION_NAME")
    endpoint_name = os.environ.get("SAGE_MAKER_ENDPOINT_NAME")

    def __init__(self):
        boto3.setup_default_session(profile_name=self.profile_name)
        # Create the AWS client for the Bedrock runtime with boto3
        self.client = boto3.client("sagemaker-runtime", region_name=self.region_name)
        self.params = {
            "EndpointName": self.endpoint_name,
            "ContentType": "application/json",
        }

    @property
    def rerank_enabled(self) -> bool:
        return False

    @classmethod
    def list_models(cls) -> List[str]:
        if not SageMakerDeployment.is_available():
            return []

        return cls.DEFAULT_MODELS

    @classmethod
    def is_available(cls) -> bool:
        return all(
            [
                cls.profile_name is not None,
                cls.region_name is not None,
                cls.endpoint_name is not None,
            ]
        )

    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        # Create the payload for the request
        json_params = {
            "prompt_truncation": "AUTO_PRESERVE_ORDER",
            "stream": True,
            "message": chat_request.message,
            "chat_history": [x.to_dict() for x in chat_request.chat_history],
            "documents": chat_request.documents,
        }
        self.params["Body"] = json.dumps(json_params)

        # Invoke the model and print the response
        result = self.client.invoke_endpoint_with_response_stream(**self.params)
        event_stream = result["Body"]
        for index, line in enumerate(SageMakerDeployment.LineIterator(event_stream)):
            stream_event = json.loads(line.decode())
            stream_event["index"] = index
            yield stream_event

    def invoke_search_queries(
        self,
        message: str,
        chat_history: List[Dict[str, str]] | None = None,
        **kwargs: Any
    ) -> list[str]:
        # Create the payload for the request
        json_params = {
            "search_queries_only": True,
            "message": message,
            "chat_history": chat_history,
        }
        self.params["Body"] = json.dumps(json_params)

        # Invoke the model and print the response
        result = self.client.invoke_endpoint(**self.params)
        response = json.loads(result["Body"].read().decode())
        return [s["text"] for s in response["search_queries"]]

    def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        return None

    # This class iterates through each line of Sagemaker's response
    # https://aws.amazon.com/blogs/machine-learning/elevating-the-generative-ai-experience-introducing-streaming-support-in-amazon-sagemaker-hosting/
    class LineIterator:
        def __init__(self, stream):
            self.byte_iterator = iter(stream)
            self.buffer = io.BytesIO()
            self.read_pos = 0

        def __iter__(self):
            return self

        def __next__(self):
            while True:
                self.buffer.seek(self.read_pos)
                line = self.buffer.readline()
                if line and line[-1] == ord("\n"):
                    self.read_pos += len(line)
                    return line[:-1]
                try:
                    chunk = next(self.byte_iterator)
                except StopIteration:
                    if self.read_pos < self.buffer.getbuffer().nbytes:
                        continue
                    raise
                if "PayloadPart" not in chunk:
                    # Unknown event type
                    continue
                self.buffer.seek(0, io.SEEK_END)
                self.buffer.write(chunk["PayloadPart"]["Bytes"])
