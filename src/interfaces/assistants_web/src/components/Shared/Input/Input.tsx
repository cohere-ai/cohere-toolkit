'use client';

import { Field, Label } from '@headlessui/react';
import { forwardRef, useState } from 'react';

import { Icon } from '@/components/Shared/Icon';
import { STYLE_LEVEL_TO_CLASSES, Text } from '@/components/Shared/Text';
import { cn } from '@/utils';

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
    const [copied, setCopied] = useState(false);
    return (
      <Field className="flex flex-col gap-y-2">
        {label && (
          <Label className="flex items-start gap-x-2">
            <Text styleAs="label" className="dark:text-marble-950">
              {label}
            </Text>
            {errorText && (
              <Text styleAs="label" className="text-red-500">
                *{errorText}
              </Text>
            )}
          </Label>
        )}
        <div className="relative flex w-full items-center gap-x-2">
          <input
            type={actionType === 'reveal' && showPassword ? 'text' : type}
            ref={ref}
            value={value}
            className={cn(
              'rounded-lg border border-volcanic-500',
              'w-full px-3 py-[18px]',
              'outline-none',
              'bg-white focus:bg-marble-950',
              'placeholder:text-volcanic-500',
              'disabled:bg-volcanic-800 disabled:text-volcanic-300',
              'dark:placeholder:text-volcanic-600',
              'dark:bg-volcanic-100 dark:text-marble-950 dark:focus:bg-volcanic-150',
              'dark:disabled:bg-volcanic-300 dark:disabled:text-volcanic-600',
              {
                'pr-8': actionType,
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
              <Icon
                className="dark:text-marble-950"
                name={!showPassword ? 'show' : 'hide'}
                kind="outline"
              />
            </button>
          )}
          {actionType === 'copy' && (
            <button
              type="button"
              onClick={() => {
                if (value) {
                  navigator.clipboard.writeText(value);
                  setCopied(true);
                  setTimeout(() => setCopied(false), 1000);
                }
              }}
              disabled={!value?.trim()}
              className={cn(
                'rounded outline-1 outline-offset-1 outline-volcanic-600',
                'absolute right-2 top-1/2 -translate-y-1/2 transform',
                'items-center justify-center'
              )}
            >
              <Icon
                className={cn({ 'dark:text-marble-950': !!value, 'text-volcanic-600': !value })}
                name="copy"
                kind={copied ? 'default' : 'outline'}
              />
            </button>
          )}
        </div>
      </Field>
    );
  }
);

Input.displayName = 'Input';
