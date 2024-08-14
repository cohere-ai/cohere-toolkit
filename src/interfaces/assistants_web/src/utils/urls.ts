import { ParseResultType, parseDomain } from 'parse-domain';

/**
 * Returns the domain name of a url.
 * * e.g. https://www.google.com -> google
 * * e.g. https://www.google.co.uk -> google
 * * e.g. https://www.en.wikipedia.co.uk/search?q=hello -> wikipedia
 * * e.g. https://www.cloud.console.aws.amazon.co.uk -> amazon
 */
export const getWebDomain = (url?: string) => {
  if (!url) return '';

  try {
    const urlObj = new URL(url);

    const parsed = parseDomain(urlObj.hostname);

    if (parsed.type === ParseResultType.Listed) {
      return parsed.domain;
    }

    return '';
  } catch {
    return '';
  }
};

/**
 * Returns the url if it is valid and safe.
 * * e.g. https://www.google.com -> ok
 * * e.g. alert('hi') -> not ok, return undefined
 * * e.g. https://www.google.com?q=<script>alert(1)</script> -> ok, return encoded url
 */
export const getSafeUrl = (url?: string | null) => {
  if (!url) return undefined;

  try {
    const urlObj = new URL(url);
    const parsed = parseDomain(urlObj.hostname);

    if (parsed.type === ParseResultType.Listed) {
      const encodedPathname = urlObj.pathname
        .split('/')
        .map((p) => encodeURIComponent(p))
        .join('/');

      const encodedSearchParamsList = [];
      for (const [key, value] of urlObj.searchParams) {
        encodedSearchParamsList.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
      }
      const encodedSearchParams =
        encodedSearchParamsList.length > 0 ? `?${encodedSearchParamsList.join('&')}` : '';

      return `${urlObj.origin}${encodedPathname}${encodedSearchParams}${urlObj.hash}`;
    }

    return undefined;
  } catch {
    return undefined;
  }
};

/**
 * Returns the url if it is valid.
 * * e.g. https://www.google.com -> ok
 * * e.g. alert('hi') -> not ok, return undefined
 *
 * @param url The url to validate.
 * @returns The url if it is valid, otherwise undefined.
 */
export const getValidURL = (url?: string | null) => {
  if (!url) return undefined;
  try {
    new URL(url);
    return url;
  } catch {
    return undefined;
  }
};
