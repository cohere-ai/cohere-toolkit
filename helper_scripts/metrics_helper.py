import re
from uuid import uuid4

import requests


def agents():
    print("Running Agents")
    ## Agents
    # Create Agent
    response = requests.post(
        f"{base_url}/agents",
        headers=headers,
        json={
            "name": str(uuid4()),
            "version": 1,
            "description": "test description",
            "preamble": "test preamble",
            "temperature": 0.5,
            "model": "command-r-plus",
            "deployment": "Cohere Platform",
            "tools": [
                "search_file",
                "read_document",
                "toolkit_calculator",
                "wikipedia",
            ],
        },
    )
    print("create agent")
    print(response.status_code)
    agent_id = response.json()["id"]
    # # List Agents
    response = requests.get(f"{base_url}/agents", headers=headers)
    print("list agents")
    print(response.status_code)

    # # Get Agent
    response = requests.get(f"{base_url}/agents/{agent_id}", headers=headers)
    print("get agent")
    print(response.status_code)

    # # Update Agent
    response = requests.put(
        f"{base_url}/agents/{agent_id}", headers=headers, json={"name": str(uuid4())}
    )
    print("update agent")
    print(response.status_code)
    # print(response.json())

    return agent_id


## Users
# Create User
def users():
    print("running users")
    # # List Users
    res = requests.get(f"{base_url}/users", headers=headers)
    print(response.status_code)
    # # Get User
    res = requests.get(f"{base_url}/users/{user_id}", headers=headers)
    print(response.status_code)
    # # Update User
    res = requests.put(
        f"{base_url}/users/{user_id}", headers=headers, json={"fullname": "new name"}
    )
    print(response.status_code)


# Chat
def chat(agent_id):
    print("Running chat")

    response = requests.post(
        f"http://localhost:8000/v1/chat-stream?agent_id={agent_id}",
        headers=headers,
        json={"message": "who is bo burnham?", "tools": [{"name": "web_search"}]},
    )

    print(response.status_code)

    conversation_id = None
    for event in response.iter_lines():
        if not event:
            continue

        str_event = str(event)

        if "stream-start" in str_event:
            match = re.search(r'"conversation_id": "([^"]*)"', str_event)
            if match:
                conversation_id = match.group(1)

    return conversation_id


def tools(conversation_id):
    print("Running tools")
    ## Tools
    # List Tools
    res = requests.get(f"{base_url}/tools", headers=headers)
    print(res.status_code)
    # List Tools per Agent
    res = requests.get(f"{base_url}/tools?agent_id={agent_id}", headers=headers)
    print(res.status_code)
    ## Conversations
    # List Conversations
    res = requests.get(f"{base_url}/conversations", headers=headers)
    print(res.status_code)
    # Get Conversation
    res = requests.get(f"{base_url}/conversations/{conversation_id}", headers=headers)
    print(res.status_code)
    # Update Conversation
    res = requests.put(
        f"{base_url}/conversations/{conversation_id}",
        headers=headers,
        json={"title": "new_title"},
    )

    # del conversation
    res = requests.delete(
        f"{base_url}/conversations/{conversation_id}", headers=headers
    )
    print(res.status_code)


# Delete Everything
def cleanup(user_id, agent_id):
    print("cleaning up")
    response = requests.delete(f"{base_url}/users/{user_id}", headers=headers)
    print(response.status_code)
    if agent_id:
        response = requests.delete(f"{base_url}/agents/{agent_id}", headers=headers)
        print(response.status_code)


base_url = "http://localhost:8000/v1"
headers = {
    "User-Id": "admin",
    "Deployment-Name": "Cohere Platform",
    "Content-Type": "application/json",
}

# Notes:
# web_search implicitly calls rerank
# - TAVILY_API_KEY required for web search
# in case of issues, prune docker images and try again
# TODO: please do not use global variables :,(

# initial setup
print("setting up")
response = requests.post(
    f"{base_url}/users", headers=headers, json={"fullname": "qa tester"}
)
response_json = response.json()
user_id = response_json["id"]
# update user id with correct value going forward
headers["User-Id"] = user_id
print("Setup user info")
print(response_json)


# TODO: make these into tests
users()
agent_id = None
agent_id = agents()
conversation_id = chat(agent_id=agent_id)
tools(conversation_id=conversation_id)
cleanup(user_id=user_id, agent_id=agent_id)
