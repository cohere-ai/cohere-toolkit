'use client';

import { PropsWithChildren, useMemo, useRef } from 'react';

import { Citation } from '@/components/Citations/Citation';
import { useContextStore } from '@/context';
import { Breakpoint, useBreakpoint } from '@/hooks/breakpoint';
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

    if (breakpoint === Breakpoint.sm) {
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
        kind: 'coral-mobile-only',
      });
    }
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

  return (
    <mark
      ref={ref}
      onClick={handleClick}
      className={cn(
        'bg-mushroom-600/[0.15] text-mushroom-150',
        {
          'bg-coral-900 text-coral-300': isHighlighted,
          'hover:bg-mushroom-600/[0.24]': !isHighlighted,
        },
        'cursor-pointer rounded'
      )}
    >
      {content}
    </mark>
  );
};
