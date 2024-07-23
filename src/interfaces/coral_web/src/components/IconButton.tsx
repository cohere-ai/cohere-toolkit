'use client';

import { Placement } from '@floating-ui/react';
import React from 'react';

import { BasicButton, Icon, IconName, Target, Tooltip } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  iconName: IconName;
  tooltip?: {
    label: string;
    size?: 'sm' | 'md';
    placement?: Placement;
  };
  size?: 'sm' | 'md';
  href?: string;
  target?: Target;
  shallow?: boolean;
  isDefaultOnHover?: boolean;
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
  tooltip,
  size = 'md',
  iconKind = 'outline',
  iconClassName,
  isDefaultOnHover = true,
  className,
  disabled,
  href,
  target,
  shallow,
  onClick,
}) => {
  const iconButton = (
    <BasicButton
      className={cn(
        'group/icon-button h-8 w-8 p-0',
        { 'h-8 w-8': size === 'md', 'h-7 w-7': size === 'sm' },
        'rounded hover:bg-mushroom-900',
        className
      )}
      startIcon={
        <Icon
          name={iconName}
          className={cn(
            'text-mushroom-400',
            'transition-colors ease-in-out',
            {
              'group-hover/icon-button:!font-iconDefault': isDefaultOnHover,
            },
            iconClassName
          )}
          kind={iconKind}
        />
      }
      size="lg"
      kind="minimal"
      disabled={disabled}
      href={href}
      target={target}
      shallow={shallow}
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
