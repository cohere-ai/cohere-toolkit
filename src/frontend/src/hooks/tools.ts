import { useQuery } from '@tanstack/react-query';

import { ManagedTool, useCohereClient } from '@/cohere-client';

export const useListTools = (enabled: boolean = true) => {
  const client = useCohereClient();
  return useQuery<ManagedTool[], Error>({
    queryKey: ['tools'],
    queryFn: async () => {
      return await client.listTools({});
    },
    refetchOnWindowFocus: false,
    enabled,
  });
};
