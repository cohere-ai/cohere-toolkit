import { FetchEventSourceInit, fetchEventSource } from '@microsoft/fetch-event-source';

import {
  Body_upload_file_v1_conversations_upload_file_post,
  CancelablePromise,
  CohereChatRequest,
  CohereClientGenerated,
  CohereNetworkError,
  CreateAgent,
  CreateUser,
  ExperimentalFeatures,
  Fetch,
  UpdateAgent,
  UpdateConversation,
  UpdateDeploymentEnv,
} from '@/cohere-client';

<<<<<<< HEAD
  constructor(reason: keyof typeof ERROR_FINISH_REASON_TO_MESSAGE) {
    const message = ERROR_FINISH_REASON_TO_MESSAGE[reason];
    super(message);
    this.reason = reason;
  }
}

export class CohereStreamError extends Error {
  public code: number;

  constructor(message: string, code: number) {
    super(message);
    this.code = code;
  }
}

export class CohereUnauthorizedError extends Error {
  constructor() {
    super('Unauthorized');
  }
}

export type Fetch = (input: RequestInfo, init?: RequestInit) => Promise<Response>;

export type ExperimentalFeatures = {
  USE_EXPERIMENTAL_LANGCHAIN: boolean;
  USE_AGENTS_VIEW: boolean;
};
=======
import { mapToChatRequest } from './mappings';
>>>>>>> main

export class CohereClient {
  private readonly hostname: string;
  private readonly fetch: Fetch;
<<<<<<< HEAD
  private readonly source: string;
  private authToken?: string;
  private onAuthTokenUpdate?: (authToken?: string) => void;
=======
  private authToken?: string;
>>>>>>> main

  public cohereService: CohereClientGenerated;
  public request?: any;

  constructor({
    hostname,
<<<<<<< HEAD
    source,
    fetch,
    authToken,
    onAuthTokenUpdate,
  }: {
    hostname: string;
    source: string;
    fetch: Fetch;
    authToken?: string;
    onAuthTokenUpdate?: (authToken?: string) => void;
=======
    fetch,
    authToken,
  }: {
    hostname: string;
    fetch: Fetch;
    authToken?: string;
>>>>>>> main
  }) {
    this.hostname = hostname;
    this.fetch = fetch;
    this.authToken = authToken;
<<<<<<< HEAD
    if (onAuthTokenUpdate) {
      this.onAuthTokenUpdate = onAuthTokenUpdate;
    }
  }

  private handleAuthTokenUpdate(response: Response) {
    const headers = response.headers;
    const authToken = headers.get('X-Toolkit-Auth-Update');
    if (authToken) {
      this.authToken = authToken;
    }
    this.onAuthTokenUpdate?.(this.authToken);
=======
    this.cohereService = new CohereClientGenerated({
      BASE: hostname,
      HEADERS: this.getHeaders(true),
    });
>>>>>>> main
  }

  public uploadFile(formData: Body_upload_file_v1_conversations_upload_file_post) {
    return this.cohereService.default.uploadFileV1ConversationsUploadFilePost({
      formData,
    });
<<<<<<< HEAD

    this.handleAuthTokenUpdate(response);
    const body = await response.json();

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as UploadFile;
=======
>>>>>>> main
  }

  public deletefile({ conversationId, fileId }: { conversationId: string; fileId: string }) {
    return this.cohereService.default.deleteFileV1ConversationsConversationIdFilesFileIdDelete({
      conversationId,
      fileId,
    });
<<<<<<< HEAD

    this.handleAuthTokenUpdate(response);
    const body = await response.json();

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as {};
  }

