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
              <Text
                styleAs="p-sm"
                className="px-6 pb-4 font-medium uppercase text-volcanic-300 dark:text-volcanic-500"
              >
                {action.group}
              </Text>
            )}
            {action.quickActions
              .filter((quickAction) => quickAction.displayInDialog !== false)
              .map((quickAction) => (
                <CommandAction key={quickAction.name} isOpen={isOpen} {...quickAction} />
              ))}
          </section>
        );
      })}
    </div>
  );
};

export default CommandActionGroup;
