import { AgentPublic } from '@/cohere-client';

/**
 * @description Checks if the agent is the base agent.
 * @param agent - The agent to check.
 */
export const checkIsBaseAgent = (agent: AgentPublic | undefined) => {
  return agent?.id === '';
};
