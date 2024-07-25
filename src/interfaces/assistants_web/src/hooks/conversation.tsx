import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

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
import { useChatRoutes, useNavigateToNewChat } from '@/hooks/chatRoutes';
import { useNotify } from '@/hooks/toast';
import { useConversationStore } from '@/stores';
import { isAbortError } from '@/utils';

export const useConversations = (params: { offset?: number; limit?: number; agentId?: string }) => {
  const client = useCohereClient();

  return useQuery<ConversationWithoutMessages[], ApiError>({
    queryKey: ['conversations', params.agentId],
    queryFn: async () => {
      const conversations = await client.listConversations(params);

      if (params.agentId) {
        return conversations;
      }

      return conversations;
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
    Conversation,
    CohereNetworkError,
    { request: UpdateConversation; conversationId: string }
  >({
    mutationFn: ({ request, conversationId }) => client.editConversation(request, conversationId),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
};

export const useDeleteConversation = () => {
  const client = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation<DeleteConversation, CohereNetworkError, { conversationId: string }>({
    mutationFn: ({ conversationId }: { conversationId: string }) =>
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
  const { agentId } = useChatRoutes();
  const { open, close } = useContextStore();
  const {
    conversation: { id: conversationId },
  } = useConversationStore();
  const notify = useNotify();
  const navigateToNewChat = useNavigateToNewChat();
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
        navigateToNewChat(agentId);
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
