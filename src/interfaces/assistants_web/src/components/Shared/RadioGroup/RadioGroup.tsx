'use client';

import { Label, Radio, RadioGroup as _RadioGroup } from '@headlessui/react';

import { Text } from '@/components/Shared/Text';
import { cn } from '@/utils';

type Option<K> = {
  value: K;
  label?: string;
};

type Props<K extends string> = {
  value: K;
  options: Option<K>[];
  disabled?: boolean;
  onChange?: (value: K) => void;
};

export function RadioGroup<K extends string>({ options, value, onChange, disabled }: Props<K>) {
  return (
    <_RadioGroup
      value={value}
      onChange={onChange}
      className="flex flex-col gap-y-5"
      disabled={disabled}
    >
      {options.map((option) => (
        <Radio
          key={option.value}
          value={option.value}
          className="flex cursor-pointer items-center gap-4"
        >
          {({ disabled, checked }) => (
            <>
              <div
                className={cn(
                  'group flex size-5 cursor-pointer items-center justify-center rounded-full border border-coral-700 transition-colors duration-300',
                  'dark:border-evolved-green-700',
                  { 'border-volcanic-600': disabled }
                )}
              >
                <span
                  className={cn(
                    'size-3 rounded-full bg-coral-700 opacity-0 transition-opacity duration-300 dark:bg-evolved-green-700',
                    {
                      'bg-volcanic-600': disabled,
                      'opacity-100': checked,
                    }
                  )}
                />
              </div>
              <Label as={Text} className={cn({ 'text-volcanic-600': disabled })}>
                {option.label ?? option.value}
              </Label>
            </>
          )}
        </Radio>
      ))}
    </_RadioGroup>
  );
}
