import { Fieldset, Input } from '@headlessui/react';
import { useState } from 'react';

import { Icon } from '@/components/Shared/Icon';
import { STYLE_LEVEL_TO_CLASSES } from '@/components/Shared/Text';
import { cn } from '@/utils';

type Props = {
  value: string;
  placeholder?: string;
  className?: string;
  maxLength?: number;
  onChange: (value: string) => void;
};

export const InputSearch: React.FC<Props> = ({
  value,
  onChange,
  maxLength,
  className,
  placeholder,
}) => {
  const [isInputFocused, setIsInputFocused] = useState(false);

  const handleClear = () => {
    onChange('');
  };

  return (
    <Fieldset className="relative w-full">
      <Input
        type="text"
        onFocus={() => setIsInputFocused(true)}
        onBlur={() => setIsInputFocused(false)}
        placeholder={placeholder}
        value={value}
        maxLength={maxLength}
        onChange={(e) => onChange(e.target.value)}
        className={cn(
          'bg-volcanic-100 text-marble-950 placeholder:text-volcanic-700 focus:bg-volcanic-150',
          'rounded-lg border border-volcanic-500 py-[10px] pl-2 pr-8',
          'w-full outline-none',
          STYLE_LEVEL_TO_CLASSES.p,
          className
        )}
      />
      <button onClick={handleClear}>
        <Icon
          name="close"
          kind="outline"
          className={cn(
            'absolute right-2 top-1/2 -translate-y-1/2 transform text-marble-950 transition-colors duration-300 hover:text-marble-800',
            'rotate-0 scale-0 transition-all',
            { '-rotate-90 scale-100': value !== '' }
          )}
        />
        <Icon
          name="search"
          kind="outline"
          className={cn(
            'absolute right-2 top-1/2 -translate-y-1/2 transform text-volcanic-700',
            'rotate-90 scale-0 transition-all',
            {
              'rotate-0 scale-100': value === '',
              'text-volcanic-600': isInputFocused,
            }
          )}
        />
      </button>
    </Fieldset>
  );
};
