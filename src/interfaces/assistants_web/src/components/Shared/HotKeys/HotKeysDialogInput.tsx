import { ComboboxInput } from '@headlessui/react';

import { Icon } from '@/components/Shared/Icon';
import { Input } from '@/components/Shared/Input';

type Props = {
  value: string;
  setValue?: (query: string) => void;
  close: VoidFunction;
  onBack?: VoidFunction;
  readOnly?: boolean;
  placeholder?: string;
};

export const HotKeysDialogInput: React.FC<Props> = ({
  value,
  setValue,
  close,
  readOnly,
  onBack,
}) => {
  return (
    <div className="mx-6 mb-3 mt-6 ">
      <span className="flex items-center gap-x-2">
        {onBack && (
          <button onClick={onBack}>
            <Icon name="arrow-left" />
          </button>
        )}
        <ComboboxInput
          as={Input}
          autoComplete="off"
          placeholder="Find a command."
          value={value}
          onChange={(event) => setValue?.(event.target.value)}
          onKeyDown={(event: React.KeyboardEvent<HTMLInputElement>) => {
            if (event.key === 'Escape') {
              close();
            }
            if (event.key === 'Backspace' || event.key === 'Delete') {
              onBack?.();
            }
          }}
          readOnly={readOnly}
          autoFocus
          className="border-none bg-transparent py-0 text-p-lg focus:bg-transparent dark:bg-transparent dark:focus:bg-transparent"
        />
      </span>
      <hr className="mt-6 border-t border-volcanic-800 dark:border-volcanic-400" />
    </div>
  );
};
