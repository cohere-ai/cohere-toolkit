'use client';

import { Field, Label } from '@headlessui/react';
import { forwardRef } from 'react';

import { STYLE_LEVEL_TO_CLASSES, Text } from '@/components/Shared/Text';
import { cn } from '@/utils';

type Props = Omit<React.HTMLProps<HTMLTextAreaElement>, 'onChange' | 'value'> & {
  value?: string;
  label?: string;
  className?: string;
  onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
};

export const Textarea: React.FC<Props> = forwardRef<HTMLTextAreaElement, Props>(
  ({ value, label, className, onChange, ...rest }, ref) => {
    return (
      <Field className="flex flex-col gap-y-2">
        {label && (
          <Label>
            <Text styleAs="label">{label}</Text>
          </Label>
        )}
        <div className="relative flex w-full">
          <textarea
            ref={ref}
            value={value}
            className={cn(
              'rounded-lg border border-volcanic-500',
              'w-full px-3 py-[18px]',
              'outline-none',
              'bg-white focus:bg-marble-950 dark:bg-volcanic-100 dark:focus:bg-volcanic-150',
              'placeholder:text-volcanic-500 dark:placeholder:text-volcanic-600',
              'disabled:bg-volcanic-800 disabled:text-volcanic-300 dark:disabled:bg-volcanic-300 dark:disabled:text-volcanic-600',
              STYLE_LEVEL_TO_CLASSES.p,
              className
            )}
            onChange={onChange}
            {...rest}
          />
        </div>
      </Field>
    );
  }
);

Textarea.displayName = 'Textarea';
