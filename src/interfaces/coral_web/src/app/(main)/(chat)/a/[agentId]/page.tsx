'use client';

import { NextPage } from 'next';
import { useContext, useEffect } from 'react';

import { ManagedTool } from '@/cohere-client';
import { ConnectDataModal } from '@/components/ConnectDataModal';
import Conversation from '@/components/Conversation';
import { ModalContext } from '@/context/ModalContext';
import { useAgent } from '@/hooks/agents';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useListTools, useShowUnauthedToolsModal } from '@/hooks/tools';
import { useCitationsStore, useConversationStore, useParamsStore } from '@/stores';

const Page: NextPage = () => {
  const { agentId } = useChatRoutes();
  const { setConversation } = useConversationStore();

  const { resetCitations } = useCitationsStore();
  const { setParams, resetFileParams } = useParamsStore();
  const { show: showUnauthedToolsModal, onDismissed } = useShowUnauthedToolsModal();
  const { data: agent } = useAgent({ agentId });
  const { data: tools } = useListTools();

  const { open, close } = useContext(ModalContext);

  useEffect(() => {
    if (showUnauthedToolsModal) {
      open({
        title: 'Connect your data',
        content: (
          <ConnectDataModal
            onClose={() => {
              onDismissed();
              close();
            }}
          />
        ),
      });
    }
  }, [showUnauthedToolsModal]);

  useEffect(() => {
    resetCitations();
    resetFileParams();

    const agentTools = (agent?.tools
      .map((name) => (tools ?? [])?.find((t) => t.name === name))
      .filter((t) => t !== undefined) ?? []) as ManagedTool[];
    setParams({
      tools: agentTools,
    });
  }, [setConversation, resetCitations, agent, tools]);

  return <Conversation agentId={agentId} startOptionsEnabled />;
};

export default Page;
