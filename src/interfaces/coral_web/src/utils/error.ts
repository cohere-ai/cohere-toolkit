import { CohereNetworkError } from '@/cohere-client';

export const isAbortError = (error: unknown) => {
  return error instanceof DOMException && error.name === 'AbortError';
};

export const isShareLinkExpiredError = (error: unknown): error is CohereNetworkError =>
  error instanceof CohereNetworkError &&
  error.status === 404 &&
  error.message === 'snapshot link has expired';

/**
 * Wraps a promise and always returns an array with the first element being the data and the second element the error.
 * If the promise errors out, the data element will be null while the error element while have a value (and vice-versa).
 * @param promiseVar A promise
 *
 * @example
 * let [data, err] = await safeAsync(GetSomeData());
 * if (err === null) {
 *    useTheData(data);
 * }
 */
export async function safeAsync<T>(promiseVar: Promise<T>): Promise<[T | null, Error | null]> {
  try {
    const data = await promiseVar;
    return [data, null];
  } catch (e) {
    return [null, e as Error];
  }
}
