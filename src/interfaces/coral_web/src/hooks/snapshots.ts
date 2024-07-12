import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import {
  GetSnapshotV1SnapshotsLinkLinkIdGetResponse,
  ListSnapshotsV1SnapshotsGetResponse,
  Snapshot,
  SnapshotData,
  useCohereClient,
} from '@/cohere-client';
import { ChatMessage } from '@/types/message';

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
        console.error(e);
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
        throw e;
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['listSnapshots'] });
    },
  });
};

/**
 * @description Returns a snapshot by link id
 */
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

export const useSnapshots = () => {
  const client = useCohereClient();
  const { data, isLoading: loadingSnapshots } = useListSnapshots();
  const snapshots = data ?? [];

  const getSnapshotLinksByConversationId = (conversationId: string) =>
    snapshots
      .filter((s) => s.conversation_id === conversationId)
      .map((s) => s.links)
      .flat();

  const deleteAllSnapshotLinks = async (conversationId: string): Promise<void> => {
    const snapshot = snapshots.find((s) => s.conversation_id === conversationId);
    if (!snapshot || !snapshot.links) return;
    try {
      await Promise.all(
        snapshot.links.map(async (linkId) => {
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
