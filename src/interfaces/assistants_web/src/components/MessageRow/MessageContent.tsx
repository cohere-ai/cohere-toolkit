'use client';

import { Transition } from '@headlessui/react';
import { PropsWithChildren } from 'react';

import { Markdown } from '@/components/Markdown';
import { CitationTextHighlighter, DataTable, MarkdownImage } from '@/components/MessageRow';
import { Icon, Skeleton, Text } from '@/components/UI';
import {
  type ChatMessage,
  MessageType,
  isAbortedMessage,
  isErroredMessage,
  isFulfilledOrTypingMessage,
  isLoadingMessage,
} from '@/types/message';
import { cn, formatFileSize } from '@/utils';

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

  if (isUserError) {
    return (
      <MessageWrapper>
        <Text>{message.text}</Text>
        <MessageInfo type="error">
          {message.error}
          {isLast && (
            <button className="ml-2 underline underline-offset-1" type="button" onClick={onRetry}>
              Retry?
            </button>
          )}
        </MessageInfo>
      </MessageWrapper>
    );
  }

  if (isUser) {
    return (
      <MessageWrapper>
        <Markdown text={message.text} renderRawHtml={false} />
        {message.files && message.files.length > 0 && (
          <div className="flex flex-wrap gap-2 py-2">
            {message.files.map((file) => (
              <div key={file.id} className="group flex w-60 gap-x-2 rounded bg-mushroom-600/10 p-3">
                <div
                  className={cn(
                    'flex h-8 w-8 flex-shrink-0 items-center justify-center rounded',
                    'bg-mushroom-600/20 text-mushroom-300 dark:text-marble-950'
                  )}
                >
                  <Icon name="file" kind="outline" />
                </div>
                <div className="flex w-full flex-grow flex-col gap-y-0.5 truncate">
                  <Text styleAs="label" className="w-full truncate font-medium">
                    {file.file_name}
                  </Text>
                  <div className="flex items-center gap-x-2 uppercase">
                    {file.file_size ? (
                      <Text styleAs="caption" className="text-volcanic-500 dark:text-marble-900">
                        {formatFileSize(file.file_size)}
                      </Text>
                    ) : (
                      <Skeleton className="h-5 w-10 bg-mushroom-600/20 dark:bg-volcanic-600" />
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </MessageWrapper>
    );
  }

  if (isLoading) {
    const hasLoadingMessage = message.text.length > 0;
    return (
      <MessageWrapper>
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
      </MessageWrapper>
    );
  }

  if (isBotError) {
    return (
      <MessageWrapper>
        {message.text.length > 0 ? (
          <Markdown text={message.text} />
        ) : (
          <Text className={cn('text-volcanic-400')}>{BOT_ERROR_MESSAGE}</Text>
        )}
        <MessageInfo type="error">{message.error}</MessageInfo>
      </MessageWrapper>
    );
  }

  const hasCitations =
    isTypingOrFulfilledMessage && message.citations && message.citations.length > 0;
  return (
    <MessageWrapper>
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
    </MessageWrapper>
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

const MessageWrapper = ({ children }: PropsWithChildren) => (
  <div className="flex w-full flex-col justify-center gap-y-1 py-1">
    <Text
      as="div"
      className="flex flex-col gap-y-1 whitespace-pre-wrap [overflow-wrap:anywhere] md:max-w-4xl"
    >
      {children}
    </Text>
  </div>
);
