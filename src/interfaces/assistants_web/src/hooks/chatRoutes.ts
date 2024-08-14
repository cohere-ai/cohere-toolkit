import { useParams, useRouter } from 'next/navigation';
import { useMemo } from 'react';

import { useIsDesktop } from '@/hooks/breakpoint';
import {
  useCitationsStore,
  useConversationStore,
  useParamsStore,
  useSettingsStore,
} from '@/stores';
import { getQueryString } from '@/utils';

export const useNavigateToNewChat = () => {
  const router = useRouter();
  const isDesktop = useIsDesktop();
  const isMobile = !isDesktop;
  const { agentId } = useChatRoutes();
  const { resetConversation } = useConversationStore();
  const { resetCitations } = useCitationsStore();
  const { resetFileParams } = useParamsStore();
  const { setLeftPanelOpen } = useSettingsStore();

  const handleNavigate = () => {
    const url = agentId ? `/a/${agentId}` : '/';
    resetConversation();
    resetCitations();
    resetFileParams();
    isMobile && setLeftPanelOpen(false);
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
