import json
import re

import requests

base_url = "http://localhost:8000/v1"

headers = {
    "User-Id": "7a7e4a99-10af-4567-955b-8f34ed5e2f1d",
    "Deployment-Name": "Cohere Platform",
    "Content-Type": "application/json",
}

# Notes:
# web_search implicitly calls rerank
# - TAVILY_API_KEY required for web search
# in case of issues, prune docker images and try again


## Users
# Create User
response = requests.post(f"{base_url}/users", headers=headers, json={"fullname": "me"})
response_json = response.json()
user_id = response_json["id"]


def agents():
    print("Running Agents")
    ## Agents
    # Create Agent
    response = requests.post(
        f"{base_url}/agents",
        headers=headers,
        json={
            "name": "hello-world",
            "model": "command-r",
            "deployment": "Cohere Platform",
            "tools": ["web_search"],
        },
    )
    agent_id = response.json()["id"]
    # # List Agents
    _ = requests.get(f"{base_url}/agents", headers=headers)

    # # Get Agent
    _ = requests.get(f"{base_url}/agents/{agent_id}", headers=headers)

    # # Update Agent
    _ = requests.put(
        f"{base_url}/agents/{agent_id}", headers=headers, json={"name": "new_name"}
    )

    return agent_id


def users():
    # # List Users
    _ = requests.get(f"{base_url}/users", headers=headers)

    # # Get User
    _ = requests.get(f"{base_url}/users/{user_id}", headers=headers)

    # # Update User
    _ = requests.put(
        f"{base_url}/users/{user_id}", headers=headers, json={"fullname": "new name"}
    )


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


## Files
# _ = requests.get(f"{base_url}/files/conversation_id", headers=headers)
# _ = requests.put(f"{base_url}/files/test-file-id", headers=headers, data={"title": "new_title"})
# _ = requests.delete(f"{base_url}/files/test-file-id", headers=headers)


# Delete Everything
def cleanup(user_id, agent_id):
    _ = requests.delete(f"{base_url}/users/{user_id}", headers=headers)
    _ = requests.delete(f"{base_url}/agents/{agent_id}", headers=headers)


agent_id = agents()
conversation_id = chat(agent_id=agent_id)

tools(conversation_id=conversation_id)
users()
cleanup(user_id=user_id, agent_id=agent_id)
