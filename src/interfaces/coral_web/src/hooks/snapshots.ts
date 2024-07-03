import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo } from 'react';

import {
  ChatRole,
  ChatMessage as CohereChatMessage,
  GetSnapshotV1SnapshotsLinkLinkIdGetResponse,
  ListSnapshotsV1SnapshotsGetResponse,
  Snapshot,
  useCohereClient,
} from '@/cohere-client';
import { BotState, ChatMessage, MessageType } from '@/types/message';

export type ChatSnapshot = Omit<Snapshot, 'messages'> & { messages?: ChatMessage[] };

/**
 * @description returns a list of snapshots
 */
const useListSnapshots = () => {
  const client = useCohereClient();

  return useQuery<ListSnapshotsV1SnapshotsGetResponse, Error>({
    queryKey: ['listSnapshots'],
    queryFn: async () => {
      try {
        return await client.listSnapshots();
      } catch (e) {
        throw e;
      }
    },
    refetchOnWindowFocus: false,
  });
};

/**
 * @description returns a conversation's snapshot link id if it exists or if the newest link is less than 15 days old
 * else, creates a new link id for the conversation
 */
export const useCreateSnapshotLinkId = () => {
  const client = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ conversationId }: { conversationId: string }) => {
      try {
        const newSnapshot = await client.createSnapshot({ conversation_id: conversationId });
        return newSnapshot.link_id;
      } catch (e) {
        console.error(e);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['listSnapshots'] });
    },
  });
};

export const useGetSnapshotByLinkId = (linkId: string) => {
  const client = useCohereClient();
  return useQuery<GetSnapshotV1SnapshotsLinkLinkIdGetResponse, Error>({
    queryKey: ['getSnapshotByLinkId', linkId],
    queryFn: async () => {
      try {
        return await client.getSnapshot({ linkId });
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
  });
};

/**
 * @description returns a conversations's snapshot information if it exists
 * and formats the messages else, returns undefined
 *
 * Expired links will still return a snapshot since the owner can still view it
 */
export const useSnapshot = (linkId: string) => {
  const { data, ...rest } = useGetSnapshotByLinkId(linkId);
  const messages = formatChatMessages(data?.messages);
  const snapshot = { ...data, messages };
  return { snapshot, ...rest };
};

const formatChatMessages = (messages: CohereChatMessage[] | undefined): ChatMessage[] =>
  !messages
    ? []
    : messages.map(({ role, message }) =>
        role === ChatRole.CHATBOT
          ? {
              type: MessageType.BOT,
              state: BotState.FULFILLED,
              text: message || '',
              responseId: '',
              generationId: '',
              originalText: '',
            }
          : {
              type: MessageType.USER,
              text: message || '',
            }
      );

export const useSnapshots = () => {
  const client = useCohereClient();

  const { data, isLoading: loadingSnapshots } = useListSnapshots();
  const snapshots = useMemo<ChatSnapshot[]>(() => {
    if (!data || !data.snapshots) return [];
    return data.snapshots.map(({ messages, ...s }) => {
      const formattedMessages = formatChatMessages(messages);
      return {
        ...s,
        messages: formattedMessages,
      };
    });
  }, [data]);

  const getSnapshotLinksByConversationId = (conversationId: string) =>
    snapshots
      .filter((s) => s.conversation_id === conversationId)
      .map((s) => s.links)
      .flat();

  const deleteAllSnapshotLinks = async (conversationId: string): Promise<void> => {
    const snapshot = snapshots.find((s) => s.conversation_id === conversationId);
    if (!snapshot) return;
    if (!snapshot.links) return;
    try {
      await Promise.all(
        snapshot?.links?.map(async ({ linkId }) => {
          if (linkId) {
            await client.deleteSnapshotLink({ linkId });
          }
        })
      );
    } catch (e) {
      console.error(e);
      throw e;
    }
  };

  return {
    snapshots,
    loadingSnapshots,
    getSnapshotLinksByConversationId,
    deleteAllSnapshotLinks,
  };
};
