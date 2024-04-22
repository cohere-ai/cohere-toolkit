import { Switch as HUSwitch } from '@headlessui/react';

import { Text } from '@/components/Shared';
import { cn } from '@/utils';

type Props = {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: React.ReactNode;
  labelPosition?: 'left' | 'right';
  name?: string;
  styleAs?: 'label' | 'p';
  displayChecked?: boolean;
  className?: string;
  dataTestId?: string;
};

export const Switch: React.FC<Props> = ({
  checked,
  onChange,
  label,
  labelPosition = 'right',
  name,
  displayChecked,
  styleAs = 'label',
  className = '',
  dataTestId,
}) => {
  return (
    <div className="group flex items-center">
      {displayChecked && <Text className="w-8">{checked ? 'On' : 'Off'}</Text>}
      <HUSwitch.Group>
        <div
          className={cn(
            'flex items-center justify-end gap-6',
            {
              'flex-row-reverse': labelPosition === 'right',
            },
            className
          )}
        >
          <HUSwitch.Label>
            {typeof label === 'string' ? <Text styleAs={styleAs}>{label}</Text> : label}
          </HUSwitch.Label>
          <HUSwitch
            name={name}
            checked={checked}
            onChange={onChange}
            className={cn(
              'relative inline-flex h-5 w-10 shrink-0 cursor-pointer rounded border-2 border-transparent',
              'transition-colors duration-200 ease-in-out',
              'focus-visible:outline focus-visible:outline-offset-4 focus-visible:outline-volcanic-900',
              'bg-primary-500 group-hover:bg-primary-400',
              {
                'bg-secondary-100 group-hover:bg-secondary-200': !checked,
              }
            )}
            data-testid={dataTestId}
          >
            <span
              aria-hidden="true"
              className={cn(
                'pointer-events-none inline-block h-4 w-5 rounded bg-white shadow-lg',
                'transform transition duration-200 ease-in-out',
                {
                  'translate-x-4': checked,
                  'translate-x-0': !checked,
                  'flex items-center': displayChecked,
                }
              )}
            ></span>
          </HUSwitch>
        </div>
      </HUSwitch.Group>
    </div>
  );
};
