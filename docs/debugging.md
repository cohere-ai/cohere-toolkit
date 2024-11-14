# How to debug dockerized Toolkit API VSCode/PyCharm
This guide will walk you through the process of debugging the dockerized Toolkit API using VSCode or PyCharm. 
Debugging allows you to inspect the code, set breakpoints, and step through the code execution to identify and fix issues.

## VSCode
To debug the dockerized Toolkit API using VSCode, follow these steps:
- Pull and open the Toolkit project in VSCode.
- Open the `.vscode/launch.json` file if exists or create a new one.
- Add the following configuration to the `configurations` array in the `launch.json` file:
```json
{
    "configurations": [
        {
            "name": "Python Debugger: Remote Attach to Toolkit",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/src/backend",
                    "remoteRoot": "/workspace/src/backend/"
                }
            ]
        },
     ................ your other configurations here(if not exists just remove the comma)..........
    ]
}  
```
- Start the Toolkit API in debug mode by running the following command:
```bash
make vscode-debug
```
- Set breakpoints in the code where you want to pause the execution
- Run the debugger by selecting the `Python Debugger: Remote Attach to Toolkit` configuration in the debug panel and clicking the play button.
![](/docs/assets/vscode_debug.png)
- The debugger will connect to the running API and pause at the breakpoints you set.

## PyCharm
To debug the dockerized Toolkit API using PyCharm, follow these steps:
- Pull and open the Toolkit project in PyCharm.
- Set the Project interpreter to the Python interpreter in the docker container.
  - Go to `PyCharm > Settings > Project: <project_name> > Python Interpreter` (Click `⌘Сmd,` on Mac).
  - Click `Add interpreter` and select `On Docker Compose`.
  ![](/docs/assets/pycharm_settings.png)
  - Choose the `docker-compose.pycharm.debug.yml` file and select the service name `backend`.
  ![](/docs/assets/pycharm_settings_interpreter.png)
  - Click `Next` to apply the changes.
  - Click `Next` after setup will be completed, click `Create` to create the new interpreter.
  - Click `Apply` and `OK` to save the changes.
- Set the breakpoints in the code where you want to pause the execution.
![](/docs/assets/pycharm_debug_breakpoint.png)
- Run next command to start the toolkit in debug mode:
```bash
make pycharm-debug
```
- To create a new debug configuration, chose `Run > Edit Configurations` from the menu. 
![](/docs/assets/pycharm_edit_config.png)
- Click on the `+` button and select `Python`
![](/docs/assets/pycharm_debug_python.png)
- Set the following configuration:
  - Name: `Toolkit Docker Debug`
  - Python interpreter: Select the interpreter you created in the previous step.
  - Script path: `src/backend/pycharm_debug_main.py`
  - Working directory: root directory of the project (e.g., `/path/to/cohere-toolkit`)
  - Clik `Apply` and `OK` to save the configuration.
![](/docs/assets/pycharm_debug_final_step.png)
- Run the debugger by selecting the `Toolkit Docker Debug` configuration in the debug panel and clicking the bug button.
- The debugger will connect to the running API and pause at the breakpoints you set.
- You can now inspect the code, set new breakpoints, step through the execution, and identify and fix issues.
- Debug breakpoints will be hit as the code is executed. For example by interacting with the Toolkit frontend.
- To stop the debugger, click the stop button in the debug panel.
