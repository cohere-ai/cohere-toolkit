import { Field } from '@headlessui/react';
import { useState } from 'react';

import { Icon } from '@/components/Shared/Icon';
import { STYLE_LEVEL_TO_CLASSES } from '@/components/Shared/Text';
import { cn } from '@/utils';

type Props = Omit<React.HTMLProps<HTMLInputElement>, 'onChange' | 'value'> & {
  value: string;
  onChange: (value: string) => void;
};

export const InputSearch: React.FC<Props> = ({ value, onChange, className, ...rest }) => {
  const [isInputFocused, setIsInputFocused] = useState(false);

  const handleClear = () => {
    onChange('');
  };

  return (
    <Field className={cn('relative w-full', className)}>
      <input
        type="text"
        onFocus={() => setIsInputFocused(true)}
        onBlur={() => setIsInputFocused(false)}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={cn(
          'bg-white placeholder:text-volcanic-700 dark:bg-volcanic-100 dark:focus:bg-volcanic-150',
          'rounded-lg border border-volcanic-500 py-[10px] pl-2 pr-8',
          'w-full outline-none',
          STYLE_LEVEL_TO_CLASSES.p
        )}
        {...rest}
      />
      <button onClick={handleClear} className="outline-none">
        <Icon
          name="close"
          kind="outline"
          className={cn(
            'absolute right-2 top-1/2 -translate-y-1/2 transform transition-colors duration-300 hover:text-marble-800',
            'rotate-0 scale-0 transition-all',
            { '-rotate-90 scale-100': value !== '' }
          )}
        />
        <Icon
          name="search"
          kind="outline"
          className={cn(
            'absolute right-2 top-1/2 -translate-y-1/2 transform dark:text-volcanic-700',
            'rotate-90 scale-0 transition-all',
            {
              'rotate-0 scale-100': value === '',
              'dark:text-volcanic-600': isInputFocused,
            }
          )}
        />
      </button>
    </Field>
  );
};
