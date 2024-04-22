import { Fragment, useContext, useState } from 'react';

import { DEFAULT_CHAT_TOOL, Document } from '@/cohere-client';
import IconButton from '@/components/IconButton';
import { DocumentIcon, Text } from '@/components/Shared';
import { Icon } from '@/components/Shared/Icon';
import { ModalContext } from '@/context/ModalContext';
import { useCitationsStore } from '@/stores';
import { cn, getSafeUrl, getWebDomain } from '@/utils';

type Props = {
  document: Document;
  keyword: string;
  isExpandable?: boolean;
};

const getToolName = (toolId?: string) => {
  // NOTE(jessica): if there is no toolId this means that this citation came from a time when we
  // only supported the web-search connector, thus it is a safe default to fall back on.
  if (!toolId || toolId === DEFAULT_CHAT_TOOL) {
    return 'from the web';
  }
  return `from ${toolId}`;
};

/**
 * Segments the snippet by the text before the found keyword and the in-context keyword itself to
 * allow for styling of the in-context keyword.
 *
 * E.g. if the snippet is "This is a snippet. Snippets are great." and the keyword is "snippet",
 * the result will be:
 * [
 *   {beforeKeyword: "This is a ", snippetKeyword: "snippet"},
 *   {beforeKeyword: ". ", snippetKeyword: "Snippet"},
 *   {beforeKeyword: "s are great."}
 * ]
 */
const getSnippetSegments = (
  snippet: string,
  keyword: string
): {
  beforeKeyword: string;
  snippetKeyword?: string;
}[] => {
  const originalSnippet = snippet;

  const normalizedSnippet = originalSnippet.toLowerCase();
  const normalizedKeyword = keyword.toLowerCase();

  if (normalizedSnippet.includes(normalizedKeyword)) {
    const sections = normalizedSnippet.split(normalizedKeyword);
    let currentIndex = 0;
    const sectionsAndKeyword = sections.reduce<{ beforeKeyword: string; snippetKeyword: string }[]>(
      (acc, section) => {
        const newIndices = [
          ...acc,
          {
            beforeKeyword: originalSnippet.slice(currentIndex, currentIndex + section.length),
            snippetKeyword: originalSnippet.slice(
              currentIndex + section.length,
              currentIndex + section.length + keyword.length
            ),
          },
        ];
        currentIndex += section.length + keyword.length;
        return newIndices;
      },
      []
    );

    return sectionsAndKeyword;
  } else {
    return [{ beforeKeyword: originalSnippet }];
  }
};

/**
 * This component renders the document metadata of a citation, with the option of showing an expandable snippet.
 */
export const CitationDocument: React.FC<Props> = ({ document, isExpandable = false, keyword }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const { open } = useContext(ModalContext);

  if (!document) return null;

  const toggleSnippet = () => {
    setIsExpanded((prev) => !prev);
  };

  const getSnippet = (beforeKeywordCharLimit?: number, lineLimitClass?: string) => {
    if (!document.text) return null;

    const snippetSections = getSnippetSegments(document.text, keyword);

    return (
      <Text className={cn('content', lineLimitClass)}>
        {snippetSections.map(({ beforeKeyword, snippetKeyword }, i) => {
          return (
            <Fragment key={i}>
              {i === 0 &&
              beforeKeywordCharLimit !== undefined &&
              beforeKeyword.length > beforeKeywordCharLimit &&
              snippetKeyword
                ? `...${beforeKeyword.slice(-1 * beforeKeywordCharLimit)}`
                : beforeKeyword}
              {snippetKeyword ? <span className="font-medium">{snippetKeyword}</span> : null}
            </Fragment>
          );
        })}
      </Text>
    );
  };

  const openFullSnippetModal = () => {
    open({
      title: '',
      content: (
        <div className="flex flex-col gap-y-3">
          <CitationInfo
            documentId={document?.document_id}
            url={document.url ?? ''}
            title={document.title ?? ''}
            isExpandable={false}
            isExpanded={true}
            isSelected={true}
            onToggleSnippet={toggleSnippet}
          />
          {getSnippet()}
        </div>
      ),
      kind: 'coral',
    });
  };

  return (
    <div
      className={cn('flex flex-col', {
        'gap-y-3': isExpanded && isExpandable,
      })}
    >
      <CitationInfo
        documentId={document?.document_id}
        url={document.url ?? ''}
        title={document.title ?? ''}
        isExpandable={isExpandable}
        isExpanded={isExpanded}
        isSelected={isExpandable}
        onToggleSnippet={toggleSnippet}
      />

      {isExpanded && isExpandable && (
        <div className="flex flex-col">
          {getSnippet(30, 'line-clamp-3')}
          {/* TODO(jessica): should we enable this/will we support this? */}
          <button
            className="self-end p-0 text-primary-900 transition-colors ease-in-out hover:text-primary-700"
            onClick={openFullSnippetModal}
            data-testid="button-see-full-snippet"
          >
            <Text as="span" styleAs="caption">
              See more
            </Text>
          </button>
        </div>
      )}
    </div>
  );
};

