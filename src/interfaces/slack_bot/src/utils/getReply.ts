import { AllMiddlewareArgs, AppMentionEvent, MessageEvent } from '@slack/bolt';

import { ApiError, CohereChatRequest, OpenAPI, Tool, ToolkitClient } from '../cohere-client';
import { DEPLOYMENT_COHERE_PLATFORM, ERRORS } from '../constants';
import { formatRagCitations } from './formatRagCitations';
import { getSanitizedMessage } from './getSanitizedMessage';
import { GetUsersRealNameArgs, getUsersRealName } from './getUsersRealName';

type GetReplyArgs = Pick<AllMiddlewareArgs, 'client'> & {
  event: MessageEvent | AppMentionEvent;
  tools?: Tool[];
  deployment?: string | null;
  model?: string | null;
  temperature?: number | null;
  preambleOverride?: string | null;
  conversationId: string | undefined;
  botUserId?: string;
  isFirstMessage?: boolean;
};

type Reply = {
  currentBotReply: string;
  responseID: string;
  errorMessage?: string;
};

/**
 * Fetches a reply using the /chat endpoint given a
 * slack event (that will contain the message text)
 */

export const getReply = async ({
  event,
  deployment,
  model,
  client,
  conversationId,
  botUserId,
  tools = [],
  temperature = null,
  preambleOverride = null,
  isFirstMessage = false,
}: GetReplyArgs): Promise<Reply> => {
  /**
   * Since we filter out edited messages in the message event listener,
   * and the property we're looking for is present in both MessageEvent and AppMentionEvent,
   * we can safely cast the event as AppMentionEvent
   */
  event = event as AppMentionEvent;
  const messageWithoutUsername = await getSanitizedMessage({
    message: event.text,
    getUsersRealName: async ({ userId }: GetUsersRealNameArgs) =>
      getUsersRealName({ userId, client }),
    botUserId,
    isFirstMessage,
  });

  const params: CohereChatRequest = {
    message: messageWithoutUsername,
    conversation_id: conversationId,
    prompt_truncation: 'AUTO_PRESERVE_ORDER',
  };

  if (model && model !== 'default') params.model = model;
  if (temperature) params.temperature = temperature;
  if (preambleOverride) params.preamble = preambleOverride;
  if (tools.length > 0) params.tools = tools;

  try {
    const toolkitClient = new ToolkitClient(OpenAPI);
    const chatResponse = await toolkitClient.default.chatV1ChatPost({
      requestBody: params,
      deploymentName: deployment ? deployment : DEPLOYMENT_COHERE_PLATFORM,
    });
    const sanitizedBotReply = await getSanitizedMessage({
      message: chatResponse.text,
      getUsersRealName: async ({ userId }: GetUsersRealNameArgs) =>
        getUsersRealName({ userId, client }),
    });

    const botReply = sanitizedBotReply + formatRagCitations(chatResponse);
    return { currentBotReply: botReply, responseID: chatResponse.generation_id || '' };
  } catch (error: any) {
    if (error instanceof ApiError) {
      return { currentBotReply: '', responseID: '', errorMessage: error.message };
    }
    return { currentBotReply: '', responseID: '', errorMessage: ERRORS.GENERAL };
  }
};
