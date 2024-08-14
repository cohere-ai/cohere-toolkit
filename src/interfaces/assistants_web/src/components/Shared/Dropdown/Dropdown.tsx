'use client';

import {
  Field,
  Label,
  Listbox,
  ListboxButton,
  ListboxOption,
  ListboxOptions,
} from '@headlessui/react';

import { Icon } from '@/components/Shared/Icon';
import { Text } from '@/components/Shared/Text';
import { cn } from '@/utils';

export type DropdownOption = {
  value: string;
  label?: string;
};

type Props = {
  options: DropdownOption[];
  value?: string;
  placeholder?: string;
  label?: string;
  className?: string;
  onChange: (value: string) => void;
};

export const Dropdown: React.FC<Props> = ({
  label,
  options,
  value,
  placeholder = 'Select an option',
  className,
  onChange,
}) => {
  const selectedOption = options.find((option) => option.value === value);

  return (
    <Field className={cn('relative flex w-full flex-col gap-y-2', className)}>
      {label && (
        <Label className="flex items-start gap-x-2">
          <Text styleAs="label">{label}</Text>
        </Label>
      )}
      <Listbox value={value} onChange={onChange}>
        {({ open }) => (
          <>
            <ListboxButton
              className={cn(
                'rounded-lg border border-volcanic-800',
                'w-full px-3 py-[18px]',
                'outline-none',
                'flex items-center justify-between',
                'bg-white focus:bg-marble-950',
                'placeholder:text-volcanic-500',
                'disabled:bg-volcanic-800 disabled:text-volcanic-300',
                'dark:placeholder:text-volcanic-600',
                'dark:bg-volcanic-100 dark:focus:bg-volcanic-150',
                'dark:disabled:bg-volcanic-300 dark:disabled:text-volcanic-600'
              )}
            >
              <Text
                as="span"
                className={cn('truncate', {
                  'text-volcanic-500 dark:text-volcanic-600': !selectedOption,
                })}
              >
                {selectedOption?.label || selectedOption?.value || placeholder}
              </Text>
              <div
                className={cn('h-5 transition-transform duration-300 ease-in-out', {
                  'rotate-180 transform': open,
                })}
              >
                <Icon name="chevron-down" />
              </div>
            </ListboxButton>
            <ListboxOptions
              anchor="bottom start"
              className={cn(
                'z-dropdown',
                'mt-1 rounded-lg border border-volcanic-800 bg-white dark:bg-volcanic-100',
                'cursor-pointer'
              )}
            >
              {options.map((option) => (
                <ListboxOption
                  key={option.value}
                  value={option.value}
                  className="w-full truncate px-3 py-2 hover:bg-marble-950 dark:hover:bg-volcanic-150"
                >
                  <Text
                    as="span"
                    className={cn('truncate', {
                      'font-bold': selectedOption?.value === option.value,
                    })}
                  >
                    {option.label ?? option.value}
                  </Text>
                </ListboxOption>
              ))}
            </ListboxOptions>
          </>
        )}
      </Listbox>
    </Field>
  );
};
