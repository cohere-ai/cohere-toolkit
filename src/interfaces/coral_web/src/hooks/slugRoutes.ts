import { useRouter } from 'next/router';
import { useMemo } from 'react';

import { getSlugRoutes } from '@/utils/getSlugRoutes';

/**
 *
 * @description This hook is used to parse the slug from the URL and return the agentId and conversationId.
 * The slug can be in the following formats:
 * - [] - /
 * - [c, :conversationId] - /c/:conversationId
 * - [a, :agentId] - /a/:agentId
 * - [a, :agentId, c, :conversationId] - /a/:agentId/c/:conversationId
 */

export const useSlugRoutes = () => {
  const router = useRouter();

  const { agentId, conversationId } = useMemo(() => {
    const slug = (router.query.slug ?? []) as string[];
    return getSlugRoutes(slug);
  }, [router.query.slug]);

  return { agentId, conversationId };
};
