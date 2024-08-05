from typing import Any, Dict, List

from transformers import AutoModelForCausalLM, AutoTokenizer

from backend.schemas.cohere_chat import CohereChatRequest
from backend.schemas.context import Context
from community.model_deployments import BaseDeployment


class HuggingFaceDeployment(BaseDeployment):
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

    def __init__(self):
        pass

    @property
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
        model = AutoModelForCausalLM.from_pretrained(model_id)

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

        gen_text = tokenizer.decode(gen_tokens[0])

        return {"text": gen_text}

    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> Any:
        """
        Built in streamming is not supported, so this function wraps the invoke_chat function to return a single response.
        """
        yield {
            "event-type": "event-start",
            "generation_id": "",
        }

        gen_text = await self.invoke_chat(chat_request)

        yield {
            "event-type": "text-generation",
            "text": gen_text.get("text", ""),
        }

        yield {
            "event-type": "stream-end",
            "finish_reason": "COMPLETE",
        }

    async def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], ctx: Context, **kwargs: Any
    ) -> Any:
        return None

    def _build_chat_history(
        self, chat_history: List[Dict[str, Any]], message: str
    ) -> List[Dict[str, Any]]:
        messages = []

        for message in chat_history:
            messages.append({"role": message["role"], "content": message["message"]})

        messages.append({"role": "USER", "content": message})

        return messages


if __name__ == "__main__":
    hugging_face = HuggingFaceDeployment()
    chat_request = CohereChatRequest(
        chat_history=[
            {"role": "USER", "message": "Hello!"},
            {"role": "CHATBOT", "message": "Hi, how can I help you?"},
        ],
        message="How are you?",
    )
    response = hugging_face.invoke_chat(chat_request)
