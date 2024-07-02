import { useMutation } from '@tanstack/react-query';

import { UpdateDeploymentEnv, useCohereClient } from '@/cohere-client';
import { CohereNetworkError } from '@/cohere-client/generated/types';

export const useUpdateDeploymentEnvVariables = () => {
  const client = useCohereClient();
  return useMutation<void, CohereNetworkError, UpdateDeploymentEnv & { name: string }>({
    mutationFn: async (request: { name: string } & UpdateDeploymentEnv) => {
      return await client.updateDeploymentEnvVariables(request);
    },
  });
};
