'use client';

import { Popover, PopoverButton, PopoverPanel } from '@headlessui/react';
import React, { useCallback } from 'react';

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

  const { agentId } = useChatRoutes();

  return (
    <Popover className="relative">
      <PopoverButton
        as="button"
        onClick={onToggle}
        className={({ open }) =>
          cn(
            'flex items-center justify-center rounded border px-1.5 py-1 outline-none transition-colors',
            getCohereColor(agentId, {
              text: true,
              contrastText: open,
              border: true,
              background: open,
            })
          )
        }
      >
        <Text styleAs="label" as="span" className="font-medium">
          Tools: {tools?.length ?? 0}
        </Text>
      </PopoverButton>
      <PopoverPanel
        className="flex origin-top -translate-y-2 flex-col transition duration-200 ease-out data-[closed]:scale-95 data-[closed]:opacity-0"
        anchor="top start"
        transition
      >
        <div
          role="listbox"
          aria-multiselectable="true"
          className={cn(
            'z-tag-suggestions] md:w-[300px]',
            'w-full rounded-md p-2 focus:outline-none',
            'bg-mushroom-950 dark:bg-volcanic-200'
          )}
        >
          <ToolOptions
            tags={tags.tools}
            onOptionSelect={handleChange}
            selectedTagIds={(tools ?? []).map((c) => c.name ?? '')}
            onSeeAll={onSeeAll}
          />
        </div>
      </PopoverPanel>
    </Popover>
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
