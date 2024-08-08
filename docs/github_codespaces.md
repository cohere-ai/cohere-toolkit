# Setting Up Cohere Toolkit with GitHub Codespaces

This guide will walk you through the process of setting up and running the Cohere Toolkit project using GitHub Codespaces. Codespaces provides a complete, configurable dev environment in the cloud, making it easy to get started with the project quickly.

## Prerequisites

- A GitHub account
- Access to the Cohere Toolkit repository

## Steps to Set Up and Run

1. **Open the Cohere Toolkit Repository**
   - Navigate to the [Cohere Toolkit repository](https://github.com/cohere-ai/cohere-toolkit) on GitHub.

2. **Launch a Codespace**
   - Click on the "Code" button (green button near the top-right of the repository page).
   - Select the "Codespaces" tab.
   - Click on "Create codespace on main" to start a new Codespace.

3. **Wait for the Codespace to Initialize**
   - GitHub will now create a new Codespace for you. This may take a few minutes.
   - Once ready, you'll see a VS Code-like interface in your browser.

4. **Run the Initialization Script**
   - Once your Codespace is ready, open a new terminal in the Codespace.
   - Run the following command to set up the environment:
     ```bash
     sh .devcontainer/init.sh
     ```
   - This script will handle necessary setup tasks defined for the project.

5. **Configure Environment Variables**
   - Open the `.env` file in the Codespace.
   - Add your Cohere API key and/or any other necessary credentials:
     ```
     COHERE_API_KEY=your_api_key_here
     ```
   - Save the file.

6. **Start the Application**
   - In the terminal, run the following command to start the Toolkit:
     ```bash
     make up
     ```

7. **Access the Application**
   - Once the application is running, Codespaces will prompt you that a service is available on port 4000.
   - Click on the "Open in Browser" button when this prompt appears.
   - Alternatively, you can go to the "Ports" tab and click on the link for port 4000.

8. **Start Using Cohere Toolkit**
   - You should now see the Cohere Toolkit interface in your browser.
   - Begin interacting with the model and exploring the Toolkit's features.

## Troubleshooting

- If you encounter any issues with package installations, try rebuilding the Codespace:
  - Go to the command palette (Ctrl+Shift+P or Cmd+Shift+P).
  - Type and select "Codespaces: Rebuild Container".

- For any persistent issues, refer to the [main troubleshooting guide](/docs/troubleshooting.md) or open an issue on the GitHub repository.

## Stopping and Managing Your Codespace

- To stop your Codespace, you can simply close the browser tab. The Codespace will automatically stop after a period of inactivity.
- To manage your Codespaces (including deletion), visit [github.com/codespaces](https://github.com/codespaces).

Remember, Codespaces usage may incur charges depending on your GitHub plan. Be sure to stop your Codespace when you're not using it to avoid unnecessary costs.

## Next Steps

Now that you have the Cohere Toolkit running in a Codespace, you can start exploring its features, customizing the application, or contributing to the project. Refer to the main [README.md](../README.md) and other documentation for more information on how to use and extend the Toolkit.
