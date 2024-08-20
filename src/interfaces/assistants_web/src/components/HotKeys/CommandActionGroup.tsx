'use client';

import { Text } from '@/components/Shared';
import { CommandAction } from '@/components/Shared/HotKeys/CommandAction';
import { type HotKeyGroupOption } from '@/components/Shared/HotKeys/domain';

type Props = {
  isOpen: boolean;
  options?: HotKeyGroupOption[];
};

const CommandActionGroup: React.FC<Props> = ({ isOpen, options = [] }) => {
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

export default CommandActionGroup;
