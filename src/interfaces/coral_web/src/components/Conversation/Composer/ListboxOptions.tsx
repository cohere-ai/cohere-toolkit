'use client';

import React, { PropsWithChildren } from 'react';

import { IconButton } from '@/components/IconButton';
import { Icon, IconName, Text } from '@/components/Shared';
import { cn } from '@/utils';

import { Tag, TagType } from './DataSourceMenu';

/**
 * @description Listbox options wrapper with a title and see all button.
 */
export const ListboxOptions: React.FC<
  PropsWithChildren<{
    title?: string;
    onSeeAll?: VoidFunction;
  }>
> = ({ title, onSeeAll, children }) => {
  return (
    <>
      {title && (
        <Text
          as="div"
          styleAs="label"
          className={cn(
            'group flex w-full items-center justify-between gap-x-1 pl-1.5 pt-1.5 font-medium'
          )}
        >
          {title}

          <IconButton
            iconName="chevron-right"
            tooltip={{ label: 'See all', size: 'sm' }}
            size="sm"
            className={cn({
              invisible: !onSeeAll,
            })}
            onClick={onSeeAll}
          />
        </Text>
      )}

      {children}
    </>
  );
};

type ListboxOptionProps = {
  focus: boolean;
  selected: boolean;
  icon: IconName;
  value: { tag: Tag; type: TagType };
  name: string;
  onSelect: VoidFunction;
  disabled?: boolean;
  description?: string;
  metadata?: React.ReactNode;
};
export const ListboxOption: React.FC<ListboxOptionProps> = ({
  icon,
  value,
  name,
  disabled,
  description,
  metadata,
  focus,
  selected,
  onSelect,
}) => {
  return (
    <div id={`listbox-option-${value.tag.id}`} role="option" tabIndex={-1} aria-selected={selected}>
      <button
        disabled={disabled}
        tabIndex={-1}
        className={cn(
          'flex w-full items-start justify-between gap-x-2 rounded p-1.5 hover:bg-mushroom-950 active:bg-mushroom-950',
          'focus:outline focus:outline-volcanic-300',
          { 'bg-mushroom-950': focus, 'cursor-not-allowed': disabled }
        )}
        onClick={onSelect}
      >
        <div className="flex flex-1 gap-x-1">
          <Icon
            name={icon}
            size="sm"
            kind="outline"
            className="flex h-[21px] items-center text-volcanic-600"
          />
          <div className="flex flex-col text-left">
            <Text
              as="span"
              className={cn({
                'text-volcanic-400': disabled,
              })}
            >
              {name}
            </Text>
            {description && (
              <Text as="span" className="text-volcanic-400">
                {description}
              </Text>
            )}
          </div>
        </div>

        {metadata}
      </button>
    </div>
  );
};
