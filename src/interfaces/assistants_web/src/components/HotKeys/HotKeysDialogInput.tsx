import { ComboboxInput } from '@headlessui/react';

import { Icon, Input, Text } from '@/components/UI';

type Props = {
  value: string;
  readOnly?: boolean;
  placeholder?: string;
  isSearch?: boolean;
  onBack?: VoidFunction;
  setValue?: (query: string) => void;
  close: VoidFunction;
};

export const HotKeysDialogInput: React.FC<Props> = ({
  value,
  setValue,
  close,
  isSearch,
  readOnly,
  onBack,
  placeholder,
}) => {
  return (
    <div className="mx-6 mb-3 mt-6">
      <span className="flex items-center gap-x-2 [&>div]:flex-grow">
        {onBack && !isSearch && (
          <button onClick={onBack}>
            <Icon name="arrow-left" />
          </button>
        )}
        {isSearch && (
          <Text styleAs="p-sm" className="w-fit rounded-lg bg-volcanic-900 p-2 dark:bg-volcanic-60">
            $
          </Text>
        )}
        <ComboboxInput
          as={Input}
          autoComplete="off"
          placeholder={placeholder}
          value={value}
          onChange={(event) => setValue?.(event.target.value)}
          onKeyDown={(event: React.KeyboardEvent<HTMLInputElement>) => {
            if (event.key === 'Escape') {
              close();
            }
            if ((event.key === 'Backspace' || event.key === 'Delete') && (!value || readOnly)) {
              onBack?.();
            }
          }}
          readOnly={readOnly}
          autoFocus
          className="w-full flex-grow border-none bg-transparent py-0 text-p-lg focus:bg-transparent dark:bg-transparent dark:focus:bg-transparent"
        />
      </span>
      <hr className="mt-6 border-t border-volcanic-800 dark:border-volcanic-400" />
    </div>
  );
};