type CitationInfoProps = {
  isExpandable: boolean;
  isExpanded: boolean;
  isSelected: boolean;
  url: string;
  title: string;
  onToggleSnippet: VoidFunction;
  documentId?: string;
};

/**
 * Displays the document metadata of a citation. This includes the
 * icon, title, and url.
 */
const CitationInfo: React.FC<CitationInfoProps> = ({
  documentId,
  isExpandable,
  isSelected,
  isExpanded,
  url,
  title,
  onToggleSnippet,
}) => {
  const {
    citations: { searchResults },
  } = useCitationsStore();

  const hasUrl = url !== '';
  const safeUrl = hasUrl ? getSafeUrl(url) : undefined;

  return (
    <div className="flex items-center justify-between gap-x-3">
      <a
        href={safeUrl}
        target="_blank"
        data-testid="link-citation-document"
        className={cn('group flex w-full cursor-pointer gap-x-2 overflow-hidden', {
          'cursor-default': !safeUrl,
        })}
      >
        <DocumentIcon
          url={safeUrl ?? ''}
          iconKind={isSelected ? 'default' : 'outline'}
          className={cn(
            'bg-primary-500/[0.16] text-primary-800/80 transition-colors duration-200 ease-in-out',
            {
              'bg-secondary-700/20 text-secondary-800': !isSelected,
            }
          )}
        />
        <div className="flex min-w-0 flex-grow flex-col justify-center">
          {hasUrl && (
            <div className={cn('flex font-medium', 'flex-wrap items-baseline gap-x-1')}>
              <Text
                as="span"
                styleAs="label-sm"
                className={cn(
                  'truncate',
                  'transition-colors duration-200 ease-in-out',
                  'text-primary-800',
                  {
                    'text-secondary-700': !isSelected,
                  }
                )}
              >
                {getWebDomain(safeUrl)}
              </Text>
            </div>
          )}

          <div className={cn('flex text-primary-900', { 'group-hover:text-primary-600': safeUrl })}>
            <Text
              as="span"
              styleAs="label"
              className={cn('truncate font-medium transition-colors duration-200 ease-in-out', {
                'text-secondary-800': !isSelected,
              })}
            >
              {title}
            </Text>
            <Icon
              name="arrow-up-right"
              className={cn('ml-1 hidden', 'transition-colors duration-200 ease-in-out', {
                'text-secondary-800': !isSelected,
                'group-hover:block': safeUrl,
              })}
            />
          </div>
        </div>
      </a>
      {isExpandable && (
        <IconButton
          iconName="chevron-down"
          iconClassName={cn(
            'text-primary-800 transition duration-200 delay-75 ease-in-out group-hover:text-primary-900',
            'hidden lg:flex',
            {
              'rotate-180': isExpanded,
            }
          )}
          onClick={onToggleSnippet}
        />
      )}
    </div>
  );
};
