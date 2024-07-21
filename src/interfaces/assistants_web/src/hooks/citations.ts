import {
  useDebouncedCallback,
  useDebouncedEffect,
  useDebouncedState,
  useResizeObserver,
} from '@react-hookz/web';
import { RefObject, useEffect, useRef, useState } from 'react';

import { useIsSmBreakpoint } from '@/hooks/breakpoint';
import { useCitationsStore } from '@/stores';
import { ChatMessage, isFulfilledOrTypingMessageWithCitations } from '@/types/message';

export type CitationToStyles = { [generationId: string]: CitationStyles };
export type CitationStyles = { top?: string; bottom?: string };

const CITATION_HEIGHT_CHANGES_PAUSE_MS = 100;
const MESSAGE_POSITION_CHANGES_PAUSE_MS = 200;
export const MESSAGE_LIST_CONTAINER_ID = 'message-list';
const MESSAGE_LIST_Y_OFFSET = 48; // includes the y-padding, height of the composer caption, and gap

/* Helper functions to access specific message row or citation elements and their ids */
export const getMessageRowId = (generationId: string) => `message-row-${generationId}`;
export const getCitationId = (generationId: string) => `citation-${generationId}`;
const getMessageRowEl = (generationId: string) =>
  document.getElementById(getMessageRowId(generationId));
const getCitationEl = (generationId: string) =>
  document.getElementById(getCitationId(generationId));
const getMessageListEl = () => document.getElementById(MESSAGE_LIST_CONTAINER_ID);

/**
 * This hook is in charge of the initial positioning of citations according to the associated message row.
 *
 * It follows the following rules:
 *   - is streaming: align it with the bottom of the composer
 *   - otherwise, align it with the top of the message row.
 *
 * Note:
 * The position calculations styles rely on the message row positions and the composer height (e.g. the
 * composer pushes all the messages up when there are toolbar actions or if the user types a long message).
 * When these values change, we need to re-trigger the positioning calculations so we listen these changes
 * and must trigger a state change to re-render the component with the latest values.
 * Sometimes you'll notice the wrong position at first but it will be corrected in the next render.
 */
export const useCalculateCitationStyles = (
  messages: ChatMessage[],
  streamingMessage: ChatMessage | null
) => {
  const messageContainerDivRef = useRef<HTMLDivElement>(null);
  const composerContainerDivRef = useRef<HTMLDivElement>(null);
  const [citationToStyles, setCitationToStyles] = useState<{
    [generationId: string]: { top?: string; bottom?: string };
  }>({});
  const willCitationPanelShow = !useIsSmBreakpoint();

  const {
    citations: { selectedCitation },
  } = useCitationsStore();

  const calculateCitationStyle = (
    m: ChatMessage
  ): { style: CitationStyles; generationId: string } | null => {
    if (!isFulfilledOrTypingMessageWithCitations(m)) {
      return null;
    }

    const generationId = m.generationId;
    const messageRowTop = getMessageRowEl(generationId)?.offsetTop;

    if (messageRowTop !== undefined) {
      return { generationId, style: { top: `${messageRowTop}px` } };
    }
    return null;
  };

  const calculateCitationStyles = useDebouncedCallback(
    () => {
      const allMessages = streamingMessage ? messages.concat(streamingMessage) : messages;
      const newCitationStyles = allMessages.reduce<CitationToStyles>((styles, m) => {
        const citeStyle = calculateCitationStyle(m);
        if (citeStyle) {
          styles[citeStyle.generationId] = citeStyle.style;
        }

        return styles;
      }, {});

      setCitationToStyles(newCitationStyles);
    },
    [messages, selectedCitation, streamingMessage],
    MESSAGE_POSITION_CHANGES_PAUSE_MS
  );

  useDebouncedEffect(
    () => {
      if (
        willCitationPanelShow &&
        streamingMessage &&
        isFulfilledOrTypingMessageWithCitations(streamingMessage)
      ) {
        const newCitationStyle = calculateCitationStyle(streamingMessage);
        if (newCitationStyle) {
          setCitationToStyles({
            ...citationToStyles,
            [newCitationStyle.generationId]: newCitationStyle.style,
          });
        }
      }
    },
    [streamingMessage, willCitationPanelShow],
    MESSAGE_POSITION_CHANGES_PAUSE_MS
  );

  useResizeObserver(
    messageContainerDivRef,
    () => {
      calculateCitationStyles();
    },
    willCitationPanelShow
  );
  useResizeObserver(composerContainerDivRef, calculateCitationStyles, willCitationPanelShow);

  return {
    citationToStyles,
    messageContainerDivRef,
    composerContainerDivRef,
  };
};

/**
 * This hook is in charge of translating the citation when a highlight is selected. It relies on the
 * citation having the correct top/bottom position according to the associated message row.
 *
 * It follows the following rules:
 *   - is last and will overflow the bottom of the message: align it with the bottom of the message.
 *   - otherwise, align it with the top of the highlight.
 *
 * Note:
 * The translateY calculations styles rely on height of the citation when it is selected.
 * When these values change (e.g. when a highlight with a different amount of docs is selected),
 * we need to re-trigger the positioning calculations so we listen for when the citation height
 * changes and must trigger a state change to re-render the component with the latest values.
 * Sometimes you'll notice the wrong position at first but it will be corrected in the next render.
 */
export const useCalculateCitationTranslateY = ({
  generationId,
  citationRef,
}: {
  generationId: string;
  citationRef: RefObject<HTMLDivElement>;
}) => {
  const {
    citations: { selectedCitation },
  } = useCitationsStore();
  const [translateY, setTranslateY] = useDebouncedState(0, CITATION_HEIGHT_CHANGES_PAUSE_MS);
  const willCitationPanelShow = !useIsSmBreakpoint();

  const calculateTranslateY = useDebouncedCallback(
    () => {
      const isSelected = selectedCitation?.generationId === generationId;
      if (!isSelected) {
        if (translateY !== 0) setTranslateY(0);
        return;
      }

      const citationEl = getCitationEl(generationId);
      const citationTop = citationEl?.offsetTop ?? 0;
      const citationHeight = citationEl?.offsetHeight ?? 0;
      const selectedHighlightY = selectedCitation?.yPosition ?? 0;

      const messageListHeight = (getMessageListEl()?.offsetHeight ?? 0) - MESSAGE_LIST_Y_OFFSET;

      if (citationHeight + selectedHighlightY < messageListHeight) {
        setTranslateY(selectedHighlightY - citationTop);
      } else {
        setTranslateY(messageListHeight - citationTop - citationHeight);
      }
    },
    [selectedCitation],
    CITATION_HEIGHT_CHANGES_PAUSE_MS
  );

  useEffect(() => {
    if (willCitationPanelShow) {
      calculateTranslateY();
    }
  }, [selectedCitation, willCitationPanelShow]);

  useResizeObserver(
    citationRef,
    () => {
      calculateTranslateY();
    },
    willCitationPanelShow
  );

  return translateY;
};
