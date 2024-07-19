/**
 * Get the query param as a string to avoid the usual
 * Array.isArray(router.query.[param])
 *    ? router.query.[param][0]
 *    : router.query.[param];
 */

export const getQueryString = (param?: string | string[] | null) => {
  if (!param) return;
  if (Array.isArray(param)) {
    return param[0] as string;
  }
  return param as string;
};
