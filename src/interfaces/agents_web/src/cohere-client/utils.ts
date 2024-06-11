import { CohereFinishStreamError, CohereNetworkError, CohereStreamError, FinishReason } from '.';

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

export const isSessionUnavailableError = (error: unknown): error is CohereNetworkError =>
  isCohereNetworkError(error) && error.status === 503;

export const isFinishedError = (error: unknown): error is CohereFinishStreamError =>
  error instanceof CohereFinishStreamError;

export const isFinishedUnexpectedError = (error: unknown): error is CohereFinishStreamError =>
  isFinishedError(error) && error.reason === FinishReason.FINISH_REASON_ERROR;

export const isStreamError = (error: unknown): error is CohereStreamError =>
  error instanceof CohereStreamError;
