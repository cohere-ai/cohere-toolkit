import { useRouter } from 'next/router';
import { useMemo } from 'react';

import { getSlugRoutes } from '@/utils/getSlugRoutes';

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

  return useMemo(() => {
    const slug = (router.query.slug ?? []) as string[];
    return getSlugRoutes(slug);
  }, [router.query.slug]);
};
