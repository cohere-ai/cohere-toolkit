// @todo: import from generated types when available
export enum FinishReason {
  FINISH_REASON_UNSPECIFIED = 'FINISH_REASON_UNSPECIFIED',
  FINISH_REASON_ERROR = 'FINISH_REASON_ERROR',
  FINISH_REASON_COMPLETE = 'FINISH_REASON_COMPLETE',
  FINISH_REASON_ERROR_TOXIC = 'FINISH_REASON_ERROR_TOXIC',
  FINISH_REASON_ERROR_LIMIT = 'FINISH_REASON_ERROR_LIMIT',
  FINISH_REASON_USER_CANCEL = 'FINISH_REASON_USER_CANCEL',
  FINISH_REASON_MAX_TOKENS = 'FINISH_REASON_MAX_TOKENS',
}

// Chat
export const COHERE_PLATFORM_DEPLOYMENT = 'Cohere Platform';
export const SAGEMAKER_DEPLOYMENT = 'SageMaker';
export const COHERE_PLATFORM_DEPLOYMENT_DEFAULT_CHAT_MODEL = 'command';
export const SAGEMAKER_DEPLOYMENT_DEFAULT_CHAT_MODEL = 'command-r';

export const DEFAULT_CHAT_TEMPERATURE = 0.3;
export const DEFAULT_CHAT_TOOL = 'Wikipedia';
export const FILE_TOOL_CATEGORY = 'File loader';

export const ERROR_FINISH_REASON_TO_MESSAGE = {
  [FinishReason.FINISH_REASON_ERROR]: 'An error occurred. Please try again.',
  [FinishReason.FINISH_REASON_ERROR_TOXIC]: 'Generation blocked by potential harmful output.',
  [FinishReason.FINISH_REASON_ERROR_LIMIT]: 'Generation stopped since context limit was reached.',
  [FinishReason.FINISH_REASON_MAX_TOKENS]: 'Generation stopped since max tokens limit was reached.',
};
