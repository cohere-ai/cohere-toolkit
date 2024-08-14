import { useState } from 'react';

import { DocumentIcon, Icon, Text } from '@/components/Shared';
import { TOOL_ID_TO_DISPLAY_INFO, TOOL_WEB_SEARCH_ID, TOOL_WIKIPEDIA_ID } from '@/constants';
import { useCitationsStore } from '@/stores';
import { getSafeUrl, getWebDomain } from '@/utils';

const getWebSourceName = (toolId?: string | null) => {
  if (!toolId) {
    return '';
  } else if (toolId === TOOL_WEB_SEARCH_ID) {
    return 'from the web';
  }
  return `from ${toolId}`;
};

type Props = {
  generationId: string;
  citationKey: string;
};

export const Citation: React.FC<Props> = ({ generationId, citationKey }) => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const { citations } = useCitationsStore();
  const citationsMap = citations.citationReferences[generationId];
  const documents = citationsMap[citationKey];
  const document = documents[selectedIndex];
  const safeUrl = getSafeUrl(document.url);

  return (
    <div className="space-y-4">
      <header className="flex items-center justify-between">
        <div className="flex gap-2">
          <div className="grid size-8 place-items-center rounded bg-white dark:bg-volcanic-150">
            {document.url ? (
              <a href={safeUrl} target="_blank" data-connectorid={document.tool_name}>
                <DocumentIcon url={safeUrl} />
              </a>
            ) : document.tool_name ? (
              <Icon name={TOOL_ID_TO_DISPLAY_INFO[document.tool_name].icon} />
            ) : (
              <Icon name="file" />
            )}
          </div>
          <div>
            {document.tool_name === TOOL_WEB_SEARCH_ID ? (
              <>
                <Text styleAs="p-xs" className="uppercase dark:text-marble-800">
                  {getWebDomain(safeUrl) + ' ' + getWebSourceName(document.tool_name)}
                </Text>
                <Text styleAs="p-sm" className="uppercase dark:text-marble-950">
                  {document.title || 'Untitled'}
                </Text>
              </>
            ) : document.tool_name === TOOL_WIKIPEDIA_ID ? (
              <>
                <Text styleAs="p-xs" className="uppercase dark:text-marble-800">
                  {getWebSourceName(document.tool_name)}
                </Text>
                <Text styleAs="p-sm" className="uppercase dark:text-marble-950">
                  {document.title || 'Untitled'}
                </Text>
              </>
            ) : (
              <>
                <Text styleAs="p-xs" className="uppercase dark:text-marble-800">
                  Tool
                </Text>
                <Text styleAs="p-sm" className="uppercase dark:text-marble-950">
                  {document.tool_name}
                </Text>
              </>
            )}
          </div>
        </div>
        {documents.length > 1 && (
          <div className="flex flex-shrink-0 items-center">
            <button
              className="py-[3px] pr-2"
              onClick={() =>
                setSelectedIndex((prev) => (prev - 1 + documents.length) % documents.length)
              }
            >
              <Icon name="chevron-left" />
            </button>
            <Text className="text-p-sm">
              {selectedIndex + 1} of {documents.length}
            </Text>
            <button
              className="py-[3px] pl-2"
              onClick={() => setSelectedIndex((prev) => (prev + 1) % documents.length)}
            >
              <Icon name="chevron-right" />
            </button>
          </div>
        )}
      </header>
      <article className="max-h-64 overflow-y-auto">
        <Text className="font-variable">{document.text}</Text>
      </article>
    </div>
  );
};
