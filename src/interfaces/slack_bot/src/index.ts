import { Prisma, PrismaClient } from '@prisma/client';
import * as Sentry from '@sentry/node';
import { App, AppOptions, Installation } from '@slack/bolt';
import { ExtendedErrorHandler } from '@slack/bolt/dist/App';
import * as dotenv from 'dotenv';

import { OpenAPI } from './cohere-client/';
import {
  commandHelp,
  setDeployment,
  setModel,
  setPreamble,
  setTemperature,
  setTools,
  setupCommand,
  summarize,
  viewDeployment,
  viewModel,
  viewPreamble,
  viewTemperature,
  viewTools,
} from './commands';
import { ALERTS, COMMAND_SUFFIX } from './constants';
import { handleFirstReply, handleThreadReply } from './handlers';
import { dismissEphemeral, stopConversation } from './reactions';
import { summarizeThread } from './shortcuts';
import { determineAction, isAppMentionEvent } from './utils/actions';
import { extractMessageHistory } from './utils/messageHistory';
import { apiView, toolsView } from './views';

export let prisma: PrismaClient;

/**
 * Due to some issues with Bolt and TS, there will be some need of 'any' typecasting.
 * Still using typescript as Bolt might improve TS support down the line.
 * ref for errs: https://github.com/slackapi/bolt-js/issues/904
 */

if (process.env.NODE_ENV === 'development') {
  console.log(`Loading environment variables from .env`);
  dotenv.config({ path: '.env' });
}

if (!process.env.SLACK_CONNECTION_MODE) {
  throw new Error(
    'Error: SLACK_CONNECTION_MODE is not set. It must be set to either "socket" or "http".',
  );
}

if (!process.env.SLACK_SIGNING_SECRET) {
  throw new Error('Error: SLACK_SIGNING_SECRET is not set');
}

if (!process.env.DATABASE_URL) {
  throw new Error('Error: DATABASE_URL is not set.');
}

if (process.env.SLACK_CONNECTION_MODE === 'socket') {
  if (!process.env.SLACK_BOT_TOKEN) {
    throw new Error('Error: SLACK_BOT_TOKEN is not set. It is required in socket mode.');
  }
  if (!process.env.SLACK_APP_TOKEN) {
    throw new Error('Error: SLACK_APP_TOKEN is not set. It is required in socket mode.');
  }
} else {
  if (!process.env.SLACK_CLIENT_ID) {
    throw new Error('Error: SLACK_CLIENT_ID is not set. It is required in http mode.');
  }
  if (!process.env.SLACK_CLIENT_SECRET) {
    throw new Error('Error: SLACK_CLIENT_SECRET is not set. It is required in http mode.');
  }
  if (!process.env.SLACK_STATE_SECRET) {
    throw new Error('Error: SLACK_STATE_SECRET is not set. It is required in http mode.');
  }
  if (!process.env.SLACK_INSTALL_PASSWORD) {
    console.warn(`SLACK_INSTALL_PASSWORD is not set. Slack app is open for public installations.`);
  }
}

/**
 * Instantiate Prisma Client.
 */
prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
});

/**
 * Enable Sentry error monitoring when DSN key is in env. This is not required for development.
 */
if (process.env.SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    tracesSampleRate: 1.0,
  });
}

/**
 * Error handling
 * See https://github.com/slackapi/bolt-js/blob/9e0b8ac8507000118ddc11d29cbce0b4d5dc9bfb/docs/_advanced/error_handling.md
 */
const errorHandler: ExtendedErrorHandler = async ({ error }) => {
  // todo: handle errors properly
  console.error(error);
  Sentry.captureException(error);
};

