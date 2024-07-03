import { FinishReason, getFinishReasonErrorMessage } from '@/cohere-client';

export class CohereNetworkError extends Error {
  public status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export class CohereFinishStreamError extends Error {
  public reason: FinishReason | string | null | undefined;

  constructor(reason: string | null | undefined, error?: string | null) {
    const message = getFinishReasonErrorMessage(reason, error);
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
