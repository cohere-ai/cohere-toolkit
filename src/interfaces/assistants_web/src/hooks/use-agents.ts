import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { uniq } from 'lodash';
import { useCallback, useMemo } from 'react';

import {
  AgentPublic,
  ApiError,
  CreateAgentRequest,
  UpdateAgentRequest,
  useCohereClient,
} from '@/cohere-client';
import { DEFAULT_AGENT_ID } from '@/constants';
import { useConversations } from '@/hooks';

export const useListAgents = () => {
  const cohereClient = useCohereClient();
  return useQuery({
    queryKey: ['listAgents'],
    queryFn: async () => {
      return await cohereClient.listAgents({});
    },
  });
};

export const useCreateAgent = () => {
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: CreateAgentRequest) => cohereClient.createAgent(request),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['listAgents'] });
    },
  });
};

export const useDeleteAgent = () => {
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (request: { agentId: string }) => {
      try {
        return await cohereClient.deleteAgent(request);
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['listAgents'] });
    },
  });
};

export const useAgent = ({ agentId }: { agentId?: string }) => {
  const cohereClient = useCohereClient();
  return useQuery({
    queryKey: ['agent', agentId],
    queryFn: async () => {
      try {
        if (!agentId) {
          return await cohereClient.getAgent(DEFAULT_AGENT_ID);
        }
        return await cohereClient.getAgent(agentId);
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
  });
};

export const useDefaultAgent = () => {
  const cohereClient = useCohereClient();
  return useQuery({
    queryKey: ['agent', DEFAULT_AGENT_ID],
    queryFn: async () => {
      try {
        return await cohereClient.getAgent(DEFAULT_AGENT_ID);
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
  });
};

/**
 * @description Returns a function to check if an agent name is unique.
 */
export const useIsAgentNameUnique = () => {
  const { data: agents } = useListAgents();
  return (name: string, omittedAgentId?: string) => {
    return agents
      ?.filter((agent) => agent.id !== omittedAgentId)
      .some((agent) => agent.name === name);
  };
};

export const useUpdateAgent = () => {
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();

  return useMutation<AgentPublic, ApiError, { request: UpdateAgentRequest; agentId: string }>({
    mutationFn: ({ request, agentId }) => {
      return cohereClient.updateAgent(request, agentId);
    },
    onSettled: (agent) => {
      queryClient.invalidateQueries({ queryKey: ['agent', agent?.id] });
      queryClient.invalidateQueries({ queryKey: ['listAgents'] });
    },
  });
};

/**
 * @description Returns the most recently used agents.
 */
export const useRecentAgents = (limit: number = 5) => {
  const { data: agents = [] } = useListAgents();
  const { data: conversations = [] } = useConversations({});

  const sortByDate = useCallback((a: { updated_at: string }, b: { updated_at: string }) => {
    return Date.parse(b.updated_at ?? '') - Date.parse(a.updated_at ?? '');
  }, []);

  const recentAgents = useMemo(() => {
    let recent = uniq(
      conversations
        .sort(sortByDate)
        .map((conversation) => conversation.agent_id ?? DEFAULT_AGENT_ID)
    )
      .map((agentId) => agents.find((agent) => agent.id === agentId))
      .slice(0, limit);

    // if there are less than `limit` recent agents, fill with the latest created agents
    if (recent.length < limit) {
      const recentIds = recent.map((agent) => agent?.id);
      const remainingAgents = agents.filter((agent) => !recentIds.includes(agent.id));
      const remainingRecentAgents = remainingAgents
        .sort(sortByDate)
        .slice(0, limit - recent.length);
      recent = recent.concat(remainingRecentAgents);
    }

    return recent.filter((a) => a !== undefined);
  }, [conversations, agents, sortByDate, limit]);

  return recentAgents;
};
