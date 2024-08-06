'use client';

import React, { useRef } from 'react';

import { Agent, ManagedTool } from '@/cohere-client';
import { Composer } from '@/components/Conversation/Composer';
import { Header } from '@/components/Conversation/Header';
import MessagingContainer from '@/components/Conversation/MessagingContainer';
import { HotKeysProvider } from '@/components/Shared/HotKeys';
import { WelcomeGuideTooltip } from '@/components/WelcomeGuideTooltip';
import { useChatHotKeys } from '@/hooks/actions';
import { useRecentAgents } from '@/hooks/agents';
import { useChat } from '@/hooks/chat';
import { useFileActions } from '@/hooks/files';
import { WelcomeGuideStep, useWelcomeGuideState } from '@/hooks/ftux';
import { useConversationStore, useSettingsStore } from '@/stores';
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

  const { addRecentAgentId } = useRecentAgents();

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

  const handleUploadFile = async (files: File[]) => {
    await uploadFiles(files, conversationId);
  };

  const handleSend = (msg?: string, overrides?: Partial<ConfigurableParams>) => {
    send({ suggestedMessage: msg }, overrides);
  };

  return (
    <div className="flex h-full w-full">
      <div className="flex h-full w-full min-w-0 flex-col rounded-l-lg rounded-r-lg border border-marble-950 bg-marble-980 md:rounded-r-none dark:border-volcanic-200 dark:bg-volcanic-100">
        <HotKeysProvider customHotKeys={chatHotKeys} />
        <Header agentId={agent?.id} />

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
    </div>
  );
};

export default Conversation;
