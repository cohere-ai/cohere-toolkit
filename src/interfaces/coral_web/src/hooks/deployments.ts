import { UseQueryResult, useMutation, useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';

import { DeploymentDefinition, useCohereClient } from '@/cohere-client';

/**
 * @description Hook to get all possible deployments.
 */
export const useListAllDeployments = (options?: {
  enabled?: boolean;
}): UseQueryResult<DeploymentDefinition[]> => {
  const cohereClient = useCohereClient();
  return useQuery<DeploymentDefinition[], Error>({
    queryKey: ['allDeployments'],
    queryFn: () => cohereClient.listDeployments({ all: true }),
    refetchOnWindowFocus: false,
    ...options,
  });
};

/**
 * @description Hook that returns available models based on the selected deployment.
 */
export const useModels = (deployment: string) => {
  const { data: deployments } = useListAllDeployments();
  const models = useMemo(() => {
    const selectedDeployment = deployments?.find(({ name }) => name === deployment);
    if (!selectedDeployment) return [];
    return selectedDeployment.models;
  }, [deployment, deployments]);

  return { models };
};

/**
 * @description Hook that provides a function for updating a deployment's configuration.
 */
export const useUpdateDeploymentConfig = () => {
  const cohereClient = useCohereClient();
  return useMutation({
    mutationFn: ({
      deploymentId,
      config,
    }: {
      deploymentId: string;
      config: Record<string, string>;
    }) => cohereClient.updateDeploymentConfig(deploymentId, { env_vars: config }),
  });
};
