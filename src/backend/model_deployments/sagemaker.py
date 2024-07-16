import io
import json
import logging
import os
import threading
import time
from typing import Any, AsyncGenerator, Dict, List

import boto3
from cohere.types import StreamedChatResponse

from backend.model_deployments.base import BaseDeployment
from backend.model_deployments.utils import get_model_config_var
from backend.schemas.cohere_chat import CohereChatRequest

SAGE_MAKER_ACCESS_KEY_ENV_VAR = "SAGE_MAKER_ACCESS_KEY"
SAGE_MAKER_SECRET_KEY_ENV_VAR = "SAGE_MAKER_SECRET_KEY"
SAGE_MAKER_SESSION_TOKEN_ENV_VAR = "SAGE_MAKER_SESSION_TOKEN"
SAGE_MAKER_REGION_NAME_ENV_VAR = "SAGE_MAKER_REGION_NAME"
SAGE_MAKER_ENDPOINT_NAME_ENV_VAR = "SAGE_MAKER_ENDPOINT_NAME"
SAGE_MAKER_ENV_VARS = [
    SAGE_MAKER_ACCESS_KEY_ENV_VAR,
    SAGE_MAKER_SECRET_KEY_ENV_VAR,
    SAGE_MAKER_SESSION_TOKEN_ENV_VAR,
    SAGE_MAKER_REGION_NAME_ENV_VAR,
    SAGE_MAKER_ENDPOINT_NAME_ENV_VAR,
]


class SageMakerDeployment(BaseDeployment):
    """
    SageMaker Deployment.
    How to setup SageMaker with Cohere:
    https://docs.cohere.com/docs/amazon-sagemaker-setup-guide
    """

    DEFAULT_MODELS = ["sagemaker-command"]

    def __init__(self, **kwargs: Any):
        # Create the AWS client for the Bedrock runtime with boto3
        self.client = boto3.client(
            "sagemaker-runtime",
            region_name=get_model_config_var(SAGE_MAKER_REGION_NAME_ENV_VAR, **kwargs),
            aws_access_key_id=get_model_config_var(
                SAGE_MAKER_ACCESS_KEY_ENV_VAR, **kwargs
            ),
            aws_secret_access_key=get_model_config_var(
                SAGE_MAKER_SECRET_KEY_ENV_VAR, **kwargs
            ),
            aws_session_token=get_model_config_var(
                SAGE_MAKER_SESSION_TOKEN_ENV_VAR, **kwargs
            ),
        )
        self.params = {
            "EndpointName": get_model_config_var(
                SAGE_MAKER_ENDPOINT_NAME_ENV_VAR, **kwargs
            ),
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
        return all([os.environ.get(var) is not None for var in SAGE_MAKER_ENV_VARS])

    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest
    ) -> AsyncGenerator[Any, Any]:
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

    async def invoke_rerank(self, query: str, documents: List[Dict[str, Any]]) -> Any:
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
