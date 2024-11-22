# How-To Guides

## How to Use Community Features

By default, the toolkit operates without community tools or deployments. To enable them, add the following line to the `configuration.yaml` file or use the `make setup` command:

```yaml
feature_flags.use_community_features: true
```

## How to Add Your Own Model Deployment

To add a custom deployment:

1. Create a deployment file and place it in the [/community/model_deployments](https://github.com/cohere-ai/cohere-toolkit/tree/main/src/community/model_deployments) folder.
2. Implement the function calls from `BaseDeployment`, similar to existing deployments.
3. Register the deployment in [src/community/config/deployments.py](https://github.com/cohere-ai/cohere-toolkit/blob/main/src/community/config/deployments.py).
4. Add the necessary environment variables to the environment template.

**For a Cohere private deployment:**
- Follow the same steps, copying the Cohere platform implementation.
- Modify the `base_url` for your private deployment and include any custom authentication steps.

## How to Call the Backend as an API

You can run the backend service and interact with it similarly to the Cohere API. Note that streaming and non-streaming endpoints are differentiated as follows:
- Streaming: `http://localhost:8000/v1/chat-stream`
- Non-streaming: `http://localhost:8000/v1/chat`

### Example API Call for Streaming:
```bash
curl --location 'http://localhost:8000/v1/chat-stream' \
--header 'User-Id: me' \
--header 'Content-Type: application/json' \
--data '{
    "message": "Tell me about the aya model"
}'
```

## How to Add Your Own Chat Interface

The core chat interface is the Coral frontend. To implement your own interface:
1. Use the backend API calls as described above in your implementation.
2. Place your interface code alongside `src/community/interfaces/`.

## How to Add a Connector to the Toolkit

If you have already created a [connector](https://docs.cohere.com/docs/connectors), you can utilize it within the toolkit by following these steps:

1. Configure your connector using `ConnectorRetriever`.
2. Add its definition in [community/config/tools.py](https://github.com/cohere-ai/cohere-toolkit/blob/main/src/community/config/tools.py), following the `Arxiv` implementation, using the category `ToolCategory.DataLoader`.

You can now use both the Coral frontend and API with your connector.

## How to Set Up Web Search with the Toolkit

To integrate Coral with web search, utilize the `Tavily_Internet_Search` tool by adding your API key to the configuration file. Alternatively, you can implement your own search provider by following these [steps](custom_tool_guides/tool_guide.md).

## How to Set Up PDF Upload with the Toolkit

For document uploads in Coral, use `File_Upload_LlamaIndex` (this requires a Cohere API key in the configuration file). You can also implement a custom document uploader by following the [steps here](custom_tool_guides/tool_guide.md).

## How to Create Your Own Tools and Retrieval Sources

The toolkit includes sample tools that you can copy to configure your own data sources, including:

- **File Loaders**: Parses PDF files and performs RAG (Retrieval-Augmented Generation). Users can upload PDFs in the Toolkit UI.
- **Data Loaders**: Queries a data source and performs RAG on extracted documents.
- **Functions**: Includes tools like a Python interpreter and calculator.

For guidance on creating your own tools or adding custom data sources, see the [tools and retrieval sources overview](custom_tool_guides/tool_guide.md).

## Theming and Customization

To customize the Coral frontend, modify the theme, color scheme, font, and other styles. Refer to our guide on [Theming and Customization](/docs/theming.md).
