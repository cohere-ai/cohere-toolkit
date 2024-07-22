'use client';

import React, { useState } from 'react';

import {
  Icon,
  InputLabel,
  STYLE_LEVEL_TO_CLASSES,
  Spinner,
  Text,
  ToggleWithAction,
} from '@/components/Shared';
import { cn } from '@/utils';

const THEME_CLASSES = {
  marble: {
    border: 'border-marble-800',
    background: 'bg-marble-1000',
    label: 'text-volcanic-100',
    icon: '',
  },
  secondary: {
    border: 'border-mushroom-800',
    background: 'bg-mushroom-950',
    label: 'text-volcanic-400',
    icon: 'text-mushroom-700',
  },
};

type StackPosition = 'start' | 'end' | 'center' | 'left' | 'right';
type Kind = 'default' | 'cell';
type Theme = 'marble' | 'secondary';
type Size = 'sm' | 'md';
type ActionType = 'copy' | 'loading' | 'success' | 'revealable' | 'search' | 'submit';

type HTMLInputProps = {
  name?: string;
  placeholder?: string;
  disabled?: boolean;
  readOnly?: boolean;
  required?: boolean;
  min?: string | number;
  max?: string | number;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  prefix?: string;
  type?: 'text' | 'password' | 'email' | 'tel' | 'url' | 'number';
  defaultValue?: string | number;
  step?: number | 'any';
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onFocus?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.ChangeEvent<HTMLInputElement>) => void;
};

export type InputProps = HTMLInputProps & {
  label?: React.ReactNode;
  tooltipLabel?: React.ReactNode;
  description?: string;
  name?: string;
  hasError?: boolean;
  errorText?: string;
  isMonospace?: boolean;
  actionType?: ActionType;
  theme?: Theme;
  kind?: Kind;
  stackPosition?: StackPosition;
  size?: Size;
  className?: string;
  truncate?: boolean;
  onCopy?: () => void | Promise<unknown>;
  onClear?: () => void;
  onSubmit?: (value: string | void) => void | Promise<unknown>;
};

/**
 * This component is in charge of the actual input functionality. Styling is handled by its parent
 * for the most part.
 */
const InnerInput = React.forwardRef<
  HTMLInputElement,
  HTMLInputProps & {
    hasError?: boolean;
    truncate?: boolean;
    className?: string;
    onCopy?: () => void;
    onClear?: () => void;
    onSubmit?: (value: string | void) => void;
    actionType?: ActionType;
    kind: Kind;
    theme: Theme;
  }
>(function InnerInputInternal(
  {
    name,
    min,
    max,
    minLength,
    maxLength,
    pattern,
    required,
    placeholder = '',
    type = 'text',
    disabled = false,
    defaultValue,
    hasError = false,
    truncate = false,
    readOnly = false,
    actionType,
    value,
    className = '',
    kind,
    prefix,
    onCopy,
    onClear,
    onSubmit,
    onChange,
    onFocus,
    onBlur,
    theme,
    ...restOfProps
  },
  ref
) {
  const [showPassword, setShowPassword] = useState(false);

  const renderIcons = () => {
    const icons: {
      isVisible: boolean;
      icon: React.ReactNode;
    }[] = [
      {
        isVisible: actionType === 'copy',
        icon: (
          <ToggleWithAction
            onClick={async () => {
              try {
                onCopy?.();
                await window?.navigator?.clipboard.writeText(value ?? '');
              } catch (e) {
                console.error(e);
              }
            }}
            alternateComponent={<Icon name="check-mark" size="md" />}
            originalComponent={<Icon name="copy" size="md" kind="outline" />}
            duration={1000}
          />
        ),
      },
      {
        isVisible: actionType === 'revealable',
        icon: (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="flex cursor-pointer items-center justify-center"
          >
            <Icon name={!showPassword ? 'show' : 'hide'} kind="outline" />
          </button>
        ),
      },
      {
        isVisible: actionType === 'loading',
        icon: <Spinner />,
      },
      {
        isVisible: actionType === 'success',
        icon: <Icon name="check-mark" className="text-success-200" size="md" />,
      },
      {
        isVisible: actionType === 'search',
        icon: onSubmit ? (
          <button type="button" onClick={() => onSubmit?.(value)}>
            <Icon
              name="search"
              kind="outline"
              size="md"
              className={cn(THEME_CLASSES[theme].icon)}
            />
          </button>
        ) : (
          <Icon name="search" kind="outline" size="md" className={cn(THEME_CLASSES[theme].icon)} />
        ),
      },
      {
        isVisible: actionType === 'submit',
        icon: (
          <button
            type="button"
            onClick={() => {
              onSubmit?.(value);
            }}
            className={cn(
              THEME_CLASSES[theme].label,
              'invisible opacity-0 transition-opacity ease-in-out',
              {
                'visible opacity-100': value ? value.trim().length : false,
              }
            )}
          >
            <Text styleAs="p-lg">Apply</Text>
          </button>
        ),
      },
    ];

    const visibleIcon = icons.find((i) => i.isVisible);
    return visibleIcon ? (
      <div
        className={cn('absolute right-3 flex items-center gap-x-2', {
          'text-danger-350': hasError && type !== 'password',
          'bottom-0 h-full justify-center': kind !== 'cell',
          'bottom-3.5 justify-end': kind === 'cell',
        })}
      >
        {onClear && value && value !== '' && (
          <button type="button" onClick={onClear} className="flex items-center justify-center">
            <Icon name="close" kind="outline" size="md" className={THEME_CLASSES[theme].icon} />
          </button>
        )}

        {visibleIcon.icon}
      </div>
    ) : null;
  };

  const icons = renderIcons();
  return (
    <>
      <span className="relative">
        {prefix && <Text className="absolute left-3 top-0 text-volcanic-100">{prefix}</Text>}
        <input
          id={name}
          ref={ref}
          type={type === 'password' && showPassword ? 'text' : type}
          name={name}
          min={min}
          max={max}
          defaultValue={defaultValue}
          minLength={minLength}
          maxLength={maxLength}
          pattern={pattern}
          required={required}
          placeholder={placeholder}
          disabled={disabled}
          value={value}
          onChange={onChange}
          onFocus={onFocus}
          onBlur={onBlur}
          readOnly={readOnly}
          spellCheck={false}
          autoComplete="off"
          className={cn(
            'placeholder:text-volcanic-600 disabled:text-volcanic-400',
            // remove spinners on number inputs
            '[-moz-appearance:_textfield] [&::-webkit-inner-spin-button]:m-0 [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:m-0 [&::-webkit-outer-spin-button]:appearance-none',
            { '!pr-8': !!icons, 'w-full truncate': truncate, '!pl-8': !!prefix },
            className
          )}
          {...restOfProps}
        />
      </span>
      {renderIcons()}
    </>
  );
});

