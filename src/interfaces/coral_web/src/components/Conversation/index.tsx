import { uniqBy } from 'lodash';
import React, { useCallback, useEffect, useMemo, useState } from 'react';

import { FILE_TOOL_CATEGORY, Tool } from '@/cohere-client';
import Composer from '@/components/Conversation/Composer';
import { Header } from '@/components/Conversation/Header';
import MessagingContainer from '@/components/Conversation/MessagingContainer';
import { DragDropFileInput, Spinner } from '@/components/Shared';
import { HotKeysProvider } from '@/components/Shared/HotKeys';
import { PromptOption } from '@/components/StartModes';
import { WelcomeGuideTooltip } from '@/components/WelcomeGuideTooltip';
import { ACCEPTED_FILE_TYPES, ReservedClasses } from '@/constants';
import { useChatHotKeys } from '@/hooks/actions';
import { useFocusComposer } from '@/hooks/actions';
import { useChat } from '@/hooks/chat';
import { useFileActions, useFilesInConversation } from '@/hooks/files';
import { WelcomeGuideStep, useWelcomeGuideState } from '@/hooks/ftux';
import { useRouteChange } from '@/hooks/route';
import { useListTools } from '@/hooks/tools';
import {
  useCitationsStore,
  useConversationStore,
  useFilesStore,
  useParamsStore,
  useSettingsStore,
} from '@/stores';
import { ChatMessage } from '@/types/message';
import { cn } from '@/utils';

type Props = {
  startOptionsEnabled?: boolean;
  conversationId?: string;
  history?: ChatMessage[];
};

/**
 * @description Renders the entire conversation pane, which includes the header, messages,
 * composer, and the citation panel.
 */
const Conversation: React.FC<Props> = ({ conversationId, startOptionsEnabled = false }) => {
  const [isDragDropInputActive, setIsDragDropInputActive] = useState(false);
  const chatHotKeys = useChatHotKeys();

  const { uploadFile } = useFileActions();
  const { welcomeGuideState, finishWelcomeGuide } = useWelcomeGuideState();
  const {
    settings: { isConfigDrawerOpen },
    setSettings,
  } = useSettingsStore();
  const {
    conversation: { messages },
  } = useConversationStore();
  const {
    citations: { selectedCitation, citationReferences },
    selectCitation,
  } = useCitationsStore();
  const { data: tools } = useListTools();
  const { files } = useFilesInConversation();
  const {
    files: { composerFiles },
  } = useFilesStore();
  const { params, setParams } = useParamsStore();

  const {
    userMessage,
    isStreaming,
    streamingMessage,
    setUserMessage,
    handleSend: send,
    handleStop,
    handleRetry,
  } = useChat({
    onSend: () => {
      if (isConfigDrawerOpen) setSettings({ isConfigDrawerOpen: false });
      if (welcomeGuideState !== WelcomeGuideStep.DONE) {
        finishWelcomeGuide();
      }
    },
  });
  const { focusComposer } = useFocusComposer();

  // Returns the first visible file loader tool from tools list
  const defaultFileLoaderTool = useMemo(
    () => tools?.find((tool) => tool.category === FILE_TOOL_CATEGORY && tool.is_visible),
    [tools?.length]
  );

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

  const [isRouteChanging] = useRouteChange();

  if (isRouteChanging) {
    return (
      <div className="flex h-full flex-grow items-center justify-center">
        <Spinner />
      </div>
    );
  }

  const enableDefaultFileLoaderTool = () => {
    if (!defaultFileLoaderTool) return;
    const visibleFileToolNames =
      tools?.filter((t) => t.category === FILE_TOOL_CATEGORY && t.is_visible).map((t) => t.name) ??
      [];

    const isDefaultFileLoaderToolEnabled = visibleFileToolNames.some((name) =>
      params.tools?.some((tool) => tool.name === name)
    );
    if (isDefaultFileLoaderToolEnabled) return;

    const newTools = uniqBy([...(params.tools ?? []), defaultFileLoaderTool], 'name');
    setParams({ tools: newTools });
  };

  const handleUploadFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFileIds = await uploadFile(e.target.files?.[0], conversationId);
    if (!newFileIds) return;
    enableDefaultFileLoaderTool();
  };

  const handleSend = (msg?: string, overrideTools?: Tool[]) => {
    const filesExist = files.length > 0 || composerFiles.length > 0;
    const enableFileLoaderTool = filesExist && !!defaultFileLoaderTool;
    const chatOverrideTools: Tool[] = [
      ...(overrideTools ?? []),
      ...(enableFileLoaderTool ? [{ name: defaultFileLoaderTool.name }] : []),
    ];

    if (filesExist) {
      enableDefaultFileLoaderTool();
    }
    send({ suggestedMessage: msg }, { tools: chatOverrideTools });
  };

  const handlePromptSelected = (option: PromptOption) => {
    focusComposer();
    setUserMessage(option.prompt);
  };

  return (
    <div className="flex h-full w-full flex-col">
      <HotKeysProvider customHotKeys={chatHotKeys} />
      <Header conversationId={conversationId} isStreaming={isStreaming} />

      <div
        className="relative flex h-full w-full flex-col"
        onDragEnter={() => setIsDragDropInputActive(true)}
        onDragOver={() => setIsDragDropInputActive(true)}
        onDragLeave={() => setIsDragDropInputActive(false)}
        onDrop={() => {
          setTimeout(() => {
            setIsDragDropInputActive(false);
          }, 100);
        }}
      >
        <DragDropFileInput
          label=""
          subLabel=""
          onChange={handleUploadFile}
          multiple={false}
          accept={ACCEPTED_FILE_TYPES}
          dragActiveDefault={true}
          className={cn(
            'absolute inset-0 z-drag-drop-input-overlay hidden h-full w-full rounded-none border-none bg-marble-100 opacity-90',
            {
              flex: isDragDropInputActive,
            }
          )}
        />
        <MessagingContainer
          conversationId={conversationId}
          startOptionsEnabled={startOptionsEnabled}
          isStreaming={isStreaming}
          onRetry={handleRetry}
          messages={messages}
          streamingMessage={streamingMessage}
          onPromptSelected={handlePromptSelected}
          composer={
            <>
              <WelcomeGuideTooltip step={3} className="absolute bottom-full mb-4" />
              <Composer
                isStreaming={isStreaming}
                value={userMessage}
                messages={messages}
                streamingMessage={streamingMessage}
                onChange={(e) => setUserMessage(e.target.value)}
                onSend={handleSend}
                onStop={handleStop}
                onUploadFile={handleUploadFile}
              />
            </>
          }
        />
      </div>
    </div>
  );
};

export default Conversation;