const appOptions: AppOptions =
  process.env.SLACK_CONNECTION_MODE === 'socket'
    ? {
        signingSecret: process.env.SLACK_SIGNING_SECRET,
        extendedErrorHandler: true,
        socketMode: true,
        token: process.env.SLACK_BOT_TOKEN,
        appToken: process.env.SLACK_APP_TOKEN,
      }
    : {
        installerOptions: {
          ...(process.env.SLACK_INSTALL_PASSWORD && {
            installPath: `/slack/install/${process.env.SLACK_INSTALL_PASSWORD}`,
          }),
          directInstall: true,
        },
        signingSecret: process.env.SLACK_SIGNING_SECRET,
        extendedErrorHandler: true,
        clientId: process.env.SLACK_CLIENT_ID,
        clientSecret: process.env.SLACK_CLIENT_SECRET,
        stateSecret: process.env.SLACK_STATE_SECRET,

        scopes: [
          'app_mentions:read',
          'channels:history',
          'channels:read',
          'chat:write',
          'commands',
          'groups:history',
          'im:history',
          'im:read',
          'im:write',
          'mpim:history',
          'mpim:read',
          'mpim:write',
          'reactions:read',
          'users:read',
          'groups:read',
          'reactions:write',
          'files:read',
        ],

        installationStore: {
          storeInstallation: async (installation) => {
            const welcomeMessage = async (type: 'create' | 'update') => {
              if (installation.bot === undefined) return;
              const welcomeMsg = ALERTS.installMessage(type);
              return await app.client.chat.postMessage({
                token: installation.bot.token,
                channel: installation.user.id,
                text: welcomeMsg,
              });
            };

            if (installation.isEnterpriseInstall && installation.enterprise !== undefined) {
              // handle storing org-wide app installation
              const oAuthInstallation = await prisma.oAuthInstallation.findFirst({
                where: { enterpriseId: installation.enterprise.id },
              });

              if (oAuthInstallation !== null) {
                await prisma.oAuthInstallation.update({
                  where: { enterpriseId: installation.enterprise.id },
                  data: { installation: installation as unknown as Prisma.JsonObject },
                });
                await welcomeMessage('update');
                return;
              } else {
                await prisma.oAuthInstallation.create({
                  data: {
                    enterpriseId: installation.enterprise.id,
                    installation: installation as unknown as Prisma.JsonObject,
                  },
                });
                await welcomeMessage('create');
                return;
              }
            }
            if (installation.team !== undefined) {
              // single team app installation
              const oAuthInstallation = await prisma.oAuthInstallation.findFirst({
                where: { teamId: installation.team.id },
              });

              if (oAuthInstallation !== null) {
                await prisma.oAuthInstallation.update({
                  where: { teamId: installation.team.id },
                  data: { installation: installation as unknown as Prisma.JsonObject },
                });
                await welcomeMessage('update');
                return;
              } else {
                await prisma.oAuthInstallation.create({
                  data: {
                    teamId: installation.team.id,
                    installation: installation as unknown as Prisma.JsonObject,
                  },
                });
                await welcomeMessage('create');
                return;
              }
            }
            throw new Error('Failed saving installation data to installationStore');
          },
          fetchInstallation: async (installQuery) => {
            if (installQuery.isEnterpriseInstall && installQuery.enterpriseId !== undefined) {
              // handle org wide app installation lookup
              const oAuthInstallation = await prisma.oAuthInstallation.findUniqueOrThrow({
                where: { enterpriseId: installQuery.enterpriseId },
              });
              return oAuthInstallation.installation as unknown as Installation<'v2', true>;
            }
            if (installQuery.teamId !== undefined) {
              // single team app installation lookup
              const oAuthInstallation = await prisma.oAuthInstallation.findUniqueOrThrow({
                where: { teamId: installQuery.teamId },
              });
              return oAuthInstallation.installation as unknown as Installation<'v2', false>;
            }
            throw new Error('Failed fetching installation');
          },
          deleteInstallation: async (installQuery) => {
            if (installQuery.isEnterpriseInstall && installQuery.enterpriseId !== undefined) {
              // org wide app installation deletion
              await prisma.oAuthInstallation.delete({
                where: { enterpriseId: installQuery.enterpriseId },
              });
              return;
            }
            if (installQuery.teamId !== undefined) {
              // single team app installation deletion
              await prisma.oAuthInstallation.delete({
                where: { teamId: installQuery.teamId },
              });
              return;
            }
            throw new Error('Failed to delete installation');
          },
        },
        customRoutes: [
          {
            path: '/health',
            method: ['GET'],
            handler: (req, res) => {
              res.writeHead(200);
              res.end(`Things are going just fine at ${req.headers.host}!`);
            },
          },
        ],
      };

/**
 * Configure OpenAPI client settings.
 */
OpenAPI.HEADERS = {
  'User-Id': '1',
};

if (process.env.TOOLKIT_API_HOST) {
  OpenAPI.BASE = process.env.TOOLKIT_API_HOST;
}

/**
 * Instantiate app.
 */
const app = new App(appOptions);
app.error(errorHandler);

/**
 * App Mentions - https://api.slack.com/events/app_mention
 * This function deals with the first reply after the bot is mentioned
 * in a channel or group message
 */
