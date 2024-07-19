'use client';

import Link from 'next/link';

import { Text } from '@/components/Shared';
import { cn } from '@/utils';

type Kind = 'primary' | 'secondary' | 'tertiary' | 'minimal';
type Theme = 'primary' | 'volcanic' | 'green';
type Size = 'sm' | 'md' | 'lg';
export type Target = '_blank' | '_self' | '_parent' | '_top';
type Type = 'button' | 'submit' | 'reset';

export type BasicButtonProps = {
  id?: string;
  label?: React.ReactNode;
  kind?: Kind;
  theme?: Theme;
  size?: Size;
  type?: Type;
  disabled?: boolean;
  hasBorders?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  className?: string;
  href?: string;
  shallow?: boolean;
  rel?: string;
  target?: Target;
  preventDefault?: boolean;
  stopPropagation?: boolean;
  form?: string;
  onClick?: React.MouseEventHandler<HTMLButtonElement | HTMLAnchorElement>;
  dataTestId?: string;
};

const getThemeStyles = (theme: Theme, kind: Kind, hasBorders: boolean) => {
  const focusStyles =
    'focus-visible:outline-offset-4 focus-visible:outline focus-visible:outline-1 focus-visible:outline-volcanic-400';
  switch (theme) {
    case 'green': {
      if (kind === 'secondary') {
        return cn(
          { 'border rounded-lg': hasBorders },
          'border-green-800 bg-green-950 text-green-250',
          'hover:bg-green-900',
          'active:bg-green-800',
          'disabled:bg-marble-950 disabled:border-marble-950 disabled:text-volcanic-400',
          focusStyles
        );
      } else {
        throw new Error(
          `Attention developer, kind: "${kind}" for green theme is not yet developed. Please add it if it's needed.`
        );
      }
    }
    case 'primary': {
      if (kind === 'primary') {
        return cn(
          { 'border rounded-lg': hasBorders },
          'border-coral-700 bg-coral-700 text-volcanic-100',
          'hover:bg-coral-950',
          'active:bg-coral-900',
          'disabled:bg-marble-950 disabled:border-marble-950 disabled:text-volcanic-400',
          focusStyles
        );
      } else if (kind === 'secondary') {
        return cn(
          { 'border rounded-lg': hasBorders },
          'border-coral-700 bg-coral-950 text-volcanic-100',
          'hover:bg-coral-700',
          'active:bg-coral-950',
          'disabled:bg-marble-950 disabled:border-marble-950 disabled:text-volcanic-400',
          focusStyles
        );
      }
    }
    case 'volcanic': {
      if (kind === 'primary') {
        return cn(
          { 'border rounded-lg': hasBorders },
          'border-volcanic-100 bg-volcanic-100 text-marble-1000',
          'hover:bg-volcanic-300 hover:border-volcanic-300',
          'active:border-volcanic-100 active:bg-volcanic-100 active:text-marble-1000',
          'disabled:bg-marble-950 disabled:border-marble-950 disabled:text-volcanic-400',
          focusStyles
        );
      } else if (kind === 'secondary') {
        return cn(
          { 'border rounded-lg': hasBorders },
          'border-marble-800 bg-marble-1000 text-volcanic-100',
          'hover:bg-marble-980 hover:border-volcanic-500 hover:text-volcanic-100',
          'active:border-volcanic-100 active:bg-marble-1000 active:text-volcanic-100',
          'disabled:bg-marble-950 disabled:border-marble-950 disabled:text-volcanic-400',
          focusStyles
        );
      } else if (kind === 'tertiary') {
        return cn(
          { 'border rounded-lg': hasBorders },
          'border-marble-800 bg-marble-980 text-volcanic-100',
          'hover:bg-marble-950 hover:text-volcanic-100',
          'active:border-volcanic-100 active:bg-marble-980 active:text-volcanic-100',
          'disabled:bg-marble-950 disabled:border-marble-950 disabled:text-volcanic-400',
          focusStyles
        );
      } else if (kind === 'minimal') {
        return cn(
          { 'border rounded-lg': hasBorders },
          'border-transparent',
          'text-volcanic-100',
          'hover:text-volcanic-300',
          'active:text-volcanic-100',
          'disabled:text-volcanic-400',
          focusStyles
        );
      }
    }
  }

  return undefined;
};

const SIZE_STYLES = {
  sm: cn('px-3 py-2'),
  md: cn('px-10 py-3'),
  lg: cn('px-10 py-4'),
};

export const BasicButton: React.FC<BasicButtonProps> = ({
  id,
  label,
  kind = 'primary',
  theme = 'volcanic',
  type = 'button',
  size = 'md',
  disabled = false,
  hasBorders = true,
  target,
  startIcon,
  endIcon,
  className,
  onClick,
  href,
  shallow,
  rel,
  preventDefault = false,
  stopPropagation = false,
  form,
  dataTestId,
}) => {
  const handleClick: React.MouseEventHandler<HTMLButtonElement | HTMLAnchorElement> = (e) => {
    if (preventDefault) e.preventDefault();
    if (stopPropagation) e.stopPropagation();
    onClick?.(e);
  };

  const styles = getThemeStyles(theme, kind, hasBorders);
  const inner = (
    <>
      {startIcon && <div className={cn('flex items-center', { 'mr-2': label })}>{startIcon}</div>}
      <Text as="span" styleAs={size === 'lg' ? 'p-lg' : 'p'}>
        {label}
      </Text>
      {endIcon && <div className={cn('flex items-center', { 'ml-2': label })}>{endIcon}</div>}
    </>
  );
  const classNames = cn(
    'group flex h-fit items-center justify-center whitespace-nowrap transition ease-in-out',
    'disabled:cursor-not-allowed',
    SIZE_STYLES[size],
    styles,
    className
  );
  // We cannot disable <a> elements natively so we show a disabled button instead
  return !disabled && href ? (
    <Link
      id={id}
      href={href}
      shallow={shallow}
      rel={rel}
      className={classNames}
      target={target || '_self'}
      onClick={handleClick}
      data-testid={dataTestId}
    >
      {inner}
    </Link>
  ) : (
    <button
      id={id}
      className={classNames}
      type={type}
      disabled={disabled}
      onClick={handleClick}
      form={form}
      data-testid={dataTestId}
    >
      {inner}
    </button>
  );
};
