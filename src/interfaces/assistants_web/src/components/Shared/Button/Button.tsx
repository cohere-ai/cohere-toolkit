'use client';

import Link from 'next/link';
import React, { HTMLAttributeAnchorTarget, ReactNode } from 'react';

import { Icon, IconName, Spinner, Text } from '@/components/Shared';
import { COHERE_BRANDED_COLORS } from '@/constants';
import { cn } from '@/utils';

export type ButtonKind = 'cell' | 'primary' | 'outline' | 'secondary';
export type ButtonTheme = COHERE_BRANDED_COLORS | 'default';

const getLabelStyles = (kind: ButtonKind, theme: ButtonTheme, disabled: boolean) => {
  if (disabled) {
    switch (kind) {
      case 'primary':
      case 'cell':
      case 'outline':
        return cn('dark:text-volcanic-200 dark:fill-volcanic-200');
      case 'secondary':
        return cn('dark:text-volcanic-700 dark:fill-volcanic-700');
      default:
        return cn('dark:text-volcanic-100 dark:fill-volcanic-100');
    }
  }

  switch (kind) {
    case 'primary':
    case 'cell':
      return cn('dark:text-marble-950 dark:fill-marble-950', {
        'text-marble-900  fill-marble-900':
          theme === 'green' ||
          theme === 'blue' ||
          theme === 'quartz' ||
          theme === 'evolved-blue' ||
          theme === 'evolved-quartz',
        // dark mode
        'dark:text-volcanic-150 dark:fill-volcanic-150':
          theme === 'evolved-green' ||
          theme === 'evolved-mushroom' ||
          theme === 'coral' ||
          theme === 'default',
      });

    case 'secondary':
      return cn('dark:text-marble-950 dark:fill-marble-950', {
        // light mode
        'text-coral-500 fill-coral-500 group-hover:text-coral-500 group-hover:fill-coral-500 dark:text-evolved-green-700 dark:fill-evolved-green-700 dark:group-hover:text-evolved-green-500 dark:group-hover:fill-evolved-green-500':
          theme == 'default',
        'text-danger-500 fill-danger-500 group-hover:text-danger-350 group-hover:fill-danger-350 dark:text-danger-500 dark:fill-danger-500 dark:group-hover:text-danger-350 dark:group-hover:fill-danger-350':
          theme == 'danger',
        'text-evolved-green-500 fill-evolved-green-500 group-hover:text-evolved-green-700 group-hover:fill-evolved-green-700 dark:text-evolved-green-700 dark:fill-evolved-green-700 dark:group-hover:text-evolved-green-500 dark:group-hover:fill-evolved-green-500':
          theme == 'evolved-green',
      });

    default:
      return cn(
        // light mode
        'text-volcanic-100 volcanic-100',
        'group-hover:text-volcanic-150 group-hover:fill-volcanic-150',

        // dark mode
        'dark:text-marble-950 dark:fill-marble-950 dark:disabled:text-volcanic-700',
        'dark:group-hover:text-marble-1000 dark:group-hover:fill-marble-1000'
      );
  }
};

const getButtonStyles = (kind: ButtonKind, theme: ButtonTheme, disabled: boolean) => {
  if (kind === 'secondary') return '';
  if (disabled) return 'bg-volcanic-600';

  if (kind === 'outline') {
    return cn('border', {
      'border-coral-700 group-hover:border-coral-600 dark:border-evolved-green-700 dark:group-hover:border-evolved-green-500':
        theme === 'default',
      'border-evolved-green-700 group-hover:border-evolved-green-500': theme === 'evolved-green',
      'border-blue-500 group-hover:border-blue-400': theme === 'blue',
      'border-coral-700 group-hover:border-coral-600': theme === 'coral',
      'border-quartz-500 group-hover:border-quartz-400': theme === 'quartz',
      'border-mushroom-500 group-hover:border-mushroom-400': theme === 'mushroom',
      'border-danger-500 group-hover:border-danger-350': theme === 'danger',
      'border-evolved-blue-500 group-hover:border-blue-400': theme === 'evolved-blue',
      'border-evolved-mushroom-500 group-hover:border-evolved-mushroom-600':
        theme === 'evolved-mushroom',
      'border-evolved-quartz-500 group-hover:border-evolved-quartz-700': theme === 'evolved-quartz',
      'border-green-250 group-hover:border-green-200': theme === 'green',
    });
  }

  return cn({
    'fill-coral-700 bg-coral-700 dark:text-volcanic-150 group-hover:bg-coral-600 dark:bg-evolved-green-700 dark:group-hover:bg-evolved-green-500':
      theme === 'default',
    'bg-evolved-green-700 group-hover:bg-evolved-green-500': theme === 'evolved-green',
    'bg-blue-500 group-hover:bg-blue-400': theme === 'blue',
    'fill-coral-700 bg-coral-700 group-hover:bg-coral-600': theme === 'coral',
    'bg-quartz-500 group-hover:bg-quartz-400': theme === 'quartz',
    'bg-mushroom-500 group-hover:bg-mushroom-400': theme === 'mushroom',
    'bg-danger-500 group-hover:bg-danger-350': theme === 'danger',
    'bg-evolved-blue-500 group-hover:bg-blue-400': theme === 'evolved-blue',
    'bg-evolved-mushroom-500 group-hover:bg-evolved-mushroom-600': theme === 'evolved-mushroom',
    'bg-evolved-quartz-500 group-hover:bg-evolved-quartz-700': theme === 'evolved-quartz',
    'bg-green-250 group-hover:bg-green-200': theme === 'green',
  });
};

