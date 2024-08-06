import { findLast } from 'lodash';

import { CustomHotKey } from '@/components/Shared/HotKeys';
import {
  CHAT_COMPOSER_TEXTAREA_ID,
  CONFIGURATION_FILE_UPLOAD_ID,
  SETTINGS_DRAWER_ID,
} from '@/constants';
import { useNavigateToNewChat } from '@/hooks/chatRoutes';
import { useConversationActions } from '@/hooks/conversation';
import { useNotify } from '@/hooks/toast';
import { useConversationStore, useFilesStore, useSettingsStore } from '@/stores';
import { MessageType, isFulfilledMessage } from '@/types/message';

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

export const useChatHotKeys = (): CustomHotKey[] => {
  const { isAgentsLeftPanelOpen, setAgentsLeftSidePanelOpen } = useSettingsStore();
  const {
    conversation: { id, messages },
  } = useConversationStore();
  const { deleteConversation } = useConversationActions();
  const { focusComposer } = useFocusComposer();
  const { error, info } = useNotify();
  const navigateToNewChat = useNavigateToNewChat();

  return [
    {
      name: 'Start a new conversation',
      commands: ['ctrl+shift+o', 'meta+shift+o'],
      action: navigateToNewChat,
    },
    {
      name: 'Delete current conversation',
      commands: ['ctrl+shift+backspace', 'meta+shift+backspace'],
      action: () => {
        if (!id) return;
        deleteConversation({ id });
      },
      options: {
        preventDefault: true,
      },
    },
    {
      name: 'Toggle left sidebar',
      commands: ['ctrl+shift+s', 'meta+shift+s'],
      action: () => {
        setAgentsLeftSidePanelOpen(!isAgentsLeftPanelOpen);
      },
      options: {
        preventDefault: true,
      },
    },
    {
      name: 'Focus on chat input',
      commands: ['shift+esc'],
      action: () => {
        focusComposer();
      },
    },
    {
      name: 'Copy last response',
      commands: ['ctrl+shift+c', 'meta+shift+c'],
      action: async () => {
        const lastBotMessage = findLast(messages, (message) => message.type === MessageType.BOT);
        if (!lastBotMessage) return;
        const lastBotMessageText = isFulfilledMessage(lastBotMessage)
          ? lastBotMessage.originalText
          : lastBotMessage.text;

        try {
          await window?.navigator?.clipboard.writeText(lastBotMessageText);
          info('Copied last response to clipboard');
        } catch (e) {
          error('Unable to copy last response');
        }
      },
      options: {
        preventDefault: true,
      },
    },
  ];
};
