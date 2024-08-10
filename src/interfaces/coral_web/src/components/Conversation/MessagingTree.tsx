'use client';

import { Transition } from '@headlessui/react';
import { usePrevious, useTimeoutEffect } from '@react-hookz/web';
import React, { ReactNode, forwardRef, memo, useEffect, useMemo, useState } from 'react';
import ScrollToBottom, { useScrollToBottom, useSticky } from 'react-scroll-to-bottom';

import { CitationPanel } from '@/components/Citations/CitationPanel';
import MessageRow from '@/components/MessageRow';
import { Button } from '@/components/Shared';
import { Welcome } from '@/components/Welcome';
import { ReservedClasses } from '@/constants';
import { MESSAGE_LIST_CONTAINER_ID, useCalculateCitationStyles } from '@/hooks/citations';
import { useFixCopyBug } from '@/hooks/fixCopyBug';
import { useAgentsStore, useCitationsStore } from '@/stores';
import { ChatMessage, MessageType, StreamingMessage, isFulfilledMessage } from '@/types/message';
import { cn } from '@/utils';
import { Handle, Position, ReactFlow } from '@xyflow/react';

import '@xyflow/react/dist/style.css';

type Props = {
  isStreaming: boolean;
  isStreamingToolEvents: boolean;
  startOptionsEnabled: boolean;
  messages: ChatMessage[];
  streamingMessage: StreamingMessage | null;
  agentId?: string;
  onRetry: VoidFunction;
  composer: ReactNode;
  conversationId?: string;
  scrollViewClassName?: string;
};

/**
 * This component is in charge of rendering anything in the main scrollable view.
 * This includes all of the message, the RAG citations, and the composer (which is sticky at the bottom).
 */
const MessagingTree: React.FC<Props> = (props) => {
  const { scrollViewClassName = '', ...rest } = props;
  return (
    <ScrollToBottom
      initialScrollBehavior="auto"
      className={cn(ReservedClasses.MESSAGES, 'relative flex h-0 flex-grow flex-col')}
      scrollViewClassName={cn(
        '!h-full',
        'flex relative mt-auto overflow-x-hidden',
        {
          // For vertically centering the content in @/components/Welcome.tsx
          'mt-0 md:mt-auto': props.messages.length === 0,
        },
        scrollViewClassName
      )}
      followButtonClassName="hidden"
      debounce={100}
    >
      <Content {...rest} />
    </ScrollToBottom>
  );
};
export default memo(MessagingTree);

/**
 * This component lays out the messages, citations, and composer.
 * In order to access the state hooks for the scroll to bottom component, we need to wrap the content in a component.
 */
const Content: React.FC<Props> = (props) => {
  const { isStreaming, messages, composer, streamingMessage } = props;
  const scrollToBottom = useScrollToBottom();
  const {
    agents: { isEditAgentPanelOpen },
  } = useAgentsStore();
  const {
    citations: { hasCitations },
  } = useCitationsStore();

  useFixCopyBug();
  const [isAtBottom] = useSticky();
  const prevIsStreaming = usePrevious(isStreaming);

  // Wait some time before being able to fetch previous messages
  // This is to prevent loading a bunch of messages on first load
  const [isReadyToFetchPreviousMessages, setIsReadyToFetchPreviousMessages] = useState(false);
  useTimeoutEffect(() => {
    setIsReadyToFetchPreviousMessages(true);
  }, 1000);

  // Show the `New Message` button if the user has scrolled up
  // and the last message is a bot message.
  // This reruns when isAtBottom or isStreaming changes only since
  // these are the only times users may miss the newest message.
  const showNewMessageButton = useMemo(() => {
    // Whether the user is at the bottom of the messages container
    if (isAtBottom) return false;
    // When isStreaming changes this means that the bot has sent a new message
    // or is in the process of sending a new message
    if (prevIsStreaming === isStreaming) return false;
    if (!streamingMessage) return false;
    return true;
  }, [isAtBottom, isStreaming]);

  // Scroll to bottom when the user adds a new message
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage?.type === MessageType.USER) {
      scrollToBottom({ behavior: 'smooth' });
    }
  }, [messages.length, scrollToBottom]);

  const { citationToStyles, messageContainerDivRef, composerContainerDivRef } =
    useCalculateCitationStyles(messages, streamingMessage);

  const handleScrollToNewMessage = () => {
    scrollToBottom({ behavior: 'smooth' });
  };

  return (
    <div className="flex h-max min-h-full w-full">
      <div id={MESSAGE_LIST_CONTAINER_ID} className={cn('flex h-auto min-w-0 flex-1 flex-col')}>
        <Messages {...props} ref={messageContainerDivRef} />
        {/* Composer container */}
        <div
          className={cn('sticky bottom-0 px-4 pb-4', 'bg-marble-1000')}
          ref={composerContainerDivRef}
        >
          <Transition
            show={showNewMessageButton}
            enter="duration-300 ease-out transition-all"
            enterFrom="translate-y-10 opacity-0"
            enterTo="translate-y-0 opacity-100"
            leave="duration-300 ease-in transition-all"
            leaveFrom="translate-y-0 opacity-100"
            leaveTo="translate-y-10 opacity-0"
            as="div"
            className="absolute bottom-full left-1/2 -z-10 flex h-fit -translate-x-1/2 transform pb-4"
          >
            <Button
              label="New message"
              splitIcon="arrow-down"
              onClick={handleScrollToNewMessage}
              hideFocusStyles
              kind="primaryOutline"
            />
          </Transition>
          {composer}
        </div>
      </div>

      <div
        className={cn('hidden h-auto border-marble-950', {
          'md:flex': hasCitations || !isEditAgentPanelOpen,
          'border-l': hasCitations,
        })}
      />
      <CitationPanel
        citationToStyles={citationToStyles}
        streamingMessage={streamingMessage}
        className={cn(
          ReservedClasses.CITATION_PANEL,
          'hidden',
          { 'md:flex': hasCitations },
          'relative h-auto w-auto',
          'md:min-w-citation-panel-md lg:min-w-citation-panel-lg xl:min-w-citation-panel-xl'
        )}
      />
    </div>
  );
};

