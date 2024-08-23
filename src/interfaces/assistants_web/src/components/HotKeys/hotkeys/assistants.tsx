'use client';

import { usePathname, useRouter } from 'next/navigation';

import { AgentLogo } from '@/components/Agents/AgentLogo';
import { SwitchAssistants } from '@/components/HotKeys/custom-views/SwitchAssistants';
import { HotKeyGroupOption } from '@/components/HotKeys/domain';
import { useChatRoutes, useRecentAgents } from '@/hooks';

export const useAssistantHotKeys = ({
  displayRecentAgentsInDialog,
}: {
  displayRecentAgentsInDialog: boolean;
}): HotKeyGroupOption[] => {
  const router = useRouter();
  const pathname = usePathname();
  const recentAgents = useRecentAgents(5);
  const { agentId } = useChatRoutes();

  const navigateToAssistants = () => {
    router.push('/discover');
  };

  const navigateToNewAssistant = () => {
    router.push('/new');
  };

  return [
    {
      group: 'Assistants',
      quickActions: [
        {
          name: 'Switch assistants',
          commands: ['ctrl+space+1-5', 'ctrl+space+1-5'],
          displayInDialog: !displayRecentAgentsInDialog,
          customView: ({ isOpen, close, onBack }) => (
            <SwitchAssistants isOpen={isOpen} close={close} onBack={onBack} />
          ),
          closeDialogOnRun: false,
          registerGlobal: false,
          options: {
            preventDefault: true,
          },
        },
        {
          name: 'See all assistants',
          action: navigateToAssistants,
          closeDialogOnRun: true,
          commands: [],
          displayInDialog: !displayRecentAgentsInDialog,
          registerGlobal: false,
        },
        {
          name: 'Create an assistant',
          action: navigateToNewAssistant,
          closeDialogOnRun: true,
          displayInDialog: !displayRecentAgentsInDialog,
          commands: [],
          registerGlobal: false,
        },
        ...recentAgents.map((agent, index) => ({
          name: agent.name,
          displayInDialog: displayRecentAgentsInDialog,
          label: (
            <div className="flex gap-x-2">
              <AgentLogo agent={agent} />
              {agent.name}
              {(agentId === agent.id || (!agent.id && pathname === '/')) && (
                <span className="ml-2 rounded bg-mushroom-800 px-2 py-1 font-mono text-p-xs uppercase text-volcanic-300 dark:bg-volcanic-400 dark:text-marble-900">
                  Selected
                </span>
              )}
            </div>
          ),
          action: () => {
            if (!agent.id) {
              router.push('/');
            } else {
              router.push(`/a/${agent.id}`);
            }
          },
          closeDialogOnRun: true,
          commands: [`ctrl+space+${index + 1}`, `ctrl+space+${index + 1}`],
          registerGlobal: true,
          options: {
            preventDefault: true,
          },
        })),
      ],
    },
  ];
};
