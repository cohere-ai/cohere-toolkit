import { useParams, useRouter } from 'next/navigation';
import { useMemo } from 'react';

import { useAgentsStore, useCitationsStore, useConversationStore, useParamsStore } from '@/stores';
import { getQueryString } from '@/utils';

export const useNavigateToNewChat = () => {
  const router = useRouter();
  const { setEditAgentPanelOpen } = useAgentsStore();
  const { resetConversation } = useConversationStore();
  const { resetCitations } = useCitationsStore();
  const { resetFileParams } = useParamsStore();

  const handleNavigate = (agentId?: string) => {
    const url = agentId ? `/a/${agentId}` : '/';
    setEditAgentPanelOpen(false);
    resetConversation();
    resetCitations();
    resetFileParams();
    router.push(url);
  };

  return handleNavigate;
};

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
