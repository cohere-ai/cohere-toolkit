'use client';

import {
  CHAT_COMPOSER_TEXTAREA_ID,
  CONFIGURATION_FILE_UPLOAD_ID,
  SETTINGS_DRAWER_ID,
} from '@/constants';
import { useFilesStore } from '@/stores';

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
