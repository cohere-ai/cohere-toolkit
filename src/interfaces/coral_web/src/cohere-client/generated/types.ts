import { ERROR_FINISH_REASON_TO_MESSAGE, FinishReason } from '@/cohere-client/constants';

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
