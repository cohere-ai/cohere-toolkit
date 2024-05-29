# Custom Tools
Follow these instructions to create your own custom tools.

Custom tools will need to be built in the `community` folder. Make sure you've enabled the `INSTALL_COMMUNITY_DEPS` build arg in the `docker-compose.yml` file by setting it to `true`.

## Step 1: Choose a Tool to Implement

You can take a tool implementation easily from: 

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

Add your tool implementation [here](https://github.com/cohere-ai/toolkit/tree/main/src/community/tools) (please note that this link is subject to change).

If you need to install a new library to run your tool, execute the following command and run `make dev` again.

```bash
poetry add <MODULE> --group community
```
### Implementing a Tool

Add the implementation inside a tool class that inherits from `BaseTool`. This class will need to implement the `call()` method, which should return a list of dictionary results.

Note: To enable citations, each result in the list should contain a "text" field.

For example, let's look at the community-implemented `ArxivRetriever`:

```python
from typing import Any, Dict, List

from langchain_community.utilities import ArxivAPIWrapper

from community.tools import BaseTool


class ArxivRetriever(BaseTool):
    def __init__(self):
        self.client = ArxivAPIWrapper()

    @classmethod
    # If your tool requires any environment variables such as API keys,
    # you will need to assert that they're not None here
    def is_available(cls) -> bool:
        return True

    # Your tool needs to implement this call() method
    def call(self, parameters: str, **kwargs: Any) -> List[Dict[str, Any]]:
        result = self.client.run(parameters)

        return [{"text": result}] # <- Return list of results, in this case there is only one
```

## Step 4: Making Your Tool Available

To make your tool available, add its definition to the community tools [config.py](https://github.com/cohere-ai/cohere-toolkit/blob/main/src/community/config/tools.py).

Start by adding the tool name to the `ToolName` enum found at the top of the file.

Next, include the tool configurations in the `AVAILABLE_TOOLS` list. The definition should include:

- Name: Use the Enum definition you just created.
- Implementation: Link the class you made in [Step 3](#step-3-implement-the-tool).
- Parameter_definitions: If your class has specific configurations or fields that need to be set on `__init__`, set their values here.
- Is_visible: A boolean value indicating whether this function should be visible in the UI.
- Is_available: A boolean value indicating that this tool is ready to use. The class definition should help check for any variables or api keys that are required.
- Error_message: A message returned when is_available is False.
- Category: The type of tool.
- Description: A brief description of the tool.
- Env_vars: A list of secrets required by the tool.

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
curl --location --request GET 'http://localhost:8000/tools' \
--header 'User-Id: me' \
--header 'Content-Type: application/json' \
--data '{}'
```

- Chat turns with tools:

```bash
curl --location 'http://localhost:8000/chat-stream' \
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
