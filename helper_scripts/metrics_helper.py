import json
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
            "model": "command-r",
            "deployment": "Cohere Platform",
            "tools": ["web_search"],
        },
    )
    print(response.status_code)
    agent_id = response.json()["id"]
    # # List Agents
    response = requests.get(f"{base_url}/agents", headers=headers)
    print(response.status_code)

    # # Get Agent
    response = requests.get(f"{base_url}/agents/{agent_id}", headers=headers)
    print(response.status_code)

    # # Update Agent
    response = requests.put(
        f"{base_url}/agents/{agent_id}", headers=headers, json={"name": "new_name"}
    )
    print(response.status_code)

    return agent_id


## Users
# Create User
def users():
    print ("running users")
    # # List Users
    res =  requests.get(f"{base_url}/users", headers=headers)
    print(response.status_code)
    # # Get User
    res =  requests.get(f"{base_url}/users/{user_id}", headers=headers)
    print(response.status_code)
    # # Update User
    res =  requests.put(
        f"{base_url}/users/{user_id}", headers=headers, json={"fullname": "new name"}
    )
    print(response.status_code)


# Chat
def chat(agent_id):
    print("Running chat")

    response = requests.post(
        f"http://localhost:8000/v1/chat-stream?agent_id={agent_id}",
        headers=headers,
        json={
            "message": "who is bo burnham?",
            "tools": [{"name": "web_search"}],
        },
    )

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
    ## Tools
    # List Tools
    _ = requests.get(f"{base_url}/tools", headers=headers)

    # List Tools per Agent
    _ = requests.get(f"{base_url}/tools?agent_id={agent_id}", headers=headers)

    ## Conversations
    # List Conversations
    _ = requests.get(f"{base_url}/conversations", headers=headers)

    # Get Conversation
    _ = requests.get(f"{base_url}/conversations/{conversation_id}", headers=headers)

    # Update Conversation
    _ = requests.put(
        f"{base_url}/conversations/{conversation_id}",
        headers=headers,
        json={"title": "new_title"},
    )

    # del conversation
    _ = requests.delete(f"{base_url}/conversations/{conversation_id}", headers=headers)


# Delete Everything
def cleanup(user_id, agent_id):
    print("cleaning up")
    response = requests.delete(f"{base_url}/users/{user_id}", headers=headers)
    print(response.status_code)
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


# users()
agent_id = agents()
cleanup(user_id=user_id, agent_id=agent_id)
# TODO: these are not working atm
# conversation_id = chat(agent_id=agent_id)
# tools(conversation_id=conversation_id)
