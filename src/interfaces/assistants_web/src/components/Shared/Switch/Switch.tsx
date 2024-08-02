'use client';

import { Placement } from '@floating-ui/react';
import { Field, Switch as HUSwitch, Label } from '@headlessui/react';

import { Text, Tooltip } from '@/components/Shared';
import { COHERE_BRANDED_COLORS } from '@/constants';
import { cn } from '@/utils';

type Props = {
  checked: boolean;
  onChange: (checked: boolean) => void;
  tooltip?: {
    label: string;
    size?: 'sm' | 'md';
    placement?: Placement;
  };
  reverse?: boolean;
  label?: string;
  name?: string;
  theme?: COHERE_BRANDED_COLORS;
  className?: string;
};

export const Switch: React.FC<Props> = ({
  checked,
  onChange,
  label,
  reverse = false,
  tooltip,
  theme = 'evolved-green',
  name,
  className = '',
}) => {
  return (
    <div className="group flex w-10 items-center">
      <Field>
        <div
          className={cn(
            'flex items-center justify-end gap-x-6',
            { 'flex-row-reverse': reverse },
            className
          )}
        >
          <HUSwitch
            name={name}
            checked={checked}
            onChange={onChange}
            className={cn(
              'relative inline-flex h-5 w-10 shrink-0 cursor-pointer rounded border-2 border-transparent',
              'transition-colors duration-300 ease-in-out',
              'focus-visible:outline focus-visible:outline-offset-4 focus-visible:outline-volcanic-500',
              {
                'bg-mushroom-900 hover:bg-mushroom-800 dark:bg-volcanic-500 dark:group-hover:bg-volcanic-400':
                  !checked,
                'bg-blue-500 group-hover:bg-blue-400': checked && theme === 'blue',
                'bg-evolved-green-700 group-hover:bg-evolved-green-500':
                  checked && theme === 'evolved-green',
                'bg-quartz-500 group-hover:bg-quartz-400': checked && theme === 'quartz',
                'bg-green-250 group-hover:bg-green-200': checked && theme === 'green',
                'bg-mushroom-600 group-hover:bg-mushroom-500': checked && theme === 'mushroom',
                'bg-coral-600 group-hover:bg-coral-500': checked && theme === 'coral',
                'bg-evolved-blue-500 group-hover:bg-blue-400': checked && theme === 'evolved-blue',
                'bg-evolved-mushroom-500 group-hover:bg-evolved-mushroom-600':
                  checked && theme === 'evolved-mushroom',
                'bg-evolved-quartz-500 group-hover:bg-evolved-quartz-700':
                  checked && theme === 'evolved-quartz',
              }
            )}
          >
            <span
              aria-hidden="true"
              className={cn(
                'pointer-events-none inline-block h-4 w-5 rounded shadow-lg',
                'transform transition-all duration-300 ease-in-out',
                {
                  'translate-x-4': checked,
                  'translate-x-0': !checked,
                  'bg-mushroom-700 dark:bg-volcanic-800': !checked,
                  'bg-marble-950': checked,
                  'bg-green-250': checked && theme === 'evolved-green',
                }
              )}
            />
          </HUSwitch>
          {label && (
            <span className="flex items-center gap-x-2">
              <Label>
                <Text styleAs="label" className="dark:text-marble-950">
                  {label}
                </Text>
              </Label>
              {tooltip && (
                <Tooltip
                  label={tooltip.label}
                  size={tooltip.size ?? 'sm'}
                  placement={tooltip.placement}
                  hover
                  hoverDelay={{ open: 250 }}
                />
              )}
            </span>
          )}
        </div>
      </Field>
    </div>
  );
};
