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
 * - [:agentId] - /:agentId
 * - [:agentId, c, :conversationId] - /:agentId/c/:conversationId
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
  // firstQuery = :agentId | c | undefined
  // secondQuery = c | :conversationId | undefined
  // thirdQuery = :conversationId | undefined
  const [firstQuery, secondQuery, thirdQuery] = slugParams;

  // []
  if (!firstQuery) {
    return { agentId: undefined, conversationId: undefined };
  }

  // [c, :conversationId]
  if (firstQuery === 'c' && isUUID(secondQuery)) {
    return { agentId: undefined, conversationId: secondQuery };
  }

  // [:agentId]
  if (!secondQuery && isUUID(firstQuery)) {
    return { agentId: firstQuery, conversationId: undefined };
  }

  // [:agentId, c, :conversationId]
  if (secondQuery === 'c' && isUUID(firstQuery) && isUUID(thirdQuery)) {
    return { agentId: firstQuery, conversationId: thirdQuery };
  }

  return { agentId: undefined, conversationId: undefined };
};