const getCellStyles = (theme: ButtonTheme, disabled: boolean) => {
  if (disabled) return 'fill-volcanic-600';

  return cn({
    'fill-coral-700 group-hover:fill-coral-600 dark:fill-evolved-green-700 dark:group-hover:fill-evolved-green-500':
      theme === 'default',
    'fill-evolved-green-700 group-hover:fill-evolved-green-500': theme === 'evolved-green',
    'fill-danger-500 group-hover:fill-danger-350': theme === 'danger',
    'fill-blue-500 group-hover:fill-blue-400': theme === 'blue',
    'fill-coral-700 group-hover:fill-coral-600': theme === 'coral',
    'fill-quartz-500 group-hover:fill-quartz-400': theme === 'quartz',
    'fill-mushroom-500 group-hover:fill-mushroom-400': theme === 'mushroom',
    'fill-evolved-blue-500 group-hover:fill-blue-400': theme === 'evolved-blue',
    'fill-evolved-mushroom-500 group-hover:fill-evolved-mushroom-600': theme === 'evolved-mushroom',
    'fill-evolved-quartz-500 group-hover:fill-evolved-quartz-700': theme === 'evolved-quartz',
    'fill-green-250 group-hover:fill-green-200': theme === 'green',
  });
};

export type ButtonProps = {
  id?: string;
  kind?: ButtonKind;
  theme?: ButtonTheme;
  label?: React.ReactNode | string;
  children?: React.ReactNode;
  icon?: IconName;
  disabled?: boolean;
  isLoading?: boolean;
  className?: string;
  iconPosition?: 'start' | 'end';
  iconOptions?: {
    className?: string;
    kind?: 'default' | 'outline';
    customIcon?: React.ReactNode;
  };
  buttonType?: 'submit' | 'reset' | 'button';
  onClick?: React.MouseEventHandler<HTMLButtonElement | HTMLAnchorElement>;
  href?: string;
  rel?: string;
  target?: HTMLAttributeAnchorTarget;
  danger?: boolean;
  stretch?: boolean;
};

