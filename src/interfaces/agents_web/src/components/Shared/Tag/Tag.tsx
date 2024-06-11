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
    primary: 'text-volcanic-900 bg-primary-100',
    secondary: 'text-volcanic-900 bg-primary-50',
  },
  secondary: {
    primary: 'text-volcanic-900 bg-secondary-100',
    secondary: 'text-volcanic-900 bg-secondary-50',
  },
  success: {
    primary: 'text-success-500 bg-success-50',
    secondary: 'text-success-500 bg-success-50',
  },
  error: {
    primary: 'text-danger-500 bg-danger-50',
    secondary: 'text-danger-500 bg-danger-50',
  },
  warning: {
    primary: 'text-blue-700 bg-blue-50',
    secondary: 'text-blue-700 bg-blue-50',
  },
  disabled: {
    primary: 'text-volcanic-700 bg-marble-300',
    secondary: 'text-volcanic-700 bg-marble-300',
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
