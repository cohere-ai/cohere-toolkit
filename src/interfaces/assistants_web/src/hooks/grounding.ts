import { useParamsStore } from '@/stores';
import { isGroundingOn } from '@/utils';

/**
 * Hook to determine if grounding is on.
 * Note: this doesn't mean that RAG was used, just that it's on.
 */
export const useIsGroundingOn = () => {
  const {
    params: { tools, fileIds },
  } = useParamsStore();

  return isGroundingOn(tools ?? [], fileIds ?? []);
};
