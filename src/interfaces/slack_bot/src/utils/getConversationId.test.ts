import { expect, test } from 'vitest';

import { getConversationId } from './getConversationId';

test('All parameters provided', async () => {
  const threadTs = '1623345678.123214';
  const channelId = 'C03SMGA4P62';
  const { conversationId } = getConversationId({ threadTs, channelId });
  expect(conversationId).toBe('1623345678_123214-C03SMGA4P62');
});

test('No threadTs provided', async () => {
  const threadTs = '';
  const channelId = 'C03SMGA4P62';
  const { conversationId } = getConversationId({ threadTs, channelId });
  expect(conversationId).toBe(undefined);
});

test('No channelId provided', async () => {
  const threadTs = '1623345678.123214';
  const channelId = '';
  const { conversationId } = getConversationId({ threadTs, channelId });
  expect(conversationId).toBe(undefined);
});

test('No params provided', async () => {
  const threadTs = '';
  const channelId = '';
  const { conversationId } = getConversationId({ threadTs, channelId });
  expect(conversationId).toBe(undefined);
});
