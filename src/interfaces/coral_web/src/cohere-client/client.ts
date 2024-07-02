import { FetchEventSourceInit, fetchEventSource } from '@microsoft/fetch-event-source';

import {
  Agent,
  CohereChatRequest,
  CohereClientGenerated,
  CohereNetworkError,
  CohereUnauthorizedError,
  Conversation,
  CreateAgent,
  Deployment,
  ExperimentalFeatures,
  Fetch,
  ListAuthStrategy,
  ListFile,
  ManagedTool,
  UpdateAgent,
  UpdateConversation,
  UpdateDeploymentEnv,
  UploadFile,
} from '@/cohere-client';

import { mapToChatRequest } from './mappings';

export class CohereClient {
  private readonly hostname: string;
  private readonly fetch: Fetch;
  private authToken?: string;

  public cohereService?: CohereClientGenerated;
  public request?: any;

  constructor({
    hostname,
    fetch,
    authToken,
  }: {
    hostname: string;
    fetch: Fetch;
    authToken?: string;
  }) {
    this.hostname = hostname;
    this.fetch = fetch;
    this.authToken = authToken;
    this.cohereService = new CohereClientGenerated({
      BASE: hostname,
      HEADERS: {
        Authorization: `Bearer ${authToken}`,
        'User-Id': 'user-id',
      },
    });
  }

  public async uploadFile({
    conversationId,
    file,
  }: {
    file: File;
    conversationId?: string;
  }): Promise<UploadFile> {
    const endpoint = `${this.getEndpoint('conversations')}/upload_file`;
    const formData = new FormData();
    formData.append('file', file, file.name);
    if (conversationId) {
      formData.append('conversation_id', conversationId);
    } else {
      /**
       * In the event a conversation_id doesn't exist yet (ie. first turn of a conversation),
       * we must upload files using a user_id instead. On successful upload, we will receive a
       * conversation_id in the response which we can use for future uploads.
       */
      formData.append('user_id', 'user_id');
    }

    const response = await this.fetch(endpoint, {
      method: 'POST',
      headers: this.getHeaders(true),
      body: formData,
    });

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
  }

  public async deletefile({ conversationId, fileId }: { conversationId: string; fileId: string }) {
    const url = `${this.getEndpoint('conversations')}/${conversationId}/files/${fileId}`;

    const response = await this.fetch(url, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

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
      onopen: onOpen,
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
    const chatRequest = mapToChatRequest(request);
    const requestBody = JSON.stringify({
      ...chatRequest,
    });
    return await fetchEventSource(this.getEndpoint('langchain-chat'), {
      method: 'POST',
      headers: { ...this.getHeaders(), ...headers },
      body: requestBody,
      signal,
      onopen: onOpen,
      onmessage: onMessage,
      onclose: onClose,
      onerror: onError,
    });
  }

  public listConversations(params: { offset?: number; limit?: number; agentId?: string }) {
    return this.cohereService?.default.listConversationsV1ConversationsGet(params);
  }

  public async getConversation({
    conversationId,
    signal,
  }: { conversationId: string } & {
    signal?: AbortSignal;
  }): Promise<Conversation> {
    const response = await this.fetch(`${this.getEndpoint('conversations')}/${conversationId}`, {
      method: 'GET',
      headers: this.getHeaders(),
      signal,
    });
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
  }

  public async deleteConversation({ conversationId }: { conversationId: string }) {
    const response = await this.fetch(`${this.getEndpoint('conversations')}/${conversationId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

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

  public async editConversation(
    request: UpdateConversation & { conversationId: string }
  ): Promise<Conversation> {
    const { conversationId, ...rest } = request;
    const endpoint = `${this.getEndpoint('conversations')}/${conversationId}`;
    const requestBody: UpdateConversation = {
      title: '',
      ...rest,
    };
    const response = await this.fetch(endpoint, {
      method: 'PUT',
      body: JSON.stringify(requestBody),
      headers: this.getHeaders(),
    });

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
  }

  public async listTools({ signal }: { signal?: AbortSignal }): Promise<ManagedTool[]> {
    const response = await this.fetch(`${this.getEndpoint('tools')}`, {
      method: 'GET',
      headers: this.getHeaders(),
      signal,
    });

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

    return body as ManagedTool[];
  }

  public async listDeployments(): Promise<Deployment[]> {
    const response = await this.fetch(`${this.getEndpoint('deployments')}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

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

    return body as Deployment[];
  }

  public async listAllDeployments(): Promise<Deployment[]> {
    const response = await this.fetch(`${this.getEndpoint('deployments')}?all=1`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

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

    return body as Deployment[];
  }

  public async updateDeploymentEnvVariables(request: UpdateDeploymentEnv & { name: string }) {
    const response = await this.fetch(
      `${this.getEndpoint('deployments')}/${request.name}/set_env_vars`,
      {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ env_vars: request.env_vars }),
      }
    );

    if (response.status === 401) {
      throw new CohereUnauthorizedError();
    }

    if (response.status !== 200) {
      throw new CohereNetworkError('Something went wrong', response.status);
    }
  }

  public async getExperimentalFeatures(): Promise<ExperimentalFeatures> {
    const response = await this.fetch(`${this.getEndpoint('experimental_features')}/`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

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

    return body as ExperimentalFeatures;
  }

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

    const body = await response.json();

    if (response.status !== 200) {
      throw new CohereNetworkError('Something went wrong', response.status);
    }

    return body as ListAuthStrategy[];
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

  public async getAgent(agentId: string): Promise<Agent> {
    const response = await this.fetch(`${this.getEndpoint('agents')}/${agentId}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    const body = await response.json();

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as Agent;
  }

  public async createAgent(request: CreateAgent): Promise<Agent> {
    const endpoint = this.getEndpoint('agents');
    const response = await this.fetch(endpoint, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });

    const body = await response.json();

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as Agent;
  }

  public async listAgents(): Promise<Agent[]> {
    const response = await this.fetch(this.getEndpoint('agents'), {
      method: 'GET',
      headers: this.getHeaders(),
    });

    const body = await response.json();

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as Agent[];
  }

  public async updateAgent(request: UpdateAgent & { agentId: string }): Promise<Agent> {
    const { agentId, ...requestBody } = request;
    const endpoint = `${this.getEndpoint('agents')}/${agentId}`;
    const response = await this.fetch(endpoint, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(requestBody),
    });

    const body = await response.json();

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as Agent;
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
      | 'agents'
  ) {
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
