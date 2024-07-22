'use client';

import { Transition, TransitionChild } from '@headlessui/react';
import React, { useCallback, useEffect, useRef } from 'react';

import { UpdateAgent } from '@/components/Agents/UpdateAgent';
import { Composer } from '@/components/Conversation/Composer';
import { Header } from '@/components/Conversation/Header';
import MessagingContainer from '@/components/Conversation/MessagingContainer';
import { HotKeysProvider } from '@/components/Shared/HotKeys';
import { WelcomeGuideTooltip } from '@/components/WelcomeGuideTooltip';
import { ReservedClasses } from '@/constants';
import { useChatHotKeys } from '@/hooks/actions';
import { useAgent, useRecentAgents } from '@/hooks/agents';
import { useChat } from '@/hooks/chat';
import { useDefaultFileLoaderTool, useFileActions } from '@/hooks/files';
import { WelcomeGuideStep, useWelcomeGuideState } from '@/hooks/ftux';
import {
  useAgentsStore,
  useCitationsStore,
  useConversationStore,
  useParamsStore,
  useSettingsStore,
} from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';
import { ChatMessage } from '@/types/message';
import { cn } from '@/utils';

type Props = {
  startOptionsEnabled?: boolean;
  conversationId?: string;
  agentId?: string;
  history?: ChatMessage[];
};

/**
 * @description Renders the entire conversation pane, which includes the header, messages,
 * composer, and the citation panel.
 */
const Conversation: React.FC<Props> = ({
  conversationId,
  agentId,
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
  const {
    agents: { isEditAgentPanelOpen },
  } = useAgentsStore();
  const { addRecentAgentId } = useRecentAgents();
  const { defaultFileLoaderTool, enableDefaultFileLoaderTool } = useDefaultFileLoaderTool();

  const { data: agent } = useAgent({ agentId });

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
      if (agentId) {
        addRecentAgentId(agentId);
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
        <Header conversationId={conversationId} agentId={agentId} isStreaming={isStreaming} />

        <div className="relative flex h-full w-full flex-col" ref={chatWindowRef}>
          <MessagingContainer
            conversationId={conversationId}
            startOptionsEnabled={startOptionsEnabled}
            isStreaming={isStreaming}
            isStreamingToolEvents={isStreamingToolEvents}
            onRetry={handleRetry}
            messages={messages}
            streamingMessage={streamingMessage}
            agentId={agentId}
            composer={
              <>
                <WelcomeGuideTooltip step={3} className="absolute bottom-full mb-4" />
                <Composer
                  isStreaming={isStreaming}
                  value={userMessage}
                  isFirstTurn={messages.length === 0}
                  streamingMessage={streamingMessage}
                  chatWindowRef={chatWindowRef}
                  requiredTools={agent?.tools}
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

      <Transition
        show={!!isEditAgentPanelOpen}
        as="div"
        className={cn(
          'absolute left-0 top-0 z-configuration-drawer md:relative',
          'border-l border-marble-950 bg-marble-1000'
        )}
        enter="transition-[width] ease-in-out duration-300"
        enterFrom="w-0"
        enterTo="w-full md:w-edit-agent-panel lg:w-edit-agent-panel-lg 2xl:w-edit-agent-panel-2xl"
        leave="transition-[width] ease-in-out duration-0 md:duration-300"
        leaveFrom="w-full md:w-edit-agent-panel lg:w-edit-agent-panel-lg 2xl:w-edit-agent-panel-2xl"
        leaveTo="w-0"
      >
        <TransitionChild
          as="div"
          className={cn('flex h-full flex-col')}
          enter="transition-[opacity] ease-in-out duration-200 delay-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="transition-[opacity] ease-in-out duration-0 md:duration-50"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <UpdateAgent agentId={agentId} />
        </TransitionChild>
      </Transition>
    </div>
  );
};

export default Conversation;