  public async listFiles({ conversationId }: { conversationId: string }): Promise<ListFile[]> {
    const response = await this.fetch(
      `${this.getEndpoint('conversations')}/${conversationId}/files`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    this.handleAuthTokenUpdate(response);
    const body = await response.json();

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as ListFile[];
=======
  }

  public listFiles({ conversationId }: { conversationId: string }) {
    return this.cohereService.default.listFilesV1ConversationsConversationIdFilesGet({
      conversationId,
    });
>>>>>>> main
  }

  public async chat({
    request,
    headers,
    agentId,
    signal,
    onOpen,
    onMessage,
    onClose,
    onError,
  }: {
    request: CohereChatRequest;
    headers?: Record<string, string>;
    agentId?: string;
    signal?: AbortSignal;
    onOpen?: FetchEventSourceInit['onopen'];
    onMessage?: FetchEventSourceInit['onmessage'];
    onClose?: FetchEventSourceInit['onclose'];
    onError?: FetchEventSourceInit['onerror'];
  }) {
    const handleAuthUpdateOnOpen = async (response: Response) => {
      this.handleAuthTokenUpdate(response);
      onOpen?.(response);
    }
    const chatRequest = mapToChatRequest(request);
    const requestBody = JSON.stringify({
      ...chatRequest,
    });

    const endpoint = `${this.getEndpoint('chat-stream')}${agentId ? `?agent_id=${agentId}` : ''}`;
    return await fetchEventSource(endpoint, {
      method: 'POST',
      headers: { ...this.getHeaders(), ...headers },
      body: requestBody,
      signal,
      onopen: handleAuthUpdateOnOpen,
      onmessage: onMessage,
      onclose: onClose,
      onerror: onError,
    });
  }

  public async langchainChat({
    request,
    headers,
    signal,
    onOpen,
    onMessage,
    onClose,
    onError,
  }: {
    request: CohereChatRequest;
    headers?: Record<string, string>;
    signal?: AbortSignal;
    onOpen?: FetchEventSourceInit['onopen'];
    onMessage?: FetchEventSourceInit['onmessage'];
    onClose?: FetchEventSourceInit['onclose'];
    onError?: FetchEventSourceInit['onerror'];
  }) {
    const handleAuthUpdateOnOpen = async (response: Response) => {
      this.handleAuthTokenUpdate(response);
      onOpen?.(response);
    }
    const chatRequest = mapToChatRequest(request);
    const requestBody = JSON.stringify({
      ...chatRequest,
    });
    return await fetchEventSource(this.getEndpoint('langchain-chat'), {
      method: 'POST',
      headers: { ...this.getHeaders(), ...headers },
      body: requestBody,
      signal,
      onopen: handleAuthUpdateOnOpen,
      onmessage: onMessage,
      onclose: onClose,
      onerror: onError,
    });
  }

<<<<<<< HEAD
  public async listConversations({
    signal,
  }: {
    signal?: AbortSignal;
  }): Promise<ConversationWithoutMessages[]> {
    const response = await this.fetch(`${this.getEndpoint('conversations')}`, {
      method: 'GET',
      headers: this.getHeaders(),
      signal,
    });

    this.handleAuthTokenUpdate(response);
    const body = await response.json();

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as ConversationWithoutMessages[];
=======
  public listConversations(params: { offset?: number; limit?: number; agentId?: string }) {
    return this.cohereService.default.listConversationsV1ConversationsGet(params);
>>>>>>> main
  }

  public getConversation({ conversationId }: { conversationId: string }) {
    return this.cohereService.default.getConversationV1ConversationsConversationIdGet({
      conversationId,
    });
<<<<<<< HEAD

    this.handleAuthTokenUpdate(response);
    const body = await response.json();

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as Conversation;
=======
>>>>>>> main
  }

  public deleteConversation({ conversationId }: { conversationId: string }) {
    return this.cohereService.default.deleteConversationV1ConversationsConversationIdDelete({
      conversationId,
    });
  }

<<<<<<< HEAD
    this.handleAuthTokenUpdate(response);
    const body = await response.json();

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }
=======
  public editConversation(requestBody: UpdateConversation, conversationId: string) {
    return this.cohereService.default.updateConversationV1ConversationsConversationIdPut({
      conversationId: conversationId,
      requestBody,
    });
  }

  public listTools({ agentId }: { agentId?: string | null }) {
    return this.cohereService.default.listToolsV1ToolsGet({ agentId });
  }
>>>>>>> main

  public listDeployments({ all }: { all?: boolean }) {
    return this.cohereService.default.listDeploymentsV1DeploymentsGet({ all });
  }

  public updateDeploymentEnvVariables(requestBody: UpdateDeploymentEnv, name: string) {
    return this.cohereService.default.setEnvVarsV1DeploymentsNameSetEnvVarsPost({
      name: name,
      requestBody,
    });
  }

<<<<<<< HEAD
    this.handleAuthTokenUpdate(response);
    const body = await response.json();

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as Conversation;
=======
  public getExperimentalFeatures() {
    return this.cohereService.default.listExperimentalFeaturesV1ExperimentalFeaturesGet() as CancelablePromise<ExperimentalFeatures>;
>>>>>>> main
  }

  public login({ email, password }: { email: string; password: string }) {
    return this.cohereService.default.loginV1LoginPost({
      requestBody: {
        strategy: 'Basic',
        payload: { email, password },
      },
    });
  }

<<<<<<< HEAD
    this.handleAuthTokenUpdate(response);
    const body = await response.json();

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }
=======
  public logout() {
    return this.cohereService.default.logoutV1LogoutGet();
  }

  public getAuthStrategies() {
    return this.cohereService.default.getStrategiesV1AuthStrategiesGet();
  }
>>>>>>> main

  public createUser(requestBody: CreateUser) {
    return this.cohereService.default.createUserV1UsersPost({
      requestBody,
    });
  }

  public async googleSSOAuth({ code }: { code: string }) {
    const response = await this.fetch(`${this.getEndpoint('google/auth')}?code=${code}`, {
      method: 'POST',
      headers: this.getHeaders(),
    });

    this.handleAuthTokenUpdate(response);
    const body = await response.json();
    this.authToken = body.token;

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError('Something went wrong', response.status);
    }

    return body as { token: string };
    // FIXME(@tomtobac): generated code doesn't have code as query parameter (TLK-765)
    // this.cohereService.default.googleAuthorizeV1GoogleAuthGet();
  }

