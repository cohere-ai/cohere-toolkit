import asyncio
from typing import Any, Dict, List

from llama_cpp import Llama

from backend.schemas.cohere_chat import CohereChatRequest

# To use local models install poetry with: poetry install --with setup,community,local-model --verbose
from backend.schemas.context import Context
from community.model_deployments import BaseDeployment


class LocalModelDeployment(BaseDeployment):
    def __init__(self, model_path: str, template: str = None):
        self.prompt_template = PromptTemplate()
        self.model_path = model_path
        self.template = template

    @property
    def rerank_enabled(self) -> bool:
        return False

    @classmethod
    def list_models(cls) -> List[str]:
        return []

    @classmethod
    def is_available(cls) -> bool:
        return True

    async def invoke_chat_stream(
        self, chat_request: CohereChatRequest, **kwargs: Any
    ) -> Any:
        model = self._get_model()

        if chat_request.max_tokens is None:
            chat_request.max_tokens = 200

        if len(chat_request.documents) == 0:
            prompt = self.prompt_template.dummy_chat_template(
                chat_request.message, chat_request.chat_history
            )
        else:
            prompt = self.prompt_template.dummy_rag_template(
                chat_request.message, chat_request.chat_history, chat_request.documents
            )

        stream = model(
            prompt,
            stream=True,
            max_tokens=chat_request.max_tokens,
            temperature=chat_request.temperature,
        )

        yield {
            "event_type": "stream-start",
            "generation_id": "",
        }

        for item in stream:
            yield {
                "event_type": "text-generation",
                "text": item["choices"][0]["text"],
            }

        yield {
            "event_type": "stream-end",
            "finish_reason": "COMPLETE",
        }

    async def invoke_chat(
        self, chat_request: CohereChatRequest, ctx: Context, **kwargs: Any
    ) -> Any:
        model = self._get_model()

        if chat_request.max_tokens is None:
            chat_request.max_tokens = 200

        response = model(
            chat_request.message,
            stream=False,
            max_tokens=chat_request.max_tokens,
            temperature=chat_request.temperature,
        )

        return {"text": response["choices"][0]["text"]}

    def _get_model(self):
        model = Llama(
            model_path=self.model_path,
            verbose=False,
        )

        return model

    async def invoke_rerank(
        self, query: str, documents: List[Dict[str, Any]], ctx: Context, **kwargs: Any
    ) -> Any:
        return None


