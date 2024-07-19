'use client';

import { flatten, sortBy, uniqBy } from 'lodash';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { Document } from '@/cohere-client';
import { DEFAULT_NUM_VISIBLE_DOCS } from '@/components/Citations/Citation';
import { CitationDocument } from '@/components/Citations/CitationDocument';
import { IconButton } from '@/components/IconButton';
import MessageRow from '@/components/MessageRow';
import { Button, Text } from '@/components/Shared';
import { ReservedClasses } from '@/constants';
import { useCitationsStore } from '@/stores';
import { ChatMessage, isFulfilledMessage } from '@/types/message';
import { cn, pluralize } from '@/utils';

type Props = {
  title: string;
  messages: ChatMessage[];
};

/**
 * @description Read only view of a shared conversation
 */
export const ReadOnlyConversation: React.FC<Props> = ({ title, messages }) => {
  const {
    citations: { citationReferences, selectedCitation },
    selectCitation,
  } = useCitationsStore();
  const hasCitations = Object.keys(citationReferences).length > 0;

  const handleClickOutside = useCallback(
    (event: MouseEvent) => {
      if (!selectedCitation) return;

      const target = event.target as Node;
      const invalidElements = Array.from(
        document.querySelectorAll(`.${ReservedClasses.MESSAGE}, .${ReservedClasses.CITATION}`)
      );

      const isClickInsideInvalidElements = invalidElements.some((node) => node.contains(target));
      if (!isClickInsideInvalidElements) {
        selectCitation(null);
      }
    },
    [selectedCitation, selectCitation]
  );

  useEffect(() => {
    window?.addEventListener('click', handleClickOutside);
    return () => {
      window?.removeEventListener('click', handleClickOutside);
    };
  }, [handleClickOutside]);

  return (
    <>
      <div
        className={cn('flex w-full flex-col gap-2 pb-28 pt-12 md:px-5', {
          'max-w-share-content': !hasCitations,
          'max-w-share-content-with-citations': hasCitations,
        })}
      >
        <Text styleAs="h3" className="text-center text-volcanic-300">
          {title}
        </Text>

        <div className={cn('my-6 w-full border-b border-marble-800')} />

        <div className="flex flex-col gap-y-4 py-6 md:gap-y-6">
          {messages.map((m, i) => (
            <div key={i} className="flex items-start justify-between gap-x-3">
              <MessageRow
                message={m}
                isLast={i === messages.length - 1}
                isStreamingToolEvents={false}
                className={cn('max-w-full md:max-w-[80%]', { 'md:max-w-full': !hasCitations })}
              />
              {isFulfilledMessage(m) && m.citations && m.citations.length > 0 && (
                <ReadOnlyConversationCitation message={m.text} generationId={m.generationId} />
              )}
            </div>
          ))}
        </div>
      </div>
      <div className="fixed bottom-0 left-0 z-read-only-conversation-footer flex w-full items-center justify-center bg-white py-4 shadow-top">
        <Button label="Start a new conversation" href="/" splitIcon="arrow-right" kind="primary" />
      </div>
    </>
  );
};

type ReadOnlyConversationCitationProps = {
  generationId: string;
  message: string;
};

/**
 * @description Simplified version of Citation.tsx for read only view of a shared conversation:
 * - Aligns with the top of the message row
 * - Does not jump next to the selected highlighted text in the message
 */
const ReadOnlyConversationCitation: React.FC<ReadOnlyConversationCitationProps> = ({
  generationId,
  message,
}) => {
  const {
    citations: { citationReferences, selectedCitation, hoveredGenerationId },
  } = useCitationsStore();
  const [isAllDocsVisible, setIsAllDocsVisible] = useState(false);
  const [keyword, setKeyword] = useState('');
  const isHovered = hoveredGenerationId === generationId;
  const isSelected = selectedCitation?.generationId === generationId;
  const startEndKeyToDocs = citationReferences[generationId];
  const uniqueDocuments = sortBy(
    uniqBy(flatten(Object.values(startEndKeyToDocs)), 'document_id'),
    'document_id'
  );
  const documents: Document[] = useMemo(() => {
    if (!startEndKeyToDocs) {
      return [];
    }

    if (selectedCitation && generationId === selectedCitation.generationId) {
      setKeyword(message.slice(Number(selectedCitation.start), Number(selectedCitation.end)));
      return startEndKeyToDocs[`${selectedCitation.start}-${selectedCitation.end}`];
    } else {
      const firstCitedTextKey = Object.keys(startEndKeyToDocs)[0];
      const [start, end] = firstCitedTextKey.split('-');
      setKeyword(message.slice(Number(start), Number(end)));
      return startEndKeyToDocs[firstCitedTextKey];
    }
  }, [startEndKeyToDocs, selectedCitation, generationId, message]);

  const highlightedDocumentIds = documents
    .slice(0, DEFAULT_NUM_VISIBLE_DOCS)
    .map((doc) => doc.document_id);

  const handleToggleAllDocsVisible = () => {
    setIsAllDocsVisible(!isAllDocsVisible);
  };

  return (
    <div
      className={cn(
        ReservedClasses.CITATION,
        'relative hidden md:flex md:w-citation-md lg:w-citation-lg xl:w-citation-xl'
      )}
    >
      <div
        className={cn(
          'absolute right-0 top-0',
          'flex w-full flex-col bg-marble-1000 p-3',
          'w-full rounded',
          'transition-[colors,opacity] duration-300 ease-in-out',
          'opacity-60',
          {
            'bg-mushroom-400/[0.08]': !isSelected,
            'bg-coral-700/[0.08]': isSelected,
            'md:-translate-x-1 lg:-translate-x-2': isHovered,
            'md:z-selected-citation': isSelected || isAllDocsVisible || isHovered,
            'opacity-100': isSelected || isHovered,
            'md:translate-y-[var(--selectedTranslateY)] md:shadow-lg': isSelected,
          }
        )}
      >
        <div className={cn('mb-4 flex items-center justify-between', { hidden: isSelected })}>
          <Text as="span" styleAs="caption" className="text-volcanic-300">
            {uniqueDocuments.length} {pluralize('reference', uniqueDocuments.length)}
          </Text>
          {uniqueDocuments.length > DEFAULT_NUM_VISIBLE_DOCS && (
            <IconButton
              className={cn(
                'h-4 w-4 text-volcanic-300 transition delay-75 duration-200 ease-in-out',
                {
                  'rotate-180': isAllDocsVisible,
                }
              )}
              onClick={handleToggleAllDocsVisible}
              iconName="chevron-down"
            />
          )}
        </div>
        <div className="flex flex-col gap-y-4">
          {uniqueDocuments.map((doc, index) => {
            const isVisible =
              (!isSelected && isAllDocsVisible) ||
              (!isSelected && index < DEFAULT_NUM_VISIBLE_DOCS) ||
              (isSelected && highlightedDocumentIds.includes(doc.document_id));

            if (!isVisible) {
              return null;
            }

            return (
              <div key={doc.document_id} className={cn()}>
                <CitationDocument isExpandable={isSelected} document={doc} keyword={keyword} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
