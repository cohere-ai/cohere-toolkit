'use client';

import Link from 'next/link';
import { ReactElement } from 'react';

import { Icon, IconName } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  href: string;
  label?: React.ReactNode;
  disabled?: boolean;
  startIcon?: ReactElement | IconName;
  endIcon?: ReactElement | IconName;
  className?: string;
  target?: '_blank' | '_self' | '_parent' | '_top';
  theme?: 'green' | 'volcanic' | 'blue' | 'quartz' | 'coral' | 'danger';
};

/**
 * Renders a link with an optional start and/or end icon
 */
export const InlineLink: React.FC<Props> = ({
  label,
  disabled = false,
  startIcon,
  endIcon,
  className,
  href,
  target = '_self',
  theme = 'green',
}) => {
  const isStartIconString = typeof startIcon === 'string';
  const isEndIconString = typeof endIcon === 'string';

  const internalLink = (
    <a
      rel="noreferrer"
      target={target}
      className={cn(
        'group inline-block cursor-pointer whitespace-nowrap underline',
        'border-y border-y-transparent focus:border-b-green-150 focus:no-underline focus:outline-none',
        {
          'hover:no-underline': !disabled,
          'text-green-250 visited:text-green-200 hover:text-green-150': theme === 'green',
          'text-volcanic-100': theme === 'volcanic',
          'text-blue-600 visited:text-blue-500 hover:text-blue-300': theme === 'blue',
          'text-quartz-700 visited:text-quartz-900 hover:text-quartz-900': theme === 'quartz',
          'text-coral-400 visited:text-coral-200 hover:text-coral-200': theme === 'coral',
          'text-danger-350': theme === 'danger',
          'cursor-not-allowed !text-volcanic-400 visited:!text-volcanic-400': disabled,
        },
        className
      )}
    >
      {startIcon && (
        <span className="mr-1 inline-block">
          {isStartIconString && <Icon name={startIcon} size="sm" />}
          {!isStartIconString && startIcon}
        </span>
      )}
      {typeof label === 'string' ? <span>{label}</span> : label}
      {endIcon && (
        <span className="ml-1 inline-block">
          {isEndIconString && <Icon name={endIcon} size="sm" />}
          {!isEndIconString && endIcon}
        </span>
      )}
    </a>
  );

  return disabled ? (
    internalLink
  ) : (
    <Link href={href} passHref legacyBehavior>
      {internalLink}
    </Link>
  );
};
