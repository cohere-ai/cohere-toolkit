import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { isNil } from 'lodash';
import { useMemo } from 'react';

import { Agent, CreateAgent, useCohereClient } from '@/cohere-client';
import { useAgentsStore } from '@/stores';

export const useListAgents = () => {
  const cohereClient = useCohereClient();
  return useQuery({
    queryKey: ['listAgents'],
    queryFn: async () => {
      try {
        return await cohereClient.listAgents();
      } catch (e) {
        console.error(e);
        throw e;
      }
    },
  });
};

export const useCreateAgent = () => {
  const cohereClient = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (request: CreateAgent) => {
      try {
        return await cohereClient.createAgent(request);
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

/**
 * @description Returns a function to check if an agent name is unique.
 */
export const useIsAgentNameUnique = () => {
  const { data: agents } = useListAgents();
  return (name: string) => !agents?.some((agent) => agent.name === name);
};

/**
 * @description Returns the most recently used agents.
 */
export const useRecentAgents = () => {
  const { data: agents } = useListAgents();

  const {
    agents: { recentAgentsIds },
  } = useAgentsStore();

  const recentAgents = useMemo(
    () =>
      recentAgentsIds
        .map((id) => agents?.find((agent) => agent.id === id))
        .filter((agent) => !isNil(agent)) as Agent[],
    [agents, recentAgentsIds]
  );

  return recentAgents;
};
