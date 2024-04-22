import { ChangeEvent, useEffect, useRef } from 'react';

import { Tool } from '@/cohere-client';
import { ComposerFiles } from '@/components/Conversation/ComposerFiles';
import { ComposerMenu } from '@/components/Conversation/ComposerMenu';
import { Icon, STYLE_LEVEL_TO_CLASSES } from '@/components/Shared';
import { CHAT_COMPOSER_TEXTAREA_ID } from '@/constants';
import { useIsDesktop } from '@/hooks/breakpoint';
import { useFileActions } from '@/hooks/files';
import { useSettingsStore } from '@/stores';
import { ChatMessage } from '@/types/message';
import { cn } from '@/utils';

type Props = {
  isStreaming: boolean;
  value: string;
  messages: ChatMessage[];
  streamingMessage: ChatMessage | null;
  onStop: VoidFunction;
  onSend: (message?: string, tools?: Tool[]) => void;
  onChange: (e: ChangeEvent<HTMLTextAreaElement>) => void;
  onUploadFile: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

const Composer: React.FC<Props> = ({
  value,
  isStreaming,
  onSend,
  onChange,
  onStop,
  onUploadFile,
}) => {
  const isReadyToReceiveMessage = !isStreaming;
  const canSend = isReadyToReceiveMessage && value.trim().length > 0;
  const {
    settings: { isMobileConvListPanelOpen },
  } = useSettingsStore();
  const { uploadingFiles, composerFiles, deleteComposerFile, deleteUploadingFile } =
    useFileActions();
  const isDesktop = useIsDesktop();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter') {
      // Do expected default behaviour (add a newline inside of the textarea)
      if (e.shiftKey) return;

      e.preventDefault();
      if (canSend) {
        onSend(undefined);
      }
    }
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

  return (
    <div className="flex w-full flex-col gap-y-2">
      <div className="flex items-end gap-x-2 md:gap-x-4">
        <ComposerMenu onUploadFile={onUploadFile} />
        <div
          className={cn(
            'flex w-full items-end',
            'transition ease-in-out',
            'rounded border bg-marble-100',
            'border-marble-500 focus-within:border-secondary-700',
            'pr-2 md:pr-4'
          )}
        >
          <div className="relative grow flex-col">
            <textarea
              id={CHAT_COMPOSER_TEXTAREA_ID}
              dir="auto"
              ref={textareaRef}
              value={value}
              placeholder="Message..."
              className={cn(
                'min-h-[3rem] md:min-h-[4rem]',
                'max-h-48 w-full flex-1 resize-none overflow-hidden',
                'self-center',
                'p-2 md:p-4',
                'rounded',
                'bg-marble-100',
                'transition ease-in-out',
                'focus:outline-none',
                STYLE_LEVEL_TO_CLASSES.p,
                'leading-[200%]'
              )}
              rows={1}
              onKeyDown={handleKeyDown}
              onChange={onChange}
            />
            <ComposerFiles
              uploadingFiles={uploadingFiles}
              composerFiles={composerFiles}
              deleteFile={deleteComposerFile}
              deleteUploadingFile={deleteUploadingFile}
            />
          </div>
          <button
            className={cn(
              'h-8 w-8',
              'my-2 ml-1 md:my-4',
              'flex flex-shrink-0 items-center justify-center rounded',
              'border transition ease-in-out',
              'border-secondary-400 bg-secondary-200 text-secondary-800 hover:bg-secondary-300'
            )}
            type="button"
            onClick={() => (canSend ? onSend(undefined) : onStop())}
          >
            {isReadyToReceiveMessage ? <Icon name="arrow-right" /> : <Square />}
          </button>
        </div>
      </div>
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

export default Composer;
