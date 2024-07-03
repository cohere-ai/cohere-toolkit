import {
  CohereFinishStreamError,
  CohereNetworkError,
  CohereStreamError,
  FinishReason,
} from '@/cohere-client';

export const isCohereNetworkError = (error: any): error is CohereNetworkError => {
  return error instanceof CohereNetworkError;
};

export const isBadRequestError = (error: unknown): error is CohereNetworkError =>
  isCohereNetworkError(error) && error.status === 400;

export const isUnauthorizedError = (error: unknown): error is CohereNetworkError =>
  isCohereNetworkError(error) && error.status === 401;

export const isForbiddenError = (error: unknown): error is CohereNetworkError =>
  isCohereNetworkError(error) && error.status === 403;

export const isNotFoundError = (error: unknown): error is CohereNetworkError =>
  isCohereNetworkError(error) && error.status === 404;

export const isFinishedError = (error: unknown): error is CohereFinishStreamError =>
  error instanceof CohereFinishStreamError;

export const isFinishedUnexpectedError = (error: unknown): error is CohereFinishStreamError =>
  isFinishedError(error) && error.reason === FinishReason.ERROR;

export const isStreamError = (error: unknown): error is CohereStreamError =>
  error instanceof CohereStreamError;

export const getFinishReasonErrorMessage = (
  reason: FinishReason | string | null | undefined,
  error?: string | null
): string => {
  switch (reason) {
    case FinishReason.ERROR: {
      return error ?? 'An error occurred. Please try again.';
    }
    case FinishReason.MAX_TOKENS: {
      return 'Generation stopped since max tokens limit was reached.';
    }
    default: {
      return 'An error occurred. Please try again.';
    }
  }
};
