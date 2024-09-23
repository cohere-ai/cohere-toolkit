import { IconName } from '@/components/UI';

/**
 * Tools
 */
export const TOOL_HYBRID_WEB_SEARCH_ID = 'hybrid_web_search';
export const TOOL_WEB_SEARCH_ID = 'web_search';
export const TOOL_SEARCH_FILE_ID = 'search_file';
export const TOOL_READ_DOCUMENT_ID = 'read_document';
export const TOOL_PYTHON_INTERPRETER_ID = 'toolkit_python_interpreter';
export const TOOL_WIKIPEDIA_ID = 'wikipedia';
export const TOOL_CALCULATOR_ID = 'toolkit_calculator';
export const TOOL_WEB_SCRAPE_ID = 'web_scrape';
export const TOOL_GOOGLE_DRIVE_ID = 'google_drive';
export const FILE_UPLOAD_TOOLS = [TOOL_SEARCH_FILE_ID, TOOL_READ_DOCUMENT_ID];
export const AGENT_SETTINGS_TOOLS = [
  TOOL_HYBRID_WEB_SEARCH_ID,
  TOOL_PYTHON_INTERPRETER_ID,
  TOOL_WEB_SCRAPE_ID,
];

export const TOOL_FALLBACK_ICON = 'circles-four';
export const TOOL_ID_TO_DISPLAY_INFO: { [id: string]: { icon: IconName } } = {
  [TOOL_WEB_SEARCH_ID]: { icon: 'web' },
  [TOOL_HYBRID_WEB_SEARCH_ID]: { icon: 'web' },
  [TOOL_WEB_SCRAPE_ID]: { icon: 'web' },
  [TOOL_PYTHON_INTERPRETER_ID]: { icon: 'code-simple' },
  [TOOL_CALCULATOR_ID]: { icon: 'calculator' },
  [TOOL_WIKIPEDIA_ID]: { icon: 'web' },
  [TOOL_SEARCH_FILE_ID]: { icon: 'search' },
  [TOOL_GOOGLE_DRIVE_ID]: { icon: 'google-drive' },
  [TOOL_READ_DOCUMENT_ID]: { icon: 'desktop' },
};
