import { Tool } from '@/cohere-client';

/**
 * Helper function to determine if grounding is on.
 * Note: this doesn't mean that RAG was used, just that it's on.
 */
export const isGroundingOn = (tools: Tool[], documents: string[]) => {
  return tools.length > 0 || documents.length > 0;
};
