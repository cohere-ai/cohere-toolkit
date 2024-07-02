import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { useRef } from 'react';

import {
  ApiError,
  CohereNetworkError,
  Conversation,
  ConversationWithoutMessages,
  DeleteConversation,
  UpdateConversation,
  useCohereClient,
} from '@/cohere-client';
import { DeleteConversations } from '@/components/Modals/DeleteConversations';
import { EditConversationTitle } from '@/components/Modals/EditConversationTitle';
import { useContextStore } from '@/context';
import { useNotify } from '@/hooks/toast';
import { useCitationsStore, useConversationStore, useParamsStore } from '@/stores';
import { isAbortError } from '@/utils';

export const useConversations = (params: { offset?: number; limit?: number; agentId?: string }) => {
  const client = useCohereClient();

  return useQuery<ConversationWithoutMessages[], ApiError>({
    queryKey: ['conversations'],
    queryFn: async () => {
      try {
        const conversations = await client.listConversations(params);
        return conversations || [];
      } catch {
        return [];
      }
    },
    retry: 0,
    refetchOnWindowFocus: false,
    initialData: [],
  });
};

export const useConversation = ({
  conversationId,
  disabledOnMount,
}: {
  conversationId?: string;
  disabledOnMount?: boolean;
}) => {
  const client = useCohereClient();

  return useQuery<Conversation | undefined, Error>({
    queryKey: ['conversation', conversationId],
    enabled: !!conversationId && !disabledOnMount,
    queryFn: async () => {
      try {
        if (!conversationId) throw new Error('Conversation ID not found');
        return await client.getConversation({
          conversationId: conversationId,
        });
      } catch (e) {
        if (!isAbortError(e)) {
          console.error(e);
          throw e;
        }
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
    Conversation | undefined,
    CohereNetworkError,
    { request: UpdateConversation; conversationId: string }
  >({
    mutationFn: async ({ request, conversationId }) =>
      client.editConversation(request, conversationId),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
};

export const useDeleteConversation = () => {
  const client = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation<
    DeleteConversation | undefined,
    CohereNetworkError,
    { conversationId: string }
  >({
    mutationFn: async ({ conversationId }: { conversationId: string }) =>
      client.deleteConversation({ conversationId }),
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
  const { resetFileParams } = useParamsStore();
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
        resetFileParams();
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