<<<<<<< HEAD
  public async listAllDeployments(): Promise<Deployment[]> {
    const response = await this.fetch(`${this.getEndpoint('deployments')}?all=1`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    this.handleAuthTokenUpdate(response);
    const body = await response.json();

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
=======
  public async oidcSSOAuth({
    code,
    strategy,
    codeVerifier,
  }: {
    code: string;
    strategy: string;
    codeVerifier?: string;
  }) {
    const body: any = {};

    if (codeVerifier) {
      // Conditionally add codeVerifier to the body
      body.code_verifier = codeVerifier;
>>>>>>> main
    }

    const response = await this.fetch(
      `${this.getEndpoint('oidc/auth')}?code=${code}&strategy=${strategy}`,
      {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(body),
      }
    );

<<<<<<< HEAD
    this.handleAuthTokenUpdate(response);

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }
=======
    const payload = await response.json();
    this.authToken = body.token;
>>>>>>> main

    if (response.status !== 200) {
      throw new CohereNetworkError('Something went wrong', response.status);
    }

    return payload as { token: string };
    // FIXME(@tomtobac): generated code doesn't have code as query parameter (TLK-765)
    // this.cohereService.default.oidcAuthorizeV1OidcAuthGet();
  }

  public getAgent(agentId: string) {
    return this.cohereService.default.getAgentByIdV1AgentsAgentIdGet({ agentId });
  }

<<<<<<< HEAD
    this.handleAuthTokenUpdate(response);
    const body = await response.json();

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }
=======
  public createAgent(requestBody: CreateAgent) {
    return this.cohereService.default.createAgentV1AgentsPost({ requestBody });
  }

  public listAgents({ offset, limit = 100 }: { offset?: number; limit?: number }) {
    return this.cohereService.default.listAgentsV1AgentsGet({ offset, limit });
  }
>>>>>>> main

  public updateAgent(requestBody: UpdateAgent, agentId: string) {
    return this.cohereService.default.updateAgentV1AgentsAgentIdPut({
      agentId: agentId,
      requestBody,
    });
  }

  public generateTitle({ conversationId }: { conversationId: string }) {
    return this.cohereService.default.generateTitleV1ConversationsConversationIdGenerateTitlePost({
      conversationId,
    });
  }

<<<<<<< HEAD
  public async login({ email, password }: { email: string; password: string }) {
    const response = await this.fetch(`${this.getEndpoint('login')}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        strategy: 'Basic',
        payload: { email, password },
      }),
    });

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    const body = await response.json();
    this.authToken = body.token;

    if (response.status !== 200) {
      throw new CohereNetworkError('Something went wrong', response.status);
    }

    return body as { token: string };
  }

  public async logout() {
    const response = await this.fetch(`${this.getEndpoint('logout')}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    this.authToken = undefined;

    if (response.status !== 200) {
      throw new CohereNetworkError('Something went wrong', response.status);
    }
  }

  public async getAuthStrategies() {
    const response = await this.fetch(`${this.getEndpoint('auth_strategies')}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    this.handleAuthTokenUpdate(response);
    const body = await response.json();

    if (response.status !== 200) {
      throw new CohereNetworkError('Something went wrong', response.status);
    }

    return body as { strategies: string[] };
  }

  public async createUser({
    name,
    email,
    password,
  }: {
    name: string;
    email: string;
    password: string;
  }) {
    const response = await this.fetch(`${this.getEndpoint('users')}/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        fullname: name,
        email,
        password,
      }),
    });

    const body = await response.json();

    if (response.status !== 200) {
      throw new CohereNetworkError('Something went wrong', response.status);
    }

    return body as {};
  }

  public async googleSSOAuth({ code }: { code: string }) {
    const response = await this.fetch(`${this.getEndpoint('google/auth')}?code=${code}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    const body = await response.json();
    this.authToken = body.token;

    if (response.status !== 200) {
      throw new CohereNetworkError('Something went wrong', response.status);
    }

    return body as { token: string };
  }

  public async oidcSSOAuth({ code, strategy }: { code: string; strategy: string }) {
    const response = await this.fetch(
      `${this.getEndpoint('oidc/auth')}?code=${code}&strategy=${strategy}`,
      {
        method: 'GET',
        headers: this.getHeaders(),
      }
    );

    const body = await response.json();
    this.authToken = body.token;

    if (response.status !== 200) {
      throw new CohereNetworkError('Something went wrong', response.status);
    }

    return body as { token: string };
  }

  private getEndpoint(
    endpoint:
      | 'upload'
      | 'chat-stream'
      | 'langchain-chat'
      | 'conversations'
      | 'tools'
      | 'deployments'
      | 'experimental_features'
      | 'login'
      | 'logout'
      | 'auth_strategies'
      | 'users'
      | 'google/auth'
      | 'oidc/auth'
  ) {
=======
  private getEndpoint(endpoint: 'chat-stream' | 'langchain-chat' | 'google/auth' | 'oidc/auth') {
>>>>>>> main
    return `${this.hostname}/v1/${endpoint}`;
  }

  private getHeaders(omitContentType = false) {
    const headers: HeadersInit = {
      ...(omitContentType ? {} : { 'Content-Type': 'application/json' }),
      ...(this.authToken ? { Authorization: `Bearer ${this.authToken}` } : {}),
      'User-Id': 'user-id',
    };
    return headers;
  }
}
