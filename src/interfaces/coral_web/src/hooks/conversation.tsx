import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { useRef } from 'react';

import {
  CohereNetworkError,
  Conversation,
  ConversationWithoutMessages,
  UpdateConversation,
  useCohereClient,
} from '@/cohere-client';
import { DeleteConversations } from '@/components/Modals/DeleteConversations';
import { EditConversationTitle } from '@/components/Modals/EditConversationTitle';
import { useContextStore } from '@/context';
import { useNotify } from '@/hooks/toast';
import { useCitationsStore, useConversationStore } from '@/stores';
import { isAbortError } from '@/utils';

export const useConversations = () => {
  const abortControllerRef = useRef<AbortController | null>(null);
  const client = useCohereClient();

  return useQuery<ConversationWithoutMessages[], Error>({
    queryKey: ['conversations'],
    queryFn: async () => {
      try {
        const conversations = await client.listConversations({
          signal: abortControllerRef.current?.signal,
        });
        return conversations;
      } catch (e) {
        if (!isAbortError(e)) {
          console.error(e);
          throw e;
        }
        return [];
      }
    },
    retry: 0,
    refetchOnWindowFocus: false,
  });
};

export const useConversation = ({
  conversationId,
  disabledOnMount,
}: {
  conversationId?: string;
  disabledOnMount?: boolean;
}) => {
  const abortControllerRef = useRef<AbortController | null>(null);
  const client = useCohereClient();

  return useQuery<Conversation, Error>({
    queryKey: ['conversation', conversationId],
    enabled: !!conversationId && !disabledOnMount,
    queryFn: async () => {
      try {
        return await client.getConversation({
          conversationId: conversationId ?? '',
          signal: abortControllerRef.current?.signal,
        });
      } catch (e) {
        if (!isAbortError(e)) {
          console.error(e);
          throw e;
        }
        return {} as Conversation;
      }
    },
    retry: 0,
    refetchOnWindowFocus: false,
  });
};

export const useEditConversation = () => {
  const client = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation<
    Conversation,
    CohereNetworkError,
    Omit<UpdateConversation, 'user_id'> & { conversationId: string }
  >({
    mutationFn: async (request) => {
      try {
        return await client.editConversation(request);
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
};

export const useDeleteConversation = () => {
  const client = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation<{}, CohereNetworkError, { conversationId: string }>({
    mutationFn: async ({ conversationId }: { conversationId: string }) => {
      return await client.deleteConversation({ conversationId });
    },
    onSettled: (_, _err, { conversationId }: { conversationId: string }) => {
      queryClient.setQueriesData<Conversation[]>(
        { queryKey: ['conversations'] },
        (oldConversations) => {
          return oldConversations?.filter((c) => c.id === conversationId);
        }
      );
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
};

export const useConversationActions = () => {
  const router = useRouter();
  const { open, close } = useContextStore();
  const {
    conversation: { id: conversationId = '' },
    resetConversation,
  } = useConversationStore();
  const { resetCitations } = useCitationsStore();
  const notify = useNotify();
  const { mutateAsync: deleteConversation, isPending } = useDeleteConversation();

  const handleDeleteConversation = async ({
    id,
    onComplete,
  }: {
    id: string;
    onComplete?: VoidFunction;
  }) => {
    const onDelete = () => {
      close();
      onComplete?.();

      if (id === conversationId) {
        resetConversation();
        resetCitations();
        router.push('/', undefined, { shallow: true }); // go to new chat
      }
    };

    const onConfirm = async () => {
      try {
        await deleteConversation({ conversationId: id });
        onDelete();
      } catch (e) {
        console.error(e);
        notify.error('Something went wrong. Please try again.');
      }
    };

    open({
      title: `Are you sure you want to delete this conversation?`,
      content: (
        <DeleteConversations
          conversationIds={[id]}
          onClose={close}
          onConfirm={onConfirm}
          isPending={isPending}
        />
      ),
    });
  };

  const editConversationTitle = ({ id, title }: { id: string; title: string }) => {
    const onClose = () => {
      close();
    };

    open({
      title: 'Edit Title',
      content: (
        <EditConversationTitle
          conversationId={id}
          initialConversationTitle={title}
          onClose={onClose}
        />
      ),
    });
  };

  return { deleteConversation: handleDeleteConversation, editConversationTitle };
};
