import { useParams, useRouter } from 'next/navigation';
import { useMemo } from 'react';

import { useCitationsStore, useConversationStore, useParamsStore } from '@/stores';
import { getQueryString } from '@/utils';

export const useNavigateToNewChat = () => {
  const router = useRouter();
  const { agentId } = useChatRoutes();
  const { resetConversation } = useConversationStore();
  const { resetCitations } = useCitationsStore();
  const { resetFileParams } = useParamsStore();

  const handleNavigate = () => {
    const url = agentId ? `/a/${agentId}` : '/';
    resetConversation();
    resetCitations();
    resetFileParams();
    router.push(url);
  };

  return handleNavigate;
};

export const useChatRoutes = () => {
  const params = useParams();
  const {
    conversation: { id },
  } = useConversationStore();

  const { agentId, conversationId } = useMemo(() => {
    return {
      agentId: getQueryString(params.agentId),
      conversationId: getQueryString(params.conversationId),
    };
  }, [params]);

  return { agentId, conversationId: conversationId || id };
};
