import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo } from 'react';

import {
  Message as CohereChatMessage,
  GetSnapshotV1SnapshotsLinkLinkIdGetResponse,
  ListSnapshotsV1SnapshotsGetResponse,
  MessageAgent,
  Snapshot,
  SnapshotData,
  useCohereClient,
} from '@/cohere-client';
import { BotState, ChatMessage, MessageType } from '@/types/message';
import { mapHistoryToMessages } from '@/utils';

type FormattedSnapshotData = Omit<SnapshotData, 'messages'> & { messages?: ChatMessage[] };
export type ChatSnapshot = Omit<Snapshot, 'snapshot'> & { snapshot: FormattedSnapshotData };
export type ChatSnapshotWithLinks = ChatSnapshot & { links: string[] };

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
  // const messages = formatChatMessages(data?.snapshot.messages);
  const messages = mapHistoryToMessages(data?.snapshot.messages);
  const snapshot = { ...data, messages };
  return { snapshot, ...rest };
};

const formatChatMessages = (messages: CohereChatMessage[] | undefined): ChatMessage[] =>
  !messages
    ? []
    : messages.map((m) =>
        m.agent === MessageAgent.CHATBOT
          ? {
              type: MessageType.BOT,
              state: BotState.FULFILLED,
              text: m.text,
              responseId: '',
              generationId: m.generation_id ?? '',
              originalText: m.text,
            }
          : {
              type: MessageType.USER,
              text: m.text,
            }
      );

export const useSnapshots = () => {
  const client = useCohereClient();
  const { data, isLoading: loadingSnapshots } = useListSnapshots();
  const snapshots = useMemo<ChatSnapshotWithLinks[]>(() => {
    if (!data) return [];
    return data.map((s) => {
      const formattedMessages = formatChatMessages(s.snapshot.messages);
      return {
        ...s,
        snapshot: {
          ...s.snapshot,
          messages: formattedMessages,
        },
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
        snapshot?.links?.map(async (linkId) => {
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
