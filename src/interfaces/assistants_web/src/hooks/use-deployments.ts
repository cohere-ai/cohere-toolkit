import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';

import { Deployment, useCohereClient } from '@/cohere-client';

/**
 * @description Hook to get all possible deployments.
 */
export const useListAllDeployments = (options?: { enabled?: boolean }) => {
  const cohereClient = useCohereClient();
  return useQuery<Deployment[], Error>({
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
  }, [deployment]);

  return { models };
};
