import { AgentPublic } from '@/cohere-client';

/**
 * @description Checks if the agent is the default agent.
 * @param agent - The agent to check.
 */
export const checkIsDefaultAgent = (agent: AgentPublic | undefined) => {
  return agent?.id === '';
};
