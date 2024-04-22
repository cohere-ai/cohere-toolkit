import { usePreviousDistinct } from '@react-hookz/web';
import { forwardRef, useEffect, useState } from 'react';
import { useLongPress } from 'react-aria';

import { Avatar } from '@/components/Avatar';
import { LongPressMenu } from '@/components/LongPressMenu';
import { MessageContent } from '@/components/MessageContent';
import { CopyToClipboardButton, CopyToClipboardIconButton } from '@/components/Shared';
import { ReservedClasses } from '@/constants';
import { Breakpoint, useBreakpoint } from '@/hooks/breakpoint';
import { getMessageRowId } from '@/hooks/citations';
import { useCitationsStore } from '@/stores';
import {
  type ChatMessage,
  isFulfilledMessage,
  isFulfilledOrTypingMessage,
  isFulfilledOrTypingMessageWithCitations,
  isUserMessage,
} from '@/types/message';
import { cn } from '@/utils';

type Props = {
  isLast: boolean;
  message: ChatMessage;
  delay?: boolean;
  className?: string;
  onCopy?: VoidFunction;
  onRetry?: VoidFunction;
};

/**
 * Renders a single message row from the user or from our models.
 */
const MessageRow = forwardRef<HTMLDivElement, Props>(function MessageRowInternal(
  { message, delay = false, isLast, className = '', onCopy, onRetry },
  ref
) {
  const breakpoint = useBreakpoint();

  const [isShowing, setIsShowing] = useState(false);
  const [isLongPressMenuOpen, setIsLongPressMenuOpen] = useState(false);
  const {
    citations: { selectedCitation, hoveredGenerationId },
    hoverCitation,
  } = useCitationsStore();

  const getMessageText = () => {
    if (isFulfilledMessage(message)) {
      return message.originalText;
    }

    return message.text;
  };

  const enableLongPress =
    (isFulfilledMessage(message) || isUserMessage(message)) && breakpoint === Breakpoint.sm;
  const { longPressProps } = useLongPress({
    onLongPress: () => setIsLongPressMenuOpen(true),
  });

  // Delay the appearance of the message to make it feel more natural.
  useEffect(() => {
    if (delay) {
      setTimeout(() => setIsShowing(true), 300);
    }
  }, []);

  const [highlightMessage, setHighlightMessage] = useState(false);
  const prevSelectedCitationGenId = usePreviousDistinct(selectedCitation?.generationId);

  useEffect(() => {
    if (isFulfilledOrTypingMessage(message) && message.citations && message.generationId) {
      if (
        selectedCitation?.generationId === message.generationId &&
        prevSelectedCitationGenId !== message.generationId
      ) {
        setHighlightMessage(true);

        setTimeout(() => {
          setHighlightMessage(false);
        }, 1000);
      }
    }
  }, [selectedCitation?.generationId, prevSelectedCitationGenId]);

  if (delay && !isShowing) return null;

  const handleOnMouseEnter = () => {
    if (isFulfilledOrTypingMessageWithCitations(message)) {
      hoverCitation(message.generationId);
    }
  };

  const handleOnMouseLeave = () => {
    if (isFulfilledOrTypingMessageWithCitations(message)) {
      hoverCitation(null);
    }
  };

  return (
    <div
      id={
        isFulfilledOrTypingMessage(message) && message.generationId
          ? getMessageRowId(message.generationId)
          : undefined
      }
      className={cn(ReservedClasses.MESSAGE, 'flex', className)}
      onMouseEnter={handleOnMouseEnter}
      onMouseLeave={handleOnMouseLeave}
      ref={ref}
    >
      <LongPressMenu
        isOpen={isLongPressMenuOpen}
        close={() => setIsLongPressMenuOpen(false)}
        className="md:hidden"
      >
        <div className={cn('flex flex-col divide-y', 'divide-marble-300')}>
          <div className="flex flex-col gap-y-4 pt-4">
            <CopyToClipboardButton
              value={getMessageText()}
              label="Copy text"
              kind="secondary"
              iconAtStart
              onClick={onCopy}
            />
          </div>
        </div>
      </LongPressMenu>
      <div
        className={cn(
          'group flex h-fit w-full flex-col gap-2 rounded-md p-2 text-left md:flex-row',
          'transition-colors ease-in-out',
          'hover:bg-secondary-50',

          {
            'bg-secondary-50':
              isFulfilledOrTypingMessage(message) &&
              message.generationId &&
              hoveredGenerationId === message.generationId,
            'bg-primary-50 hover:bg-primary-50': highlightMessage,
          }
        )}
        {...(enableLongPress && longPressProps)}
      >
        <div className="flex w-full gap-x-2">
          <Avatar message={message} />
          <div className="flex w-full min-w-0 max-w-message flex-1 flex-col items-center gap-x-1 md:flex-row">
            <MessageContent isLast={isLast} message={message} onRetry={onRetry} />
            <div
              className={cn('flex h-full items-end justify-end self-end', {
                'hidden md:invisible md:flex':
                  !isFulfilledMessage(message) && !isUserMessage(message),
                'hidden md:invisible md:flex md:group-hover:visible': !isLast,
              })}
            >
              <CopyToClipboardIconButton value={getMessageText()} onClick={onCopy} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});
export default MessageRow;
