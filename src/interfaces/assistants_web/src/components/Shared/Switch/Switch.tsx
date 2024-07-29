'use client';

import { Field, Switch as HUSwitch, Label } from '@headlessui/react';

import { Text } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  name?: string;
  theme?: 'blue' | 'evolved-green' | 'quartz' | 'green' | 'mushroom' | 'coral';
  className?: string;
};

export const Switch: React.FC<Props> = ({
  checked,
  onChange,
  label,
  theme = 'evolved-green',
  name,
  className = '',
}) => {
  return (
    <div className="group flex items-center">
      <Field>
        <div className={cn('flex items-center justify-end gap-x-6', className)}>
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
            <Label>
              <Text className="dark:text-marble-950">{label}</Text>
            </Label>
          )}
        </div>
      </Field>
    </div>
  );
};
