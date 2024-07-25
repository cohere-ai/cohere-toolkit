'use client';

import React, { PropsWithChildren } from 'react';

import { Icon, IconName, Switch, Text } from '@/components/Shared';
import { cn } from '@/utils';

/**
 * @description Listbox options wrapper with a title and see all button.
 */
export const ListboxOptions: React.FC<
  PropsWithChildren<{
    title?: string;
    onSeeAll?: VoidFunction;
  }>
> = ({ title, children }) => {
  return (
    <div className="flex flex-col gap-y-1">
      {title && (
        <Text as="div" styleAs="label" className="p-2 dark:text-marble-800">
          {title}
        </Text>
      )}
      {children}
    </div>
  );
};

type ListboxOptionProps = {
  icon: IconName;
  name: string;
  selected: boolean;
  onSelect: VoidFunction;
};
export const ListboxOption: React.FC<ListboxOptionProps> = ({ icon, name, selected, onSelect }) => {
  return (
    <div
      className={cn(
        'flex w-full items-start justify-between gap-x-2 rounded p-1.5',
        'focus:outline focus:outline-volcanic-300'
      )}
    >
      <div className="flex flex-1 justify-between gap-x-2">
        <div className="flex gap-x-2">
          <div className="relative flex items-center justify-center rounded bg-mushroom-800 p-1 dark:bg-volcanic-200">
            <Icon
              name={icon}
              kind="outline"
              size="sm"
              className="flex items-center text-volcanic-400 dark:text-marble-950"
            />
            <div className="absolute -bottom-0.5 -right-0.5  size-2 rounded-full bg-success-300" />
          </div>
          <div className="flex flex-col text-left">
            <Text as="span" className="dark:text-marble-950">
              {name}
            </Text>
          </div>
        </div>
        <Switch theme="evolved-green" checked={selected} onChange={onSelect} />
      </div>
    </div>
  );
};
