'use client';

import { Popover, PopoverButton, PopoverPanel } from '@headlessui/react';
import { PropsWithChildren, useMemo, useRef } from 'react';

import { Citation } from '@/components/Citations/Citation';
import { NewCitation } from '@/components/Citations/NewCitation';
import { useContextStore } from '@/context';
import { useBrandedColors } from '@/hooks/brandedColors';
import { Breakpoint, useBreakpoint } from '@/hooks/breakpoint';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useCitationsStore, useConversationStore, useSettingsStore } from '@/stores';
import { FulfilledMessage, TypingMessage, isFulfilledOrTypingMessage } from '@/types/message';
import { cn } from '@/utils';
import { createStartEndKey } from '@/utils';

const FALLBACK_CODE_SNIPPET_TEXT = '[source]';

type Props = PropsWithChildren<{
  generationId: string;
  start: string;
  end: string;
  isCodeSnippet?: boolean;
}>;

/**
 * A component that highlights text and allows the user to click on it to run an action
 * It is used to highlight citations in the chat, which are created by using a custom remark plugin
 * @param children The text to highlight
 * @param generationId The generation id that the citation refers to
 * @param start The start index of the citation
 * @param end The end index of the citation
 * @param isCodeSnippet Whether or not the citation is inside of a code snippet
 */
export const CitationTextHighlighter: React.FC<Props> = ({
  children,
  generationId,
  start,
  end,
  isCodeSnippet = false,
}) => {
  const { agentId } = useChatRoutes();
  const breakpoint = useBreakpoint();
  const { open } = useContextStore();
  const {
    conversation: { messages },
  } = useConversationStore();
  const {
    citations: { citationReferences, selectedCitation },
    selectCitation,
  } = useCitationsStore();
  const { setSettings } = useSettingsStore();
  const ref = useRef<HTMLElement>(null);
  const isGenerationSelected = selectedCitation?.generationId === generationId;
  const message = messages.find((m) => {
    return isFulfilledOrTypingMessage(m) && m.generationId === generationId;
  }) as FulfilledMessage | TypingMessage | undefined;
  const isHighlighted = useMemo(() => {
    return (
      isGenerationSelected && selectedCitation?.start === start && selectedCitation?.end === end
    );
  }, [end, selectedCitation, start, isGenerationSelected]);

  const { text, bg, contrastText, hover } = useBrandedColors(agentId);

  const handleClick = () => {
    setSettings({ isConfigDrawerOpen: false });

    if (
      isGenerationSelected &&
      selectedCitation?.start === start &&
      selectedCitation?.end === end
    ) {
      selectCitation(null);
      return;
    }
    selectCitation({
      generationId,
      start,
      end,
      yPosition: ref.current?.offsetTop ?? null,
    });

    open({
      content: (
        <Citation
          className="bg-coral-900"
          generationId={generationId}
          // Used to find the keyword to bold but since we don't have it yet here when the message is
          // still streaming in we can just ignore it for now instead of not showing the popup at all
          message={message?.originalText ?? ''}
        />
      ),
      title: 'OUTPUT',
    });
  };

  let content = children;

  if (isCodeSnippet) {
    const startEndKeyToDoc = citationReferences[generationId];
    const startEndKey = createStartEndKey(start, end);
    if (
      startEndKeyToDoc &&
      startEndKeyToDoc[startEndKey] &&
      startEndKeyToDoc[startEndKey].length > 0
    ) {
      const snippet = startEndKeyToDoc[startEndKey][0];
      const url = snippet.url ?? '';
      const domain = url.split('/')[2] ?? '';
      const domainWithoutWWW = domain.replace('www.', '');
      content = domainWithoutWWW || FALLBACK_CODE_SNIPPET_TEXT;
    } else {
      content = FALLBACK_CODE_SNIPPET_TEXT;
    }
  }

  if (breakpoint == Breakpoint.sm) {
    return (
      <mark
        ref={ref}
        onClick={handleClick}
        className={cn(
          'bg-transparent',
          text,
          {
            [`${bg} ${contrastText}`]: isHighlighted,
            [`${hover(bg)} hover:bg-opacity-35 dark:hover:bg-opacity-35`]: !isHighlighted,
          },
          'cursor-pointer rounded'
        )}
      >
        {content}
      </mark>
    );
  }

  const startEndKey = createStartEndKey(start, end);

  return (
    <Popover className="group inline-block">
      <PopoverButton
        // ref={ref}
        className={cn('cursor-pointer rounded bg-transparent', text, {
          [`${bg} ${contrastText}`]: isHighlighted,
          [`${hover(bg)} hover:bg-opacity-35 dark:hover:bg-opacity-35`]: !isHighlighted,
        })}
      >
        {content}
      </PopoverButton>
      <PopoverPanel
        anchor="bottom"
        className="z-30 h-fit w-[466px] rounded border border-volcanic-400 bg-volcanic-200 p-4"
      >
        <NewCitation generationId={generationId} citationKey={startEndKey} />
      </PopoverPanel>
    </Popover>
  );
};
