import { Field } from '@headlessui/react';
import { useRef, useState } from 'react';

import { Icon } from '@/components/Shared/Icon';
import { STYLE_LEVEL_TO_CLASSES } from '@/components/Shared/Text';
import { cn } from '@/utils';

type Props = Omit<React.HTMLProps<HTMLInputElement>, 'onChange' | 'value'> & {
  value: string;
  onChange: (value: string) => void;
};

export const InputSearch: React.FC<Props> = ({ value, onChange, className, ...rest }) => {
  const [isInputFocused, setIsInputFocused] = useState(false);
  const searchChatHistoryRef = useRef<HTMLInputElement>(null);

  const handleClear = () => {
    onChange('');
  };
  const handleFocus = () => {
    !!searchChatHistoryRef.current && searchChatHistoryRef.current.focus();
  };

  const iconStyles = cn(
    'absolute right-2 top-1/2 -translate-y-1/2',
    'transform transition-all scale-0',
    'fill-volcanic-600',
    {
      'fill-volcanic-700': isInputFocused,
    }
  );

  return (
    <Field className={cn('relative w-full', className)}>
      <input
        ref={searchChatHistoryRef}
        type="text"
        onFocus={() => setIsInputFocused(true)}
        onBlur={() => setIsInputFocused(false)}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={cn(
          'bg-white placeholder:text-volcanic-700 dark:bg-volcanic-100 dark:focus:bg-volcanic-150',
          'rounded-lg border border-volcanic-800 py-[10px] pl-2 pr-8',
          'w-full outline-none',
          STYLE_LEVEL_TO_CLASSES.p
        )}
        {...rest}
      />
      <button onClick={!value ? handleFocus : handleClear} className="outline-none">
        <Icon
          name="search"
          kind="outline"
          className={cn(iconStyles, 'rotate-90', {
            'rotate-0 scale-100': value === '',
          })}
        />
        <Icon
          name="close"
          className={cn(iconStyles, 'rotate-0 duration-300', {
            '-rotate-90 scale-100': value !== '',
          })}
        />
      </button>
    </Field>
  );
};
