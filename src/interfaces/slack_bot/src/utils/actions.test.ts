import {
  AppMentionEvent,
  BotMessageEvent,
  Context,
  FileShareMessageEvent,
  GenericMessageEvent,
} from '@slack/bolt';
import { afterEach, describe, expect, test, vi } from 'vitest';

import { SlackMessages, determineAction } from './actions';

// Mock database calls
// the whole file needs to be mocked to avoid importing/executing the index file
vi.mock('./getChannelSettings', () => {
  return {
    getChannelSettings: async (args: {
      teamId: string | undefined;
      enterpriseId: string | undefined;
      channelId: string;
    }) => {
      return {
        tools: args.teamId === 'tool-enabled-team' ? ['test-tool'] : [],
      };
    },
  };
});

const mockContext: Context = {
  isEnterpriseInstall: false,
  teamId: 'cohere-team',
  enterpriseId: 'cohere-enterprise',
  channelId: 'test',
};

describe('determineAction', () => {
  afterEach(() => {
    vi.clearAllMocks();
    vi.resetAllMocks();
  });

  test('Ignores BotMessageEvent with unknown bot_id', async () => {
    const event: BotMessageEvent = {
      type: 'message',
      subtype: 'bot_message',
      event_ts: '1',
      channel: 'test',
      channel_type: 'channel',
      ts: '1',
      text: 'I am a bot',
      bot_id: 'test',
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('ignore');
  });

  test('BotMessageEvent with whitelisted bot_id is not ignored', async () => {
    vi.stubEnv('ALLOWED_BOT_IDS', 'allowed-bot-id');

    const event: BotMessageEvent = {
      type: 'message',
      subtype: 'bot_message',
      event_ts: '1',
      channel: 'test',
      channel_type: 'channel',
      ts: '1',
      text: 'I am a bot',
      bot_id: 'allowed-bot-id',
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('chat');

    vi.unstubAllEnvs();
  });

  test('BotMessageEvent with not whitelisted bot_id is ignored', async () => {
    vi.stubEnv('ALLOWED_BOT_IDS', 'allowed-bot-id');

    const event: BotMessageEvent = {
      type: 'message',
      subtype: 'bot_message',
      event_ts: '1',
      channel: 'test',
      channel_type: 'channel',
      ts: '1',
      text: 'I am a bot',
      bot_id: 'not-allowed-bot-id',
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('ignore');

    vi.unstubAllEnvs();
  });

  test('Ignores GenericMessageEvent with a bot_id', async () => {
    const event: GenericMessageEvent = {
      type: 'message',
      subtype: undefined,
      event_ts: '1',
      channel: 'test',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel_type: 'channel',
      bot_id: 'bot',
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('ignore');
  });

  test('Ignores GenericMessageEvent with no content', async () => {
    const event: GenericMessageEvent = {
      type: 'message',
      subtype: undefined,
      event_ts: '1',
      channel: 'test',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel_type: 'channel',
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('ignore');
  });

  test('Ignores AppMentionEvent with no content', async () => {
    const event: AppMentionEvent = {
      type: 'app_mention',
      username: 'test',
      text: '',
      ts: 'test',
      channel: 'test',
      event_ts: 'test',
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('ignore');
  });

  test('FileShareMessageEvent events with `summarize` in the message text are marked as `file-summarize`', async () => {
    const event: FileShareMessageEvent = {
      type: 'message',
      subtype: 'file_share',
      text: 'summarize this file',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel: 'test',
      channel_type: 'channel',
      event_ts: '2',
      files: [
        {
          name: 'test-file',
          title: 'test-file',
          external_type: '',
          username: 'test-user',
          channels: [],
          groups: [],
          id: 'test-file',
          created: 1,
          mimetype: 'application/pdf',
          filetype: 'pdf',
          pretty_type: 'pdf',
          editable: false,
          size: 10,
          mode: 'hosted',
          is_external: false,
          is_public: false,
          public_url_shared: false,
          display_as_bot: false,
          permalink: 'url',
          url_private: 'url',
        },
      ],
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('file-summarize');
  });

  test('GenericMessageEvent events with a file in the message history and with `summarize` in the message text are marked as `file-summarize`', async () => {
    const event: GenericMessageEvent = {
      type: 'message',
      text: 'summarize the file in this thread',
      subtype: undefined,
      event_ts: '1',
      channel: 'test',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel_type: 'channel',
    };

    const messages: SlackMessages = [
      {
        files: [
          {
            name: 'test-file',
            title: 'test-file',
            external_type: '',
            username: 'test-user',
            channels: [],
            groups: [],
            id: 'test-file',
            created: 1,
            mimetype: 'application/pdf',
            filetype: 'pdf',
            pretty_type: 'pdf',
            editable: false,
            size: 10,
            mode: 'hosted',
            is_external: false,
            is_public: false,
            public_url_shared: false,
            display_as_bot: false,
            permalink: 'url',
            url_private: 'url',
          },
        ],
      },
    ];
    const action = await determineAction(mockContext, event, messages);
    expect(action.type).toBe('file-summarize');
  });

  test('FileShareMessageEvent events are marked as `file-rag`', async () => {
    const event: FileShareMessageEvent = {
      type: 'message',
      subtype: 'file_share',
      text: 'question about this file?',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel: 'test',
      channel_type: 'channel',
      event_ts: '2',
      files: [
        {
          name: 'test-file',
          title: 'test-file',
          external_type: '',
          username: 'test-user',
          channels: [],
          groups: [],
          id: 'test-file',
          created: 1,
          mimetype: 'application/pdf',
          filetype: 'pdf',
          pretty_type: 'pdf',
          editable: false,
          size: 10,
          mode: 'hosted',
          is_external: false,
          is_public: false,
          public_url_shared: false,
          display_as_bot: false,
          permalink: 'url',
          url_private: 'url',
        },
      ],
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('file-rag');
  });

  test('GenericMessageEvent with a file in the message history are marked as `file-rag`', async () => {
    const event: GenericMessageEvent = {
      type: 'message',
      text: 'who wrote this paper?',
      subtype: undefined,
      event_ts: '1',
      channel: 'test',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel_type: 'channel',
    };

    const messages: SlackMessages = [
      {
        files: [
          {
            name: 'test-file',
            title: 'test-file',
            external_type: '',
            username: 'test-user',
            channels: [],
            groups: [],
            id: 'test-file',
            created: 1,
            mimetype: 'application/pdf',
            filetype: 'pdf',
            pretty_type: 'pdf',
            editable: false,
            size: 10,
            mode: 'hosted',
            is_external: false,
            is_public: false,
            public_url_shared: false,
            display_as_bot: false,
            permalink: 'url',
            url_private: 'url',
          },
        ],
      },
    ];

    const action = await determineAction(mockContext, event, messages);
    expect(action.type).toBe('file-rag');
  });

  test('GenericMessageEvent with context are marked as `chat`', async () => {
    const event: GenericMessageEvent = {
      type: 'message',
      text: 'I have a question...',
      subtype: undefined,
      event_ts: '1',
      channel: 'test',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel_type: 'channel',
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('chat');
  });

  test('AppMentionEvent with context are marked as `chat`', async () => {
    const event: AppMentionEvent = {
      type: 'app_mention',
      username: 'test',
      text: 'hello',
      ts: 'test',
      channel: 'test',
      event_ts: 'test',
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('chat');
  });

  test('FileShareMessageEvent events with `summarize` in the message text and an invalid file are marked as `file-invalid`', async () => {
    const event: FileShareMessageEvent = {
      type: 'message',
      subtype: 'file_share',
      text: 'summarize this file',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel: 'test',
      channel_type: 'channel',
      event_ts: '2',
      files: [
        {
          name: 'test-file',
          title: 'test-file',
          external_type: '',
          username: 'test-user',
          channels: [],
          groups: [],
          id: 'test-file',
          created: 1,
          mimetype: 'application/invalid',
          filetype: 'invalid',
          pretty_type: 'invalid',
          editable: false,
          size: 10,
          mode: 'hosted',
          is_external: false,
          is_public: false,
          public_url_shared: false,
          display_as_bot: false,
          permalink: 'url',
          url_private: 'url',
        },
      ],
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('file-invalid');
  });

  test('FileShareMessageEvent events with an invalid file are marked as `file-invalid`', async () => {
    const event: FileShareMessageEvent = {
      type: 'message',
      subtype: 'file_share',
      text: 'question about this file?',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel: 'test',
      channel_type: 'channel',
      event_ts: '2',
      files: [
        {
          name: 'test-file',
          title: 'test-file',
          external_type: '',
          username: 'test-user',
          channels: [],
          groups: [],
          id: 'test-file',
          created: 1,
          mimetype: 'application/invalid',
          filetype: 'invalid',
          pretty_type: 'invalid',
          editable: false,
          size: 10,
          mode: 'hosted',
          is_external: false,
          is_public: false,
          public_url_shared: false,
          display_as_bot: false,
          permalink: 'url',
          url_private: 'url',
        },
      ],
    };
    const action = await determineAction({ ...mockContext, teamId: 'rag-enabled-team' }, event);
    expect(action.type).toBe('file-invalid');
  });

  test('FileShareMessageEvent events with `summarize` in the message text and a file with no url_private are marked as `file-invalid`', async () => {
    const event: FileShareMessageEvent = {
      type: 'message',
      subtype: 'file_share',
      text: 'summarize this file',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel: 'test',
      channel_type: 'channel',
      event_ts: '2',
      files: [
        {
          name: 'test-file',
          title: 'test-file',
          external_type: '',
          username: 'test-user',
          channels: [],
          groups: [],
          id: 'test-file',
          created: 1,
          mimetype: 'application/pdf',
          filetype: 'pdf',
          pretty_type: 'pdf',
          editable: false,
          size: 10,
          mode: 'hosted',
          is_external: false,
          is_public: false,
          public_url_shared: false,
          display_as_bot: false,
          permalink: 'url',
        },
      ],
    };
    const action = await determineAction(mockContext, event);
    expect(action.type).toBe('file-invalid');
  });

  test('FileShareMessageEvent events with a file with no url_private are marked as `chat`', async () => {
    const event: FileShareMessageEvent = {
      type: 'message',
      subtype: 'file_share',
      text: 'question about this file?',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel: 'test',
      channel_type: 'channel',
      event_ts: '2',
      files: [
        {
          name: 'test-file',
          title: 'test-file',
          external_type: '',
          username: 'test-user',
          channels: [],
          groups: [],
          id: 'test-file',
          created: 1,
          mimetype: 'application/pdf',
          filetype: 'pdf',
          pretty_type: 'pdf',
          editable: false,
          size: 10,
          mode: 'hosted',
          is_external: false,
          is_public: false,
          public_url_shared: false,
          display_as_bot: false,
          permalink: 'url',
        },
      ],
    };
    const action = await determineAction({ ...mockContext, teamId: 'rag-enabled-team' }, event);
    expect(action.type).toBe('file-invalid');
  });

  test('GenericMessageEvent with tools enabled are marked as `chat-rag`', async () => {
    const event: GenericMessageEvent = {
      type: 'message',
      text: 'I have a question...',
      subtype: undefined,
      event_ts: '1',
      channel: 'test',
      user: 'U05LUQL8X2R',
      ts: '2',
      channel_type: 'channel',
    };
    const action = await determineAction({ ...mockContext, teamId: 'tool-enabled-team' }, event);
    expect(action.type).toBe('chat-rag');
  });

  test('AppMentionEvent with tools enabled are marked as `chat-rag`', async () => {
    const event: AppMentionEvent = {
      type: 'app_mention',
      username: 'test',
      text: 'hello',
      ts: 'test',
      channel: 'test',
      event_ts: 'test',
    };
    const action = await determineAction({ ...mockContext, teamId: 'tool-enabled-team' }, event);
    expect(action.type).toBe('chat-rag');
  });
});
