import { AgentPublic } from '@/cohere-client';
import { DEFAULT_AGENT_ID } from '@/constants';

/**
 * @description Checks if the agent is the base agent.
 * @param agent - The agent to check.
 */
export const checkIsDefaultAgent = (agent: AgentPublic | undefined) => {
  return agent?.id === DEFAULT_AGENT_ID;
};
