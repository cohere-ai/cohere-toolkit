import { AgentPublic } from '@/cohere-client';
import { FileAccept } from '@/components/UI';
import { DEPLOYMENT_COHERE_PLATFORM } from '@/constants/setup';
import {
  AGENT_SETTINGS_TOOLS,
  FILE_UPLOAD_TOOLS,
  TOOL_READ_DOCUMENT_ID,
  TOOL_SEARCH_FILE_ID,
  TOOL_WEB_SCRAPE_ID,
} from '@/constants/tools';

export const DEFAULT_CONVERSATION_NAME = 'New Conversation';
export const DEFAULT_AGENT_MODEL = 'command-r-plus';
export const DEFAULT_TYPING_VELOCITY = 35;
export const CONVERSATION_HISTORY_OFFSET = 100;

export const DEFAULT_PREAMBLE =
  "## Task And Context\nYou help people answer their questions and other requests interactively. You will be asked a very wide array of requests on all kinds of topics. You will be equipped with a wide range of search engines or similar tools to help you, which you use to research your answer. You should focus on serving the user's needs as best you can, which will be wide-ranging.\n\n## Style Guide\nUnless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling.";

export const DEFAULT_AGENT_TOOLS = [TOOL_SEARCH_FILE_ID, TOOL_READ_DOCUMENT_ID, TOOL_WEB_SCRAPE_ID];

export const BASE_AGENT: AgentPublic = {
  id: '',
  deployments: [],
  name: 'Command R+',
  description: 'Ask questions and get answers based on your files.',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  preamble: '',
  version: 1,
  temperature: 0.3,
  tools: [...AGENT_SETTINGS_TOOLS, ...FILE_UPLOAD_TOOLS],
  model: DEFAULT_AGENT_MODEL,
  deployment: DEPLOYMENT_COHERE_PLATFORM,
  user_id: '',
  is_private: false,
};

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
  'application/vnd.apache.parquet',
];
export const MAX_NUM_FILES_PER_UPLOAD_BATCH = 50;
