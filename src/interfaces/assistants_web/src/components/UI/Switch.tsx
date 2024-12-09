'use client';

import { Placement } from '@floating-ui/react';
import { Field, Switch as HUSwitch, Label } from '@headlessui/react';

import { Text, Tooltip } from '@/components/UI';
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
  showCheckedState?: boolean;
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
  showCheckedState = false,
  className = '',
}) => {
  const themeColors: Partial<Record<COHERE_BRANDED_COLORS, string>> = {
    blue: 'bg-blue-500 group-hover:bg-blue-400',
    'evolved-green': 'bg-evolved-green-700 group-hover:bg-evolved-green-500',
    quartz: 'bg-quartz-500 group-hover:bg-quartz-400',
    green: 'bg-green-250 group-hover:bg-green-200',
    mushroom: 'bg-mushroom-600 group-hover:bg-mushroom-500',
    coral: 'bg-coral-600 group-hover:bg-coral-500',
    'evolved-blue': 'bg-evolved-blue-500 group-hover:bg-blue-400',
    'evolved-mushroom': 'bg-evolved-mushroom-500 group-hover:bg-evolved-mushroom-600',
    'evolved-quartz': 'bg-evolved-quartz-500 group-hover:bg-evolved-quartz-700',
  };

  const checkedColor = checked
    ? themeColors[theme]
    : 'bg-mushroom-900 hover:bg-mushroom-800 dark:bg-volcanic-500 dark:group-hover:bg-volcanic-400';

  const toggleTextClassNames = cn(
    'pointer-events-none absolute',
    'pt-0.5 font-variable text-[6px] font-medium uppercase',
    'transform transition-all duration-300 ease-in-out'
  );
  return (
    <div className="group flex w-[30px] items-center">
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
              'relative inline-flex h-4 w-[30px] shrink-0 cursor-pointer rounded border-2 border-transparent',
              'transition-colors duration-300 ease-in-out',
              'focus-visible:outline focus-visible:outline-offset-4 focus-visible:outline-volcanic-500',
              checkedColor
            )}
          >
            {showCheckedState && (
              <>
                <Text
                  aria-hidden="true"
                  className={cn(toggleTextClassNames, {
                    'translate-x-[3px] opacity-100': checked,
                    'translate-x-[14px] opacity-0': !checked,
                  })}
                >
                  On
                </Text>
                <Text
                  aria-hidden="true"
                  className={cn(toggleTextClassNames, 'text-mushroom-700 dark:text-volcanic-800', {
                    'translate-x-[14px] opacity-100': !checked,
                    'translate-x-0 opacity-0': checked,
                  })}
                >
                  Off
                </Text>
              </>
            )}
            <span
              aria-hidden="true"
              className={cn(
                'pointer-events-none absolute h-3 w-3 rounded shadow-lg',
                'transform transition-all duration-300 ease-in-out',
                {
                  'translate-x-[14px]': checked,
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
