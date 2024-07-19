'use client';

import React from 'react';

import { Icon, InputLabel } from '@/components/Shared';
import { cn } from '@/utils';

type CheckboxProps = {
  checked: boolean;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  disabled?: boolean;
  indeterminate?: boolean;
  label?: string;
  name?: string;
  tooltipLabel?: React.ReactNode;
  size?: 'sm' | 'md';
  theme?: 'primary' | 'secondary';
  className?: string;
  labelClassName?: string;
  labelSubContainerClassName?: string;
  labelContainerClassName?: string;
  dataTestId?: string;
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
    size = 'md',
    theme = 'primary',
    className,
    labelClassName,
    labelContainerClassName,
    labelSubContainerClassName,
    dataTestId,
  },
  ref
) {
  const handleKeyPress = (event: React.KeyboardEvent<HTMLLabelElement>) => {
    // on space key press, trigger onChange
    if (event.code === 'Space' && !disabled) {
      onChange({ target: { checked: !checked } } as React.ChangeEvent<HTMLInputElement>);
    }
  };

  return (
    <label
      tabIndex={0}
      onKeyDown={handleKeyPress}
      className={cn(
        'group relative rounded focus-visible:outline focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-100',
        'flex items-center',
        { 'min-h-[16px] min-w-[16px]': !label && size === 'md' },
        { 'min-h-[14px] min-w-[14px]': !label && size === 'sm' },
        className
      )}
    >
      <input
        ref={ref}
        id={name}
        name={name}
        type="checkbox"
        disabled={disabled}
        checked={checked}
        onChange={onChange}
        className="hidden"
        data-testid={dataTestId}
      />
      <span
        className={cn(
          'absolute flex cursor-pointer items-center justify-center rounded-sm',
          'transition-colors duration-200 ease-in-out',
          {
            'h-4 w-4': size === 'md',
            'h-3.5 w-3.5': size === 'sm',
            'bg-coral-700 group-hover:bg-coral-800': checked && theme === 'primary',
            'bg-mushroom-500 group-hover:bg-mushroom-600': checked && theme === 'secondary',
            'cursor-not-allowed bg-marble-950': disabled,
            'border border-marble-800 bg-white group-hover:bg-marble-950': !checked && !disabled,
          }
        )}
        role="checkbox"
        aria-checked={checked}
      >
        {checked ? (
          <Icon name="check-mark" className="text-white" size={size} />
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
          name={name}
          labelClassName={labelClassName}
          labelContainerClassName={labelSubContainerClassName}
          containerClassName={labelContainerClassName}
          styleAs="p"
        />
      )}
    </label>
  );
});
