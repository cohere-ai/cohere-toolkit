import { findLast } from 'lodash';
import { useTheme } from 'next-themes';
import { useRouter } from 'next/navigation';

import { ShareModal } from '@/components/ShareModal';
import { HotKeyGroupOption } from '@/components/Shared/HotKeys/domain';
import {
  CHAT_COMPOSER_TEXTAREA_ID,
  CONFIGURATION_FILE_UPLOAD_ID,
  SETTINGS_DRAWER_ID,
} from '@/constants';
import { useContextStore } from '@/context';
import { useChatRoutes, useNavigateToNewChat } from '@/hooks/chatRoutes';
import { useConversationActions } from '@/hooks/conversation';
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
      content: <ShareModal conversationId={id} />,
    });
  };

  return [
    {
      quickActions: [
        {
          name: 'New conversation',
          commands: ['ctrl+shift+o', 'meta+shift+o'],
          action: navigateToNewChat,
          options: {
            preventDefault: true,
          },
        },
        {
          name: 'Share conversation',
          commands: ['ctrl+alt+a', 'meta+alt+a'],
          action: handleOpenShareModal,
          options: {
            preventDefault: true,
          },
        },
        {
          name: 'Delete conversation',
          commands: ['ctrl+shift+backspace', 'meta+shift+backspace'],
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

export const useAssistantHotKeys = (): HotKeyGroupOption[] => {
  const router = useRouter();

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
          action: () => alert('implement me'),
          commands: ['ctrl+space+1-5', 'ctrl+space+1-5'],
          options: {
            preventDefault: true,
          },
        },
        {
          name: 'See all assistants',
          action: navigateToAssistants,
          commands: [],
        },
        {
          name: 'Create an assistant',
          action: navigateToNewAssistant,
          commands: [],
        },
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
          commands: [],
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
          commands: [],
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
