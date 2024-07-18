'use client';

import cx from 'classnames';
import { ReactElement } from 'react';

import { Icon, IconName, Text } from '@/components/Shared';

export type TagKind = 'primary' | 'secondary';
export type TagTheme = 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'disabled';

export type TagProps = {
  kind?: TagKind;
  theme?: TagTheme;
  label?: string;
  startIcon?: ReactElement | IconName;
  endIcon?: ReactElement | IconName;
  children?: React.ReactNode;
  className?: string;
};

const TAG_THEME_CLASSES = {
  primary: {
    primary: 'text-volcanic-100 bg-coral-900',
    secondary: 'text-volcanic-100 bg-coral-950',
  },
  secondary: {
    primary: 'text-volcanic-100 bg-mushroom-900',
    secondary: 'text-volcanic-100 bg-mushroom-950',
  },
  success: {
    primary: 'text-success-200 bg-success-950',
    secondary: 'text-success-200 bg-success-950',
  },
  error: {
    primary: 'text-danger-350 bg-danger-950',
    secondary: 'text-danger-350 bg-danger-950',
  },
  warning: {
    primary: 'text-blue-500 bg-blue-950',
    secondary: 'text-blue-500 bg-blue-950',
  },
  disabled: {
    primary: 'text-volcanic-400 bg-marble-950',
    secondary: 'text-volcanic-400 bg-marble-950',
  },
};

export const Tag: React.FC<TagProps> = ({
  label = '',
  startIcon,
  endIcon,
  children,
  className,
  theme = 'primary',
  kind = 'primary',
}) => {
  const isStartIconString = typeof startIcon === 'string';
  const isEndIconString = typeof endIcon === 'string';

  return (
    <Text as="div" styleAs="label">
      <span
        className={cx(
          TAG_THEME_CLASSES[theme][kind],
          'flex w-fit items-center rounded px-2 py-1',
          className
        )}
      >
        {startIcon && (
          <span className="mr-1 flex items-center">
            {isStartIconString && <Icon name={startIcon} size="sm" />}
            {!isStartIconString && startIcon}
          </span>
        )}
        {label || children}
        {endIcon && (
          <span className="ml-1 flex items-center">
            {isEndIconString && <Icon name={endIcon} size="sm" />}
            {!isEndIconString && startIcon}
          </span>
        )}
      </span>
    </Text>
  );
};
