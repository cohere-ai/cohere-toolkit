import { useMutation } from '@tanstack/react-query';

import { CohereNetworkError, UpdateDeploymentEnv, useCohereClient } from '@/cohere-client';

export const useUpdateDeploymentEnvVariables = () => {
  const client = useCohereClient();
  return useMutation<void, CohereNetworkError, UpdateDeploymentEnv & { name: string }>({
    mutationFn: async (request: { name: string } & UpdateDeploymentEnv) => {
      return await client.updateDeploymentEnvVariables(request);
    },
  });
};
