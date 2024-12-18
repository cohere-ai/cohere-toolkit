### 1. **Create an Authentication Class**
You need to create a class specifically for your tool's authentication. For great examples, check out the implementations for GMail, GDrive or Slack.

### 2. **Inheritance**
Your authentication class should inherit from:
- `BaseToolAuthentication`: Provides the base interface and required methods for implementing tool authentication.
- `ToolAuthenticationCacheMixin`: Handles caching the authentication tokens for tools.

### 3. **Required Methods**
The following methods are mandatory for the authentication class:

#### a. `get_auth_url(self, user_id: str) -> str`
- **Purpose**: This method generates the URL that the frontend will use to initiate the authentication process. This typically starts the Single Sign-On (SSO) process by redirecting the user to an authorization provider (e.g., Google OAuth, GitHub, etc.).
- **Implementation**: You need to build a URL that your tool uses to authenticate users. This usually involves appending parameters such as the client ID, redirect URI, and any other authorization parameters.

#### Example:
```python
class MyToolAuth(BaseToolAuthentication, ToolAuthenticationCacheMixin):
    def get_auth_url(self, user_id: str) -> str:
        # Build and return the authentication URL for the frontend
        return f"https://mytool.com/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
```

#### b. `try_refresh_token(self, session: DBSessionDep, user_id: str, tool_auth: ToolAuth) -> bool`
- **Purpose**: Optionally, if your SSO provider offers refresh tokens, this method will implement the logic to refresh the access token when it expires. If you do not need to handle token refreshing, simply return `False`.
- **Implementation**: This method should communicate with the provider's token endpoint to refresh the token and return `True` if successful, `False` otherwise.

#### Example:
```python
def try_refresh_token(self, session: DBSessionDep, user_id: str, tool_auth: ToolAuth) -> bool:
    # Example logic to refresh the token
    refresh_token = tool_auth.refresh_token
    if refresh_token:
        response = requests.post("https://mytool.com/oauth2/token", data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        })
        if response.status_code == 200:
            new_access_token = response.json().get('access_token')
            # Update the tool_auth in the database with the new token
            tool_auth.access_token = new_access_token
            session.commit()
            return True

    return False
```

#### c. `retrieve_auth_token(self, request: Request, session: DBSessionDep, user_id: str) -> str`
- **Purpose**: This method handles the logic for retrieving the access token. After the user is redirected back to the app (e.g., after granting permission via OAuth), the code or token provided by the OAuth provider needs to be exchanged for an access token.
- **Implementation**: Typically, this involves consuming a `code` query parameter returned by the authorization provider and then making a request to the provider's token endpoint to get the actual access token.

#### Example:
```python
def retrieve_auth_token(self, request: Request, session: DBSessionDep, user_id: str) -> str:
    # Get the authorization code from the query parameters
    auth_code = request.query_params.get("code")
    if not auth_code:
        raise ValueError("Authorization code missing")

    # Exchange the authorization code for an access token
    response = requests.post("https://mytool.com/oauth2/token", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
    })

    if response.status_code != 200:
        raise ValueError("Failed to retrieve access token")

    # Extract the access token from the response
    access_token = response.json().get("access_token")

    # Save the token to the database for the user
    tool_auth = ToolAuth(user_id=user_id, access_token=access_token)
    session.add(tool_auth)
    session.commit()

    return access_token
```

### 4. **Integrate the Auth Class**
Once you've created your authentication class, integrate it into your tool’s configuration so that the frontend can use it for authenticating users when interacting with the tool.

To do so, go to your tool's `get_tool_definition` method and add:
`auth_implementation=<YourAuthClass>,`
