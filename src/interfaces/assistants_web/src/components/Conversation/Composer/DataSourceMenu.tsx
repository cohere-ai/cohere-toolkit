'use client';

import { useClickOutside } from '@react-hookz/web';
import { uniq, uniqBy } from 'lodash';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { ManagedTool } from '@/cohere-client';
import { ListboxOption, ListboxOptions } from '@/components/Conversation/Composer/ListboxOptions';
import { IconButton } from '@/components/IconButton';
import { IconName, Text } from '@/components/Shared';
import { CHAT_COMPOSER_TEXTAREA_ID, TOOL_FALLBACK_ICON } from '@/constants';
import { useParamsStore } from '@/stores';
import { cn } from '@/utils';

export const OVERVIEW_START_MAX_ITEMS = 3;

export enum TagType {
  TOOL = 'tool',
  FILE = 'file',
}

enum MenuMode {
  OVERVIEW = 'overview',
  TOOLS = 'tools',
  FILES = 'files',
}

type TagValue = { tag: Tag; type: TagType };
export type Tag = {
  id: string;
  name: string;
  getValue: () => ManagedTool | string;
  disabled?: boolean;
  icon?: IconName;
  description?: string;
  metadata?: React.ReactNode;
};

export type Props = {
  show: boolean;
  tagQuery: string;
  tags: { fileIds: Tag[]; tools: Tag[] };
  totalTags: { fileIds: number };
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
  tagQuery,
  onChange,
  tags,
  totalTags,
  onHide,
  onToggle,
  onSeeAll,
}) => {
  const [focusedTag, setFocusedTag] = useState<TagValue | undefined>();
  const {
    params: { fileIds, tools },
    setParams,
  } = useParamsStore();
  const buttonAndMenuRef = useRef<HTMLDivElement>(null);
  const [menuMode, setMenuMode] = useState<MenuMode>(MenuMode.OVERVIEW);

  const overviewTools = useMemo(() => {
    if (tagQuery.length <= 1) return tags.tools.slice(0, OVERVIEW_START_MAX_ITEMS);
    return tags.tools;
  }, [tagQuery, tags.tools]);
  const overviewFiles = useMemo(() => {
    if (tagQuery.length <= 1) return tags.fileIds.slice(0, OVERVIEW_START_MAX_ITEMS);
    return tags.fileIds;
  }, [tagQuery, tags.fileIds]);

  const scrollToTag = (tag?: Tag) => {
    if (!tag) return;

    const el = document.getElementById(`listbox-option-${tag.id}`);
    if (el) {
      el.scrollIntoView({ block: 'nearest' });
    }
  };

  const focusFirstTag = () => {
    if (!focusedTag || !focusedTag.tag || tags.tools.every((t) => t.name !== focusedTag.tag.name)) {
      if (menuMode === MenuMode.OVERVIEW || menuMode === MenuMode.TOOLS) {
        if (!tags.tools[0]) return;

        setFocusedTag({ tag: tags.tools[0], type: TagType.TOOL });
        scrollToTag(tags.tools[0]);
      } else {
        if (!tags.fileIds[0]) return;

        setFocusedTag({ tag: tags.fileIds[0], type: TagType.FILE });
        scrollToTag(tags.fileIds[0]);
      }
    } else {
      scrollToTag(focusedTag.tag);
    }
  };

  const hideMenu = useCallback(() => {
    if (menuMode !== MenuMode.OVERVIEW) {
      setMenuMode(MenuMode.OVERVIEW);
    }
    onHide();
  }, [menuMode, onHide]);

  const handleChange = useCallback(
    (value: { tag: Tag; type: TagType }) => {
      switch (value.type) {
        case TagType.TOOL: {
          setParams({
            tools: uniqBy([...(tools ?? []), value.tag.getValue() as ManagedTool], 'name'),
          });
          break;
        }
        case TagType.FILE: {
          setParams({ fileIds: uniq([...(fileIds ?? []), value.tag.getValue() as string]) });
          break;
        }
      }

      setFocusedTag(undefined);
      onChange(value);
      hideMenu();
    },
    [fileIds, onChange, setParams, tools, hideMenu]
  );

  const handleArrowKey = useCallback(
    (e: KeyboardEvent | React.KeyboardEvent) => {
      setFocusedTag((prev) => {
        const toolsToSearch = menuMode === MenuMode.OVERVIEW ? overviewTools : tags.tools;
        const filesToSearch = menuMode === MenuMode.OVERVIEW ? overviewFiles : tags.fileIds;
        const tagsToSearch = toolsToSearch.concat(filesToSearch);
        const lastToolIndex = toolsToSearch.length - 1;
        const curIndex = tagsToSearch.findIndex((t) => t.id === prev?.tag.id);

        if (curIndex !== -1) {
          const nextIndex = curIndex + (e.key === 'ArrowUp' ? -1 : 1);
          if (nextIndex === tagsToSearch.length || nextIndex === -1) {
            return prev;
          }
          return {
            tag: tagsToSearch[nextIndex],
            type: nextIndex <= lastToolIndex ? TagType.TOOL : TagType.FILE,
          };
        }
        return prev;
      });
      e.preventDefault();
      e.stopPropagation();
      return;
    },
    [menuMode, overviewTools, overviewFiles, tags.tools, tags.fileIds]
  );

  const handleEnter = useCallback(
    (e: KeyboardEvent | React.KeyboardEvent) => {
      if (focusedTag) {
        handleChange(focusedTag);
        e.preventDefault();
        e.stopPropagation();
      }
    },
    [focusedTag, handleChange]
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent | React.KeyboardEvent) => {
      if (!show) return;
      if (e.key === 'Escape' || e.code === 'Space') {
        hideMenu();
        return;
      }

      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        handleArrowKey(e);
        return;
      }

      if (e.key === 'Enter') {
        handleEnter(e);
        return;
      }
    },
    [handleArrowKey, handleEnter, hideMenu, show]
  );

  useEffect(() => {
    const composer = document.getElementById(CHAT_COMPOSER_TEXTAREA_ID);
    if (!composer) return;
    composer.addEventListener('keydown', handleKeyDown);

    return () => composer.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  useEffect(() => {
    focusFirstTag();
  }, [focusedTag, tags.tools, tagQuery]);

  useEffect(() => {
    if (show) {
      focusFirstTag();
    } else if (menuMode !== MenuMode.OVERVIEW) {
      setMenuMode(MenuMode.OVERVIEW);
    }
  }, [show]);

  useClickOutside(buttonAndMenuRef, hideMenu);

  return (
    <div ref={buttonAndMenuRef}>
      <IconButton
        iconName="at"
        tooltip={{ label: 'Use data source', size: 'sm' }}
        onClick={onToggle}
        size="sm"
      />
      {show && (
        <div
          role="listbox"
          aria-multiselectable="true"
          className={cn(
            'absolute bottom-[85%] left-[1%] z-tag-suggestions max-h-[200px] md:w-[468px]',
            'w-full overflow-y-scroll rounded bg-marble-1000 p-2 shadow-menu focus:outline-none'
          )}
        >
          {menuMode === MenuMode.TOOLS && (
            <ToolOptions
              tags={tags.tools}
              selectedTagIds={(tools ?? []).map((c) => c.name ?? '')}
              focusedTag={focusedTag}
              onOptionSelect={handleChange}
            />
          )}

          {menuMode === MenuMode.FILES && (
            <FileOptions
              tags={tags.fileIds}
              selectedTagIds={fileIds ?? []}
              focusedTag={focusedTag}
              onOptionSelect={handleChange}
            />
          )}

          {menuMode === MenuMode.OVERVIEW && (
            <>
              <ToolOptions
                isOverview
                tags={overviewTools}
                focusedTag={focusedTag}
                onOptionSelect={handleChange}
                selectedTagIds={(tools ?? []).map((c) => c.name ?? '')}
                onSeeAll={() => {
                  setMenuMode(MenuMode.TOOLS);
                  setFocusedTag({ tag: tags.tools[0], type: TagType.TOOL });
                  focusFirstTag();
                  onSeeAll();
                }}
              />

              <FileOptions
                isOverview
                totalTags={totalTags.fileIds}
                tags={overviewFiles}
                focusedTag={focusedTag}
                onOptionSelect={handleChange}
                selectedTagIds={fileIds ?? []}
                onSeeAll={() => {
                  setMenuMode(MenuMode.FILES);
                  setFocusedTag({ tag: tags.fileIds[0], type: TagType.FILE });
                  focusFirstTag();
                  onSeeAll();
                }}
              />
            </>
          )}
        </div>
      )}
    </div>
  );
};

const ToolOptions: React.FC<{
  tags: Tag[];
  isOverview?: boolean;
  selectedTagIds: string[];
  focusedTag?: { tag: Tag; type: TagType };
  onOptionSelect: (tag: { tag: Tag; type: TagType }) => void;
  onSeeAll?: VoidFunction;
}> = ({ tags, selectedTagIds, isOverview, focusedTag, onSeeAll, onOptionSelect }) => {
  return (
    <ListboxOptions title={isOverview ? 'Tools' : undefined} onSeeAll={onSeeAll}>
      {tags.map((tag) => {
        let selected = selectedTagIds.some((t) => t === tag.id);

        return (
          <ListboxOption
            key={tag.id}
            value={{ type: TagType.TOOL, tag }}
            icon={tag.icon ?? TOOL_FALLBACK_ICON}
            disabled={tag.disabled}
            name={tag.name}
            description={tag.description}
            selected={selected}
            focus={tag.id === (focusedTag?.tag?.id ?? '')}
            onSelect={() => onOptionSelect({ type: TagType.TOOL, tag })}
            metadata={
              selected ? (
                <Text as="span" className="text-volcanic-500">
                  Selected
                </Text>
              ) : undefined
            }
          />
        );
      })}
    </ListboxOptions>
  );
};

const FileOptions: React.FC<{
  tags: Tag[];
  isOverview?: boolean;
  totalTags?: number;
  focusedTag?: { tag: Tag; type: TagType };
  selectedTagIds: string[];
  onOptionSelect: (tag: { tag: Tag; type: TagType }) => void;
  onSeeAll?: VoidFunction;
}> = ({ totalTags, tags, selectedTagIds, isOverview, onSeeAll, focusedTag, onOptionSelect }) => {
  const hasFiles = totalTags !== 0;

  return (
    <ListboxOptions
      title={isOverview ? 'Files' : undefined}
      onSeeAll={hasFiles ? onSeeAll : undefined}
    >
      {hasFiles ? (
        tags.map((tag) => (
          <ListboxOption
            key={tag.id}
            value={{ type: TagType.FILE, tag }}
            focus={tag.id === (focusedTag?.tag?.id ?? '')}
            selected={selectedTagIds.some((t) => t === tag.id)}
            onSelect={() => onOptionSelect({ type: TagType.FILE, tag })}
            icon="clip"
            name={tag.name}
            metadata={
              <Text as="span" className="flex-shrink-0 whitespace-nowrap text-volcanic-500">
                {selectedTagIds.some((t) => t === tag.id) ? 'Selected' : tag.metadata}
              </Text>
            }
          />
        ))
      ) : (
        <Text as="span" className="p-1.5 text-volcanic-400">
          You don&apos;t have any files, upload one to use with the assistant.
        </Text>
      )}
    </ListboxOptions>
  );
};
