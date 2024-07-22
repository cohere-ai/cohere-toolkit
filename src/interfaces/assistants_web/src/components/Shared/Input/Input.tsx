'use client';

import { Field, Label, Input as _Input } from '@headlessui/react';
import { forwardRef, useState } from 'react';

import { Icon } from '@/components/Shared/Icon';
import { STYLE_LEVEL_TO_CLASSES, Text } from '@/components/Shared/Text';
import { cn } from '@/utils';

type Props = {
  value?: string;
  label?: string;
  name?: string;
  type?: 'text' | 'email' | 'password';
  placeholder?: string;
  required?: boolean;
  readOnly?: boolean;
  errorText?: string;
  className?: string;
  disabled?: boolean;
  actionType?: 'copy' | 'reveal';
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

export const Input: React.FC<Props> = forwardRef<HTMLInputElement, Props>(
  (
    {
      label,
      name,
      value,
      type = 'text',
      placeholder,
      required,
      readOnly,
      disabled,
      className,
      errorText,
      actionType,
      onChange,
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);
    const [copied, setCopied] = useState(false);
    return (
      <Field className="flex flex-col gap-y-2">
        {label && (
          <Label className="flex items-start gap-x-2">
            <Text styleAs="label" className="text-marble-950">
              {label}
            </Text>
            {errorText && (
              <Text styleAs="label" className="text-red-500">
                *{errorText}
              </Text>
            )}
          </Label>
        )}
        <div className="flex items-center gap-x-2">
          <_Input
            type={actionType === 'reveal' && showPassword ? 'text' : type}
            name={name}
            ref={ref}
            value={value}
            placeholder={placeholder}
            required={required}
            readOnly={readOnly}
            disabled={disabled}
            className={cn(
              'rounded-lg border border-volcanic-500',
              'w-full px-3 py-[18px]',
              'outline-none',
              'bg-volcanic-100 focus:bg-volcanic-150',
              'text-marble-950 placeholder:text-volcanic-600',
              STYLE_LEVEL_TO_CLASSES.p,
              className
            )}
            onChange={onChange}
          />
          {actionType === 'reveal' && (
            <button
              type="button"
              onClick={() => setShowPassword((prev) => !prev)}
              className="cursor-pointer items-center justify-center"
            >
              <Icon
                className="text-marble-950"
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
              className="cursor-pointer items-center justify-center"
            >
              <Icon className="text-marble-950" name="copy" kind={copied ? 'default' : 'outline'} />
            </button>
          )}
        </div>
      </Field>
    );
  }
);

Input.displayName = 'Input';
