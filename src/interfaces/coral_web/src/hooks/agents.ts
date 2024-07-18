import { useLocalStorageValue } from '@react-hookz/web';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { isNil } from 'lodash';
import { useMemo } from 'react';

import { Agent, ApiError, CreateAgent, UpdateAgent, useCohereClient } from '@/cohere-client';
import { LOCAL_STORAGE_KEYS } from '@/constants';

export const useListAgents = () => {
  const cohereClient = useCohereClient();
  return useQuery({
    queryKey: ['listAgents'],
    queryFn: () => cohereClient.listAgents({}),
  });
};

export const useCreateAgent = () => {
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (request: CreateAgent) => cohereClient.createAgent(request),
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
    enabled: !!agentId,
    queryFn: async () => {
      try {
        if (!agentId) throw new Error('Agent ID not found');
        return await cohereClient.getAgent(agentId);
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
  });
};

export const useDefaultAgent = (enabled?: boolean) => {
  const cohereClient = useCohereClient();
  return useQuery({
    queryKey: ['defaultAgent'],
    enabled: enabled,
    queryFn: async () => {
      return await cohereClient.getDefaultAgent();
    },
  });
};

/**
 * @description Returns a function to check if an agent name is unique.
 */
export const useIsAgentNameUnique = () => {
  const { data: agents } = useListAgents();
  return (name: string, omittedAgentId?: string) =>
    agents?.every((agent) => agent.name !== name || agent.id === omittedAgentId);
};

export const useUpdateAgent = () => {
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation<Agent, ApiError, { request: UpdateAgent; agentId: string }>({
    mutationFn: ({ request, agentId }) => cohereClient.updateAgent(request, agentId),
    onSettled: (agent) => {
      queryClient.invalidateQueries({ queryKey: ['agent', agent?.id] });
      queryClient.invalidateQueries({ queryKey: ['listAgents'] });
    },
  });
};

/**
 * @description Returns the most recently used agents.
 */

export const useRecentAgents = () => {
  const { data: agents } = useListAgents();

  const { set, value: recentAgentsIds } = useLocalStorageValue(LOCAL_STORAGE_KEYS.recentAgents, {
    defaultValue: [] as string[],
  });

  const addRecentAgentId = (agentId: string) => {
    if (!recentAgentsIds) return;
    set([...recentAgentsIds.filter((id) => id !== agentId), agentId]);
  };

  const removeRecentAgentId = (agentId: string) => {
    if (!recentAgentsIds) return;
    set(recentAgentsIds.filter((id) => id !== agentId));
  };

  const recentAgents = useMemo(() => {
    if (!recentAgentsIds) return [];
    return recentAgentsIds
      .map((id) => agents?.find((agent) => agent.id === id))
      .filter((agent) => !isNil(agent)) as Agent[];
  }, [agents, recentAgentsIds]);

  return { recentAgents, addRecentAgentId, removeRecentAgentId };
};
