import { useParams } from 'next/navigation';
import { useMemo } from 'react';

import { getQueryString } from '@/utils';

export const useChatRoutes = () => {
  const params = useParams();

  const { agentId, conversationId } = useMemo(() => {
    return {
      agentId: getQueryString(params.agentId),
      conversationId: getQueryString(params.conversationId),
    };
  }, [params]);

  return { agentId, conversationId };
};
