'use client';

import { Popover, PopoverButton, PopoverPanel } from '@headlessui/react';
import React from 'react';

import { AgentPublic, ToolDefinition } from '@/cohere-client';
import { Icon, Switch, Text } from '@/components/UI';
import { useAvailableTools, useBrandedColors } from '@/hooks';
import { useParamsStore } from '@/stores';
import { checkIsBaseAgent, cn, getToolIcon } from '@/utils';

export type Props = {
  agent?: AgentPublic;
  tools?: ToolDefinition[];
};

/**
 * @description Displays a list of available tools and data sources that the user can select from.
 */
export const DataSourceMenu: React.FC<Props> = ({ agent, tools }) => {
  const {
    params: { tools: paramsTools },
  } = useParamsStore();
  const { availableTools, handleToggle } = useAvailableTools({
    agent,
    allTools: tools,
  });

  const { text, contrastText, border, bg } = useBrandedColors(agent?.id);
  const isBaseAgent = checkIsBaseAgent(agent);
  return (
    <Popover className="relative">
      <PopoverButton
        as="button"
        className={({ open }) =>
          cn(
            'flex items-center justify-center rounded border px-1.5 py-1 outline-none transition-colors',
            border,
            { [bg]: open }
          )
        }
      >
        {({ open }) => (
          <Text
            styleAs="label"
            as="span"
            className={cn('font-medium', text, { [contrastText]: open })}
          >
            Tools: {isBaseAgent ? paramsTools?.length ?? 0 : availableTools.length ?? 0}
          </Text>
        )}
      </PopoverButton>
      <PopoverPanel
        className="flex min-w-[200px] origin-top -translate-y-2 flex-col transition duration-200 ease-out data-[closed]:scale-95 data-[closed]:opacity-0"
        anchor="top start"
        transition
      >
        <div
          className={cn(
            'z-tag-suggestions flex flex-col',
            'w-full rounded-md p-2 focus:outline-none',
            'bg-mushroom-950 dark:bg-volcanic-150'
          )}
        >
          <Text styleAs="label" className="mb-2 text-mushroom-300 dark:text-marble-800">
            Available tools
          </Text>
          {availableTools.length === 0 && (
            <Text as="span" styleAs="caption" className="text-mushroom-400 dark:text-volcanic-500">
              No tools available
            </Text>
          )}
          {availableTools.map((tool, i) => (
            <div
              key={tool.name}
              className={cn(
                'flex w-full items-start justify-between gap-x-2 px-1.5 py-3',
                'focus:outline focus:outline-volcanic-300',
                {
                  'border-b border-mushroom-800 dark:border-volcanic-300 md:w-[300px]':
                    i !== availableTools.length - 1,
                }
              )}
            >
              <div className="flex flex-1 justify-between gap-x-2">
                <div className="flex gap-x-2">
                  <div className="relative flex items-center justify-center rounded bg-mushroom-800 p-1 dark:bg-volcanic-200">
                    <Icon
                      name={getToolIcon(tool.name)}
                      kind="outline"
                      size="sm"
                      className="flex items-center fill-mushroom-300 dark:fill-marble-800"
                    />
                    <div
                      className={cn(
                        'absolute -bottom-0.5 -right-0.5  size-2 rounded-full transition-colors duration-300',
                        {
                          'bg-success-300': !!paramsTools?.find((t) => t.name === tool.name),
                          'bg-mushroom-400 dark:bg-volcanic-600': !paramsTools?.find(
                            (t) => t.name === tool.name
                          ),
                        }
                      )}
                    />
                  </div>
                  <div className="flex flex-col text-left">
                    <Text as="span">{tool.display_name}</Text>
                  </div>
                </div>
                {isBaseAgent && (
                  <Switch
                    theme="evolved-blue"
                    checked={!!paramsTools?.find((t) => t.name === tool.name)}
                    onChange={(checked) => handleToggle(tool.name!, checked)}
                    showCheckedState
                  />
                )}
              </div>
            </div>
          ))}
        </div>
      </PopoverPanel>
    </Popover>
  );
};
