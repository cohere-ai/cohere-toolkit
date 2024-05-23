![](/docs/assets/banner.png)

# Cohere Toolkit

Toolkit is a collection of prebuilt components enabling users to quickly build and deploy RAG applications.

- [Try Toolkit](#try-now)
- [About Toolkit](#about-toolkit)
- [Toolkit Setup](/docs/setup.md)
- [Troubleshooting](/docs/troubleshooting.md)
- [How to guides](/docs/how_to_guides.md)
  - [How to set up command model providers](/docs/command_model_providers.md)
  - [How to add tools](/docs/custom_tool_guides/tool_guide.md)
  - [How to add authentication](/docs/auth_guide.md)
  - [How to deploy toolkit services](/docs/service_deployments.md)
  - [How to customize the theme](/docs/theming.md)
  - [How to contribute](#contributing)
- [Try Cohere's Command Showcase](https://coral.cohere.com/)

![](/docs/assets/toolkit.gif)

## Try Now:

Try the default Toolkit application yourself by deploying it in a container locally. Either with `docker run`: 
```bash

docker run -e COHERE_API_KEY='>>YOUR_API_KEY<<' -p 8000:8000 -p 4000:4000 ghcr.io/cohere-ai/cohere-toolkit:latest

```

or cloning and running locally:

```bash
git clone https://github.com/cohere-ai/cohere-toolkit.git
make first-run
```

Go to [localhost:4000](http://localhost:4000/) in your browser and start chatting with the model. 

*For the above you will need to have [Docker](https://www.docker.com/products/docker-desktop/) and [Docker-compose >= 2.22](https://docs.docker.com/compose/install/) installed. [Go here for a more detailed setup.](/docs/setup.md)*

## About Toolkit

![](/docs/assets/toolkit_graphic.png)

- **Interfaces** - these can be any frontend, application, bot or integration. You can customize any type of interface for your use case. By default included is: 
  - Cohere's Web UI at `src/interfaces/coral_web` - A web app built in Next.js. Includes a simple SQL database out of the box to store conversation history in the app.
- **Backend API** - `src/backend` this follows a similar structure to the [Cohere Chat API](https://docs.cohere.com/reference/chat) but also include customizable elements: 
  - **Model** - you can customize with which provider you access Cohere's Command models. By default included in the toolkit is Cohere's Platform, Sagemaker, Azure, Bedrock, HuggingFace, local models. [More details here.](/docs/command_model_providers.md)
  - **Retrieval**- you can customize tools and data sources that the application is run with. By default, we have configured a Langchain data retriever to test RAG on Wikipedia and your own uploaded documents. It is possible to add any tool including any tools or retrievers from LangChain or LlamaIndex. You can also use a connector you have created.
- **Service Deployment Guides** - we also include guides for how to deploy the toolkit services in production including with AWS, GCP and Azure. [More details here.](/docs/service_deployments.md)

## Contributing

Contributions are what drive an open source community, any contributions made are greatly appreciated. To get started, check out our [documentation.](CONTRIBUTING.md)


## Contributors

<a href="https://github.com/cohere-ai/cohere-toolkit/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=cohere-ai/cohere-toolkit" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

### Deploying to Google Cloud Run

Before deploying to Google Cloud Run, you'll need a postgres database accessible to your Google Cloud Project, authenticated by a username and password. You'll be prompted for a `DATABASE_URL` before the container builds.

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)