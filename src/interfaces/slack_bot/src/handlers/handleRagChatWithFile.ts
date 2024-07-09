import { WebClient } from '@slack/web-api';
import { formatRagCitations } from 'src/utils/formatRagCitations';

import { ApiError, OpenAPI, ToolkitClient } from '../cohere-client';
import { DEPLOYMENT_COHERE_PLATFORM, ERRORS } from '../constants';
import { PageText, SlackFile, getFileChunks } from '../utils/files';
import { getSanitizedMessage } from '../utils/getSanitizedMessage';
import { GetUsersRealNameArgs, getUsersRealName } from '../utils/getUsersRealName';
import { getSlackFile } from '../utils/slackAuth';

type HandleRagChatWithFile = {
  client: WebClient;
  file: SlackFile | undefined;
  text: string;
  deployment: string | null;
  model: string | null;
  teamId?: string;
  botUserId?: string;
  enterpriseId?: string;
  conversationId: string | undefined;
  isFirstMessage?: boolean;
};

type Reply = {
  currentBotReply?: string;
  responseID?: string;
  errorMessage?: string;
};

export const handleRagChatWithFile = async ({
  client,
  file,
  text,
  deployment,
  model,
  teamId,
  botUserId,
  enterpriseId,
  conversationId,
  isFirstMessage = false,
}: HandleRagChatWithFile): Promise<Reply> => {
  // This should never be triggered, but just in case
  if (!file || !file.url_private) {
    return {
      errorMessage: ERRORS.CHAT,
    };
  }

  const message = await getSanitizedMessage({
    message: text,
    getUsersRealName: async ({ userId }: GetUsersRealNameArgs) =>
      getUsersRealName({ userId, client }),
    botUserId,
    isFirstMessage,
  });

  const fileData = await getSlackFile(file.url_private, enterpriseId, teamId);

  let fileChunks: PageText[] = [];
  try {
    fileChunks = await getFileChunks(file, fileData);
  } catch (error) {
    return {
      errorMessage: `handleRagChatWithFile - unexpected error ${error}`,
    };
  }

  try {
    const documents = fileChunks.map((chunk, index) => {
      return {
        id: `${index}`,
        title: `page: ${chunk.pageNumber}`,
        text: chunk.text,
        url: `page: ${chunk.pageNumber}`,
      };
    });
    const toolkitClient = new ToolkitClient(OpenAPI);
    const chatResponse = await toolkitClient.default.chatV1ChatPost({
      requestBody: {
        message,
        model,
        documents,
        conversation_id: conversationId,
        temperature: 0.1,
        prompt_truncation: 'AUTO_PRESERVE_ORDER',
      },
      deploymentName: deployment ? deployment : DEPLOYMENT_COHERE_PLATFORM,
    });

    const sanitizedBotReply = await getSanitizedMessage({
      message: chatResponse.text,
      getUsersRealName: async ({ userId }: GetUsersRealNameArgs) =>
        getUsersRealName({ userId, client }),
    });

    const botReply = sanitizedBotReply + formatRagCitations(chatResponse);

    if (!chatResponse.generation_id) {
      return {
        currentBotReply: '',
        responseID: '',
        errorMessage: ERRORS.GENERAL,
      };
    }

    return { currentBotReply: botReply, responseID: chatResponse.generation_id };
  } catch (error: any) {
    console.error(error);
    if (error instanceof ApiError) {
      return {
        currentBotReply: '',
        responseID: '',
        errorMessage: error.message,
      };
    }
    return {
      currentBotReply: '',
      responseID: '',
      errorMessage: ERRORS.GENERAL,
    };
  }
};
