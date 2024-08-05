'use client';

import { MouseEvent, forwardRef, useImperativeHandle, useState } from 'react';

import { Button, ButtonKind, Icon, IconName, Tooltip } from '@/components/Shared';
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
      label={copied ? 'Copied!' : label}
      icon="copy"
      iconPosition={iconAtStart ? 'start' : 'end'}
      className={className}
      disabled={disabled}
      aria-label={copied ? 'copied' : 'copy'}
    />
  );
});

type CopyToClipboardIconButtonProps = {
  iconName?: IconName;
  value: string;
  onClick?: React.MouseEventHandler<HTMLElement>;
  disabled?: boolean;
  iconClassName?: string;
  buttonClassName?: string;
};

export const CopyToClipboardIconButton: React.FC<CopyToClipboardIconButtonProps> = ({
  iconName = 'copy',
  value,
  onClick,
  disabled,
  iconClassName,
  buttonClassName,
}) => {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async (e: MouseEvent<HTMLElement>) => {
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
        label={isCopied ? 'Copied!' : 'Copy'}
        duration={1000}
        size="sm"
        showOutline={false}
        hover
        className="-translate-x-[40%]"
        buttonClassName={buttonClassName}
        icon={
          <Icon
            aria-disabled={disabled}
            name={iconName}
            kind={isCopied ? 'default' : 'outline'}
            className={cn(
              'flex rounded p-2',
              'transition ease-in-out',
              'fill-volcanic-300 hover:bg-mushroom-900 hover:fill-mushroom-300 dark:fill-mushroom-800 dark:hover:bg-inherit dark:hover:fill-mushroom-800',
              iconClassName
            )}
            onClick={handleCopy}
          />
        }
      />
    </div>
  );
};