/**
 * This component handles styling and rendering of the Input component.
 * There are two kinds in this design system:
 * - default - input with borders only around the input itself
 * - cell - input with borders surrounding the input and the label
 *
 * Refer to Storybook for a better illustration.
 */
export const Input = React.forwardRef<HTMLInputElement, InputProps>(function InputInternal(
  {
    kind = 'cell',
    size = 'md',
    label,
    tooltipLabel,
    description,
    disabled,
    truncate,
    actionType,
    hasError = false,
    readOnly = false,
    errorText,
    isMonospace = false,
    theme = 'marble',
    className = '',
    onCopy,
    onSubmit,
    stackPosition,
    ...restInputProps
  },
  ref
) {
  const roundedClasses = cn({
    'rounded-lg': !stackPosition,
    'rounded-t-lg rounded-b-none': stackPosition === 'start',
    'rounded-b-lg rounded-t-none': stackPosition === 'end',
    'rounded-none': stackPosition === 'center',
    'rounded-l-lg rounded-r-none': stackPosition === 'left',
    'rounded-r-lg rounded-l-none': stackPosition === 'right',
  });
  const borderClasses = cn(roundedClasses, {
    [THEME_CLASSES[theme].border]: !hasError,
    'border-danger-350 border-b': hasError,
    border: !stackPosition || stackPosition === 'end',
    'border-x border-t': stackPosition === 'center' || stackPosition === 'start',
    'border-l border-t border-b': stackPosition === 'left',
    'border-r border-t border-b': stackPosition === 'right',
  });

  const backgroundClasses = cn({
    [THEME_CLASSES[theme].background]: !hasError,
    'bg-danger-950': hasError,
  });

  const labelClasses = cn({
    'text-danger-350': hasError,
    [THEME_CLASSES[theme].label]: !hasError,
    'pl-3 pt-2.5': kind === 'cell',
    'mb-2': kind === 'default',
  });

  const inputClasses = cn(backgroundClasses, borderClasses, 'w-full px-3', {
    'focus-visible:outline-none': stackPosition,
    'focus-visible:outline focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-100':
      !stackPosition,
    [STYLE_LEVEL_TO_CLASSES.code]: isMonospace,
    [STYLE_LEVEL_TO_CLASSES.p]: !isMonospace,
    'text-danger-350': hasError,
    'py-3': kind === 'default' && size === 'sm',
    'py-4': kind === 'default' && size === 'md',
    'pt-7 pb-2.5': kind === 'cell',
    'border-marble-800 bg-marble-950': disabled,
  });

  return (
    <div className={cn('relative', className)}>
      {label && (
        <InputLabel
          name={restInputProps.name}
          tooltipLabel={tooltipLabel}
          containerClassName={cn({ 'absolute w-fit z-10': kind === 'cell' })}
          className={labelClasses}
          label={
            typeof label === 'string' ? (
              <Text as="span" styleAs="label">
                {label}
              </Text>
            ) : (
              label
            )
          }
        />
      )}
      <div
        className={cn('relative w-full', {
          // Classes in charge of showing a focus ring, separated out to appear on top of the elements for stacked elements
          'focus-within:before:rounded-t-lg': stackPosition === 'start',
          'focus-within:before:rounded-b-lg': stackPosition === 'end',
          'focus-within:before:rounded-none': stackPosition === 'center',
          'focus-within:before:pointer-events-none focus-within:before:absolute focus-within:before:left-0 focus-within:before:top-0 focus-within:before:z-10':
            stackPosition,
          'focus-within:before:h-full focus-within:before:w-full focus-within:before:outline focus-within:before:outline-1 focus-within:before:outline-offset-4':
            stackPosition,
        })}
      >
        <InnerInput
          {...restInputProps}
          ref={ref}
          disabled={disabled}
          truncate={truncate}
          actionType={actionType}
          onCopy={onCopy}
          onSubmit={onSubmit}
          readOnly={readOnly}
          className={inputClasses}
          kind={kind}
          theme={theme}
        />
      </div>

      {(errorText && hasError) || description ? (
        <Text
          as="div"
          styleAs="caption"
          className={cn('py-2', {
            'text-volcanic-400': !hasError && description,
            'text-danger-350': errorText && hasError,
          })}
        >
          {hasError && errorText}
          {!hasError && description}
        </Text>
      ) : null}
    </div>
  );
});
