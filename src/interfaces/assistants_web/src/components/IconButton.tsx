'use client';

import { Placement } from '@floating-ui/react';
import React, { HTMLAttributeAnchorTarget, ReactElement } from 'react';

import { Button, IconName, Tooltip } from '@/components/Shared';
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
  target?: HTMLAttributeAnchorTarget;
  shallow?: boolean;
  iconKind?: 'default' | 'outline';
  iconClassName?: string;
  disabled?: boolean;
  className?: string;
  outline?: boolean;
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
  shallow,
  outline = false,
  onClick,
}) => {
  const iconButton = (
    <Button
      kind={outline ? 'outline' : 'secondary'}
      disabled={disabled}
      href={href}
      onClick={onClick}
      hrefOptions={{ target, shallow }}
      icon={iconName}
      iconOptions={{ kind: iconKind, className: iconClassName, customIcon: icon }}
      className={cn(className, 'group/icon-button h-8 w-8 p-0', {
        'h-8 w-8': size === 'md',
        'h-7 w-7': size === 'sm',
        'p-2': outline,
      })}
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
