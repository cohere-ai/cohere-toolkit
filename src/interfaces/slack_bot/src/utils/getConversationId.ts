type GetConversationIdArgs = {
  threadTs: string;
  channelId: string;
};

type ConversationId = {
  conversationId: string | undefined;
};

/**
 *   A consistent conversation ID is needed to
 *   maintain context on the chat endpoint logs for analytics.
 *   This function generates a conversation ID based on the thread
 *   timestamp (parent message) and channel ID
 * */
export const getConversationId = ({
  threadTs,
  channelId,
}: GetConversationIdArgs): ConversationId => {
  if (threadTs === '' || channelId === '') {
    return { conversationId: undefined };
  }
  const tsWithoutDecimal = threadTs.replace('.', '_');
  const conversationId = `${tsWithoutDecimal}-${channelId}`;
  return { conversationId };
};
