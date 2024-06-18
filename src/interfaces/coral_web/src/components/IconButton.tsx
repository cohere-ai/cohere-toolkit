import React from 'react';

import { BasicButton, Icon, IconName, Target, Text, Tooltip } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  iconName: IconName;
  tooltipLabel?: React.ReactNode;
  size?: 'sm' | 'md';
  href?: string;
  target?: Target;
  shallow?: boolean;
  isDefaultOnHover?: boolean;
  iconKind?: 'default' | 'outline';
  iconClassName?: string;
  disabled?: boolean;
  className?: string;
  dataTestId?: string;
  onClick?: (e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
};

/**
 * @description Convenience component for rendering an icon button that follows Chat UI's design patterns.
 */
const IconButton: React.FC<Props> = ({
  iconName,
  tooltipLabel,
  size = 'md',
  iconKind = 'outline',
  iconClassName,
  isDefaultOnHover = true,
  className,
  disabled,
  href,
  target,
  shallow,
  dataTestId,
  onClick,
}) => {
  const iconButton = (
    <BasicButton
      className={cn(
        'group/icon-button h-8 w-8 p-0',
        { 'h-8 w-8': size === 'md', 'h-7 w-7': size === 'sm' },
        'rounded hover:bg-secondary-100',
        className
      )}
      startIcon={
        <Icon
          name={iconName}
          className={cn(
            'text-secondary-700',
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
      dataTestId={dataTestId}
      onClick={onClick}
    />
  );

  return tooltipLabel ? (
    <Tooltip label={tooltipLabel} size="sm" hover hoverDelay={{ open: 250 }}>
      {iconButton}
    </Tooltip>
  ) : (
    iconButton
  );
};
export default IconButton;
