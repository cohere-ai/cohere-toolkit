'use client';

import cx from 'classnames';
import Link from 'next/link';
import { MouseEventHandler, ReactElement, ReactNode } from 'react';

import { Icon, IconName } from '@/components/Shared/Icon';

type ButtonType = 'button' | 'submit' | 'reset';
export type MinimalButtonTheme = 'volcanic' | 'secondary';
export type MinimalButtonSize = 'sm' | 'md' | 'lg';

export type MinimalButtonProps = {
  id?: string;
  label?: ReactNode | string;
  children?: ReactNode;
  type?: ButtonType;
  disabled?: boolean;
  size?: MinimalButtonSize;
  theme?: MinimalButtonTheme;
  /* Icon left-aligned at the start of the button */
  startIcon?: ReactElement | IconName;
  /* Icon right-aligned at the end of the button */
  endIcon?: ReactElement | IconName;
  className?: string;
  onClick?: MouseEventHandler<HTMLButtonElement | HTMLAnchorElement>;
  href?: string;
  rel?: string;
  target?: string;
  preventDefault?: boolean;
  stopPropagation?: boolean;
  form?: string;
  hideFocusStyles?: boolean;
  /* Determines if the start or end icon will transition inwards */
  animate?: boolean;
  [key: string]: any;
};

export const MinimalButton: React.FC<MinimalButtonProps> = ({
  id,
  label,
  children,
  type = 'button',
  disabled = false,
  size = 'md',
  theme = 'volcanic',
  target,
  startIcon,
  endIcon,
  className,
  onClick,
  href,
  rel,
  preventDefault = false,
  stopPropagation = false,
  hideFocusStyles = false,
  animate = true,
  form,
  ...rest
}) => {
  const themeClasses: { [key in MinimalButtonTheme]: string } = {
    volcanic: cx({
      'visited:text-coral-400': href,
      'text-volcanic-400': disabled,
      'text-volcanic-100': !disabled,
    }),
    secondary: cx({
      'visited:text-coral-400': href,
      'text-volcanic-60': disabled,
      'text-mushroom-950': !disabled,
    }),
  };

  const isStartIconString = typeof startIcon === 'string';
  const isEndIconString = typeof endIcon === 'string';

  const inner = (
    <span className={cx('flex items-center', themeClasses[theme])}>
      {isStartIconString && <Icon name={startIcon} size={size} />}
      {!isStartIconString && startIcon}
      <span
        className={cx({
          'pl-3': startIcon && !!label && animate,
          'pl-1': startIcon && !!label && !animate,
          'duration-400 transition-all ease-in-out group-hover:pl-1 group-hover:pr-2':
            startIcon && !endIcon && !disabled && animate,
        })}
      >
        {label || children}
      </span>
      {endIcon && (
        <span
          className={cx('flex items-center', {
            'duration-400 transition-all ease-in-out group-hover:pl-1 group-hover:pr-2':
              !disabled && animate,
            'pl-3': !!label && animate,
            'pl-1': !!label && !animate,
          })}
        >
          {isEndIconString && <Icon name={endIcon} size={size} />}
          {!isEndIconString && endIcon}
        </span>
      )}
    </span>
  );

  const buttonClassNames = cx(
    'group inline-block max-w-full',
    'disabled:cursor-not-allowed',
    {
      'focus-visible:outline-1 focus-visible:outline focus-visible:outline-coral-700 rounded-sm':
        !hideFocusStyles,
    },
    className
  );

  const handleClick: React.MouseEventHandler<HTMLButtonElement | HTMLAnchorElement> = (e) => {
    if (preventDefault) e.preventDefault();
    if (stopPropagation) e.stopPropagation();
    if (onClick) onClick(e);
  };

  const { splitIcon, ...allowedProps } = rest;
  // We cannot disable <a> elements natively so we show a disabled button instead
  return !disabled && href ? (
    <Link
      {...allowedProps}
      id={id}
      href={href}
      rel={rel}
      onClick={handleClick}
      className={buttonClassNames}
      target={target || '_self'}
    >
      {inner}
    </Link>
  ) : (
    <button
      {...rest}
      id={id}
      type={type}
      disabled={disabled}
      onClick={handleClick}
      form={form}
      className={buttonClassNames}
    >
      {inner}
    </button>
  );
};