export const Button: React.FC<ButtonProps> = ({
  id,
  kind = 'primary',
  theme = 'default',
  label,
  children,
  icon,
  disabled = false,
  isLoading = false,
  className,
  iconOptions,
  buttonType,
  onClick,
  href,
  rel,
  target,
  stretch = false,
  iconPosition = kind === 'cell' ? 'end' : 'start',
}) => {
  const labelStyles = getLabelStyles(kind, theme, disabled);
  const buttonStyles = getButtonStyles(kind, theme, disabled);
  const animate = (!!icon || !!iconOptions?.customIcon) && (!!label || !!children); // we only want to animate if there is an icon and a label

  const animateClasses = cn({
    'duration-400 transform transition-transform ease-in-out group-hover:-translate-x-1.5': animate,
  });

  const iconElement = isLoading ? (
    <Spinner />
  ) : icon || kind === 'cell' ? (
    <Icon
      name={icon ?? 'arrow-right'}
      kind={iconOptions?.kind ?? 'outline'}
      className={cn(
        { [animateClasses]: iconPosition === 'end' && kind !== 'cell' },
        labelStyles,
        iconOptions?.className
      )}
    />
  ) : (
    iconOptions?.customIcon ?? undefined
  );

  const labelElement =
    typeof label === 'string' ? (
      <Text className={cn(labelStyles)}>{label}</Text>
    ) : (
      label ?? children
    );

  const inner =
    kind !== 'cell' ? (
      <div
        className={cn(
          'group flex h-cell-button items-center justify-center gap-x-3 rounded-md',
          buttonStyles,
          {
            'h-fit justify-start': kind === 'secondary',
            'px-5': kind !== 'secondary',
          }
        )}
      >
        {iconPosition === 'start' && iconElement}
        {labelElement && (
          <div
            className={cn({
              [animateClasses]: iconPosition === 'start',
              'px-2': kind === 'outline',
              'w-full': stretch && kind === 'secondary',
            })}
          >
            {labelElement}
          </div>
        )}
        {iconPosition === 'end' && iconElement}
      </div>
    ) : (
      cellInner(theme, iconElement, labelElement, iconPosition, disabled, animate)
    );

  return !disabled && href ? (
    <Link
      id={id}
      href={href}
      onClick={onClick}
      rel={rel}
      target={target}
      className={cn(
        'group select-none',
        {
          'cursor-not-allowed': disabled,
          'w-full': stretch,
        },
        className
      )}
    >
      {inner}
    </Link>
  ) : (
    <button
      id={id}
      type={buttonType}
      disabled={disabled}
      onClick={onClick}
      className={cn(
        'group select-none',
        {
          'cursor-not-allowed': disabled,
          'w-full': stretch,
        },
        className
      )}
    >
      {inner}
    </button>
  );
};

const cellInner = (
  theme: ButtonTheme,
  icon: ReactNode,
  label: ReactNode,
  iconPosition: 'start' | 'end',
  disabled: boolean,
  animate: boolean
) => {
  const isEndIcon = iconPosition === 'end';
  const buttonStyles = getButtonStyles('cell', theme, disabled);
  const baseStyles = 'flex h-cell-button items-center group';

  const elementStyles = cn(
    baseStyles,
    buttonStyles,

    {
      'duration-400 transition-spacing ease-in-out': animate,
      'group-hover:pl-2': isEndIcon && animate,
      'group-hover:pr-2': !isEndIcon && animate,
    }
  );

  const cellTheme = getCellStyles(theme, disabled);
  const cellElement = (
    <>
      <RightCell className={cellTheme} flip={isEndIcon} />
      <LeftCell className={cellTheme} flip={isEndIcon} />
    </>
  );

  const iconCellElement = (
    <>
      {isEndIcon && cellElement}
      <div
        className={cn(elementStyles, {
          'rounded-l-md pl-2': !isEndIcon,
          'rounded-r-md pr-2': isEndIcon,
        })}
      >
        {icon}
      </div>
      {!isEndIcon && cellElement}
    </>
  );

  return (
    <div className={cn(baseStyles, 'ml-0.5')}>
      {!isEndIcon && iconCellElement}
      <div
        className={cn(elementStyles, 'flex-grow px-1', {
          'rounded-r-md pr-4': !isEndIcon,
          'rounded-l-md pl-4': isEndIcon,
        })}
      >
        {label}
      </div>
      {isEndIcon && iconCellElement}
    </div>
  );
};

const RightCell = ({ className, flip }: { className: string; flip?: boolean }) => {
  return (
    <svg
      viewBox="0 0 18 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn('relative h-cell-button', className, {
        '-scale-y-100': flip,
      })}
    >
      <path d="M10.899 0H0V40H2C4.40603 40 6.55968 38.5075 7.4045 36.2547L17.4533 9.45786C19.1694 4.88161 15.7864 0 10.899 0Z" />
    </svg>
  );
};

const LeftCell = ({ className, flip }: { className: string; flip?: boolean }) => {
  return (
    <svg
      viewBox="0 0 18 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn('relative h-cell-button', className, {
        '-scale-y-100': flip,
      })}
    >
      <path d="M7.101 40H18V0H16C13.594 0 11.4403 1.49249 10.5955 3.74532L0.546698 30.5421C-1.1694 35.1184 2.21356 40 7.101 40Z" />
    </svg>
  );
};
