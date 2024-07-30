'use client';

import { useContext } from 'react';

import { Dropdown } from '@/components/Shared';
import { useContextStore } from '@/context';
import { BannerContext } from '@/context/BannerContext';
import { useListAllDeployments } from '@/hooks/deployments';
import { useParamsStore } from '@/stores';

import { EditEnvVariablesModal } from './EditEnvVariablesButton';

export const DeploymentsDropdown: React.FC = () => {
  const { message: bannerMessage, setMessage } = useContext(BannerContext);
  const { open, close } = useContextStore();

  const {
    params: { deployment },
    setParams,
  } = useParamsStore();
  const { data: allDeployments = [] } = useListAllDeployments();
  const deploymentOptions = allDeployments.map(({ name }) => ({
    label: name,
    value: name,
  }));

  return (
    <Dropdown
      placeholder="Select a deployment"
      value={deployment}
      onChange={(deploymentName: string) => {
        const deployment = allDeployments.find((d) => d.name === deploymentName);
        if (deployment && !deployment.is_available) {
          open({
            title: 'Configure Model Deployment',
            content: <EditEnvVariablesModal onClose={close} defaultDeployment={deployment.name} />,
          });
        } else if (bannerMessage) {
          setMessage('');
        }
        setParams({ deployment: deploymentName });
      }}
      options={deploymentOptions}
    />
  );
};