app.event('app_mention', async ({ context, event, say, client }) => {
  /**
   * The first message (until it's been replied to) does not have a thread_ts,
   * therefore, 'return' if it exists. Threads are dealt with in a different function.
   */
  if (event.thread_ts) return;
  const action = await determineAction(context, event);
  // Exit early if this is not a valid action
  if (action.type === 'ignore') return;

  await handleFirstReply({ context, action, say, client });
});

/**
 * Message Event - https://api.slack.com/events/message
 * This deals with threading messages in channels the bot is a part of,
 * and all direct messages (DMs) to the bot.
 */
app.message(async ({ context, event, client, say }) => {
  const messages = await extractMessageHistory(client, event);
  const action = await determineAction(context, event, messages);

  // Exit early if this is not a valid action
  if (action.type === 'ignore') return;
  // Exit early if this is an app mention event since these are dealt with in a different function.
  if (isAppMentionEvent(action.event)) return;

  const channelType = action.event.channel_type;
  const threadTs = action.event.thread_ts;
  const botUserId = context.botUserId;

  // For threaded replies
  const firstMsgText = threadTs && messages[0].text;
  const lastMsgText = threadTs && messages[messages.length - 1].text;
  const firstMsgIncludesBot = firstMsgText && firstMsgText.includes(`<@${botUserId}>`);
  const lastMsgIncludesBot = lastMsgText && lastMsgText.includes(`<@${botUserId}>`);

  // Handle First DM Message

  /**
   * Handle Thread Response. Make sure the bot only replies to:
   * 1. Threads within DMs
   * 2. Threads who's first or latest message includes a bot mention
   */ if (
    (channelType === 'im' && threadTs) ||
    ((firstMsgIncludesBot || lastMsgIncludesBot) && threadTs)
  ) {
    await handleThreadReply({ context, action, client, messages, say });
  } else if (channelType === 'im') await handleFirstReply({ context, action, client, say });
});

/**
 * Shortcuts - https://api.slack.com/interactivity/shortcuts/using#shortcut_types
 */

//Sends a summary of the thread as a new message to the thread
app.shortcut('summarize_thread', summarizeThread);

/**
 * Slash Commands - https://api.slack.com/interactivity/slash-commands#getting_started
 */
app.command(`/command-help${COMMAND_SUFFIX}`, commandHelp);
app.command(`/set-tools${COMMAND_SUFFIX}`, setTools);
app.command(`/set-model${COMMAND_SUFFIX}`, setModel);
app.command(`/set-deployment${COMMAND_SUFFIX}`, setDeployment);
app.command(`/set-preamble${COMMAND_SUFFIX}`, setPreamble);
app.command(`/set-temperature${COMMAND_SUFFIX}`, setTemperature);
app.command(`/setup-command${COMMAND_SUFFIX}`, setupCommand);
app.command(`/summarize${COMMAND_SUFFIX}`, summarize);
app.command(`/view-tools${COMMAND_SUFFIX}`, viewTools);
app.command(`/view-deployment${COMMAND_SUFFIX}`, viewDeployment);
app.command(`/view-model${COMMAND_SUFFIX}`, viewModel);
app.command(`/view-preamble${COMMAND_SUFFIX}`, viewPreamble);
app.command(`/view-temperature${COMMAND_SUFFIX}`, viewTemperature);

/**
 * Views - Used to extract information from Modals after submission
 */

app.view('api_view', apiView);
app.view('tools_view', toolsView);
app.view({ callback_id: 'api_view_success', type: 'view_closed' }, async ({ ack }) => {
  await ack();
});
app.view({ callback_id: 'tools_view_success', type: 'view_closed' }, async ({ ack }) => {
  await ack();
});

/**
 * Block Actions - https://api.slack.com/reference/block-kit/block-elements#button
 */

// This action dismisses the ephemeral message sent by the bot when the button is clicked
app.action('dismiss_ephemeral', dismissEphemeral);

// Feedback actions are tied to the feedback buttons put on every bot response
app.action('stop_conversation', stopConversation);

// Input field acknowledgements - used to acknowledge the user's input within text fields and checkboxes
// Helps avoid errors on slack
app.action('checkbox-action', async ({ ack }) => await ack());
app.action('api-key-lock-action', async ({ ack }) => await ack());

(async () => {
  // Start your app
  await app.start(process.env.PORT || 3000);
  console.log('🪸  Slack bot is running!');
})();
