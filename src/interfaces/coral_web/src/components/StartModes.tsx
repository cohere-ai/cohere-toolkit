import { Transition } from '@headlessui/react';
import React, { useState } from 'react';

import { Icon, IconName, Tabs, Text } from '@/components/Shared';
import { useStartModes } from '@/hooks/startModes';
import { useParamsStore } from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';
import { cn } from '@/utils/cn';

export type PromptOption = { prompt: string; params: Partial<ConfigurableParams> };

type Props = {
  show: boolean;
  className?: string;
  onPromptSelected?: (option: PromptOption) => void;
};

/**
 * @description Renders start mode options and prompts for new conversations.
 */
export const StartModes: React.FC<Props> = ({ show, className = '', onPromptSelected }) => {
  const { modes, getSelectedModeIndex } = useStartModes();
  const { setParams } = useParamsStore();
  const [selectedMode, setSelectedMode] = useState(getSelectedModeIndex);

  const handleTabChange = (index: number) => {
    setSelectedMode(index);

    if (modes[index].params) {
      setParams(modes[index].params);
    }
    modes[index].onChange?.();
  };

  return (
    <Transition
      appear
      show={show}
      as="div"
      enter="transition-all duration-200 ease-out delay-200"
      enterFrom="opacity-0 translate-y-2"
      enterTo="opacity-100 translate-y-0"
      leave="transition-opacity duration-300 delay-100"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
      className={cn('flex flex-col items-center gap-y-6', className)}
    >
      <Text styleAs="h5" className="text-center">
        Choose an option to get started
      </Text>

      <div className={cn('w-full max-w-[820px]', 'rounded-lg border border-marble-400')}>
        <Tabs
          tabs={modes.map((m) => m.title)}
          selectedIndex={selectedMode}
          onChange={handleTabChange}
          panelsClassName="lg:pt-5 pt-5 pb-4"
          fitTabsContent={false}
          tabClassName="pt-1"
          tabGroupClassName="px-4"
        >
          {modes.map((m) => (
            <div key={m.title} className="flex flex-col gap-y-5">
              <Text>{m.description}</Text>
              <div className="flex flex-col gap-2.5 md:flex-row">
                {m.promptOptions.map((promptOption) => (
                  <PromptOptionButton
                    {...promptOption}
                    key={promptOption.title}
                    onClick={() => {
                      onPromptSelected?.({ prompt: promptOption.prompt, params: m.params });
                    }}
                  />
                ))}
              </div>
            </div>
          ))}
        </Tabs>
      </div>
    </Transition>
  );
};

type PromptOptionButtonProps = {
  title: string;
  description: React.ReactNode;
  icon: IconName;
  prompt: string;
  onClick: (prompt: string) => void;
};

const PromptOptionButton: React.FC<PromptOptionButtonProps> = ({
  title,
  description,
  icon,
  prompt,
  onClick,
}) => {
  return (
    <button
      className={cn(
        'flex w-full gap-2 rounded-md border border-marble-400 p-3 text-left md:flex-col md:p-4',
        'bg-marble-200 transition-colors ease-in-out hover:bg-marble-300'
      )}
      onClick={() => onClick(prompt)}
    >
      <div className="flex h-8 w-8 flex-none items-center justify-center rounded bg-secondary-500/25 text-secondary-600">
        <Icon name={icon} kind="outline" />
      </div>
      <div className="flex flex-grow flex-col gap-y-2">
        <Text as="span" styleAs="label" className="font-medium">
          {title}
        </Text>
        <Text>{description}</Text>
      </div>
    </button>
  );
};
