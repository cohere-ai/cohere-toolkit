'use client';

import { Popover, PopoverButton, PopoverPanel } from '@headlessui/react';
import { PropsWithChildren } from 'react';

import { Citation } from '@/components/Citations/Citation';
import { useContextStore } from '@/context';
import { useBrandedColors } from '@/hooks/brandedColors';
import { Breakpoint, useBreakpoint } from '@/hooks/breakpoint';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useCitationsStore } from '@/stores';
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
    citations: { citationReferences },
  } = useCitationsStore();
  const startEndKey = createStartEndKey(start, end);

  const { text, lightText, bg, contrastText, hover, dark, light } = useBrandedColors(agentId);

  const handleClick = () => {
    open({
      content: <Citation generationId={generationId} citationKey={startEndKey} />,
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
        onClick={handleClick}
        className={cn(
          'cursor-pointer rounded bg-transparent',
          light(text),
          dark(lightText),
          hover(bg),
          hover(contrastText)
        )}
      >
        {content}
      </mark>
    );
  }

  return (
    <Popover className="group inline-block">
      <PopoverButton
        className={cn(
          'cursor-pointer rounded bg-transparent',
          light(text),
          dark(lightText),
          hover(bg),
          hover(contrastText)
        )}
      >
        {content}
      </PopoverButton>
      <PopoverPanel
        anchor="bottom"
        className="z-tooltip h-fit w-[466px] rounded border bg-white p-4 dark:border-volcanic-400 dark:bg-volcanic-200"
      >
        <Citation generationId={generationId} citationKey={startEndKey} />
      </PopoverPanel>
    </Popover>
  );
};
