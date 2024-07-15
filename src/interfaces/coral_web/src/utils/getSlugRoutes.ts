const isUUID = (value: string) => {
  const isValidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

  return isValidRegex.test(value);
};

/**
 *
 * @description This function is used to parse the slug from the URL and return the agentId and conversationId.
 * The slug can be in the following formats:
 * - [] - /
 * - [c, :conversationId] - /c/:conversationId
 * - [a, :agentId] - /a/:agentId
 * - [a, :agentId, c, :conversationId] - /a/:agentId/c/:conversationId
 */
export const getSlugRoutes = (
  slugParams?: string | string[]
): {
  agentId: string | undefined;
  conversationId: string | undefined;
} => {
  if (!slugParams || typeof slugParams === 'string') {
    return { agentId: undefined, conversationId: undefined };
  }

  // Possible values are:
  // firstQuery = [:agentId, c, a, undefined]
  // secondQuery = [c, :conversationId, undefined]
  // thirdQuery = [c, undefined]
  // fourthQuery = [:conversationId, undefined]
  const [firstQuery, secondQuery, thirdQuery, fourthQuery] = slugParams;

  // [/]
  if (!firstQuery) {
    return { agentId: undefined, conversationId: undefined };
  }

  // [/c/:conversationId]
  if (firstQuery === 'c' && isUUID(secondQuery)) {
    return { agentId: undefined, conversationId: secondQuery };
  }

  // [/a/:agentId]
  if (firstQuery === 'a' && isUUID(secondQuery) && !thirdQuery) {
    return { agentId: secondQuery, conversationId: undefined };
  }
  // [/a/:agentId/c/:conversationId]
  if (firstQuery === 'a' && isUUID(secondQuery) && thirdQuery === 'c' && isUUID(fourthQuery)) {
    return { agentId: secondQuery, conversationId: fourthQuery };
  }

  return { agentId: undefined, conversationId: undefined };
};
