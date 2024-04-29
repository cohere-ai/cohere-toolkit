# Custom tools and retrieval sources
Follow these instructions to create your own custom tools.

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

Add your tool implementation [here](https://github.com/cohere-ai/toolkit/tree/main/src/community/tools) (please note that this link might change). The specific subfolder used will depend on the type of tool you're implementing.

If you need to install a new module to run your tool, execute the following command and run `make dev` again.

```bash
poetry add <MODULE> --group community
```

If you're working on a File or Data Loader, follow the steps outlined in [Implementing a Retriever](#implementing-a-retriever).

If you're implementing a Function Tool, refer to the steps in [Implementing a Function Tool](#implementing-a-function-tool).

### Implementing a Retriever

Add the implementation inside a tool class that inherits `BaseRetrieval` and needs to implement the function `def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:`

You can define custom configurations for your tool within the `__init__` function. Set the exact values for these variables during [Step 4](#step-4-making-your-tool-available).

You can also develop a tool that requires a token or authentication. To do this, simply set your variable in the .env file.

For example, for Wikipedia we have a custom configuration:

```python
class LangChainWikiRetriever(BaseRetrieval):
    """
    This class retrieves documents from Wikipedia using the langchain package.
    This requires wikipedia package to be installed.
    """

    def __init__(self, chunk_size: int = 300, chunk_overlap: int = 0):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        wiki_retriever = WikipediaRetriever()
        docs = wiki_retriever.get_relevant_documents(query)
        text_splitter = CharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        documents = text_splitter.split_documents(docs)
        return [
            {
                "text": doc.page_content,
                "title": doc.metadata.get("title", None),
                "url": doc.metadata.get("source", None),
            }
            for doc in documents
        ]
```

And for internet search, we need an API key

```python
class TavilyInternetSearch(BaseRetrieval):
    def __init__(self):
        if "TAVILY_API_KEY" not in os.environ:
            raise ValueError("Please set the TAVILY_API_KEY environment variable.")

        self.api_key = os.environ["TAVILY_API_KEY"]
        self.client = TavilyClient(api_key=self.api_key)

    def retrieve_documents(self, query: str, **kwargs: Any) -> List[Dict[str, Any]]:
        content = self.client.search(query=query, search_depth="advanced")

        if "results" not in content:
            return []

        return [
            {
                "url": result["url"],
                "text": result["content"],
            }
            for result in content["results"]
```

Note that all Retrievers should return a list of Dicts, and each Dict should contain at least a `text` key.

### Implementing a Function Tool

Add the implementation inside a tool class that inherits `BaseFunctionTool` and needs to implement the function  `def call(self, parameters: str, **kwargs: Any) -> List[Dict[str, Any]]:` 

For example, for calculator 

```python
from typing import Any
from py_expression_eval import Parser
from typing import List, Dict

from backend.tools.function_tools.base import BaseFunctionTool

class CalculatorFunctionTool(BaseFunctionTool):
    """
    Function Tool that evaluates mathematical expressions.
    """

    def call(self, parameters: str, **kwargs: Any) -> List[Dict[str, Any]]:
        math_parser = Parser()
        to_evaluate = parameters.get("code", "").replace("pi", "PI").replace("e", "E")
        result = []
        try:
            result = {"result": math_parser.parse(to_evaluate).evaluate({})}
        except Exception:
            result = {"result": "Parsing error - syntax not allowed."}
        return result
```

## Step 4: Making Your Tool Available

To make your tool available, add its definition to the tools config [here](https://github.com/cohere-ai/cohere-toolkit/blob/main/src/community/config/tools.py).

Start by adding the tool name to the `ToolName` enum found at the top of the file.

Next, include the tool configurations in the `AVAILABLE_TOOLS` list. The definition should include:

- Name: Use the Enum definition you just created.
- Implementation: Link the class you made in [Step 3](#step-3-implement-the-tool).
- Parameter_definitions: If your class has specific configurations or fields that need to be set on `__init__`, set their values here.
- Is_visible: A boolean value indicating whether this function should be visible in the UI.
- Category: The type of tool.
- Description: A brief description of the tool.
- Env_vars: A list of secrets required by the tool.

Function tool with custom parameter definitions:

```python
  ToolName.Python_Interpreter: ManagedTool(
      name=ToolName.Python_Interpreter,
      implementation=python_interpreter.PythonInterpreterFunctionTool,
      parameter_definitions={
          "code": {
              "description": "Python code to execute using an interpreter",
              "type": "str",
              "required": True,
          }
      },
      is_visible=True,
      category=Category.Function,
      description="Runs python code in a sandbox.",
  ),
```

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

If you would like to go above and beyond, it would be helpful to add some unit tests to ensure that your tool is working as expected. Create a file [here](https://github.com/cohere-ai/cohere-toolkit/tree/main/src/community/tests/tools) and add a few cases.
