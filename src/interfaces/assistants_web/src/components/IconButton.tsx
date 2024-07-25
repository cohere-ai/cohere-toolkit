'use client';

import { Placement } from '@floating-ui/react';
import React, { ReactElement } from 'react';

import { BasicButton, IconName, Target, Tooltip, Icon as _Icon } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  iconName?: IconName;
  icon?: ReactElement;
  tooltip?: {
    label: string;
    size?: 'sm' | 'md';
    placement?: Placement;
  };
  size?: 'sm' | 'md';
  href?: string;
  target?: Target;
  shallow?: boolean;
  iconKind?: 'default' | 'outline';
  iconClassName?: string;
  disabled?: boolean;
  className?: string;
  onClick?: (e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
};

/**
 * @description Convenience component for rendering an icon button that follows Chat UI's design patterns.
 */
export const IconButton: React.FC<Props> = ({
  iconName,
  icon,
  tooltip,
  size = 'md',
  iconKind = 'outline',
  iconClassName,
  className,
  disabled,
  href,
  target,
  onClick,
}) => {
  const Icon = icon ? (
    icon
  ) : iconName ? (
    <_Icon name={iconName} className={iconClassName} kind={iconKind} />
  ) : null;

  const iconButton = (
    <BasicButton
      className={cn(
        'group/icon-button h-8 w-8 p-0',
        { 'h-8 w-8': size === 'md', 'h-7 w-7': size === 'sm' },
        'rounded hover:bg-mushroom-900 dark:text-marble-800 dark:hover:bg-volcanic-200',
        className
      )}
      startIcon={Icon}
      size="lg"
      kind="minimal"
      disabled={disabled}
      href={href}
      target={target}
      onClick={onClick}
    />
  );

  return tooltip ? (
    <Tooltip
      label={tooltip.label}
      size={tooltip.size ?? 'sm'}
      placement={tooltip.placement}
      hover
      hoverDelay={{ open: 250 }}
    >
      {iconButton}
    </Tooltip>
  ) : (
    iconButton
  );
};
