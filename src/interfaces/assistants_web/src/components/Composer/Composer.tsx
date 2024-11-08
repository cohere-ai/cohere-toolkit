'use client';

import { useResizeObserver } from '@react-hookz/web';
import React, { useEffect, useRef, useState } from 'react';

import { AgentPublic, ToolDefinition } from '@/cohere-client';
import { ComposerError, ComposerFiles, ComposerToolbar } from '@/components/Composer';
import { DragDropFileInput, Icon, STYLE_LEVEL_TO_CLASSES } from '@/components/UI';
import { CHAT_COMPOSER_TEXTAREA_ID } from '@/constants';
import { useAvailableTools, useBreakpoint, useIsDesktop } from '@/hooks';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';
import { ChatMessage } from '@/types/message';
import { cn } from '@/utils';

type Props = {
  isStreaming: boolean;
  value: string;
  streamingMessage: ChatMessage | null;
  onStop: VoidFunction;
  onSend: (message?: string, overrides?: Partial<ConfigurableParams>) => void;
  onChange: (message: string) => void;
  onUploadFile: (files: File[]) => void;
  agent?: AgentPublic;
  tools?: ToolDefinition[];
  chatWindowRef?: React.RefObject<HTMLDivElement>;
  lastUserMessage?: ChatMessage;
};

export const Composer: React.FC<Props> = ({
  value,
  isStreaming,
  agent,
  tools,
  onSend,
  onChange,
  onStop,
  onUploadFile,
  chatWindowRef,
  lastUserMessage,
}) => {
  const isDesktop = useIsDesktop();
  const breakpoint = useBreakpoint();
  const isSmallBreakpoint = breakpoint === 'sm';
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { unauthedTools } = useAvailableTools({ agent, allTools: tools });
  const isToolAuthRequired = unauthedTools.length > 0;

  const [chatWindowHeight, setChatWindowHeight] = useState(0);
  const [isDragDropInputActive, setIsDragDropInputActive] = useState(false);

  const isReadyToReceiveMessage = !isStreaming;
  const isComposerDisabled = isToolAuthRequired;
  const canSend = isReadyToReceiveMessage && value.trim().length > 0 && !isComposerDisabled;

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter') {
      // Do expected default behaviour (add a newline inside of the textarea)
      if (e.shiftKey || isSmallBreakpoint) return;

      e.preventDefault();
      if (canSend) {
        onSend(value);
        onChange('');
      }
    }

    if (e.key === 'ArrowUp' && value.trim() === '' && !isStreaming) {
      onChange(lastUserMessage?.text || '');
      setTimeout(() => {
        textareaRef.current?.setSelectionRange(
          textareaRef.current?.value.length,
          textareaRef.current?.value.length
        );
      }, 0);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (isComposerDisabled) {
      return;
    }

    onChange(e.target.value);
  };

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;

      // if the content overflows the max height, show the scrollbar
      if (textarea.scrollHeight > textarea.clientHeight + 2) {
        textarea.style.overflowY = 'scroll';
      } else {
        textarea.style.overflowY = 'hidden';
      }
    }
  }, [value]);

  useEffect(() => {
    if (!textareaRef.current) return;
    let timer: NodeJS.Timeout;
    if (isDesktop) {
      /**
       * The textarea focus state is delayed so that the slide in transition can finish on smaller screens
       * See `chat/src/components/Layout.tsx` for the transition duration and details
       */
      timer = setTimeout(() => {
        textareaRef.current?.focus();
      }, 500);
    } else {
      textareaRef.current?.blur();
    }
    return () => clearTimeout(timer);
  }, [isDesktop]);

  useResizeObserver(chatWindowRef || null, (e) => {
    setChatWindowHeight(e.target.clientHeight);
  });

  return (
    <div className="flex w-full flex-col">
      <div
        className={cn(
          'relative flex w-full flex-col',
          'transition ease-in-out',
          'rounded border bg-marble-980 dark:bg-volcanic-100',
          'border-marble-800 dark:border-volcanic-200',
          {
            'bg-marble-950 dark:bg-mushroom-150': isComposerDisabled,
          }
        )}
        onDragEnter={() => setIsDragDropInputActive(true)}
        onDragOver={() => setIsDragDropInputActive(true)}
        onDragLeave={() => setIsDragDropInputActive(false)}
        onDrop={() => {
          setTimeout(() => {
            setIsDragDropInputActive(false);
          }, 100);
        }}
      >
        <DragDropFileInput active={isDragDropInputActive} onUploadFile={onUploadFile} />
        <div className="relative flex items-end p-2">
          <textarea
            id={CHAT_COMPOSER_TEXTAREA_ID}
            dir="auto"
            ref={textareaRef}
            value={value}
            placeholder="Message..."
            className={cn(
              'w-full flex-1 resize-none overflow-hidden',
              'self-center',
              'px-2',
              'rounded',
              'bg-transparent',
              'transition ease-in-out',
              'placeholder:text-volcanic-600 focus:outline-none dark:placeholder:text-marble-800',
              STYLE_LEVEL_TO_CLASSES.p,
              'leading-[150%]'
            )}
            style={{
              maxHeight: `${
                chatWindowHeight * (isSmallBreakpoint || breakpoint === 'md' ? 0.6 : 0.75)
              }px`,
            }}
            rows={1}
            onKeyDown={handleKeyDown}
            onChange={handleChange}
            disabled={isComposerDisabled}
          />
          <button
            className={cn(
              'size-8',
              'flex flex-shrink-0 items-center justify-center rounded',
              'transition ease-in-out',
              'text-mushroom-300 hover:bg-mushroom-900 dark:text-marble-950 dark:hover:bg-mushroom-300',
              { 'text-mushroom-600 dark:text-marble-800': !canSend }
            )}
            type="button"
            onClick={() => {
              if (canSend) {
                onSend(value);
              } else {
                onStop();
              }
            }}
          >
            {isReadyToReceiveMessage ? <Icon name="arrow-submit" /> : <Square />}
          </button>
        </div>
        <ComposerFiles />
        <ComposerToolbar onUploadFile={onUploadFile} agent={agent} tools={tools} />
      </div>
      <ComposerError className="pt-2" />
    </div>
  );
};

const Square = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="1em"
    height="1em"
    fill="currentColor"
    stroke="currentColor"
    strokeWidth="0"
    viewBox="0 0 448 512"
  >
    <path d="M400 32H48C21.5 32 0 53.5 0 80v352c0 26.5 21.5 48 48 48h352c26.5 0 48-21.5 48-48V80c0-26.5-21.5-48-48-48z" />
  </svg>
);
