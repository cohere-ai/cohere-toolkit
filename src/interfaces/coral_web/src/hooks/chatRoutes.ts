import { useParams } from 'next/navigation';
import { useMemo } from 'react';

export const useChatRoutes = () => {
  const params = useParams();

  const { agentId, conversationId } = useMemo(() => {
    return {
      agentId: params.agentId as string | undefined,
      conversationId: params.conversationId as string | undefined,
    };
  }, [params]);

  return { agentId, conversationId };
};
