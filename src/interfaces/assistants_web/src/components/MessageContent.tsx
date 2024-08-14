'use client';

import { Transition } from '@headlessui/react';
import { PropsWithChildren } from 'react';

import { CitationTextHighlighter } from '@/components/Citations/CitationTextHighlighter';
import { DataTable } from '@/components/DataTable';
import { MarkdownImage } from '@/components/MarkdownImage';
import { MessageFile } from '@/components/MessageFile';
import { Icon } from '@/components/Shared';
import { Markdown, Text } from '@/components/Shared';
import {
  type ChatMessage,
  MessageType,
  isAbortedMessage,
  isErroredMessage,
  isFulfilledOrTypingMessage,
  isLoadingMessage,
} from '@/types/message';
import { cn } from '@/utils';

type Props = {
  isLast: boolean;
  message: ChatMessage;
  onRetry?: VoidFunction;
};

const BOT_ERROR_MESSAGE = 'Unable to generate a response since an error was encountered. ';

export const MessageContent: React.FC<Props> = ({ isLast, message, onRetry }) => {
  const isUser = message.type === MessageType.USER;
  const isLoading = isLoadingMessage(message);
  const isBotError = isErroredMessage(message);
  const isUserError = isUser && message.error;
  const isAborted = isAbortedMessage(message);
  const isTypingOrFulfilledMessage = isFulfilledOrTypingMessage(message);

  let content: React.ReactNode = null;

  if (isUserError) {
    content = (
      <>
        <Text>{message.text}</Text>
        <MessageInfo type="error">
          {message.error}
          {isLast && (
            <button className="underline underline-offset-1" type="button" onClick={onRetry}>
              Retry?
            </button>
          )}
        </MessageInfo>
      </>
    );
  } else if (isUser) {
    content = (
      <>
        <Markdown text={message.text} renderRawHtml={false} />
        {message.files && message.files.length > 0 && (
          <div className="flex flex-wrap gap-2 py-2">
            {message.files.map((file) => (
              <MessageFile key={file.id} name={file.file_name} size={file.file_size} />
            ))}
          </div>
        )}
      </>
    );
  } else if (isLoading) {
    const hasLoadingMessage = message.text.length > 0;
    content = (
      <Text className={cn('flex min-w-0 text-volcanic-400')} as="span">
        {hasLoadingMessage && (
          <Transition
            as="div"
            appear={true}
            show={true}
            enterFrom="opacity-0"
            enterTo="opacity-full"
            enter="transition-opacity ease-in-out duration-500"
          >
            {message.text}
          </Transition>
        )}
        {!hasLoadingMessage && (
          <span className="w-max">
            <div className="animate-typing-ellipsis overflow-hidden whitespace-nowrap pr-1">
              ...
            </div>
          </span>
        )}
      </Text>
    );
  } else if (isBotError) {
    content = (
      <>
        {message.text.length > 0 ? (
          <Markdown text={message.text} />
        ) : (
          <Text className={cn('text-volcanic-400')}>{BOT_ERROR_MESSAGE}</Text>
        )}
        <MessageInfo type="error">{message.error}</MessageInfo>
      </>
    );
  } else {
    const hasCitations =
      isTypingOrFulfilledMessage && message.citations && message.citations.length > 0;
    content = (
      <>
        <Markdown
          className={cn({
            'text-volcanic-400': isAborted,
          })}
          text={message.text}
          customComponents={{
            img: MarkdownImage as any,
            cite: CitationTextHighlighter as any,
            table: DataTable as any,
          }}
          renderLaTex={!hasCitations}
        />
        {isAborted && (
          <MessageInfo>
            This generation was stopped.{' '}
            {isLast && isAborted && (
              <button className="underline underline-offset-1" type="button" onClick={onRetry}>
                Retry?
              </button>
            )}
          </MessageInfo>
        )}
      </>
    );
  }

  return (
    <div className="flex w-full flex-col justify-center gap-y-1 py-1">
      <Text
        as="div"
        className="flex flex-col gap-y-1 whitespace-pre-wrap [overflow-wrap:anywhere] md:max-w-4xl"
      >
        {content}
      </Text>
    </div>
  );
};

const MessageInfo = ({
  type = 'default',
  children,
}: PropsWithChildren & { type?: 'default' | 'error' }) => (
  <div
    className={cn('flex items-start gap-1', {
      'text-volcanic-400': type === 'default',
      'text-danger-350': type === 'error',
    })}
  >
    <Icon name="warning" size="sm" className="mt-1 flex flex-shrink-0 items-center" />
    <Text as="span">{children}</Text>
  </div>
);
