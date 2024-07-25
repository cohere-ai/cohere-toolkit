'use client';

import { useClickOutside } from '@react-hookz/web';
import React, { useCallback, useRef } from 'react';

import { ManagedTool } from '@/cohere-client';
import { ListboxOption, ListboxOptions } from '@/components/Conversation/Composer/ListboxOptions';
import { IconName, Text } from '@/components/Shared';
import { TOOL_FALLBACK_ICON } from '@/constants';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useParamsStore } from '@/stores';
import { cn } from '@/utils';
import { getCohereColor } from '@/utils/getCohereColor';

type TagValue = { tag: Tag };
export type Tag = {
  id: string;
  name: string;
  getValue: () => ManagedTool | string;
  icon?: IconName;
};

export type Props = {
  show: boolean;
  tagQuery: string;
  tags: { fileIds: Tag[]; tools: Tag[] };
  onChange: (tag: TagValue) => void;
  onHide: VoidFunction;
  onToggle: VoidFunction;
  onSeeAll: VoidFunction;
};

/**
 * @description Displays a list of available tools and data sources that the user can select from.
 * These can be filtered by the tagQuery, which starts with '@' and ends when a space character is found
 */
export const DataSourceMenu: React.FC<Props> = ({
  show,
  onChange,
  tags,
  onHide,
  onToggle,
  onSeeAll,
}) => {
  const {
    params: { tools },
    setParams,
  } = useParamsStore();
  const buttonAndMenuRef = useRef<HTMLDivElement>(null);

  const handleChange = useCallback(
    (value: { tag: Tag }) => {
      const newTools = (tools ?? [])?.includes(value.tag.getValue() as ManagedTool)
        ? tools?.filter((t) => t !== value.tag.getValue())
        : (tools ?? []).concat(value.tag.getValue() as ManagedTool);

      setParams({
        tools: newTools,
      });

      onChange(value);
    },
    [onChange, setParams, tools]
  );

  useClickOutside(buttonAndMenuRef, onHide);
  const { agentId } = useChatRoutes();

  return (
    <div ref={buttonAndMenuRef}>
      <button
        onClick={onToggle}
        className={cn(
          'flex items-center justify-center rounded border px-1.5 py-1 transition-colors',
          getCohereColor(agentId, {
            text: true,
            contrastText: show,
            border: true,
            background: show,
          })
        )}
      >
        <Text styleAs="label" as="span" className="font-medium">
          Tools: {tools?.length ?? 0}
        </Text>
      </button>
      {show && (
        <div
          role="listbox"
          aria-multiselectable="true"
          className={cn(
            'absolute bottom-12 left-12 z-tag-suggestions max-h-[200px] md:w-[300px]',
            'w-full overflow-y-scroll rounded p-2 focus:outline-none',
            'bg-marble-1000 dark:bg-volcanic-150'
          )}
        >
          <ToolOptions
            tags={tags.tools}
            onOptionSelect={handleChange}
            selectedTagIds={(tools ?? []).map((c) => c.name ?? '')}
            onSeeAll={onSeeAll}
          />
        </div>
      )}
    </div>
  );
};

const ToolOptions: React.FC<{
  tags: Tag[];
  selectedTagIds: string[];
  onOptionSelect: (tag: { tag: Tag }) => void;
  onSeeAll?: VoidFunction;
}> = ({ tags, selectedTagIds, onSeeAll, onOptionSelect }) => {
  return (
    <ListboxOptions title="Available tools" onSeeAll={onSeeAll}>
      {tags.map((tag) => {
        let selected = selectedTagIds.some((t) => t === tag.id);
        return (
          <ListboxOption
            key={tag.id}
            icon={tag.icon ?? TOOL_FALLBACK_ICON}
            selected={selected}
            name={tag.name}
            onSelect={() => onOptionSelect({ tag })}
          />
        );
      })}
    </ListboxOptions>
  );
};
