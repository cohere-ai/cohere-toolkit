
# How to guides

## How to use community features

By default, the toolkit runs without community tools or deployments. If you want to enable them, add the following to the .env file or use `make setup` to set this variable:

```bash
USE_COMMUNITY_FEATURES=True
```

## How to add your own model deployment

To add your own deployment:
  1. Create a deployment file, add it to [/community/model_deployments](https://github.com/cohere-ai/cohere-toolkit/tree/main/src/community/model_deployments) folder, implement the function calls from `BaseDeployment` similar to the other deployments.
  2. Add the deployment to [src/community/config/deployments.py](https://github.com/cohere-ai/cohere-toolkit/blob/main/src/community/config/deployments.py)
  3. Add the environment variables required to the env template.
- To add a Cohere private deployment, use the steps above copying the cohere platform implementation changing the base_url for your private deployment and add in custom auth steps.

## How to call the backend as an API

It is possible to just run the backend service, and call it in the same manner as the Cohere API. Note streaming and non streaming endpoints are split into 'http://localhost:8000/v1/chat-stream' and 'http://localhost:8000/v1/chat' compared to the API. For example, to stream:

```bash
curl --location 'http://localhost:8000/v1/chat-stream' \
--header 'User-Id: me' \
--header 'Content-Type: application/json' \
--data '{
    "message": "Tell me about the aya model"
}
'
```

## How to add your own chat interface

Currently the core chat interface is the Coral frontend. To add your own interface, take the steps above for call the backend as an API in your implementation and add it alongside `src/community/interfaces/`.

## How to add a connector to the Toolkit

If you have already created a [connector](https://docs.cohere.com/docs/connectors), it can be used in the toolkit with `ConnectorRetriever`. Add in your configuration and then add the definition in [community/config/tools.py](https://github.com/cohere-ai/cohere-toolkit/blob/main/src/community/config/tools.py) similar to `Arxiv` implementation with the category `Category.DataLoader`. You can now use the Coral frontend and API with the connector.

## How to set up web search with the Toolkit

To use Coral with web search, simply use the `Tavily_Internet_Search` tool by adding your API key to the env file. Alternatively you can use any search provider of your choosing, either with your own implementation or an integration implementation (such as LangChain) by following these [steps below](custom_tool_guides/tool_guide.md).

## How to set up PDF Upload with the Toolkit

To use Coral with document upload, simply use the `File_Upload_LlamaIndex` or `File_Upload_Langchain` (this needs a cohere API key in the .env file) tool or by adding your API key to the env file. Alternatively you can use any document uploader of your choosing, either with your own implementation or an integration implementation (such as LangChain) by following these [steps below](custom_tool_guides/tool_guide.md).

## How to create your own tools and retrieval sources

Toolkit includes some sample tools that you can copy to configure your own data sources:

- File loaders - Parses a PDF file and performs RAG. Enables users to upload PDF in Toolkit UI. Users have an option to use either Langchain or Llamaindex, whichever is preferred. Langchain is used by default.
- Data loaders - This tool queries a data source and then performs RAG on extracted documents. We used Langchain's Wikiretriever as the sample data source.
- Functions - Python interpreter and calculator tools.

To create your own tools or add custom data sources, see our guide: [tools and retrieval sources overview](custom_tool_guides/tool_guide.md)

## Theming and customization

To customize the Coral frontend, you can modify the theme, color scheme, font, and other styles. see our guide: [Theming and customization](/docs/theming.md)

# Use Experimental Features

**Please note that these are experimental features.**

## LangChain MultiHop

Chatting with multi hop tool usage through LangChain is enabled by setting experimental feature flag to True in `.env`. 

```bash
USE_EXPERIMENTAL_LANGCHAIN=True
```

By setting this flag to true, only tools that have a LangChain implementation can be utilized. 
These exist under `LANGCHAIN_TOOLS` and require a `to_lanchain_tool()` function on the tool implementation which returns a LangChain compatible tool. 
Python interpreter and Tavily Internet search are provided in the toolkit by default once the environment is set up.

Example API call:
```bash
curl --location 'http://localhost:8000/v1/langchain-chat' \
--header 'User-Id: me' \
--header 'Content-Type: application/json' \
--data '{
    "message": "Tell me about the aya model",
    "tools": [{"name": "Python_Interpreter"},{"name": "Internet_Search"}]
}'
```

Currently, citations are not supported in LangChain multi hop.
