'use client';

import { useResizeObserver } from '@react-hookz/web';
import React, { useEffect, useRef, useState } from 'react';

import { ComposerError } from '@/components/Conversation/Composer/ComposerError';
import { ComposerFiles } from '@/components/Conversation/Composer/ComposerFiles';
import { ComposerToolbar } from '@/components/Conversation/Composer/ComposerToolbar';
import { DragDropFileUploadOverlay } from '@/components/Conversation/Composer/DragDropFileUploadOverlay';
import { FirstTurnSuggestions } from '@/components/FirstTurnSuggestions';
import { Icon, STYLE_LEVEL_TO_CLASSES } from '@/components/Shared';
import { CHAT_COMPOSER_TEXTAREA_ID } from '@/constants';
import { useBreakpoint, useIsDesktop } from '@/hooks/breakpoint';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';
import { useDataSourceTags } from '@/hooks/tags';
import { useUnauthedTools } from '@/hooks/tools';
import { useSettingsStore } from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';
import { ChatMessage } from '@/types/message';
import { cn } from '@/utils';

type Props = {
  isFirstTurn: boolean;
  isStreaming: boolean;
  value: string;
  streamingMessage: ChatMessage | null;
  onStop: VoidFunction;
  onSend: (message?: string, overrides?: Partial<ConfigurableParams>) => void;
  onChange: (message: string) => void;
  onUploadFile: (files: File[]) => void;
  requiredTools?: string[];
  chatWindowRef?: React.RefObject<HTMLDivElement>;
};

export const Composer: React.FC<Props> = ({
  isFirstTurn,
  value,
  isStreaming,
  requiredTools,
  onSend,
  onChange,
  onStop,
  onUploadFile,
  chatWindowRef,
}) => {
  const {
    settings: { isMobileConvListPanelOpen },
  } = useSettingsStore();
  const isDesktop = useIsDesktop();
  const breakpoint = useBreakpoint();
  const isSmallBreakpoint = breakpoint === 'sm';
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { isToolAuthRequired } = useUnauthedTools();
  const { agentId } = useChatRoutes();
  const { suggestedTags, totalTags, setTagQuery, tagQuery, getTagQuery } = useDataSourceTags({
    requiredTools,
  });
  const { data: experimentalFeatures } = useExperimentalFeatures();

  const [isComposing, setIsComposing] = useState(false);
  const [chatWindowHeight, setChatWindowHeight] = useState(0);
  const [isDragDropInputActive, setIsDragDropInputActive] = useState(false);
  const [showDataSourceMenu, setShowDataSourceMenu] = useState(false);

  const isReadyToReceiveMessage = !isStreaming;
  const isAgentsModeOn = !!experimentalFeatures?.USE_AGENTS_VIEW;
  const isComposerDisabled = isToolAuthRequired && isAgentsModeOn;
  const canSend = isReadyToReceiveMessage && value.trim().length > 0 && !isComposerDisabled;

  const handleCompositionStart = () => {
    setIsComposing(true);
  };

  const handleCompositionEnd = () => {
    setIsComposing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !isComposing) {
      // Do expected default behaviour (add a newline inside of the textarea)
      if (e.shiftKey || isSmallBreakpoint) return;

      e.preventDefault();
      if (canSend) {
        onSend(value);
        setTagQuery('');
        setShowDataSourceMenu(false);
        onChange('');
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (isComposerDisabled) {
      return;
    }

    onChange(e.target.value);
    if (textareaRef.current) {
      const newTagQuery = getTagQuery(e.target.value, textareaRef.current.selectionStart);
      setTagQuery(newTagQuery);

      if (newTagQuery.length === 1 && !showDataSourceMenu) {
        setShowDataSourceMenu(true);
      } else if (newTagQuery.length === 0 && showDataSourceMenu) {
        setShowDataSourceMenu(false);
      }
    }
  };

  const handleTagSelect = () => {
    if (!textareaRef.current) return;
    onChange(value.slice(0, value.length - tagQuery.length));
    setTagQuery('');
    setShowDataSourceMenu(false);
  };

  const handleDataSourceMenuClick = () => {
    setShowDataSourceMenu((prevShow) => !prevShow);
  };

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
      textarea.addEventListener('compositionstart', handleCompositionStart);
      textarea.addEventListener('compositionend', handleCompositionEnd);

      // if the content overflows the max height, show the scrollbar
      if (textarea.scrollHeight > textarea.clientHeight + 2) {
        textarea.style.overflowY = 'scroll';
      } else {
        textarea.style.overflowY = 'hidden';
      }

      return () => {
        if (textarea) {
          textarea.removeEventListener('compositionstart', handleCompositionStart);
          textarea.removeEventListener('compositionend', handleCompositionEnd);
        }
      };
    }
  }, [value]);

  useEffect(() => {
    if (!textareaRef.current) return;
    let timer: NodeJS.Timeout;
    if (!isMobileConvListPanelOpen || isDesktop) {
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
  }, [isMobileConvListPanelOpen, isDesktop, textareaRef.current]);

  useResizeObserver(chatWindowRef || null, (e) => {
    setChatWindowHeight(e.target.clientHeight);
  });

  return (
    <div className="flex w-full flex-col">
      {!agentId && <FirstTurnSuggestions isFirstTurn={isFirstTurn} onSuggestionClick={onSend} />}
      <div
        className={cn(
          'relative flex w-full flex-col',
          'transition ease-in-out',
          'rounded border bg-marble-1000',
          'border-marble-800 focus-within:border-mushroom-400',
          {
            'border-marble-800 bg-marble-950': isComposerDisabled,
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
        <DragDropFileUploadOverlay active={isDragDropInputActive} onUploadFile={onUploadFile} />
        <div className="relative flex items-end pr-2 md:pr-4">
          <textarea
            id={CHAT_COMPOSER_TEXTAREA_ID}
            dir="auto"
            ref={textareaRef}
            value={value}
            placeholder="Message..."
            className={cn(
              'w-full flex-1 resize-none overflow-hidden',
              'self-center',
              'px-2 pb-3 pt-2 md:px-4 md:pb-6 md:pt-4',
              'rounded',
              'bg-marble-1000',
              'transition ease-in-out',
              'placeholder:text-volcanic-600 focus:outline-none',
              STYLE_LEVEL_TO_CLASSES.p,
              'leading-[150%]',
              {
                'bg-marble-950': isComposerDisabled,
              }
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
              'h-8 w-8',
              'my-2 ml-1 md:my-4',
              'flex flex-shrink-0 items-center justify-center rounded',
              'transition ease-in-out',
              'text-mushroom-300 hover:bg-mushroom-900',
              { 'text-mushroom-600': !canSend }
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
            {isReadyToReceiveMessage ? <Icon name="arrow-right" /> : <Square />}
          </button>
        </div>
        <ComposerFiles />
        <ComposerToolbar
          isStreaming={isStreaming}
          onUploadFile={onUploadFile}
          onDataSourceMenuToggle={handleDataSourceMenuClick}
          menuProps={{
            show: showDataSourceMenu,
            tagQuery: tagQuery,
            tags: suggestedTags,
            totalTags: totalTags,
            onChange: handleTagSelect,
            onHide: () => setShowDataSourceMenu(false),
            onToggle: handleDataSourceMenuClick,
            onSeeAll: () => textareaRef.current?.focus(),
          }}
        />
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
