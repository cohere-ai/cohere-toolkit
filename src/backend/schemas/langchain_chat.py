from typing import List
from pydantic import Field
from backend.schemas.chat import BaseChatRequest
from backend.schemas.tool import Tool


class LangchainChatRequest(BaseChatRequest):
    """
    Request shape for Langchain Streamed Chat.
    """

    # TODO: add in langchain specific tools

    tools: List[Tool] | None = Field(
        default_factory=list,
        title="""
            List of custom or managed tools to use for the response.
            If passing in managed tools, you only need to provide the name of the tool.
            If passing in custom tools, you need to provide the name, description, and optionally parameter defintions of the tool.
            Passing a mix of custom and managed tools is not supported. 

            Managed Tools Examples:
            tools=[
                {
                    "name": "Wiki Retriever - LangChain",
                },
                {
                    "name": "Calculator",
                }
            ]

            Custom Tools Examples:
            tools=[
                {
                    "name": "movie_title_generator",
                    "description": "tool to generate a cool movie title",
                    "parameter_definitions": {
                        "synopsis": {
                            "description": "short synopsis of the movie",
                            "type": "str",
                            "required": true
                        }
                    }
                },
                {
                    "name": "random_number_generator",
                    "description": "tool to generate a random number between min and max",
                    "parameter_definitions": {
                        "min": {
                            "description": "minimum number",
                            "type": "int",
                            "required": true
                        },
                        "max": {
                            "description": "maximum number",
                            "type": "int",
                            "required": true
                        }
                    }  
                },
                {
                    "name": "joke_generator",
                    "description": "tool to generate a random joke",
                }
            ]
        """,
    )
