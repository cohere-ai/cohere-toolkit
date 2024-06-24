import { useRouter } from 'next/router';
import { useMemo } from 'react';

/**
 *
 * @description This hook is used to parse the slug from the URL and return the agentId and conversationId.
 * The slug can be in the following formats:
 * - [] - /
 * - [c, :conversationId] - /c/:conversationId
 * - [:agentId] - /:agentId
 * - [:agentId, c, :conversationId] - /:agentId/c/:conversationId
 */

export const useSlugRoutes = () => {
  const router = useRouter();

  const slug = (router.query.slug ?? []) as string[];
  const [firstQuery, secondQuery, thirdQuery] = slug;

  return useMemo(() => {
    // []
    if (!firstQuery) return { agentId: undefined, conversationId: undefined };
    // [c, :conversationId]
    if (firstQuery === 'c') {
      return { agentId: undefined, conversationId: secondQuery };
    }
    // [:agentId]
    if (!secondQuery) {
      return { agentId: firstQuery, conversationId: undefined };
    }
    // [:agentId, c, :conversationId]
    if (secondQuery === 'c') {
      return { agentId: firstQuery, conversationId: thirdQuery };
    }
    return { agentId: undefined, conversationId: undefined };
  }, [firstQuery, secondQuery, thirdQuery]);
};
