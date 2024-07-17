'use client';

import { Transition } from '@headlessui/react';
import { flatten, sortBy, uniqBy } from 'lodash';
import React, { useRef } from 'react';
import { useMemo, useState } from 'react';

import { Document } from '@/cohere-client';
import { CitationDocument } from '@/components/Citations/CitationDocument';
import { IconButton } from '@/components/IconButton';
import { Text } from '@/components/Shared/Text';
import { ReservedClasses } from '@/constants';
import { CitationStyles, useCalculateCitationTranslateY } from '@/hooks/citations';
import { useCitationsStore } from '@/stores';
import { cn, pluralize } from '@/utils';

type Props = {
  generationId: string;
  message: string;
  isLastStreamed?: boolean;
  styles?: CitationStyles;
  className?: string;
};

export const DEFAULT_NUM_VISIBLE_DOCS = 3;

/**
 * Placeholder component for a citation.
 * This component is in charge of rendering the citations for a given generation.
 * @params {string} generationId - the id of the generation
 * @params {string} message - the message that was sent
 * @params {boolean} isLastStreamed - if the citation is for the last streamed message
 * @params {number} styles - top and bottom styling, depending on the associated message row
 * @params {string} className - additional class names to add to the citation
 */
export const Citation = React.forwardRef<HTMLDivElement, Props>(function CitationInternal(
  { generationId, message, className = '', styles, isLastStreamed = false },
  ref
) {
  const {
    citations: { citationReferences, selectedCitation, hoveredGenerationId },
    hoverCitation,
  } = useCitationsStore();

  const containerRef = useRef<HTMLDivElement>(null);
  const [keyword, setKeyword] = useState('');
  const isSelected = selectedCitation?.generationId === generationId;
  const isSomeSelected = !!selectedCitation?.generationId;
  const isHovered = hoveredGenerationId === generationId;
  const [isAllDocsVisible, setIsAllDocsVisible] = useState(false);

  const startEndKeyToDocs = citationReferences[generationId];
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

  const translateY = useCalculateCitationTranslateY({
    generationId,
    citationRef: containerRef,
  });

  if (!startEndKeyToDocs || documents.length === 0 || (!isSelected && !!selectedCitation)) {
    return null;
  }

  const highlightedDocumentIds = documents
    .slice(0, DEFAULT_NUM_VISIBLE_DOCS)
    .map((doc) => doc.document_id);

  const uniqueDocuments = sortBy(
    uniqBy(flatten(Object.values(startEndKeyToDocs)), 'document_id'),
    'document_id'
  );
  const uniqueDocumentsUrls = uniqBy(uniqueDocuments, 'url');

  const handleMouseEnter = () => {
    hoverCitation(generationId);
  };

  const handleMouseLeave = () => {
    hoverCitation(null);
  };

  const handleToggleAllDocsVisible = () => {
    setIsAllDocsVisible(!isAllDocsVisible);
  };

  return (
    <Transition
      as="div"
      id={generationId ? `citation-${generationId}` : undefined}
      show={true}
      enter="delay-300 duration-300 ease-out transition-[transform,opacity]" // delay to wait for the citation side panel to open
      enterFrom="translate-x-2 opacity-0"
      enterTo="translate-x-0 opacity-100"
      leave="duration-300 ease-in transition-[transform,opacity]"
      leaveFrom="translate-x-0 opacity-100"
      leaveTo="translate-x-2 opacity-0"
      ref={containerRef}
      style={{
        ...styles,
        ...(translateY !== 0 && isSelected
          ? {
              '--selectedTranslateY': `${translateY}px`,
            }
          : {}),
      }}
      className={cn(
        'rounded md:w-citation-md lg:w-citation-lg xl:w-citation-xl',
        'bg-marble-1000 transition-[transform,top] duration-300 ease-in-out',
        'md:absolute md:left-2.5 lg:left-[18px]',
        {
          'md:-translate-x-1 lg:-translate-x-2': isHovered,
          'md:z-selected-citation': isSelected || isAllDocsVisible || isHovered,
          'md:translate-y-[var(--selectedTranslateY)] md:shadow-lg': isSelected,
        }
      )}
    >
      <div
        ref={ref}
        className={cn(
          ReservedClasses.CITATION,
          'rounded md:w-citation-md md:p-3 lg:w-citation-lg xl:w-citation-xl',
          'transition-[colors,opacity] duration-300 ease-in-out',
          {
            'opacity-60': !isSelected && !isHovered && (!isLastStreamed || isSomeSelected),
            'opacity-90': !isSelected && isHovered,
            'bg-mushroom-400/[0.08]': !isSelected,
            'bg-coral-700/[0.08]': isSelected,
            'flex flex-col gap-y-4 lg:gap-y-6': isSelected,
          },
          className
        )}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <Text className="text-coral-300 md:hidden">{keyword}</Text>

        <div className={cn('mb-4 flex items-center justify-between', { hidden: isSelected })}>
          <Text as="span" styleAs="caption" className="text-volcanic-300">
            {uniqueDocumentsUrls.length} {pluralize('reference', uniqueDocumentsUrls.length)}
          </Text>
          {uniqueDocumentsUrls.length > DEFAULT_NUM_VISIBLE_DOCS && (
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

        <div className="flex w-full flex-col gap-y-4">
          {isSelected
            ? uniqueDocuments.map((doc) => {
                const isVisible = highlightedDocumentIds.includes(doc.document_id);

                if (!isVisible) {
                  return null;
                }

                return (
                  <CitationDocument
                    key={doc.document_id}
                    isExpandable={isSelected}
                    document={doc}
                    keyword={keyword}
                  />
                );
              })
            : uniqueDocumentsUrls.map((doc, index) => {
                const isVisible = isAllDocsVisible || index < DEFAULT_NUM_VISIBLE_DOCS;

                if (!isVisible) {
                  return null;
                }

                return (
                  <CitationDocument
                    key={doc.url}
                    isExpandable={isSelected}
                    document={doc}
                    keyword={keyword}
                  />
                );
              })}
        </div>
      </div>
    </Transition>
  );
});
