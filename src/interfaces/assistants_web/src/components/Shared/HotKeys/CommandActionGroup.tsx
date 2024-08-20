'use client';

import { Text } from '@/components/Shared';
import { CommandAction } from '@/components/Shared/HotKeys/CommandAction';
import { type HotKeyGroupOption } from '@/components/Shared/HotKeys/domain';

type Props = {
  isOpen: boolean;
  options?: HotKeyGroupOption[];
};

const CommandActionGroup: React.FC<Props> = ({ isOpen, options = [] }) => {
  return (
    <div className="flex flex-col gap-y-4">
      {options.map((action, i) => {
        return (
          <section key={i} className="flex flex-col">
            {action.group && (
              <Text styleAs="p-sm" className="px-6 pb-4 uppercase dark:text-marble-800">
                {action.group}
              </Text>
            )}
            {action.quickActions.map((quickAction) => (
              <CommandAction key={quickAction.name} isOpen={isOpen} {...quickAction} />
            ))}
          </section>
        );
      })}
    </div>
  );
};

export default CommandActionGroup;
