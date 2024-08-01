'use client';

import React from 'react';

import { Icon, IconName, Input, Switch, Text } from '@/components/Shared';
import { getCohereTheme } from '@/utils/cohereColors';

type Props = {
  checked: boolean;
  icon: IconName;
  label: string;
  description: string;
  onToggle: (checked: boolean) => void;
  disabled?: boolean;
  errorMessage?: string | null;
  agentId?: string;
  inputOptions?: {
    label: string;
    placeholder: string;
    value: string;
    onChange: React.ChangeEventHandler<HTMLInputElement>;
    description?: string;
    testId?: string;
    disabled?: boolean;
  };
};

/**
 * @description Styled card for displaying information about a tool/connector with a toggle.
 */
export const ToggleCard: React.FC<Props> = ({
  checked,
  disabled = false,
  icon,
  label,
  agentId,
  description,
  inputOptions,
  errorMessage,
  onToggle,
}) => {
  return (
    <div className="flex flex-col rounded-md border border-mushroom-700 bg-mushroom-950 p-4 dark:border-volcanic-300 dark:bg-volcanic-150">
      <div className="flex items-start gap-x-6">
        <div className="flex flex-grow flex-col gap-y-2">
          <div className="flex items-center gap-x-2">
            <div className="flex size-6 items-center justify-center rounded bg-mushroom-800 dark:bg-volcanic-200">
              <Icon
                name={icon}
                kind="outline"
                size="sm"
                className="fill-mushroom-400 dark:fill-marble-950"
              />
            </div>
            <Text styleAs="label" as="span" className="font-medium">
              {label}
            </Text>
          </div>
          <Text styleAs="p-sm" className="text-mushroom-300 dark:text-marble-800">
            {description}
          </Text>
          {errorMessage && (
            <Text styleAs="p-sm" className="text-danger-350">
              Error: {errorMessage}
            </Text>
          )}
        </div>
        {!disabled && (
          <Switch
            checked={checked}
            onChange={onToggle}
            className="flex-shrink-0 gap-0"
            theme={getCohereTheme(agentId)}
          />
        )}
      </div>
      {inputOptions && (
        <Input
          label="Site (Optional)"
          placeholder="Ground on 1 domain e.g. wikipedia.org"
          value={inputOptions.value}
          onChange={inputOptions.onChange}
          disabled={inputOptions.disabled || disabled}
        />
      )}
    </div>
  );
};
