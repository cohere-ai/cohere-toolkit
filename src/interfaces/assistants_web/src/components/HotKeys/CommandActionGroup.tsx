'use client';

import { CommandAction, type HotKeyGroupOption } from '@/components/HotKeys';
import { Text } from '@/components/UI';

type Props = {
  isOpen: boolean;
  options?: HotKeyGroupOption[];
};

export const CommandActionGroup: React.FC<Props> = ({ isOpen, options = [] }) => {
  return (
    <div className="flex flex-col gap-y-4">
      {options.map((action, i) => {
        if (action.quickActions.length === 0) {
          return null;
        }
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
                <CommandAction key={quickAction.name} isOpen={isOpen} hotkey={quickAction} />
              ))}
          </section>
        );
      })}
    </div>
  );
};
