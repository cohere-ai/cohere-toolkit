'use client';

import {
  FloatingPortal,
  Placement,
  flip,
  offset,
  useClick,
  useDismiss,
  useFloating,
  useHover,
  useInteractions,
  useRole,
} from '@floating-ui/react';
import cx from 'classnames';
import { PropsWithChildren, useEffect, useState } from 'react';

import { Icon, Text } from '@/components/Shared';

export type TooltipProps = PropsWithChildren<{
  label: React.ReactNode;
  size?: 'sm' | 'md';
  hover?: boolean;
  hoverDelay?: number | Partial<{ open: number; close: number }>;
  duration?: number;
  icon?: React.ReactNode;
  iconClassName?: string;
  buttonClassName?: string;
  className?: string;
  onClickTrigger?: () => void;
  showOutline?: boolean;
  placement?: Placement;
}>;

/**
 * Tooltip component is used to display a small piece of information when the user clicks over an icon.
 * We use floating-ui to handle the positioning and manage the state of the tooltip.
 * @param label - The text that will be displayed inside the tooltip.
 * @param hover - If true, the tooltip will be displayed when the user hovers over the trigger element.
 * @param duration - The time in milliseconds that the tooltip will be displayed. If not provided, the tooltip will be displayed until the user clicks outside of it.
 * @param icon - The icon that will be displayed. If not provided, the default icon will be used.
 * @param textClassname - The class name that will be applied to the text.
 * @param iconClassName - The class name that will be applied to the icon.
 * @param className - The class name that will be applied to the tooltip.
 */
export const Tooltip: React.FC<TooltipProps> = ({
  label,
  className,
  size = 'md',
  hover: hoverEnabled = false,
  hoverDelay,
  children,
  iconClassName,
  buttonClassName,
  icon,
  duration,
  onClickTrigger,
  showOutline = true,
  placement = 'top-start',
}) => {
  const [open, setOpen] = useState(false);

  const { x, y, refs, strategy, context } = useFloating({
    open,
    onOpenChange: setOpen,
    placement,
    middleware: [offset(5), flip()],
  });

  const click = useClick(context);
  const dismiss = useDismiss(context);
  const role = useRole(context);
  const hover = useHover(context, { enabled: hoverEnabled, delay: hoverDelay });

  const { getReferenceProps, getFloatingProps } = useInteractions([click, dismiss, role, hover]);
  const { onClick, ...restReferenceProps } = getReferenceProps();

  useEffect(() => {
    if (duration && open) {
      setTimeout(() => setOpen(false), duration);
    }
  }, [open, duration]);

  return (
    <>
      {children ? (
        <div ref={refs.setReference} {...restReferenceProps}>
          {children}
        </div>
      ) : (
        <button
          type="button"
          className={cx(
            'flex h-full items-center',
            {
              'focus:rounded focus:outline focus:outline-1 focus:outline-offset-2 focus:outline-volcanic-400':
                showOutline,
            },
            buttonClassName
          )}
          ref={refs.setReference}
          {...restReferenceProps}
          onClick={(e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => {
            e.stopPropagation();
            const floatingUIOnClick = onClick as (
              e: React.MouseEvent<HTMLButtonElement, MouseEvent>
            ) => void;
            floatingUIOnClick(e);

            if (onClickTrigger) {
              onClickTrigger();
            }
          }}
        >
          {icon || (
            <Icon
              name="information"
              kind="outline"
              className={cx(iconClassName || 'text-volcanic-300', {
                'hover:!font-iconDefault': hoverEnabled,
              })}
            />
          )}
        </button>
      )}
      <FloatingPortal>
        {open && (
          <div
            className={cx(
              'z-tooltip',
              {
                'max-w-[400px] rounded-sm border-none bg-mushroom-150 px-1 py-0.5': size === 'sm',
                'max-w-[300px] rounded border border-marble-950 bg-marble-980 px-4 py-2.5':
                  size === 'md',
              },
              className
            )}
            ref={refs.setFloating}
            style={{
              position: strategy,
              top: y ?? 0,
              left: x ?? 0,
            }}
            {...getFloatingProps()}
          >
            {size === 'sm' ? (
              <Text as="span" styleAs="p-sm" className="flex text-marble-950">
                {label}
              </Text>
            ) : (
              <Text as="span">{label}</Text>
            )}
          </div>
        )}
      </FloatingPortal>
    </>
  );
};