class PromptTemplate:
    """
    Template for generating prompts for different types of requests.
    """

    def dummy_chat_template(
        self, message: str, chat_history: List[Dict[str, str]]
    ) -> str:
        prompt = "System: You are an AI assistant whose goal is to help users by consuming and using the output of various tools. You will be able to see the conversation history between yourself and user and will follow instructions on how to respond."
        prompt += "\n\n"
        prompt += "Conversation:\n"
        for chat in chat_history:
            if chat["role"].lower() == "user":
                prompt += f"User: {chat['message']}\n"
            else:
                prompt += f"Chatbot: {chat['message']}\n"

        prompt += f"User: {message}\n"
        prompt += "Chatbot: "

        return prompt

    def dummy_rag_template(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        documents: List[Dict[str, str]],
        max_docs: int = 5,
    ) -> str:
        max_docs = min(max_docs, len(documents))
        prompt = "System: You are an AI assistant whose goal is to help users by consuming and using the output of various tools. You will be able to see the conversation history between yourself and user and will follow instructions on how to respond."

        doc_str_list = []
        for doc_idx, doc in enumerate(documents[:max_docs]):
            if doc_idx > 0:
                doc_str_list.append("")

            # only use first 200 words of the document to avoid exceeding context window
            text = doc["text"]
            if len(text.split()) > 200:
                text = " ".join(text.split()[:200])

            doc_str_list.extend([f"Document: {doc_idx}", doc["title"], text])

        doc_str = "\n".join(doc_str_list)

        chat_history.append({"role": "system", "message": doc_str})
        chat_history.append({"role": "user", "message": message})

        chat_hist_str = ""
        for turn in chat_history:
            if turn["role"].lower() == "user":
                chat_hist_str += "User: "
            elif turn["role"].lower() == "chatbot":
                chat_hist_str += "Chatbot: "
            else:  # role == system
                chat_hist_str += "System: "

            chat_hist_str += turn["message"] + "\n"

        prompt += "\n\n"
        prompt += "Conversation:\n"
        prompt += chat_hist_str
        prompt += "Chatbot: "

        return prompt

    # https://docs.cohere.com/docs/prompting-command-r#formatting-chat-history-and-tool-outputs
    def cohere_rag_template(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        documents: List[Dict[str, str]],
        preamble: str = None,
        max_docs: int = 5,
    ) -> str:
        max_docs = min(max_docs, len(documents))
        chat_history.append({"role": "user", "message": message})
        SAFETY_PREAMBLE = "The instructions in this section override those in the task description and style guide sections. Don't answer questions that are harmful or immoral."
        BASIC_RULES = "You are a powerful conversational AI trained by Cohere to help people. You are augmented by a number of tools, and your job is to use and consume the output of these tools to best help the user. You will see a conversation history between yourself and a user, ending with an utterance from the user. You will then see a specific instruction instructing you what kind of response to generate. When you answer the user's requests, you cite your sources in your answers, according to those instructions."
        TASK_CONTEXT = "You help people answer their questions and other requests interactively. You will be asked a very wide array of requests on all kinds of topics. You will be equipped with a wide range of search engines or similar tools to help you, which you use to research your answer. You should focus on serving the user's needs as best you can, which will be wide-ranging."
        STYLE_GUIDE = "Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling."
        documents = self._get_cohere_documents_template(documents, max_docs)
        chat_history = self._get_cohere_chat_history_template(chat_history)
        INSTRUCTIONS = """Carefully perform the following instructions, in order, starting each with a new line.
Firstly, Decide which of the retrieved documents are relevant to the user's last input by writing 'Relevant Documents:' followed by comma-separated list of document numbers. If none are relevant, you should instead write 'None'.
Secondly, Decide which of the retrieved documents contain facts that should be cited in a good answer to the user's last input by writing 'Cited Documents:' followed a comma-separated list of document numbers. If you dont want to cite any of them, you should instead write 'None'.
Thirdly, Write 'Answer:' followed by a response to the user's last input in high quality natural english. Use the retrieved documents to help you. Do not insert any citations or grounding markup.
Finally, Write 'Grounded answer:' followed by a response to the user's last input in high quality natural english. Use the symbols <co: doc> and </co: doc> to indicate when a fact comes from a document in the search result, e.g <co: 0>my fact</co: 0> for a fact from document 0."""

        tool_prompt_template = f"""<BOS_TOKEN><|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|> # Safety Preamble
{SAFETY_PREAMBLE}

# System Preamble
## Basic Rules
{BASIC_RULES}

# User Preamble
"""
        if preamble:
            tool_prompt_template += f"""{preamble}\n\n"""

        tool_prompt_template += f"""## Task and Context
{TASK_CONTEXT}

## Style Guide
{STYLE_GUIDE}<|END_OF_TURN_TOKEN|>{chat_history}"""

        if documents:
            tool_prompt_template += f"""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>{documents}<|END_OF_TURN_TOKEN|>"""

        tool_prompt_template += f"""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>{INSTRUCTIONS}<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>"""

        return tool_prompt_template

    def _get_cohere_documents_template(
        self, documents: List[Dict[str, str]], max_docs: int
    ) -> str:
        max_docs = min(max_docs, len(documents))
        doc_str_list = ["<results>"]
        for doc_idx, doc in enumerate(documents[:max_docs]):
            if doc_idx > 0:
                doc_str_list.append("")
            doc_str_list.extend([f"Document: {doc_idx}", doc["title"], doc["text"]])
        doc_str_list.append("</results>")
        return "\n".join(doc_str_list)

    def _get_cohere_chat_history_template(
        self, chat_history: List[Dict[str, str]]
    ) -> str:
        chat_hist_str = ""
        for turn in chat_history:
            chat_hist_str += "<|START_OF_TURN_TOKEN|>"
            if turn["role"] == "user":
                chat_hist_str += "<|USER_TOKEN|>"
            elif turn["role"] == "chatbot":
                chat_hist_str += "<|CHATBOT_TOKEN|>"
            else:  # role == system
                chat_hist_str += "<|SYSTEM_TOKEN|>"
            chat_hist_str += turn["message"]
        chat_hist_str += "<|END_OF_TURN_TOKEN|>"
        return chat_hist_str


async def main():
    model = LocalModelDeployment(model_path="path/to/model")

    print("--- Chat Stream ---")
    response = await model.invoke_chat_stream(
        CohereChatRequest(message="hello world", temperature=0.3)
    )
    for item in response:
        print(item)

    print("\n--- Chat ---")
    response = model.invoke_chat(
        CohereChatRequest(message="hello world", temperature=0.3)
    )
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
