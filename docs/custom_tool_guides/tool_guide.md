# Custom Tools
Follow these instructions to create your own custom tools.

For information on how to add authentication to your tool, please refer to the [Tool Auth guide.](/docs/custom_tool_guides/tool_auth_guide.md)

Custom tools will need to be built in the `community` folder. Make sure you've enabled the `INSTALL_COMMUNITY_DEPS` build arg in the `docker-compose.yml` file by setting it to `true`.

## Step 1: Choose a Tool to Implement

You can take a tool code implementation easily from: 

- LangChain
    - Tools: [Tools | 🦜️🔗 LangChain](https://python.langchain.com/docs/integrations/tools/)
    - Retrievers: [Retrievers | 🦜️🔗 LangChain](https://python.langchain.com/docs/integrations/retrievers/)
    - Vector Store: [Vector stores | 🦜️🔗 LangChain](https://python.langchain.com/docs/integrations/vectorstores/)
- Llama index
    - Data Connectors: [Data Connectors | Llama Index](https://docs.llamaindex.ai/en/v0.9.48/api_reference/readers.html)
- Connector
    - https://github.com/cohere-ai/quick-start-connectors
- Custom implementation

## Step 2: Select Your Tool Type

There are three types of tools:

- Data Loader: This tool type retrieves data from a source. Examples include the LangChain Wikipedia retriever and Arxiv.
- File Loader: This tool type loads and parses files. Examples include the LangChain Vector DB Retriever and LlamaIndex Upload PDF Retriever.
- Function: This is a unique tool type that performs a specific action. Examples include the Python Interpreter and Calculator.

## Step 3: Implement the Tool

Add your tool implementation [here](https://github.com/cohere-ai/cohere-toolkit/tree/main/src/community/tools) (please note that this link is subject to change).

If you need to install a new library to run your tool, execute the following command and run `make dev` again.

```bash
poetry add <MODULE> --group community
```
### Implementing a Langchain Tool

Add the implementation inside a tool class that inherits from `BaseTool`. This class will need to implement the `call()` method, which should return a list of dictionary results.

Note: To enable citations, each result in the list should contain a "text" field.

For example, let's look at the community-implemented `ArxivRetriever`:

```python
from typing import Any, Dict, List

from langchain_community.utilities import ArxivAPIWrapper

from community.tools import BaseTool


class ArxivRetriever(BaseTool):
    ID = "arxiv"

    def __init__(self):
        self.client = ArxivAPIWrapper()

    @classmethod
    # If your tool requires any environment variables such as API keys,
    # you will need to assert that they're not None here
    def is_available(cls) -> bool:
        return True

    @classmethod
    # You will need to add a tool definition here
    def get_tool_definition(cls) -> ToolDefinition:
        return ToolDefinition(
            name=cls.ID,    
            display_name="Arxiv",
            implementation=cls,
            parameter_definitions={
                "query": {
                    "description": "Query for retrieval.",
                    "type": "str",
                    "required": True,
                }
            },
            is_visible=False,
            is_available=cls.is_available(),
            error_message=cls.generate_error_message(),
            category=ToolCategory.DataLoader,
            description="Retrieves documents from Arxiv.",
        )

    # Your tool needs to implement this call() method
    def call(self, parameters: str, **kwargs: Any) -> List[Dict[str, Any]]:
        result = self.client.run(parameters)

        return [{"text": result}] # <- Return list of results, in this case there is only one
```

### Implementing a Custom Tool

In the tools folder, add a new file for your custom tool implementation. As a starting point, we recommend copy pasting the existing Calculator tool. Modify the class name and `NAME` attribute to suit your tool.

IMPORTANT: the call() method is where the tool call itself happens, i.e: this is where you want to perform your business logic (API call, data ETL, hardcoded response, etc). You can set custom parameters that you can use with the `parameter_definitions` key when specifying your tool config (see below). The return value of this tool MUST BE a list of dictionaries that have the text (required), url (optional), title (optional) fields as keys.

For example:
```python
return [{"text": "The fox is blue", "url": "wikipedia.org/foxes", "title": "Color of foxes"}, {..}, {..}]
```

Next, add your tool class to the init file by locating it in `src/community/tools/__init__.py`. Import your tool here, then add it to the `__all__` list.

Finally, you will need to add your tool definition to the config file. Locate it in `src/community/config/tools.py`, and import your tool at the top with `from backend.tools import ..`. 

Finally, to enable your tool, add your tool as an enum value. For example, `My_Tool = MyToolClass`.

## Step 5: Test Your Tool!

Now, when you run the toolkit, all the visible tools, including the one you just added, should be available!

- Run `make dev`
- Open [http://localhost:4000/](http://localhost:4000/)
- Open the side panel
- Your tool should be there!
- Select it and send a message that triggers it
- Appreciate a grounded response with something ✨you created from scratch✨!

Remember, you can also access your tools via the API.

- List tools:

```bash
curl --location --request GET 'http://localhost:8000/v1/tools' \
--header 'User-Id: me' \
--header 'Content-Type: application/json' \
--data '{}'
```

- Chat turns with tools:

```bash
curl --location 'http://localhost:8000/v1/chat-stream' \
--header 'User-Id: me' \
--header 'Content-Type: application/json' \
--data '{
    "message": "Tell me about the aya model",
    "tools": [{"name": "Arxiv"}]
}
'
```

## Step 6 (extra): Add Unit tests

If you would like to go above and beyond, it would be helpful to add some unit tests to ensure that your tool is working as expected. Create a file [here](https://github.com/cohere-ai/cohere-toolkit/tree/main/src/community/tests/tools) and add a few test cases.
