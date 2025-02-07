'use client';

import { ChangeEvent, useEffect } from 'react';

import { InputLabel, Text } from '@/components/UI';
import { cn } from '@/utils';

type Props = {
  label: string;
  min: number;
  max: number;
  step: number;
  value: number;
  onChange: (value: number) => void;
  sublabel?: string;
  className?: string;
  tooltipLabel?: React.ReactNode;
  formatValue?: (value: number) => string;
};

/**
 *
 * Renders a slider with a label, a minimum, maximum and step value, and optional subLabel and tooltip.
 * Styling for the thumb is located in main.css
 */
export const Slider: React.FC<Props> = ({
  label,
  sublabel,
  min,
  max,
  step,
  value,
  onChange,
  tooltipLabel,
  formatValue,
  className = '',
}) => {
  // if `max` is changed dynamically don't allow the value to surpass it
  useEffect(() => {
    if (value > max) onChange(Math.min(value, max));
  }, [max, onChange, value]);

  // if `min` is changed dynamically don't allow the value to go below it
  useEffect(() => {
    if (value < min) onChange(Math.max(value, min));
  }, [min, onChange, value]);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);

    onChange(value);
  };

  return (
    <div className={cn('flex flex-col space-y-4', className)}>
      <div className="flex w-full items-center justify-between">
        <InputLabel label={label} tooltipLabel={tooltipLabel} sublabel={sublabel} />
        <Text>{formatValue ? formatValue(value) : value}</Text>
      </div>
      <div className="flex items-center">
        <input
          type="range"
          value={value}
          max={max}
          min={min}
          step={step}
          onChange={handleChange}
          className={cn(
            'flex w-full cursor-pointer appearance-none items-center rounded-lg border outline-none active:cursor-grabbing',
            'focus-visible:outline focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-100'
          )}
        />
      </div>
    </div>
  );
};
