'use client';

import { Field, Label } from '@headlessui/react';
import { forwardRef, useState } from 'react';

import { Icon } from '@/components/Shared/Icon';
import { STYLE_LEVEL_TO_CLASSES, Text } from '@/components/Shared/Text';
import { cn } from '@/utils';

import { CopyToClipboardIconButton } from '../CopyToClipboardButton';

type Props = Omit<React.HTMLProps<HTMLInputElement>, 'onChange' | 'value'> & {
  value?: string;
  label?: string;
  type?: 'text' | 'email' | 'password';
  errorText?: string;
  className?: string;
  actionType?: 'copy' | 'reveal';
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

export const Input: React.FC<Props> = forwardRef<HTMLInputElement, Props>(
  ({ value, label, type = 'text', errorText, className, actionType, onChange, ...rest }, ref) => {
    const [showPassword, setShowPassword] = useState(false);
    return (
      <Field className="flex flex-col gap-y-2">
        {label && (
          <Label className="flex items-start gap-x-2">
            <Text styleAs="label">{label}</Text>
          </Label>
        )}
        <div className="relative flex w-full items-center gap-x-2">
          <input
            type={actionType === 'reveal' && showPassword ? 'text' : type}
            ref={ref}
            value={value}
            className={cn(
              'w-full px-3 py-[18px]',
              'outline-none',
              'rounded-lg border border-volcanic-800 dark:border-volcanic-500',
              'bg-white focus:bg-volcanic-950 dark:bg-volcanic-100 dark:focus:bg-volcanic-150',
              'placeholder:text-volcanic-500 dark:placeholder:text-volcanic-600',
              'disabled:bg-volcanic-800 disabled:text-volcanic-300 dark:disabled:bg-volcanic-300 dark:disabled:text-volcanic-600',
              {
                'pr-8': actionType,
                'border-danger-500 text-danger-500 dark:border-danger-500': errorText,
              },
              STYLE_LEVEL_TO_CLASSES.p,
              className
            )}
            onChange={onChange}
            {...rest}
          />
          {actionType === 'reveal' && (
            <button
              type="button"
              onClick={() => setShowPassword((prev) => !prev)}
              className={cn(
                'rounded outline-1 outline-offset-1 outline-volcanic-600',
                'absolute right-2 top-1/2 -translate-y-1/2 transform',
                'items-center justify-center'
              )}
            >
              <Icon name={!showPassword ? 'show' : 'hide'} kind="outline" />
            </button>
          )}
          {actionType === 'copy' && (
            <CopyToClipboardIconButton
              value={value ?? ''}
              disabled={!value?.trim()}
              buttonClassName={cn(
                'rounded outline-1 outline-offset-1 outline-volcanic-600',
                'absolute right-2 top-1/2 -translate-y-1/2 transform',
                'items-center justify-center'
              )}
              iconClassName={cn({ 'dark:fill-marble-950': !!value, 'fill-volcanic-600': !value })}
            />
          )}
        </div>
        {errorText && (
          <Text styleAs="label-sm" className="text-danger-500 dark:text-danger-500">
            {errorText}
          </Text>
        )}
      </Field>
    );
  }
);

Input.displayName = 'Input';
