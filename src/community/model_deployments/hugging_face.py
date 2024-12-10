import re
from typing import Any, Dict, List

from transformers import AutoModelForCausalLM, AutoTokenizer

from backend.chat.enums import StreamEvent
from backend.schemas.chat import ChatMessage
from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from community.model_deployments.community_deployment import CommunityDeployment


class HuggingFaceDeployment(CommunityDeployment):
    """
    The first time you run this code, it will download all the shards of the model from the Hugging Face model hub.
    This usually takes a while, so you might want to run this code separately and not as part of the toolkit.
    For that, you can run the following command:
        poetry run python3 src/community/model_deployments/hugging_face.py
    """

    DEFAULT_MODELS = [
        "CohereForAI/c4ai-command-r-v01",
        "CohereForAI/c4ai-command-r-plus",
    ]

    def __init__(self, **kwargs: Any):
        self.ctx = kwargs.get("ctx", None)

    @classmethod
    def name(cls) -> str:
        return "Hugging Face"

    @classmethod
    def env_vars(cls) -> List[str]:
        return []

    @classmethod
    def rerank_enabled(self) -> bool:
        return False

    @classmethod
    def list_models(cls) -> List[str]:
        if not HuggingFaceDeployment.is_available():
            return []

        return cls.DEFAULT_MODELS

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def invoke_chat(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
        model_id = chat_request.model
        if model_id == "command-r":
            model_id = self.DEFAULT_MODELS[0]

        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")

        # Format message with the command-r-plus chat template
        messages = self._build_chat_history(
            chat_request.chat_history, chat_request.message
        )
        input_ids = tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
        )

        gen_tokens = model.generate(
            input_ids,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.3,
        )

        gen_text = self.clean_text(tokenizer.decode(gen_tokens[0]))

        return {"text": gen_text}

    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> Any:
        """
        Built in streamming is not supported, so this function wraps the invoke_chat function
        to return a single response.

        Args:
            chat_request: Chat request
            ctx: Context
            **kwargs: Additional arguments
        """
        yield {
            "event_type": StreamEvent.STREAM_START,
            "generation_id": "",
        }

        gen_text = await self.invoke_chat(chat_request)

        yield {
            "event_type": StreamEvent.TEXT_GENERATION,
            "text": gen_text.get("text", ""),
        }

        yield {
            "event_type": StreamEvent.STREAM_END,
            "finish_reason": "COMPLETE",
        }

    async def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], ctx: Context, **kwargs: Any
    ) -> Any:
        return None

    def _build_chat_history(
        self, chat_history: List[ChatMessage], message: str
    ) -> List[Dict[str, Any]]:
        """
        Build chat history for the model.

        Args:
            chat_history: Chat history
            message: User message

        Returns:
            List[Dict[str, Any]]: Chat history
        """
        messages = []

        for message in chat_history:
            messages.append({"role": message["role"], "content": message["message"]})

        messages.append({"role": "user", "content": message})

        return messages

    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing all text between <| and |> tags.

        Args:
            text: Text to clean

        Returns:
            str: Cleaned text
        """
        cleaned_text = re.sub(r'<\|USER_TOKEN\|>.*?<\|END_OF_TURN_TOKEN\|>', '', text)
        cleaned_text = re.sub(r'<[^>]+>', '', cleaned_text)
        return cleaned_text.strip()
