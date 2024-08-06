'use client';

import { ReactNode, useEffect, useRef } from 'react';

import { Icon, Text } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  number?: number;
  title?: string | ReactNode;
  description?: string | ReactNode;
  children: ReactNode;
  isExpanded?: boolean;
  setIsExpanded?: (expanded: boolean) => void;
};
export const CollapsibleSection: React.FC<Props> = ({
  number,
  title,
  description,
  children,
  isExpanded = false,
  setIsExpanded,
}) => {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (isExpanded) {
      ref.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
        inline: 'nearest',
      });
    }
  }, [isExpanded]);

  return (
    <div
      ref={ref}
      className={cn(
        'flex w-full max-w-screen-md flex-col rounded-md',
        'space-y-5 border p-6',
        'border-volcanic-800 bg-volcanic-950 dark:border-volcanic-200 dark:bg-volcanic-150'
      )}
    >
      {/* Visible portion */}
      <button
        className="flex w-full flex-col space-y-1"
        disabled={!setIsExpanded}
        onClick={() => setIsExpanded && setIsExpanded(!isExpanded)}
      >
        <div className="flex w-full items-center justify-between">
          <div className="flex w-full items-center space-x-2.5">
            {number && (
              <Text
                styleAs="p-sm"
                className={cn(
                  'flex items-center justify-center',
                  'h-[18px] w-[18px] rounded-[4px] border',
                  'border-coral-700 text-coral-700 dark:border-evolved-green-700 dark:text-evolved-green-700'
                )}
              >
                {number}
              </Text>
            )}
            {title && typeof title === 'string' ? <Text className="text-lg">{title}</Text> : title}
          </div>
          <Icon
            name="chevron-down"
            size="lg"
            className={cn('transition-transform duration-300', {
              hidden: !setIsExpanded,
              'rotate-180 transform': isExpanded,
            })}
          />
        </div>
        {description && typeof description === 'string' ? (
          <Text className="text-left dark:text-marble-800">{description}</Text>
        ) : (
          description
        )}
      </button>
      {isExpanded && children}
    </div>
  );
};
