import { FetchEventSourceInit, fetchEventSource } from '@microsoft/fetch-event-source';

import {
  CohereChatRequest,
  Conversation,
  ConversationWithoutMessages,
  DefaultService,
  Deployment,
  ERROR_FINISH_REASON_TO_MESSAGE,
  FinishReason,
  ListFile,
  Tool,
  UpdateConversation,
  UpdateDeploymentEnv,
  UploadFile,
} from '.';
import { mapToChatRequest } from './mappings';

export class CohereNetworkError extends Error {
  public status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export class CohereFinishStreamError extends Error {
  public reason: FinishReason;

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

export type Fetch = (input: RequestInfo, init?: RequestInit) => Promise<Response>;

export type ExperimentalFeatures = {
  USE_EXPERIMENTAL_LANGCHAIN: boolean;
  USE_AGENTS_VIEW: boolean;
};

export class CohereClient {
  private readonly hostname: string;
  private readonly fetch: Fetch;
  private readonly source: string;

  public cohereService?: DefaultService;
  public request?: any;

  constructor({ hostname, source, fetch }: { hostname: string; source: string; fetch: Fetch }) {
    this.hostname = hostname;
    this.source = source;
    this.fetch = fetch;
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
    return await fetchEventSource(this.getEndpoint('chat-stream'), {
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

    const body = await response.json();

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as ConversationWithoutMessages[];
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

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as Conversation;
  }

  public async listTools({ signal }: { signal?: AbortSignal }): Promise<Tool[]> {
    const response = await this.fetch(`${this.getEndpoint('tools')}`, {
      method: 'GET',
      headers: this.getHeaders(),
      signal,
    });

    const body = await response.json();

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as Tool[];
  }

  public async listDeployments(): Promise<Deployment[]> {
    const response = await this.fetch(`${this.getEndpoint('deployments')}`, {
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

    return body as Deployment[];
  }

  public async listAllDeployments(): Promise<Deployment[]> {
    const response = await this.fetch(`${this.getEndpoint('deployments')}?all=1`, {
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

    if (response.status !== 200) {
      throw new CohereNetworkError(
        body?.message || body?.error || 'Something went wrong',
        response.status
      );
    }

    return body as ExperimentalFeatures;
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
  ) {
    return `${this.hostname}/v1/${endpoint}`;
  }

  private getHeaders(omitContentType = false) {
    const headers: HeadersInit = {
      ...(omitContentType ? {} : { 'Content-Type': 'application/json' }),
      'User-Id': 'user-id',
    };
    return headers;
  }
}
