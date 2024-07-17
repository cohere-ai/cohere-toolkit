'use client';

import { useState } from 'react';

import { Document } from '@/cohere-client';
import { CitationDocumentHeader } from '@/components/Citations/CitationDocumentHeader';
import { CitationDocumentSnippet } from '@/components/Citations/CitationDocumentSnippet';
import { cn } from '@/utils';

type Props = {
  document: Document;
  keyword: string;
  isExpandable?: boolean;
};

/**
 * This component renders the document metadata of a citation, with the option of showing an expandable snippet.
 */
export const CitationDocument: React.FC<Props> = (props) => {
  const { document, isExpandable = false } = props;
  const [isExpanded, setIsExpanded] = useState(true);

  if (!document) return null;

  const toggleSnippet = () => {
    setIsExpanded((prev) => !prev);
  };

  return (
    <div
      className={cn('flex flex-col', {
        'gap-y-3': isExpanded && isExpandable,
      })}
    >
      <CitationDocumentHeader
        toolId={document.tool_name ?? undefined}
        url={document.url ?? ''}
        title={document.title && document.title.length > 0 ? document.title : undefined}
        isExpandable={isExpandable}
        isExpanded={isExpanded}
        isSelected={isExpandable}
        onToggleSnippet={toggleSnippet}
      />

      {isExpanded && isExpandable && (
        <CitationDocumentSnippet
          {...props}
          toolId={document.tool_name ?? undefined}
          onToggle={toggleSnippet}
        />
      )}
    </div>
  );
};
