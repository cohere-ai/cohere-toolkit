// @todo: import from generated types when available
export enum FinishReason {
  ERROR = 'ERROR',
  COMPLETE = 'COMPLETE',
  MAX_TOKENS = 'MAX_TOKENS',
}

// Chat
export const COHERE_PLATFORM_DEPLOYMENT = 'Cohere Platform';
export const SAGEMAKER_DEPLOYMENT = 'SageMaker';
export const COHERE_PLATFORM_DEPLOYMENT_DEFAULT_CHAT_MODEL = 'command';
export const SAGEMAKER_DEPLOYMENT_DEFAULT_CHAT_MODEL = 'command-r';

export const DEFAULT_CHAT_TEMPERATURE = 0.3;
export const DEFAULT_CHAT_TOOL = 'Wikipedia';
export const FILE_TOOL_CATEGORY = 'File loader';
