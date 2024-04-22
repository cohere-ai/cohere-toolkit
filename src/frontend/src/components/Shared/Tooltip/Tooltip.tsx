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
import { useEffect, useState } from 'react';

import { Icon, Text } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  label: React.ReactNode;
  children?: React.ReactNode;
  hover?: boolean;
  duration?: number;
  icon?: React.ReactNode;
  iconClassName?: string;
  buttonClassName?: string;
  textClassname?: string;
  className?: string;
  showOutline?: boolean;
  placement?: Placement;
  onClickTrigger?: () => void;
};

/**
 * Tooltip component is used to display a small piece of information when the user clicks over an icon.
 * We use floating-ui to handle the positioning and manage the state of the tooltip.
 * @param label - The text that will be displayed inside the tooltip.
 * @param duration - The time in milliseconds that the tooltip will be displayed. If not provided, the tooltip will be displayed until the user clicks outside of it.
 * @param icon - The icon that will be displayed. If not provided, the default icon will be used.
 * @param textClassname - The class name that will be applied to the text.
 * @param iconClassName - The class name that will be applied to the icon.
 * @param className - The class name that will be applied to the tooltip.
 */
export const Tooltip: React.FC<Props> = ({
  label,
  className,
  hover: hoverEnabled = false,
  children,
  iconClassName,
  buttonClassName,
  textClassname,
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
  const hover = useHover(context, { enabled: hoverEnabled });

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
          className={cn(
            'flex h-full items-center',
            {
              'focus:rounded focus:outline focus:outline-1 focus:outline-offset-2 focus:outline-volcanic-700':
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
              className={cn(iconClassName || 'text-volcanic-800', {
                'hover:!font-iconDefault': hoverEnabled,
              })}
            />
          )}
        </button>
      )}
      <FloatingPortal>
        {open && (
          <div
            className={cn(
              'z-50 max-w-[300px] rounded border border-marble-400 bg-marble-200 px-4 py-2.5',
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
            <Text className={cn('whitespace-normal text-volcanic-800', textClassname)}>
              {label}
            </Text>
          </div>
        )}
      </FloatingPortal>
    </>
  );
};
