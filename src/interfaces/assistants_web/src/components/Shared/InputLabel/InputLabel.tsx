'use client';

import { Text, Tooltip } from '@/components/Shared';
import { cn } from '@/utils';

export type Props = {
  label: React.ReactNode;
  children?: React.ReactNode;
  name?: string;
  sublabel?: React.ReactNode;
  containerClassName?: string;
  className?: string;
  labelContainerClassName?: string;
  labelClassName?: string;
  tooltipLabel?: React.ReactNode;
  onClick?: React.MouseEventHandler<HTMLLabelElement>;
  styleAs?: 'label' | 'p';
};

export const InputLabel: React.FC<Props> = ({
  label,
  children,
  sublabel,
  containerClassName,
  className,
  labelClassName,
  labelContainerClassName,
  tooltipLabel,
  name,
  onClick,
  styleAs = 'label',
}) => {
  return (
    <label className={cn('flex flex-col', containerClassName)} htmlFor={name} onClick={onClick}>
      <div className={cn('flex w-full flex-col gap-y-1 pb-0.5', className)}>
        <span className={cn('flex items-center gap-x-1', labelContainerClassName)}>
          {typeof label === 'string' ? (
            <Text
              className={cn('text-volcanic-100 dark:text-marble-950', labelClassName)}
              as="span"
              styleAs={styleAs}
            >
              {label}
            </Text>
          ) : (
            label
          )}
          {tooltipLabel && (
            <Tooltip label={tooltipLabel} hover iconClassName="fill-volcanic-500 mb-0.5" />
          )}
        </span>

        {sublabel && (
          <Text styleAs="caption" className="text-volcanic-500">
            {sublabel}
          </Text>
        )}
      </div>
      {children}
    </label>
  );
};
