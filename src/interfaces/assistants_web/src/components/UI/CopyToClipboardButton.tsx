'use client';

import { MouseEvent, forwardRef, useImperativeHandle, useState } from 'react';

import { Button, ButtonKind, IconButton, IconName, Tooltip } from '@/components/UI';
import { cn } from '@/utils';

type CopyToClipboardButtonProps = {
  value: string;
  label?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  kind?: ButtonKind;
  disabled?: boolean;
  className?: string;
  iconAtStart?: boolean;
  onClick?: React.MouseEventHandler<HTMLElement>;
};

type CopyToClipboardButtonHandle = {
  triggerCopy: (e: MouseEvent<HTMLElement>) => void;
};

/**
 * Displays a button where, when clicked, copies text to your clipboard
 */
export const CopyToClipboardButton = forwardRef<
  CopyToClipboardButtonHandle,
  CopyToClipboardButtonProps
>(function CopyButton(
  {
    label,
    value,
    disabled = false,
    className = '',
    kind = 'primary',
    iconAtStart = false,
    onClick,
  },
  ref
) {
  const [copied, setCopied] = useState(false);

  const available = !!window?.navigator?.clipboard;
  const buttonLabel = !available ? 'Copy (requires HTTPS)' : copied ? 'Copied!' : label;

  const handleCopy = async (e: MouseEvent<HTMLElement>) => {
    e.stopPropagation();
    e.preventDefault();

    try {
      await window?.navigator?.clipboard.writeText(value ?? '');
      setCopied(true);
      setTimeout(() => setCopied(false), 1000);
    } catch (e) {
      console.error(e);
    } finally {
      onClick?.(e);
    }
  };

  useImperativeHandle(ref, () => ({
    triggerCopy(e: MouseEvent<HTMLElement>) {
      handleCopy(e);
    },
  }));

  return (
    <Button
      kind={kind}
      onClick={handleCopy}
      label={buttonLabel}
      icon="copy"
      iconPosition={iconAtStart ? 'start' : 'end'}
      className={className}
      disabled={disabled || !available}
      aria-label={copied ? 'copied' : 'copy'}
    />
  );
});

type CopyToClipboardIconButtonProps = {
  iconName?: IconName;
  value: string;
  onClick?: React.MouseEventHandler<HTMLElement>;
  disabled?: boolean;
  duration?: number;
  hoverDelay?: {
    open?: number;
    close?: number;
  };
  iconClassName?: string;
  buttonClassName?: string;
};

export const CopyToClipboardIconButton: React.FC<CopyToClipboardIconButtonProps> = ({
  iconName = 'copy',
  value,
  onClick,
  disabled,
  duration,
  hoverDelay,
  iconClassName,
  buttonClassName,
}) => {
  const [isCopied, setIsCopied] = useState(false);

  const available = !!window?.navigator?.clipboard;
  const label = !available ? 'Copy (requires HTTPS)' : isCopied ? 'Copied!' : 'Copy';

  const handleCopy = async (e: MouseEvent<HTMLElement>) => {
    if (!available) {
      return;
    }
    try {
      await window?.navigator?.clipboard.writeText(value ?? '');
      setIsCopied(true);
    } catch (e) {
      console.error(e);
    } finally {
      setTimeout(() => {
        setIsCopied(false);
      }, 1000);
      onClick?.(e);
    }
  };

  return (
    <div>
      <Tooltip
        label={label}
        duration={duration}
        size="sm"
        showOutline={false}
        hover
        hoverDelay={hoverDelay}
        className="-translate-x-[40%]"
        buttonClassName={buttonClassName}
      >
        <IconButton
          aria-disabled={disabled || !available}
          disabled={disabled || !available}
          iconName={iconName}
          iconKind={isCopied ? 'default' : 'outline'}
          className="grid place-items-center rounded hover:bg-mushroom-900 dark:hover:bg-volcanic-200"
          iconClassName={cn(
            'text-volcanic-300 fill-volcanic-300 group-hover/icon-button:fill-mushroom-300',
            'dark:fill-marble-800 dark:group-hover/icon-button:fill-marble-800',
            iconClassName
          )}
          onClick={handleCopy}
        />
      </Tooltip>
    </div>
  );
};
