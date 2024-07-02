import { useLocalStorageValue } from '@react-hookz/web';
import { useQuery } from '@tanstack/react-query';

import { ManagedTool, useCohereClient } from '@/cohere-client';
import { LOCAL_STORAGE_KEYS } from '@/constants';

export const useListTools = (enabled: boolean = true) => {
  const client = useCohereClient();
  return useQuery<ManagedTool[], Error>({
    queryKey: ['tools'],
    queryFn: () => client.listTools({}),
    refetchOnWindowFocus: false,
    enabled,
  });
};

/**
 * @description A hook that returns a list of tools that require authentication
 */
export const useUnauthedTools = (enabled: boolean = true) => {
  const { data: tools } = useListTools(enabled);
  const unauthedTools = tools?.filter((tool) => tool.is_auth_required) ?? [];
  const isToolAuthRequired = unauthedTools.length > 0;
  return { unauthedTools, isToolAuthRequired };
};

export const useShowUnauthedToolsModal = () => {
  const { isToolAuthRequired } = useUnauthedTools();
  const { value: hasDismissed, set } = useLocalStorageValue(
    LOCAL_STORAGE_KEYS.unauthedToolsModalDismissed,
    {
      defaultValue: false,
      initializeWithValue: true,
    }
  );
  return {
    show: !hasDismissed && isToolAuthRequired,
    onDismissed: () => set(true),
  };
};
