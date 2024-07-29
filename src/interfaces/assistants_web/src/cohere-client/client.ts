import { FetchEventSourceInit, fetchEventSource } from '@microsoft/fetch-event-source';

import {
  Body_batch_upload_file_v1_conversations_batch_upload_file_post,
  Body_upload_file_v1_conversations_upload_file_post,
  CancelablePromise,
  CohereChatRequest,
  CohereClientGenerated,
  CohereNetworkError,
  CohereUnauthorizedError,
  CreateAgent,
  CreateSnapshot,
  CreateUser,
  ExperimentalFeatures,
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
      HEADERS: async () => this.getHeaders(true),
    });

    this.cohereService.request.config.interceptors.response.use((response) => {
      if (response.status === 401) {
        throw new CohereUnauthorizedError();
      }
      return response;
    });
  }

  public uploadFile(formData: Body_upload_file_v1_conversations_upload_file_post) {
    return this.cohereService.default.uploadFileV1ConversationsUploadFilePost({
      formData,
    });
  }

  public batchUploadFile(formData: Body_batch_upload_file_v1_conversations_batch_upload_file_post) {
    return this.cohereService.default.batchUploadFileV1ConversationsBatchUploadFilePost({
      formData,
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
      openWhenHidden: true, // When false, the requests will be paused when the tab is hidden and resume/retry when the tab is visible again
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

  public editConversation(requestBody: UpdateConversation, conversationId: string) {
    return this.cohereService.default.updateConversationV1ConversationsConversationIdPut({
      conversationId: conversationId,
      requestBody,
    });
  }

  public listTools({ agentId }: { agentId?: string | null }) {
    return this.cohereService.default.listToolsV1ToolsGet({ agentId });
  }

  public listDeployments({ all }: { all?: boolean }) {
    return this.cohereService.default.listDeploymentsV1DeploymentsGet({ all });
  }

  public updateDeploymentEnvVariables(requestBody: UpdateDeploymentEnv, name: string) {
    return this.cohereService.default.setEnvVarsV1DeploymentsNameSetEnvVarsPost({
      name: name,
      requestBody,
    });
  }

  public getExperimentalFeatures() {
    return this.cohereService.default.listExperimentalFeaturesV1ExperimentalFeaturesGet() as CancelablePromise<ExperimentalFeatures>;
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

    const body = await response.json();
    this.authToken = body.token;

    if (response.status !== 200) {
      throw new CohereNetworkError('Something went wrong', response.status);
    }

    return body as { token: string };
    // FIXME(@tomtobac): generated code doesn't have code as query parameter (TLK-765)
    // this.cohereService.default.googleAuthorizeV1GoogleAuthGet();
  }

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
    }

    const response = await this.fetch(
      `${this.getEndpoint('oidc/auth')}?code=${code}&strategy=${strategy}`,
      {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(body),
      }
    );

    const payload = await response.json();
    this.authToken = body.token;

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

  public getDefaultAgent() {
    return this.cohereService.default.getDefaultAgentV1DefaultAgentGet();
  }

  public createAgent(requestBody: CreateAgent) {
    return this.cohereService.default.createAgentV1AgentsPost({ requestBody });
  }

  public listAgents({ offset, limit = 100 }: { offset?: number; limit?: number }) {
    return this.cohereService.default.listAgentsV1AgentsGet({ offset, limit });
  }

  public updateAgent(requestBody: UpdateAgent, agentId: string) {
    return this.cohereService.default.updateAgentV1AgentsAgentIdPut({
      agentId: agentId,
      requestBody,
    });
  }

  public deleteAgent(request: { agentId: string }) {
    return this.cohereService.default.deleteAgentV1AgentsAgentIdDelete(request);
  }

  public generateTitle({ conversationId }: { conversationId: string }) {
    return this.cohereService.default.generateTitleV1ConversationsConversationIdGenerateTitlePost({
      conversationId,
    });
  }

  public listSnapshots() {
    return this.cohereService.default.listSnapshotsV1SnapshotsGet();
  }

  public createSnapshot(requestBody: CreateSnapshot) {
    return this.cohereService.default.createSnapshotV1SnapshotsPost({ requestBody });
  }

  public getSnapshot({ linkId }: { linkId: string }) {
    return this.cohereService.default.getSnapshotV1SnapshotsLinkLinkIdGet({ linkId });
  }

  public deleteSnapshotLink({ linkId }: { linkId: string }) {
    return this.cohereService.default.deleteSnapshotLinkV1SnapshotsLinkLinkIdDelete({ linkId });
  }

  public deleteSnapshot({ snapshotId }: { snapshotId: string }) {
    return this.cohereService.default.deleteSnapshotV1SnapshotsSnapshotIdDelete({ snapshotId });
  }

  private getEndpoint(endpoint: 'chat-stream' | 'langchain-chat' | 'google/auth' | 'oidc/auth') {
    return `${this.hostname}/v1/${endpoint}`;
  }

  private getHeaders(omitContentType = false) {
    const headers: HeadersInit = {
      ...(omitContentType ? {} : { 'Content-Type': 'application/json' }),
      ...(this.authToken ? { Authorization: `Bearer ${this.authToken}` } : {}),
      'User-Id': 'user-id',
      Connection: 'keep-alive',
      'X-Date': new Date().getTime().toString(),
    };
    return headers;
  }
}
