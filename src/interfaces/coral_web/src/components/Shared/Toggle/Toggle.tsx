'use client';

import { Cell } from '@/components/Shared/Cell/Cell';
import { cn } from '@/utils';

type ToggleOption = {
  icon: React.ReactNode;
  value: string;
};

type Props = React.PropsWithChildren<{
  options: ToggleOption[];
  selectedValue?: string;
  className?: string;
  onSelect?: (value: string) => void;
}>;

/**
 * A toggle with cell-shaped buttons.
 */
export const Toggle: React.FC<Props> = ({
  className = '',
  options = [],
  selectedValue,
  onSelect,
}) => {
  const selectedOption = selectedValue ?? options[0].value;
  return (
    <div
      className={cn('flex w-fit rounded-lg border border-green-800 bg-green-950 p-0.5', className)}
    >
      {options.map((option, i) => {
        const isFirst = i === 0;
        const selected = option.value === selectedOption;
        const isEvenOption = i % 2 === 0;
        const isLastOption = i === options.length - 1;

        return (
          <button
            key={i}
            type="button"
            onClick={() => onSelect?.(option.value)}
            className={cn('focus:outline-none', { '-ml-1': !isFirst, 'text-green-250': !selected })}
          >
            <Cell
              size="md"
              theme={selected ? 'green' : 'transparent'}
              leftCell={isFirst ? false : isEvenOption ? 'flip' : true}
              rightCell={isLastOption ? false : isEvenOption ? true : 'flip'}
              className={cn({ 'text-green-250': !selected })}
            >
              {option.icon}
            </Cell>
          </button>
        );
      })}
    </div>
  );
};
