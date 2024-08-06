'use client';

import { forwardRef, useEffect, useState } from 'react';
import { useLongPress } from 'react-aria';

import { Avatar } from '@/components/Avatar';
import { IconButton } from '@/components/IconButton';
import { LongPressMenu } from '@/components/LongPressMenu';
import { MessageContent } from '@/components/MessageContent';
import { Button, CopyToClipboardButton, CopyToClipboardIconButton } from '@/components/Shared';
import { ToolEvents } from '@/components/ToolEvents';
import { Breakpoint, useBreakpoint } from '@/hooks/breakpoint';
import {
  type ChatMessage,
  isAbortedMessage,
  isErroredMessage,
  isFulfilledMessage,
  isFulfilledOrTypingMessage,
  isUserMessage,
} from '@/types/message';
import { cn } from '@/utils';

type Props = {
  isLast: boolean;
  message: ChatMessage;
  isStreamingToolEvents: boolean;
  delay?: boolean;
  className?: string;
  onCopy?: VoidFunction;
  onRetry?: VoidFunction;
};

/**
 * Renders a single message row from the user or from our models.
 */
const MessageRow = forwardRef<HTMLDivElement, Props>(function MessageRowInternal(
  { message, delay = false, isLast, isStreamingToolEvents, className = '', onCopy, onRetry },
  ref
) {
  const breakpoint = useBreakpoint();

  const [isShowing, setIsShowing] = useState(false);
  const [isLongPressMenuOpen, setIsLongPressMenuOpen] = useState(false);
  const [isStepsExpanded, setIsStepsExpanded] = useState<boolean>(true);
  const hasSteps =
    (isFulfilledOrTypingMessage(message) ||
      isErroredMessage(message) ||
      isAbortedMessage(message)) &&
    !!message.toolEvents &&
    message.toolEvents.length > 0;

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

  if (delay && !isShowing) return null;

  return (
    <div className={cn('flex', className)} ref={ref}>
      <LongPressMenu
        isOpen={isLongPressMenuOpen}
        close={() => setIsLongPressMenuOpen(false)}
        className="md:hidden"
      >
        <div className="divide-marble-950' flex flex-col divide-y">
          <div className="flex flex-col gap-y-4 pt-4">
            <CopyToClipboardButton
              value={getMessageText()}
              label="Copy text"
              kind="secondary"
              iconAtStart
              onClick={onCopy}
            />
            {hasSteps && (
              <Button
                label={`${isStepsExpanded ? 'Hide' : 'Show'} steps`}
                icon="list"
                iconOptions={{ className: 'dark:fill-marble-800' }}
                kind="secondary"
                aria-label={`${isStepsExpanded ? 'Hide' : 'Show'} steps`}
                onClick={() => setIsStepsExpanded((prevIsExpanded) => !prevIsExpanded)}
              />
            )}
          </div>
        </div>
      </LongPressMenu>
      <div
        className={cn(
          'group flex h-fit w-full flex-col gap-2 rounded-md p-2 text-left md:flex-row',
          'transition-colors ease-in-out',
          'hover:bg-mushroom-950 dark:hover:bg-volcanic-150'
        )}
        {...(enableLongPress && longPressProps)}
      >
        <div className="flex w-full gap-x-2">
          <Avatar message={message} />
          <div className="flex w-full min-w-0 max-w-message flex-1 flex-col items-center gap-x-3 md:flex-row">
            <div className="w-full">
              {hasSteps && (
                <ToolEvents
                  show={isStepsExpanded}
                  events={message.toolEvents}
                  isStreaming={isStreamingToolEvents}
                  isLast={isLast}
                />
              )}

              <MessageContent isLast={isLast} message={message} onRetry={onRetry} />
            </div>
            <div
              className={cn('flex h-full items-end justify-end self-end', {
                'hidden md:invisible md:flex':
                  !isFulfilledMessage(message) && !isUserMessage(message),
                'hidden md:invisible md:flex md:group-hover:visible': !isLast,
              })}
            >
              {hasSteps && (
                <IconButton
                  tooltip={{ label: `${isStepsExpanded ? 'Hide' : 'Show'} steps`, size: 'sm' }}
                  iconName="list"
                  className="grid place-items-center rounded hover:bg-mushroom-900 dark:hover:bg-volcanic-200"
                  iconClassName={cn(
                    'text-volcanic-300 group-hover/icon-button:fill-mushroom-300',
                    'dark:fill-marble-800 dark:group-hover/icon-button:fill-marble-800',
                    {
                      'hidden md:invisible md:flex': !isFulfilledMessage(message),
                    }
                  )}
                  onClick={() => setIsStepsExpanded((prevIsExpanded) => !prevIsExpanded)}
                />
              )}
              <CopyToClipboardIconButton value={getMessageText()} onClick={onCopy} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});
export default MessageRow;
