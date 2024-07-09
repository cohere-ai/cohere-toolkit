import { Action } from './utils/actions';

export const COMMAND_SUFFIX = process.env.COMMAND_SUFFIX || '';

// todo: change to follow the format of the other envs above
export const DEFAULT_CHAT_TEMPERATURE = 0.3;

export const PENDING_MESSAGES: { [key in Action['type']]: string } = {
  chat: '_Typing..._',
  'file-invalid': '_Typing..._',
  'file-summarize': '_Summarizing file..._',
  'file-rag': '_Reading file..._',
  'chat-rag': '_Deep diving..._',
  ignore: 'Unsupported action',
};
export const ALERTS = {
  THREAD_SUMMARY_PREFIX: `*:page_facing_up: Here's a summary of the thread:*`,
  FILE_SUMMARY_PREFIX: `*:page_facing_up: Here's a summary of the file:*`,
  RAG_SOURCES_PREFIX: '*Sources:*',
  MODEL_NOT_IN_DM:
    'The `/set-model` command can only be used in a DM conversation between you and Command.',
  SUMMARIZE_COMMAND_REGISTERED: 'Working on a summary! :memo:',
  SHORTCUT_NOT_IN_THREAD: 'This shortcut can only be used in threads.',
  NOT_SLACK_THREAD_LINK:
    `Whoops, that doesn't appear to be a slack thread link. Check out the guide below to learn how to copy thread links: ` +
    `<https://slack.com/help/articles/203274767-Forward-messages-in-Slack#copy-a-link-to-a-message|Copy a link to a message>`,
  TYPING: '_Typing..._',
  MODEL_PREFIX: '*Model:*',
  NOT_ADMIN: `Sorry, Command can only be set up by a workspace admin. If you would like to set up Command, please contact them.`,
  channelModelSet: (channelName: string, modelName: string | null, userId?: string) =>
    `All messages ${
      channelName !== 'directmessage' ? `in ${channelName} ` : ''
    }will now be processed with the \`${modelName ? modelName : 'default'}\` model.${
      userId ? ` Set by <@${userId}>.` : ''
    }`,
  channelDeploymentSet: (channelName: string, deploymentName: string | null, userId?: string) =>
    `All messages ${
      channelName !== 'directmessage' ? `in ${channelName} ` : ''
    }will now be processed with the \`${deploymentName ? deploymentName : DEPLOYMENT_COHERE_PLATFORM}\` model deployment.${
      userId ? ` Set by <@${userId}>.` : ''
    }`,
  channelDeploymentView: (channelName: string, deploymentName: string | null) =>
    `All messages ${
      channelName !== 'directmessage' ? `in ${channelName} ` : ''
    }are currently being processed with the \`${deploymentName ? deploymentName : DEPLOYMENT_COHERE_PLATFORM}\` deployment.`,
  channelModelView: (channelName: string, modelName: string | null) =>
    `All messages ${
      channelName !== 'directmessage' ? `in ${channelName} ` : ''
    }are currently being processed with the \`${modelName ? modelName : 'default'}\` model.`,
  PROMPT_TOO_LONG:
    'Due to the length of your prompt, some information may be left out. Reducing your prompt to below 4000 characters may produce better results.',
  channelTemperatureSet: (channelName: string, temperature: number, userId?: string) =>
    `All messages ${
      channelName !== 'directmessage' ? `in ${channelName} ` : ''
    }will now be processed with a temperature of \`${temperature}\`.${
      userId ? ` Set by <@${userId}>.` : ''
    }`,
  channelTemperatureView: (channelName: string, temperature: number) =>
    `All messages ${
      channelName !== 'directmessage' ? `in ${channelName} ` : ''
    }are currently being processed with a temperature of \`${temperature}\`.`,
  channelPreambleOverrideSet: (
    channelName: string,
    preambleOverride: string | null,
    userId?: string,
  ) =>
    `All messages ${
      channelName !== 'directmessage' ? `in ${channelName} ` : ''
    }will now be processed with the following preamble override:\n\`\`\`\n${
      preambleOverride || '<Default Preamble>'
    }\n\`\`\`\n${userId ? `Set by <@${userId}>.` : ''}`,
  channelPreambleOverrideView: (channelName: string, preambleOverride: string | null) =>
    `All messages ${
      channelName !== 'directmessage' ? `in ${channelName} ` : ''
    }are currently being processed with the following preamble override:\n\`\`\`\n${
      preambleOverride || '<Default Preamble>'
    }\n\`\`\``,
  installMessage: (type: 'create' | 'update') =>
    type === 'create'
      ? `Hi! Thank's for having me here!` +
        `\nIf you're an admin/owner, you can get me setup for the Slack workspace using the \`/setup-command\` command.` +
        ` If you're not an admin — please ping an admin/owner to let them know!`
      : `Hi! Let's get a conversation going! Tag me in a message using \`@Command\` to get started!` +
        `\nTo learn more about me, use the \`/command-help\` command.`,
};
export const MAX_PROMPT_LENGTH = 4000;
export const PROMPTS = {
  summarizeFile: (fileText: string) =>
    `Summarize the following text extracted from a file:\n${fileText}`,
  summarizeThread: (conversationHistory: string) =>
    `Summarize the following conversation history:\n${conversationHistory}`,
};
export const ERRORS = {
  PREFIX: 'Whoops,',
  GENERAL: 'There was an error. Please try again.',
  CHAT: 'There was an error getting a reply. Please adjust your prompt according to our <https://docs.cohere.com/docs/usage-guidelines|Usage Guidelines> and try again.',
  SUMMARIZE: 'There was an error getting your summary. Please try again.',
  SUMMARIZE_CHAR_LIMIT:
    ":confused: There's not enough conversation history to summarize. Please provide more than 500 characters.",
  INVALID_SUMMARIZE_FILE_TYPE: `Sorry, I can't summarize that file type. I can summarize PDFs, Word documents (doc and docx), and text files.`,
  INVALID_RAG_CHAT_FILE_TYPE: `Sorry, I can't read that file type. Currently I can only read PDFs.`,
  INVALID_TEMPERATURE:
    'The value you provided is not a valid temperature (0.0-5.0). Please try again.',
  USER_NOT_IN_CHANNEL:
    'Looks like the conversation linked is from a private channel. Summaries can only be generated for public channels or private channels you are a member of.',
};
export const SLACK_API_ERRORS: { [key: string]: string } = {
  not_in_channel:
    "Looks like I'm not in the channel you specified. Please invite me to the channel and try again.",
  channel_not_found:
    "Looks like I cannot find the channel you specified. If it's a private channel, please invite me to the channel and try again.",
  thread_not_found: 'Oops, I cannot find the thread you specified.',
  access_denied: 'Sorry, I do not have the required access permissions.',
};
export const STOP_REPLYING_MESSAGE = 'I will stop responding :speak_no_evil:';
export const HELP_MESSAGE = `Hi! I'm Command, Cohere's conversational AI in Slack! :wave:

You can chat with me to learn new subjects through open and engaging conversations. You can also summarize a thread that you missed out on with a built in shortcut.


\`\`\`Slash Commands\`\`\`

*:orange_book: Feature and help commands*:

\`/command-help\` - Show this help message
\`/summarize [thread link]\` - Post a summary of a slack thread given a link

*:gear: Configuration commands*:

\`/set-model [model name]\` - Set the model used for a specific channel
\`/set-deployment [deployment name]\` - Set the deployment used for a specific channel
\`/view-deployment\` - View the deployment used for a specific channel
\`/view-model\` - View the model used for a specific channel
\`/set-temperature [0.0 - 5.0]\` - Set the temperature used for a specific channel
\`/view-temperature\` - View the temperature used for a specific channel
\`/set-preamble [preamble]\` - Set the preamble override used for a specific channel
\`/view-preamble\` - View the preamble override used for a specific channel
\`/set-tools\` - Set tools for a specific channel
\`/view-tools [all]\` - View all tools available in your Cohere account or tools enabled for a specific channel
\`/setup-command\` - _Admins only_ - Setup Command for the workspace


\`\`\`Context Menu Options\`\`\`
\`Summarize thread\` - Post a summary of a thread with one simple click


*:question: What does that reaction mean?*

:shushing_face: - To indicate Command should stop responding in the current thread.
:warning: - An error occurred while processing the specific message that has this reaction. The message sender will be provided with more information regarding the error in an ephemeral message.


For further support, feel free to reach out to <mailto:support@cohere.com?Subject=Command%20Slackbot%20Support|support@cohere.com>.
`;

export const ACCEPTABLE_SUMMARIZE_FILE_TYPES = new Set(['pdf', 'doc', 'docx', 'text']);
export const ACCEPTABLE_RAG_CHAT_FILE_TYPES = new Set(['pdf']);

export const DEPLOYMENT_COHERE_PLATFORM = 'Cohere Platform';
