import logging
from typing import List, Dict, Generator, Any
from community.model_deployments import BaseDeployment
from backend.schemas.cohere_chat import CohereChatRequest
from transformers import AutoTokenizer, AutoModelForCausalLM
from cohere.types import StreamedChatResponse


class HuggingFaceDeployment(BaseDeployment):
    DEFAULT_MODELS = ["CohereForAI/c4ai-command-r-v01", "CohereForAI/c4ai-command-r-plus"]
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
    
    def invoke_chat(self, chat_request: CohereChatRequest, **kwargs: Any) -> Any:
        model_id = chat_request.model
        if model_id == "command-r":
            model_id = self.DEFAULT_MODELS[0]

        print(model_id)

        tokenizer = AutoTokenizer.from_pretrained(model_id)
        print(tokenizer)
        model = AutoModelForCausalLM.from_pretrained(model_id)
        
        print(model)
        # Format message with the command-r-plus chat template
        messages = self._build_chat_history(chat_request.chat_history, chat_request.message)
        print(messages)
        input_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")
        print(input_ids)
        gen_tokens = model.generate(
            input_ids, 
            max_new_tokens=100, 
            do_sample=True, 
            temperature=0.3,
            )

        print(gen_tokens)

        gen_text = tokenizer.decode(gen_tokens[0])
        
        print(gen_text)
        exit()
        return gen_text
    

    def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Generator[StreamedChatResponse, None, None]:
        model_id = chat_request.model
        if model_id is None:
            model_id = self.DEFAULT_MODELS[0]

        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)

        # Format message with the command-r-plus chat template
        messages = self._build_chat_history(chat_request.chat_history, chat_request.message)
        input_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")

        gen_tokens = model.generate_stream(
            input_ids, 
            max_new_tokens=100, 
            do_sample=True, 
            temperature=0.3,
            )
        
        print(gen_tokens)
        
        gen_text = tokenizer.decode(gen_tokens[0])
        yield StreamedChatResponse(
            message=gen_text,
            chat_history=messages
        )


    def invoke_search_queries(
        self,
        message: str,
        chat_history: List[Dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> list[str]:
        logging.warning("invoke_search_queries not implemented for HuggingFaceDeployment")
        return []
    

    def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], **kwargs: Any
    ) -> Any:
        return None


    def _build_chat_history(self, chat_history: List[Dict[str, Any]], message: str) -> List[Dict[str, Any]]:
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
            {"role": "CHATBOT", "message": "Hi, how can I help you?"}
        ],
        message="How are you?"
    )
    response = hugging_face.invoke_chat(chat_request)
    print(response)