const MessageNode = ({ data: {
  message,
  isLastInList,
  isStreamingToolEvents,
  streamingMessage,
  onRetry,
  i,
} }: {
  data: {
    message: any,
    isLastInList: boolean,
    isStreamingToolEvents: boolean,
    streamingMessage: any,
    onRetry: VoidFunction,
    i: number,
  }
}) => {
  return <>
    <Handle
      type="target"
      position={Position.Top}
      style={{ visibility: 'hidden' }}
    />
    <Handle
      type="source"
      position={Position.Bottom}
      style={{ visibility: 'hidden' }}
    />
    <MessageRow
      key={i}
      message={message}
      isLast={isLastInList && !streamingMessage}
      isStreamingToolEvents={isStreamingToolEvents}
      className={cn({
        // Hide the last message if it is the same as the separate streamed message
        // to avoid a flash of duplicate messages.
        hidden:
          isLastInList &&
          streamingMessage &&
          isFulfilledMessage(streamingMessage) &&
          isFulfilledMessage(message) &&
          streamingMessage.generationId === message.generationId,
      })}
      onRetry={onRetry}
    /></>
}

const StreamingMessageNode = ({ data: {
  isStreamingToolEvents,
  streamingMessage,
  onRetry,
  i,
} }: {
  data: {
    message: any,
    isLastInList: boolean,
    isStreamingToolEvents: boolean,
    streamingMessage: any,
    onRetry: VoidFunction,
    i: number,
  }
}) => {
  return <>
    <Handle
      type="target"
      position={Position.Top}
      style={{ background: '#555' }}
    />
    <Handle
      type="source"
      position={Position.Bottom}
      style={{ background: '#555' }}
    />
    <MessageRow
      isLast
      isStreamingToolEvents={isStreamingToolEvents}
      message={streamingMessage}
      onRetry={onRetry}
    />
  </>
}

type MessagesProps = Props;
/**
 * This component is in charge of rendering the messages.
 */
const Messages = forwardRef<HTMLDivElement, MessagesProps>(function MessagesInternal(
  { onRetry, messages, streamingMessage, agentId, isStreamingToolEvents },
  ref
) {
  const isChatEmpty = messages.length === 0;

  if (isChatEmpty) {
    return (
      <div className="m-auto p-4">
        <Welcome show={isChatEmpty} agentId={agentId} />
      </div>
    );
  }

  const nodeTypes = useMemo(() => ({ message: MessageNode, streamingMessage: StreamingMessageNode }), []);

  const nodes = messages.map((message, i) => {
    const isLastInList = i === messages.length - 1;
    return {
      id: 'node-' + i,
      type: 'message',
      position: { x: 250, y: 5 + i * 100 },
      isConnectable: true,
      targetPosition: Position.Top,
      sourcePosition: Position.Bottom,
      data: {
        message,
        isLastInList,
        isStreamingToolEvents,
        streamingMessage,
        onRetry,
        i,
      },
    };
  })

  if (streamingMessage) {
    nodes.push({
      id: 'streaming-message',
      type: 'streamingMessage',
      position: { x: 250, y: 5 + messages.length * 100 },
      isConnectable: true,
      targetPosition: Position.Top,
      sourcePosition: Position.Bottom,
      data: {
        isStreamingToolEvents,
        streamingMessage,
        onRetry,
        i: messages.length,
      }
    })
  }

  const initialEdges = nodes.flatMap((_, i) => {
    if (i === 0) return [];
    return { id: `e${i}`, source: `node-${i - 1}`, target: `node-${i}` };
  })

  return (
    <div className="flex h-full flex-col gap-y-4 px-4 py-6 md:gap-y-6" ref={ref}>
      <div style={{ width: '100%', height: '100%' }}>
        <ReactFlow nodes={nodes} nodeTypes={nodeTypes} edges={initialEdges} />
      </div>

      {/* {messages.map((m, i) => {
          const isLastInList = i === messages.length - 1;
          return (
            <MessageRow
              key={i}
              message={m}
              isLast={isLastInList && !streamingMessage}
              isStreamingToolEvents={isStreamingToolEvents}
              className={cn({
                // Hide the last message if it is the same as the separate streamed message
                // to avoid a flash of duplicate messages.
                hidden:
                  isLastInList &&
                  streamingMessage &&
                  isFulfilledMessage(streamingMessage) &&
                  isFulfilledMessage(m) &&
                  streamingMessage.generationId === m.generationId,
              })}
              onRetry={onRetry}
            />
          );
        })} */}
    </div>
  );
});
