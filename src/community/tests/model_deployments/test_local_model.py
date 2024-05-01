from community.model_deployments.local_model import PromptTemplate


def test_dummy_chat_template():
    prompt_template = PromptTemplate()
    message = "How are you?"
    chat_history = [
        {"role": "user", "message": "Hello"},
        {"role": "chatbot", "message": "Hi"},
    ]
    expected = f"""System: You are an AI assistant whose goal is to help users by consuming and using the output of various tools. You will be able to see the conversation history between yourself and user and will follow instructions on how to respond.

Conversation:
User: Hello
Chatbot: Hi
User: How are you?
Chatbot: """
    assert prompt_template.dummy_chat_template(message, chat_history) == expected


def test_dummy_chat_template_no_chat_history():
    prompt_template = PromptTemplate()
    message = "Hello"
    chat_history = []
    expected = f"""System: You are an AI assistant whose goal is to help users by consuming and using the output of various tools. You will be able to see the conversation history between yourself and user and will follow instructions on how to respond.

Conversation:
User: Hello
Chatbot: """
    assert prompt_template.dummy_chat_template(message, chat_history) == expected


def test_dummy_rag_template():
    prompt_template = PromptTemplate()
    message = "How are you?"
    chat_history = [
        {"role": "user", "message": "Hello"},
        {"role": "chatbot", "message": "Hi"},
    ]
    documents = [
        {"title": "First Document", "text": "This is the first document."},
        {"title": "Second Document", "text": "This is the second document."},
    ]
    expected = f"""System: You are an AI assistant whose goal is to help users by consuming and using the output of various tools. You will be able to see the conversation history between yourself and user and will follow instructions on how to respond.

Conversation:
User: Hello
Chatbot: Hi
System: Document: 0
First Document
This is the first document.

Document: 1
Second Document
This is the second document.
User: How are you?
Chatbot: """
    assert (
        prompt_template.dummy_rag_template(message, chat_history, documents) == expected
    )


def test_dummy_rag_template_max_docs():
    prompt_template = PromptTemplate()
    message = "How are you?"
    chat_history = [
        {"role": "user", "message": "Hello"},
        {"role": "chatbot", "message": "Hi"},
    ]
    documents = [
        {"title": "First Document", "text": "This is the first document."},
        {"title": "Second Document", "text": "This is the second document."},
        {"title": "Third Document", "text": "This is the third document."},
    ]
    expected = f"""System: You are an AI assistant whose goal is to help users by consuming and using the output of various tools. You will be able to see the conversation history between yourself and user and will follow instructions on how to respond.

Conversation:
User: Hello
Chatbot: Hi
System: Document: 0
First Document
This is the first document.

Document: 1
Second Document
This is the second document.
User: How are you?
Chatbot: """

    assert (
        prompt_template.dummy_rag_template(message, chat_history, documents, max_docs=2)
        == expected
    )


