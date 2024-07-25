import Link from 'next/link';
import React, { HTMLAttributeAnchorTarget, ReactNode } from 'react';

import { cn } from '@/utils';

import { Icon, IconName } from '../Icon';
import { Spinner } from '../Spinner';
import { Text } from '../Text';

export type ButtonKind = 'cell' | 'primary' | 'outline' | 'secondary';
export type ButtonTheme = 'acrylic-blue' | 'evolved-green' | 'coral' | 'quartz' | 'mushroom-marble';

const getLabelStyles = (kind: ButtonKind, theme: ButtonTheme, disabled: boolean) => {
  if (disabled) return cn('dark:text-volcanic-700 dark:fill-volcanic-700');

  switch (kind) {
    case 'primary':
    case 'cell':
      if (theme === 'evolved-green') {
        return cn('dark:text-volcanic-150 dark:fill-volcanic-150');
      }
    case 'secondary':
      if (theme === 'evolved-green') {
        return cn(
          'dark:text-evolved-green-700 dark:fill-evolved-green-700',
          'dark:group-hover:text-evolved-green-500 dark:group-hover:fill-evolved-green-500'
        );
      }
    default:
      return cn(
        'dark:text-marble-950 dark:fill-marble-950',
        'dark:group-hover:text-marble-1000 dark:group-hover:fill-marble-1000'
      );
  }
};

const getButtonStyles = (kind: ButtonKind, theme: ButtonTheme, disabled: boolean) => {
  if (kind === 'secondary') return '';
  if (disabled) return 'dark:bg-volcanic-600';

  if (kind === 'outline') {
    return cn('border', {
      'dark:border-evolved-green-700 dark:group-hover:border-evolved-green-500':
        theme === 'evolved-green',
      'dark:border-blue-500 dark:group-hover:border-blue-400': theme === 'acrylic-blue',
      'dark:border-coral-700 dark:group-hover:border-coral-600': theme === 'coral',
      'dark:border-quartz-500 dark:group-hover:border-quartz-400': theme === 'quartz',
      'dark:border-mushroom-500 dark:group-hover:border-mushroom-400': theme === 'mushroom-marble',
    });
  } else {
    return cn({
      'dark:bg-evolved-green-700 dark:group-hover:bg-evolved-green-500': theme === 'evolved-green',
      'dark:bg-blue-500 dark:group-hover:bg-blue-400': theme === 'acrylic-blue',
      'dark:fill-coral-700 dark:bg-coral-700 dark:group-hover:bg-coral-600': theme === 'coral',
      'dark:bg-quartz-500 dark:group-hover:bg-quartz-400': theme === 'quartz',
      'dark:bg-mushroom-500 dark:group-hover:bg-mushroom-400': theme === 'mushroom-marble',
    });
  }
};

const getCellStyles = (theme: ButtonTheme, disabled: boolean) => {
  if (disabled) return 'dark:fill-volcanic-600';

  return cn({
    'dark:fill-evolved-green-700 dark:group-hover:fill-evolved-green-500':
      theme === 'evolved-green',
    'dark:fill-blue-500 dark:group-hover:fill-blue-400': theme === 'acrylic-blue',
    'dark:fill-coral-700 dark:group-hover:fill-coral-600': theme === 'coral',
    'dark:fill-quartz-500 dark:group-hover:fill-quartz-400': theme === 'quartz',
    'dark:fill-mushroom-500 dark:group-hover:fill-mushroom-400': theme === 'mushroom-marble',
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
  buttonType?: 'submit' | 'reset' | 'button' | undefined;
  onClick?: React.MouseEventHandler<HTMLButtonElement | HTMLAnchorElement>;
  href?: string;
  hrefOptions?: {
    shallow?: boolean;
    rel?: string;
    target?: HTMLAttributeAnchorTarget;
  };
  animate?: boolean;
  danger?: boolean;
};

export const Button: React.FC<ButtonProps> = ({
  id,
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
  hrefOptions,
  animate = true,
  danger = false,
  kind = danger ? 'secondary' : 'primary',
  theme = kind === 'secondary' ? 'mushroom-marble' : 'acrylic-blue',
  iconPosition = kind === 'cell' ? 'end' : 'start',
}) => {
  const labelStyles = danger
    ? 'text-danger-500 fill-danger-500'
    : getLabelStyles(kind, theme, disabled);
  const buttonStyles = getButtonStyles(kind, theme, disabled);
  const shouldAnimate = animate && !disabled;

  const iconElement = isLoading ? (
    <Spinner />
  ) : icon || kind === 'cell' ? (
    <Icon
      name={icon ?? 'arrow-right'}
      kind={iconOptions?.kind ?? 'outline'}
      className={cn(labelStyles, iconOptions?.className)}
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
          'group flex items-center justify-center rounded-md',
          buttonStyles,
          className,
          { 'justify-start': kind === 'secondary', 'h-cell-button': kind !== 'secondary' }
        )}
      >
        {iconPosition === 'start' && iconElement}
        <div
          className={cn({
            'pl-3': iconPosition === 'start',
            'pr-3': iconPosition === 'end',
            'duration-400 transition-spacing ease-in-out': shouldAnimate,
            'group-hover:pl-1': shouldAnimate && iconPosition === 'start',
            'group-hover:pr-1': shouldAnimate && iconPosition === 'end',
          })}
        >
          {labelElement}
        </div>
        {iconPosition === 'end' && iconElement}
      </div>
    ) : (
      cellInner(theme, iconElement, labelElement, shouldAnimate, iconPosition, disabled)
    );

  return !disabled && href ? (
    <Link
      id={id}
      href={href}
      onClick={onClick}
      {...hrefOptions}
      className={cn('w-full', { 'cursor-not-allowed': disabled })}
    >
      {inner}
    </Link>
  ) : (
    <button
      id={id}
      type={buttonType}
      disabled={disabled}
      onClick={onClick}
      className={cn('w-full', { 'cursor-not-allowed': disabled })}
    >
      {inner}
    </button>
  );
};

const cellInner = (
  theme: ButtonTheme,
  icon: ReactNode,
  label: ReactNode,
  animate: boolean,
  iconPosition: 'start' | 'end',
  disabled: boolean
) => {
  const isEndIcon = iconPosition === 'end';
  const buttonStyles = getButtonStyles('cell', theme, disabled);
  const baseStyles = 'flex h-cell-button items-center group';
  const elementStyles = cn(baseStyles, buttonStyles, '-mx-0.5', {
    'duration-400 transition-spacing ease-in-out': animate,
    'group-hover:pl-2': animate && isEndIcon,
    'group-hover:pr-2': animate && !isEndIcon,
  });

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
        className={cn(elementStyles, 'px-1', {
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
