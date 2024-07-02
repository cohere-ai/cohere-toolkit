import { FetchEventSourceInit, fetchEventSource } from '@microsoft/fetch-event-source';

import {
  Body_upload_file_v1_conversations_upload_file_post,
  CohereChatRequest,
  CohereClientGenerated,
  CohereNetworkError,
  CreateAgent,
  CreateUser,
  Fetch,
  UpdateAgent,
  UpdateConversation,
  UpdateDeploymentEnv,
} from '@/cohere-client';

import { mapToChatRequest } from './mappings';

export class CohereClient {
  private readonly hostname: string;
  private readonly fetch: Fetch;
  private authToken?: string;

  public cohereService: CohereClientGenerated;
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

  public uploadFile({ file, conversation_id }: Body_upload_file_v1_conversations_upload_file_post) {
    return this.cohereService.default.uploadFileV1ConversationsUploadFilePost({
      formData: { conversation_id, file },
    });
  }

  public deletefile({ conversationId, fileId }: { conversationId: string; fileId: string }) {
    return this.cohereService.default.deleteFileV1ConversationsConversationIdFilesFileIdDelete({
      conversationId,
      fileId,
    });
  }

  public listFiles({ conversationId }: { conversationId: string }) {
    return this.cohereService.default.listFilesV1ConversationsConversationIdFilesGet({
      conversationId,
    });
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
    return this.cohereService.default.listConversationsV1ConversationsGet(params);
  }

  public getConversation({ conversationId }: { conversationId: string }) {
    return this.cohereService.default.getConversationV1ConversationsConversationIdGet({
      conversationId,
    });
  }

  public deleteConversation({ conversationId }: { conversationId: string }) {
    return this.cohereService.default.deleteConversationV1ConversationsConversationIdDelete({
      conversationId,
    });
  }

  public editConversation(request: UpdateConversation, conversationId: string) {
    return this.cohereService.default.updateConversationV1ConversationsConversationIdPut({
      conversationId: conversationId,
      requestBody: request,
    });
  }

  public listTools({ agentId }: { agentId?: string | null }) {
    return this.cohereService.default.listToolsV1ToolsGet({ agentId });
  }

  public listDeployments({ all }: { all?: boolean }) {
    return this.cohereService.default.listDeploymentsV1DeploymentsGet({ all });
  }

  public updateDeploymentEnvVariables(request: UpdateDeploymentEnv, name: string) {
    return this.cohereService.default.setEnvVarsV1DeploymentsNameSetEnvVarsPost({
      name: name,
      requestBody: request,
    });
  }

  public getExperimentalFeatures() {
    return this.cohereService.default.listExperimentalFeaturesV1ExperimentalFeaturesGet();
  }

  public login({ email, password }: { email: string; password: string }) {
    return this.cohereService.default.loginV1LoginPost({
      requestBody: {
        strategy: 'Basic',
        payload: { email, password },
      },
    });
  }

  public logout() {
    return this.cohereService.default.logoutV1LogoutGet();
  }

  public getAuthStrategies() {
    return this.cohereService.default.getStrategiesV1AuthStrategiesGet();
  }

  public createUser({ fullname, email, password }: CreateUser) {
    return this.cohereService.default.createUserV1UsersPost({
      requestBody: { fullname, email, password },
    });
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
    // FIXME: generated code doesn't have code as query parameter
    // this.cohereService.default.googleAuthorizeV1GoogleAuthGet();
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
    // FIXME: generated code doesn't have code as query parameter
    // this.cohereService.default.oidcAuthorizeV1OidcAuthGet();
  }

  public getAgent(agentId: string) {
    return this.cohereService.default.getAgentByIdV1AgentsAgentIdGet({ agentId });
  }

  public createAgent(request: CreateAgent) {
    return this.cohereService.default.createAgentV1AgentsPost({ requestBody: request });
  }

  public async listAgents({ offset, limit = 100 }: { offset?: number; limit?: number }) {
    return this.cohereService.default.listAgentsV1AgentsGet({ offset, limit });
  }

  public updateAgent(request: UpdateAgent, agentId: string) {
    return this.cohereService.default.updateAgentV1AgentsAgentIdPut({
      agentId: agentId,
      requestBody: request,
    });
  }

  private getEndpoint(endpoint: 'chat-stream' | 'langchain-chat' | 'google/auth' | 'oidc/auth') {
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
