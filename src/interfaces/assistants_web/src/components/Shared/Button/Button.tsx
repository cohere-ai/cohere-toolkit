import Link from 'next/link';
import React, { HTMLAttributeAnchorTarget, ReactNode } from 'react';

import { Icon, IconName, Spinner, Text } from '@/components/Shared';
import { cn } from '@/utils';

export type ButtonKind = 'cell' | 'primary' | 'outline' | 'secondary';
export type ButtonTheme = 'blue' | 'coral' | 'evolved-green' | 'quartz' | 'mushroom' | 'danger';

const getLabelStyles = (kind: ButtonKind, theme: ButtonTheme, disabled: boolean) => {
  if (disabled) {
    return cn('text-volcanic-700 fill-volcanic-700');
  }

  switch (kind) {
    case 'primary':
    case 'cell':
      if (theme === 'evolved-green') {
        return cn('dark:text-volcanic-150 fill-volcanic-150');
      }
    case 'secondary':
      if (theme === 'evolved-green') {
        return cn(
          'text-evolved-green-700 fill-evolved-green-700',
          'group-hover:text-evolved-green-500 group-hover:fill-evolved-green-500'
        );
      } else if (theme === 'danger') {
        return cn(
          'text-danger-500 fill-danger-500',
          'group-hover:text-danger-350 group-hover:fill-danger-350'
        );
      }
    default:
      return cn(
        'text-marble-950 fill-marble-950',
        'group-hover:text-marble-1000 group-hover:fill-marble-1000'
      );
  }
};

const getButtonStyles = (kind: ButtonKind, theme: ButtonTheme, disabled: boolean) => {
  if (kind === 'secondary') return '';
  if (disabled) return 'bg-volcanic-600';

  if (kind === 'outline') {
    return cn('border', {
      'border-danger-500 group-hover:border-danger-350': theme === 'danger',
      'border-evolved-green-700 group-hover:border-evolved-green-500': theme === 'evolved-green',
      'border-blue-500 group-hover:border-blue-400': theme === 'blue',
      'border-coral-700 group-hover:border-coral-600': theme === 'coral',
      'border-quartz-500 group-hover:border-quartz-400': theme === 'quartz',
      'border-volcanic-500 group-hover:border-volcanic-400': theme === 'mushroom',
    });
  } else {
    return cn({
      'bg-danger-500 group-hover:bg-danger-350': theme === 'danger',
      'bg-evolved-green-700 group-hover:bg-evolved-green-500': theme === 'evolved-green',
      'bg-blue-500 group-hover:bg-blue-400': theme === 'blue',
      'fill-coral-700 bg-coral-700 group-hover:bg-coral-600': theme === 'coral',
      'bg-quartz-500 group-hover:bg-quartz-400': theme === 'quartz',
      'bg-mushroom-500 group-hover:bg-mushroom-400': theme === 'mushroom',
    });
  }
};

const getCellStyles = (theme: ButtonTheme, disabled: boolean) => {
  if (disabled) return 'fill-volcanic-600';

  return cn({
    'fill-danger-500 group-hover:fill-danger-350': theme === 'danger',
    'fill-evolved-green-700 group-hover:fill-evolved-green-500': theme === 'evolved-green',
    'fill-blue-500 group-hover:fill-blue-400': theme === 'blue',
    'fill-coral-700 group-hover:fill-coral-600': theme === 'coral',
    'fill-quartz-500 group-hover:fill-quartz-400': theme === 'quartz',
    'fill-mushroom-500 group-hover:fill-mushroom-400': theme === 'mushroom',
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
  animate?: boolean;
  danger?: boolean;
  stretch?: boolean;
};

export const Button: React.FC<ButtonProps> = ({
  id,
  kind = 'primary',
  theme = kind === 'secondary' ? 'mushroom' : 'blue',
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
  animate = true,
  stretch = false,
  iconPosition = kind === 'cell' ? 'end' : 'start',
}) => {
  const labelStyles = getLabelStyles(kind, theme, disabled);
  const buttonStyles = getButtonStyles(kind, theme, disabled);
  const animateStyles =
    animate && !disabled
      ? cn('duration-400 transition-spacing ease-in-out', {
          'pl-3 group-hover:pl-1': iconPosition === 'start',
          'pr-3 group-hover:pr-1': iconPosition === 'end',
        })
      : undefined;

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
          'group flex h-cell-button w-fit items-center justify-center rounded-md',
          buttonStyles,
          className,
          {
            'h-fit justify-start': kind === 'secondary',
            'w-full': stretch,
            'space-x-3': !animateStyles,
          }
        )}
      >
        {iconPosition === 'start' && iconElement}
        {labelElement && <div className={cn(animateStyles)}>{labelElement}</div>}
        {iconPosition === 'end' && iconElement}
      </div>
    ) : (
      cellInner(theme, iconElement, labelElement, !disabled && animate, iconPosition, disabled)
    );

  return !disabled && href ? (
    <Link
      id={id}
      href={href}
      onClick={onClick}
      rel={rel}
      target={target}
      className={cn({ 'cursor-not-allowed': disabled, 'w-full': stretch })}
    >
      {inner}
    </Link>
  ) : (
    <button
      id={id}
      type={buttonType}
      disabled={disabled}
      onClick={onClick}
      className={cn({ 'cursor-not-allowed': disabled, 'w-full': stretch })}
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
