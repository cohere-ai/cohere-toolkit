import re
import json
import requests

base_url = "http://localhost:8000/v1"

headers = {
    "User-Id": "me",
    "Deployment-Name": "Cohere Platform",
    "Content-Type": "application/json",
}

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
            "name": "New agent",
            "model": "command-r",
            "deployment": "Cohere Platform",
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
    _ = requests.delete(f"{base_url}/agents/{agent_id}", headers=headers)

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
def chat():
    print("Running Agents")
    
    response = requests.post(
        "http://localhost:8000/v1/chat-stream",
        headers=headers,
        json={"message": "who is bo burnham?", "tools": [{"name": "Wikipedia"}]},
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


def tools():
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
def del_user():
    _ = requests.delete(f"{base_url}/users/{user_id}", headers=headers)
    

agents()
chat()
users()
del_user()