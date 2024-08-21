'use client';

import { CommandAction, type HotKeyGroupOption } from '@/components/HotKeys';
import { Text } from '@/components/UI';

type Props = {
  isOpen: boolean;
  options?: HotKeyGroupOption[];
};

export const CommandActionGroup: React.FC<Props> = ({ isOpen, options = [] }) => {
  return options.map((action) => {
    return (
      <section key={action.group}>
        <Text styleAs="p-sm" className="mx-3 p-4 uppercase dark:text-marble-800">
          {action.group}
        </Text>
        {action.quickActions.map((quickAction) => (
          <CommandAction key={quickAction.name} isOpen={isOpen} {...quickAction} />
        ))}
      </section>
    );
  });
};
