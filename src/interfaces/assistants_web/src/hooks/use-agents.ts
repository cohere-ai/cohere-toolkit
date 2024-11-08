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
import { DEFAULT_AGENT } from '@/constants';
import { useConversations } from '@/hooks';

export const useGetDefaultAgent = () => {
  const cohereClient = useCohereClient();

  return useQuery({
    queryKey: ['defaultAgent'],
    queryFn: async () => cohereClient.getDefaultAgent(),
  });
};

export const useListAgents = () => {
  const cohereClient = useCohereClient();
  return useQuery({
    queryKey: ['listAgents'],
    queryFn: async () => {
      // Get default agent
      const defaultAgent = await cohereClient.getDefaultAgent();
      // Get all agents
      const agents = await cohereClient.listAgents({});

      return agents.concat(defaultAgent);
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
  const defaultAgent = useGetDefaultAgent();
  return useQuery({
    queryKey: ['agent', agentId],
    queryFn: async () => {
      try {
        if (!agentId) {
          return defaultAgent;
        }
        return await cohereClient.getAgent(agentId);
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
  const { data: defaultAgent = DEFAULT_AGENT } = useGetDefaultAgent();

  const sortByDate = useCallback((a: { updated_at: string }, b: { updated_at: string }) => {
    return Date.parse(b.updated_at ?? '') - Date.parse(a.updated_at ?? '');
  }, []);

  const recentAgents = useMemo(() => {
    let recent = uniq(conversations.sort(sortByDate).map((conversation) => conversation.agent_id))
      .map((agentId) => agents.find((agent) => agent.id === agentId))
      .map((agent) => (!agent ? defaultAgent : agent))
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

    // if still there are less than `limit` recent agents, fill with base agent
    if (recent.length < limit && recent.every((agent) => agent?.id !== defaultAgent.id)) {
      recent = recent.concat(defaultAgent);
    }

    return recent;
  }, [conversations, agents, sortByDate, limit]);

  return recentAgents;
};
