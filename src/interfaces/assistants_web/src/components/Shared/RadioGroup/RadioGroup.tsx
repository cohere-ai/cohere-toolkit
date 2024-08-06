'use client';

import { Field, Label, Radio, RadioGroup as _RadioGroup } from '@headlessui/react';

import { Text } from '@/components/Shared/Text';

type Option<K> = {
  value: K;
  label?: string;
};

type Props<K extends string> = {
  value: K;
  options: Option<K>[];
  onChange?: (value: K) => void;
};

export function RadioGroup<K extends string>({ options, value, onChange }: Props<K>) {
  return (
    <_RadioGroup value={value} onChange={onChange} className="flex flex-col gap-y-5">
      {options.map((option) => (
        <Field key={option.value} className="flex items-center gap-4">
          <Radio
            value={option.value}
            className="group flex size-5 items-center justify-center rounded-full border border-coral-700 dark:border-evolved-green-700"
          >
            <span className="size-3 rounded-full bg-coral-700 opacity-0 transition-opacity duration-300 group-data-[checked]:opacity-100 dark:bg-evolved-green-700" />
          </Radio>
          <Label>
            <Text className="dark:text-marble-950">{option.label ?? option.value}</Text>
          </Label>
        </Field>
      ))}
    </_RadioGroup>
  );
}
