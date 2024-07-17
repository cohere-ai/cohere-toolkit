'use client';

import { NextPage } from 'next';
import { useContext, useEffect } from 'react';

import { ManagedTool } from '@/cohere-client';
import { ConnectDataModal } from '@/components/ConnectDataModal';
import Conversation from '@/components/Conversation';
import { BannerContext } from '@/context/BannerContext';
import { ModalContext } from '@/context/ModalContext';
import { useAgent } from '@/hooks/agents';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useListAllDeployments } from '@/hooks/deployments';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';
import { useListTools, useShowUnauthedToolsModal } from '@/hooks/tools';
import { useCitationsStore, useConversationStore, useParamsStore } from '@/stores';

const Page: NextPage = () => {
  const { agentId } = useChatRoutes();
  const { setConversation } = useConversationStore();

  const { resetCitations } = useCitationsStore();
  const {
    params: { deployment },
    setParams,
    resetFileParams,
  } = useParamsStore();
  const { show: showUnauthedToolsModal, onDismissed } = useShowUnauthedToolsModal();
  const { data: allDeployments } = useListAllDeployments();
  const { data: agent } = useAgent({ agentId });
  const { data: tools } = useListTools();
  const { data: experimentalFeatures } = useExperimentalFeatures();
  const isLangchainModeOn = !!experimentalFeatures?.USE_EXPERIMENTAL_LANGCHAIN;

  const { setMessage } = useContext(BannerContext);
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

  useEffect(() => {
    if (!deployment && allDeployments) {
      const firstAvailableDeployment = allDeployments.find((d) => d.is_available);
      if (firstAvailableDeployment) {
        setParams({ deployment: firstAvailableDeployment.name });
      }
    }
  }, [deployment, allDeployments]);

  useEffect(() => {
    if (!isLangchainModeOn) return;
    setMessage('You are using an experimental langchain multihop flow. There will be bugs.');
  }, [isLangchainModeOn]);

  return <Conversation agentId={agentId} startOptionsEnabled />;
};

export default Page;