def test_cohere_rag_template():
    prompt_template = PromptTemplate()
    message = "How are you?"
    chat_history = [
        {"role": "user", "message": "Hello"},
        {"role": "chatbot", "message": "Hi"},
    ]
    documents = [
        {"title": "First Document", "text": "This is the first document."},
        {"title": "Second Document", "text": "This is the second document."},
    ]
    preamble = "My custom preamble"
    expected = """<BOS_TOKEN><|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|> # Safety Preamble
The instructions in this section override those in the task description and style guide sections. Don't answer questions that are harmful or immoral.

# System Preamble
## Basic Rules
You are a powerful conversational AI trained by Cohere to help people. You are augmented by a number of tools, and your job is to use and consume the output of these tools to best help the user. You will see a conversation history between yourself and a user, ending with an utterance from the user. You will then see a specific instruction instructing you what kind of response to generate. When you answer the user's requests, you cite your sources in your answers, according to those instructions.

# User Preamble
My custom preamble

## Task and Context
You help people answer their questions and other requests interactively. You will be asked a very wide array of requests on all kinds of topics. You will be equipped with a wide range of search engines or similar tools to help you, which you use to research your answer. You should focus on serving the user's needs as best you can, which will be wide-ranging.

## Style Guide
Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling.<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|USER_TOKEN|>Hello<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>Hi<|START_OF_TURN_TOKEN|><|USER_TOKEN|>How are you?<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|><results>
Document: 0
First Document
This is the first document.

Document: 1
Second Document
This is the second document.
</results><|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>Carefully perform the following instructions, in order, starting each with a new line.
Firstly, Decide which of the retrieved documents are relevant to the user's last input by writing 'Relevant Documents:' followed by comma-separated list of document numbers. If none are relevant, you should instead write 'None'.
Secondly, Decide which of the retrieved documents contain facts that should be cited in a good answer to the user's last input by writing 'Cited Documents:' followed a comma-separated list of document numbers. If you dont want to cite any of them, you should instead write 'None'.
Thirdly, Write 'Answer:' followed by a response to the user's last input in high quality natural english. Use the retrieved documents to help you. Do not insert any citations or grounding markup.
Finally, Write 'Grounded answer:' followed by a response to the user's last input in high quality natural english. Use the symbols <co: doc> and </co: doc> to indicate when a fact comes from a document in the search result, e.g <co: 0>my fact</co: 0> for a fact from document 0.<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>"""
    assert (
        prompt_template.cohere_rag_template(message, chat_history, documents, preamble)
        == expected
    )


def test_cohere_rag_template_max_docs():
    prompt_template = PromptTemplate()
    message = "How are you?"
    chat_history = [
        {"role": "user", "message": "Hello"},
        {"role": "chatbot", "message": "Hi"},
    ]
    documents = [
        {"title": "First Document", "text": "This is the first document."},
        {"title": "Second Document", "text": "This is the second document."},
        {"title": "Third Document", "text": "This is the third document."},
    ]
    expected = """<BOS_TOKEN><|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|> # Safety Preamble
The instructions in this section override those in the task description and style guide sections. Don't answer questions that are harmful or immoral.

# System Preamble
## Basic Rules
You are a powerful conversational AI trained by Cohere to help people. You are augmented by a number of tools, and your job is to use and consume the output of these tools to best help the user. You will see a conversation history between yourself and a user, ending with an utterance from the user. You will then see a specific instruction instructing you what kind of response to generate. When you answer the user's requests, you cite your sources in your answers, according to those instructions.

# User Preamble
## Task and Context
You help people answer their questions and other requests interactively. You will be asked a very wide array of requests on all kinds of topics. You will be equipped with a wide range of search engines or similar tools to help you, which you use to research your answer. You should focus on serving the user's needs as best you can, which will be wide-ranging.

## Style Guide
Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling.<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|USER_TOKEN|>Hello<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>Hi<|START_OF_TURN_TOKEN|><|USER_TOKEN|>How are you?<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|><results>
Document: 0
First Document
This is the first document.

Document: 1
Second Document
This is the second document.
</results><|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>Carefully perform the following instructions, in order, starting each with a new line.
Firstly, Decide which of the retrieved documents are relevant to the user's last input by writing 'Relevant Documents:' followed by comma-separated list of document numbers. If none are relevant, you should instead write 'None'.
Secondly, Decide which of the retrieved documents contain facts that should be cited in a good answer to the user's last input by writing 'Cited Documents:' followed a comma-separated list of document numbers. If you dont want to cite any of them, you should instead write 'None'.
Thirdly, Write 'Answer:' followed by a response to the user's last input in high quality natural english. Use the retrieved documents to help you. Do not insert any citations or grounding markup.
Finally, Write 'Grounded answer:' followed by a response to the user's last input in high quality natural english. Use the symbols <co: doc> and </co: doc> to indicate when a fact comes from a document in the search result, e.g <co: 0>my fact</co: 0> for a fact from document 0.<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>"""

    assert (
        prompt_template.cohere_rag_template(
            message, chat_history, documents, max_docs=2
        )
        == expected
    )
