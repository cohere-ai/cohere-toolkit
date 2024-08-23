import Link from 'next/link';
import { useState } from 'react';

import { Markdown } from '@/components/Markdown';
import { DocumentIcon, Icon, Text } from '@/components/UI';
import { TOOL_ID_TO_DISPLAY_INFO, TOOL_WEB_SEARCH_ID, TOOL_WIKIPEDIA_ID } from '@/constants';
import { useBrandedColors } from '@/hooks';
import { useCitationsStore } from '@/stores';
import { cn, getSafeUrl, getWebDomain } from '@/utils';

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
  agentId?: string;
};

export const Citation: React.FC<Props> = ({ generationId, citationKey, agentId }) => {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const { citations } = useCitationsStore();
  const citationsMap = citations.citationReferences[generationId];
  const documents = citationsMap[citationKey];
  const document = documents[selectedIndex];
  const safeUrl = getSafeUrl(document.url);
  const { text, lightText, fill, lightFill, dark, light } = useBrandedColors(agentId);

  const brandedClassName = cn(dark(lightText), light(text), dark(lightFill), light(fill));

  return (
    <div className="space-y-4">
      <header className="flex items-center justify-between">
        <div className="flex gap-2">
          <div className="grid size-8 place-items-center rounded bg-mushroom-800 dark:bg-volcanic-150">
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
                <Text styleAs="p-xs" className={cn('uppercase', brandedClassName)}>
                  {getWebDomain(safeUrl) + ' ' + getWebSourceName(document.tool_name)}
                </Text>
                {document.url ? (
                  <Link href={document.url} target="_blank">
                    <Text
                      styleAs="p-sm"
                      className={cn('uppercase underline hover:no-underline', brandedClassName)}
                    >
                      {document.title || 'Untitled'}
                      <Icon
                        name="arrow-up-right"
                        className={cn('ml-1 inline-block h-4 w-4 [&_svg]:mt-1', brandedClassName)}
                      />
                    </Text>
                  </Link>
                ) : (
                  <Text styleAs="p-sm" className={cn('uppercase', brandedClassName)}>
                    {document.title || 'Untitled'}
                  </Text>
                )}
              </>
            ) : document.tool_name === TOOL_WIKIPEDIA_ID ? (
              <>
                <Text styleAs="p-xs" className={cn('uppercase', brandedClassName)}>
                  {getWebSourceName(document.tool_name)}
                </Text>
                {document.url ? (
                  <Link href={document.url} target="_blank">
                    <Text
                      styleAs="p-sm"
                      className={cn('uppercase underline hover:no-underline', brandedClassName)}
                    >
                      {document.title || 'Untitled'}
                      <Icon
                        name="arrow-up-right"
                        className={cn('ml-1 inline-block h-4 w-4 [&_svg]:mt-1', brandedClassName)}
                      />
                    </Text>
                  </Link>
                ) : (
                  <Text styleAs="p-sm" className={cn('uppercase', brandedClassName)}>
                    {document.title || 'Untitled'}
                  </Text>
                )}
              </>
            ) : (
              <>
                <Text styleAs="p-xs" className="uppercase">
                  Tool
                </Text>
                <Text styleAs="p-sm" className="uppercase">
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
        <Markdown className="font-variable" text={document.text} />
      </article>
    </div>
  );
};
