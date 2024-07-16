import { ApiError, OpenAPI, ToolkitClient } from '../cohere-client';
import { ALERTS, DEPLOYMENT_COHERE_PLATFORM, ERRORS, PROMPTS } from '../constants';
import { SlackFile, getFileRawText } from '../utils/files';
import { getSlackFile } from '../utils/slackAuth';

type HandleSummarizeFileArgs = {
  file?: SlackFile;
  teamId?: string;
  enterpriseId?: string;
  deployment?: string | null;
  model?: string | null;
};

type Reply = {
  currentBotReply?: string;
  responseID?: string;
  errorMessage?: string;
};

export const handleSummarizeFile = async ({
  file,
  teamId,
  enterpriseId,
  deployment,
  model,
}: HandleSummarizeFileArgs): Promise<Reply> => {
  // This should never be triggered, but just in case
  if (!file || !file.url_private) {
    return {
      errorMessage: ERRORS.SUMMARIZE,
    };
  }

  const fileData = await getSlackFile(file.url_private, enterpriseId, teamId);

  let fileText = '';
  try {
    fileText = await getFileRawText(file, fileData);
  } catch (error) {
    console.error('handleSummarizeFile - unexpected error', error);
    return {
      errorMessage: ERRORS.INVALID_SUMMARIZE_FILE_TYPE,
    };
  }

  if (fileText.length < 500) {
    return {
      errorMessage: ERRORS.SUMMARIZE_CHAR_LIMIT,
    };
  }
  try {
    const toolkitClient = new ToolkitClient(OpenAPI);
    const summaryResponse = await toolkitClient.default.chatV1ChatPost({
      requestBody: {
        message: PROMPTS.summarizeFile(fileText),
        model: model,
      },
      deploymentName: deployment ? deployment : DEPLOYMENT_COHERE_PLATFORM,
    });
    const currentBotReply = `${ALERTS.FILE_SUMMARY_PREFIX}${
      file.name ? `\n\n*Original File Name:* \`${file.name}\`` : ''
    }\n\n${summaryResponse.text}`;

    return {
      currentBotReply,
      responseID: summaryResponse.response_id || undefined,
    };
  } catch (error) {
    console.error(error);
    if (error instanceof ApiError) {
      return { currentBotReply: '', responseID: '', errorMessage: error.message };
    }
    return { currentBotReply: '', responseID: '', errorMessage: ERRORS.SUMMARIZE };
  }
};
