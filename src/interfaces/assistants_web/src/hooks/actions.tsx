import { useTheme } from 'next-themes';
import { usePathname, useRouter } from 'next/navigation';

import { AgentLogo } from '@/components/Agents/AgentLogo';
import { HotKeyGroupOption, SwitchAssistants } from '@/components/HotKeys';
import { ShareConversation } from '@/components/Modals/ShareConversation';
import {
  CHAT_COMPOSER_TEXTAREA_ID,
  CONFIGURATION_FILE_UPLOAD_ID,
  SETTINGS_DRAWER_ID,
} from '@/constants/setup';
import { useContextStore } from '@/context';
import { useChatRoutes, useNavigateToNewChat } from '@/hooks';
import { useRecentAgents } from '@/hooks';
import { useConversationActions } from '@/hooks';
import { useConversationStore, useFilesStore, useSettingsStore } from '@/stores';

export const useFocusComposer = () => {
  const focusComposer = () => {
    const chatInput = document.getElementById(CHAT_COMPOSER_TEXTAREA_ID) as HTMLTextAreaElement;
    if (!chatInput) return;

    chatInput.focus();
  };
  const blurComposer = () => {
    const chatInput = document.getElementById(CHAT_COMPOSER_TEXTAREA_ID) as HTMLTextAreaElement;
    if (!chatInput) return;
    chatInput.blur();
  };
  return { focusComposer, blurComposer };
};

/**
 * Focus actions for the drag & drop file input in the configuration panel
 */
export const useFocusFileInput = () => {
  const {
    files: { isFileInputQueuedToFocus },
    clearFocusFileInput: clearFocus,
  } = useFilesStore();

  const focusFileInput = () => {
    const fileInput = document.getElementById(CONFIGURATION_FILE_UPLOAD_ID) as HTMLInputElement;
    const settingsDrawer = document.getElementById(SETTINGS_DRAWER_ID) as HTMLElement;
    if (!fileInput || !settingsDrawer) return;

    const top = fileInput.getBoundingClientRect().top;
    settingsDrawer.scrollTo({ top, behavior: 'smooth' });
    clearFocus();
  };

  return { isFileInputQueuedToFocus, focusFileInput };
};

export const useConversationHotKeys = (): HotKeyGroupOption[] => {
  const {
    conversation: { id },
  } = useConversationStore();
  const { deleteConversation } = useConversationActions();
  const navigateToNewChat = useNavigateToNewChat();
  const { open } = useContextStore();

  if (!id)
    return [
      {
        quickActions: [
          {
            name: 'New conversation',
            commands: ['ctrl+shift+o', 'meta+shift+o'],
            registerGlobal: true,
            closeDialogOnRun: true,
            action: navigateToNewChat,
            options: {
              preventDefault: true,
            },
          },
        ],
      },
    ];

  const handleOpenShareModal = () => {
    if (!id) return;
    open({
      title: 'Share link to conversation',
      content: <ShareConversation conversationId={id} />,
    });
  };

  return [
    {
      quickActions: [
        {
          name: 'New conversation',
          commands: ['ctrl+shift+o', 'meta+shift+o'],
          registerGlobal: true,
          closeDialogOnRun: true,
          action: navigateToNewChat,
          options: {
            preventDefault: true,
          },
        },
        {
          name: 'Share conversation',
          commands: ['ctrl+alt+a', 'meta+alt+a'],
          registerGlobal: true,
          closeDialogOnRun: true,
          action: handleOpenShareModal,
          options: {
            preventDefault: true,
          },
        },
        {
          name: 'Delete conversation',
          commands: ['ctrl+shift+backspace', 'meta+shift+backspace'],
          registerGlobal: true,
          closeDialogOnRun: true,
          action: () => {
            if (!id) return;
            deleteConversation({ id });
          },
          options: {
            preventDefault: true,
          },
        },
      ],
    },
  ];
};

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
          customView: ({ close, onBack }) => <SwitchAssistants close={close} onBack={onBack} />,
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
                <span className="ml-2 rounded bg-volcanic-950 px-2 py-1 font-mono text-p-xs uppercase text-volcanic-300 dark:bg-volcanic-400 dark:text-marble-900">
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

export const useSettingsHotKeys = (): HotKeyGroupOption[] => {
  const { theme, setTheme } = useTheme();

  return [
    {
      group: 'Settings',
      quickActions: [
        {
          name: 'Set theme to Light',
          closeDialogOnRun: false,
          commands: [],
          registerGlobal: false,
          action: () => {
            if (theme === 'light') return;
            if (document.startViewTransition) {
              document.startViewTransition(() => setTheme('light'));
            } else {
              setTheme('light');
            }
          },
        },
        {
          name: 'Set theme to Dark',
          closeDialogOnRun: false,
          commands: [],
          registerGlobal: false,
          action: () => {
            if (theme === 'dark') return;
            if (document.startViewTransition) {
              document.startViewTransition(() => setTheme('dark'));
            } else {
              setTheme('dark');
            }
          },
        },
      ],
    },
  ];
};

export const useViewHotKeys = (): HotKeyGroupOption[] => {
  const { isLeftPanelOpen, setLeftPanelOpen } = useSettingsStore();
  return [
    {
      group: 'View',
      quickActions: [
        {
          name: 'Show or hide left sidebar',
          commands: ['ctrl+shift+s', 'meta+shift+s'],
          closeDialogOnRun: true,
          registerGlobal: true,
          action: () => {
            setLeftPanelOpen(!isLeftPanelOpen);
          },
          options: {
            preventDefault: true,
          },
        },
      ],
    },
  ];
};
