'use client';

import React, { useCallback, useEffect, useRef } from 'react';

import { Agent, ManagedTool } from '@/cohere-client';
import { Composer } from '@/components/Conversation/Composer';
import { Header } from '@/components/Conversation/Header';
import MessagingContainer from '@/components/Conversation/MessagingContainer';
import RightPanel from '@/components/Conversation/RightPanel';
import { HotKeysProvider } from '@/components/Shared/HotKeys';
import { WelcomeGuideTooltip } from '@/components/WelcomeGuideTooltip';
import { ReservedClasses } from '@/constants';
import { useChatHotKeys } from '@/hooks/actions';
import { useRecentAgents } from '@/hooks/agents';
import { useChat } from '@/hooks/chat';
import { useDefaultFileLoaderTool, useFileActions } from '@/hooks/files';
import { WelcomeGuideStep, useWelcomeGuideState } from '@/hooks/ftux';
import {
  useCitationsStore,
  useConversationStore,
  useParamsStore,
  useSettingsStore,
} from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';
import { ChatMessage } from '@/types/message';

type Props = {
  startOptionsEnabled?: boolean;
  conversationId?: string;
  agent?: Agent;
  tools?: ManagedTool[];
  history?: ChatMessage[];
};

/**
 * @description Renders the entire conversation pane, which includes the header, messages,
 * composer, and the citation panel.
 */
const Conversation: React.FC<Props> = ({
  conversationId,
  agent,
  tools,
  startOptionsEnabled = false,
}) => {
  const chatHotKeys = useChatHotKeys();

  const { uploadFiles } = useFileActions();
  const { welcomeGuideState, finishWelcomeGuide } = useWelcomeGuideState();
  const {
    settings: { isConfigDrawerOpen },
    setSettings,
  } = useSettingsStore();
  const {
    conversation: { messages },
  } = useConversationStore();
  const {
    citations: { selectedCitation },
    selectCitation,
  } = useCitationsStore();
  const {
    params: { fileIds },
  } = useParamsStore();

  const { addRecentAgentId } = useRecentAgents();
  const { defaultFileLoaderTool, enableDefaultFileLoaderTool } = useDefaultFileLoaderTool();

  const {
    userMessage,
    isStreaming,
    isStreamingToolEvents,
    streamingMessage,
    setUserMessage,
    handleSend: send,
    handleStop,
    handleRetry,
  } = useChat({
    onSend: () => {
      if (agent) {
        addRecentAgentId(agent.id);
      }
      if (isConfigDrawerOpen) setSettings({ isConfigDrawerOpen: false });
      if (welcomeGuideState !== WelcomeGuideStep.DONE) {
        finishWelcomeGuide();
      }
    },
  });

  const chatWindowRef = useRef<HTMLDivElement>(null);

  const handleClickOutside = useCallback(
    (event: MouseEvent) => {
      if (!selectedCitation) return;

      const target = event.target as Node;
      const invalidElements = Array.from(
        document.querySelectorAll(`.${ReservedClasses.MESSAGE}, .${ReservedClasses.CITATION}`)
      );
      const validParentElements = Array.from(
        document.querySelectorAll(
          `.${ReservedClasses.MESSAGES}, .${ReservedClasses.CITATION_PANEL}`
        )
      );

      const isClickInsideInvalidElements = invalidElements.some((node) => node.contains(target));
      const isClickInsideValidParentElements = validParentElements.some((node) =>
        node.contains(target)
      );
      if (!isClickInsideInvalidElements && isClickInsideValidParentElements) {
        selectCitation(null);
      }
    },
    [selectedCitation, selectCitation]
  );

  useEffect(() => {
    window?.addEventListener('click', handleClickOutside);
    return () => {
      window?.removeEventListener('click', handleClickOutside);
    };
  }, [handleClickOutside]);

  const handleUploadFile = async (files: File[]) => {
    const newFileIds = await uploadFiles(files, conversationId);
    if (!newFileIds) return;
    enableDefaultFileLoaderTool();
  };

  const handleSend = (msg?: string, overrides?: Partial<ConfigurableParams>) => {
    const areFilesSelected = fileIds && fileIds.length > 0;
    const enableFileLoaderTool = areFilesSelected && !!defaultFileLoaderTool;

    if (enableFileLoaderTool) {
      enableDefaultFileLoaderTool();
    }
    send({ suggestedMessage: msg }, overrides);
  };

  return (
    <div className="flex h-full w-full">
      <div className="flex h-full w-full min-w-0 flex-col">
        <HotKeysProvider customHotKeys={chatHotKeys} />
        <Header conversationId={conversationId} agentId={agent?.id} isStreaming={isStreaming} />

        <div className="relative flex h-full w-full flex-col" ref={chatWindowRef}>
          <MessagingContainer
            conversationId={conversationId}
            startOptionsEnabled={startOptionsEnabled}
            isStreaming={isStreaming}
            isStreamingToolEvents={isStreamingToolEvents}
            onRetry={handleRetry}
            messages={messages}
            streamingMessage={streamingMessage}
            agentId={agent?.id}
            composer={
              <>
                <WelcomeGuideTooltip step={3} className="absolute bottom-full mb-4" />
                <Composer
                  isStreaming={isStreaming}
                  value={userMessage}
                  streamingMessage={streamingMessage}
                  chatWindowRef={chatWindowRef}
                  agent={agent}
                  tools={tools}
                  onChange={(message) => setUserMessage(message)}
                  onSend={handleSend}
                  onStop={handleStop}
                  onUploadFile={handleUploadFile}
                />
              </>
            }
          />
        </div>
      </div>
      <div className="w-full flex-shrink-0 px-6 md:w-[280px] lg:w-[360px]">
        <RightPanel />
      </div>
    </div>
  );
};

export default Conversation;
