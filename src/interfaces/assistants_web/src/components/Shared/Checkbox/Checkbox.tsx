'use client';

import React from 'react';

import { Icon, InputLabel } from '@/components/Shared';
import { cn } from '@/utils';

type CheckboxProps = {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  indeterminate?: boolean;
  label?: string;
  name?: string;
  tooltipLabel?: React.ReactNode;
  theme?: 'coral' | 'evolved-green';
  className?: string;
  labelClassName?: string;
  labelSubContainerClassName?: string;
  labelContainerClassName?: string;
};

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(function CheckboxInternal(
  {
    checked,
    indeterminate = false,
    onChange,
    tooltipLabel,
    name,
    label,
    disabled,
    theme = 'coral',
    className,
    labelClassName,
    labelContainerClassName,
    labelSubContainerClassName,
  },
  ref
) {
  const groupName = name ?? label;

  const handleKeyPress = (event: React.KeyboardEvent<HTMLLabelElement>) => {
    // on space key press, trigger onChange
    if (event.code === 'Space' && !disabled) {
      onChange(!checked);
    }
  };

  return (
    <label
      tabIndex={0}
      onKeyDown={handleKeyPress}
      className={cn(
        'group relative rounded focus-visible:outline focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-100',
        'flex items-center',
        'min-h-4 min-w-4',
        className
      )}
    >
      <input
        ref={ref}
        id={groupName}
        name={groupName}
        type="checkbox"
        disabled={disabled}
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="hidden"
      />
      <span
        className={cn(
          'absolute flex cursor-pointer items-center justify-center rounded-sm',
          'transition-colors duration-200 ease-in-out',
          'size-5',
          {
            'bg-coral-600 group-hover:bg-coral-500': checked && theme === 'coral',
            'bg-evolved-green-700 group-hover:bg-evolved-green-500':
              checked && theme === 'evolved-green',
            'cursor-not-allowed border border-volcanic-800 bg-volcanic-800 group-hover:bg-volcanic-700 dark:bg-volcanic-300 dark:group-hover:bg-volcanic-400':
              disabled,
            'border border-marble-800 bg-white group-hover:bg-marble-980 dark:bg-volcanic-150 dark:group-hover:bg-volcanic-300':
              !checked && !disabled,
          }
        )}
        role="checkbox"
        aria-checked={checked}
      >
        {checked ? (
          <Icon
            name="checkmark"
            className={cn({
              'fill-marble-1000': theme === 'coral',
              'fill-green-200': theme === 'evolved-green',
              'fill-volcanic-500': disabled,
            })}
          />
        ) : indeterminate ? (
          <span className="h-[1.5px] w-2 bg-marble-800" />
        ) : null}
      </span>
      {label && (
        <InputLabel
          className={cn('cursor-pointer select-none pl-10 pt-0.5', {
            'cursor-not-allowed': disabled,
          })}
          label={label}
          tooltipLabel={tooltipLabel}
          name={groupName}
          labelClassName={labelClassName}
          labelContainerClassName={labelSubContainerClassName}
          containerClassName={labelContainerClassName}
          styleAs="p"
        />
      )}
    </label>
  );
});
