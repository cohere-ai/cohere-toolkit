import type { StaticImport } from 'next/dist/shared/lib/get-img-props';

import GoogleDriveIconSVG from '@/assets/svg/google-drive-icon.svg';
import { IconName } from '@/components/Shared';
import { FileAccept } from '@/components/Shared/DragDropFileInput';

export const DEFAULT_CONVERSATION_NAME = 'New Conversation';
export const DEFAULT_TYPING_VELOCITY = 35;

export const DEPLOYMENT_COHERE_PLATFORM = 'Cohere Platform';
export const DEPLOYMENT_SINGLE_CONTAINER = 'Single Container';
export const DEFAULT_AGENT_MODEL = 'command-r-plus';
export const DEFAULT_PREAMBLE =
  "## Task And Context\nYou help people answer their questions and other requests interactively. You will be asked a very wide array of requests on all kinds of topics. You will be equipped with a wide range of search engines or similar tools to help you, which you use to research your answer. You should focus on serving the user's needs as best you can, which will be wide-ranging.\n\n## Style Guide\nUnless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling.";

export const ACCEPTED_FILE_TYPES: FileAccept[] = [
  'text/csv',
  'text/plain',
  'text/html',
  'text/markdown',
  'text/tab-separated-values',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'application/json',
  'application/pdf',
  'application/epub+zip',
];
export const MAX_NUM_FILES_PER_UPLOAD_BATCH = 50;

/**
 * Special HTML ids and CSS classes
 */
// Classes used to identify certain elements
export enum ReservedClasses {
  MESSAGES = 'messages',
  CITATION_PANEL = 'side-panel',
  MESSAGE = 'message',
  CITATION = 'citation',
}
export const CHAT_COMPOSER_TEXTAREA_ID = 'composer';
export const CONFIGURATION_FILE_UPLOAD_ID = 'file-upload';
export const SETTINGS_DRAWER_ID = 'settings';

/**
 * Local Storage
 */
export const LOCAL_STORAGE_KEYS = {
  welcomeGuideState: 'onboarding/welcome/onboardState',
  welcomeGuideInfoBox: 'onboarding/welcome/infoBox',
  recentAgents: 'recentAgents',
  unauthedToolsModalDismissed: 'tools/unauthedModal/dismissed',
};

/**
 * Cookies
 */
export const COOKIE_KEYS = {
  authToken: 'authToken',
};

/**
 * Tools
 */
export const TOOL_WEB_SEARCH_ID = 'web_search';
export const TOOL_PYTHON_INTERPRETER_ID = 'toolkit_python_interpreter';
export const TOOL_CALCULATOR_ID = 'toolkit_calculator';
export const TOOL_WIKIPEDIA_ID = 'wikipedia';
export const TOOL_SEARCH_FILE_ID = 'search_file';
export const TOOL_READ_DOCUMENT_ID = 'read_document';
export const TOOL_GOOGLE_DRIVE_ID = 'google_drive';

export const TOOL_FALLBACK_ICON = 'circles-four';
export const TOOL_ID_TO_DISPLAY_INFO: { [id: string]: { icon: IconName } } = {
  [TOOL_WEB_SEARCH_ID]: { icon: 'search' },
  [TOOL_PYTHON_INTERPRETER_ID]: { icon: 'code' },
  [TOOL_CALCULATOR_ID]: { icon: 'calculator' },
  [TOOL_WIKIPEDIA_ID]: { icon: 'web' },
  [TOOL_SEARCH_FILE_ID]: { icon: 'search' },
};
export const TOOL_ID_TO_ICON: { [id: string]: StaticImport } = {
  [TOOL_GOOGLE_DRIVE_ID]: GoogleDriveIconSVG,
};

export const MAX_TIMEOUT_PREFETCH = 5000;
export const DEFAULT_AGENT_TOOLS = [TOOL_SEARCH_FILE_ID, TOOL_READ_DOCUMENT_ID];
