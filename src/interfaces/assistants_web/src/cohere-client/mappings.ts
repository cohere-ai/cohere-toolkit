import { DEFAULT_CHAT_TEMPERATURE } from './constants';
import { CohereChatRequest } from './generated';

export const mapToChatRequest = (request: CohereChatRequest): CohereChatRequest => {
  return {
    agent_id: request.agent_id,
    message: request.message,
    model: request.model,
    temperature: request.temperature ?? DEFAULT_CHAT_TEMPERATURE,
    conversation_id: request.conversation_id,
    documents: request.documents,
    tools: request.tools,
    file_ids: request.file_ids,
  };
};
