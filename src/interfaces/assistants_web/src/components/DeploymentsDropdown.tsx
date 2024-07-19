'use client';

import { useContext } from 'react';

import { Dropdown, DropdownOptionGroups } from '@/components/Shared';
import { BannerContext } from '@/context/BannerContext';
import { ModalContext } from '@/context/ModalContext';
import { useListAllDeployments } from '@/hooks/deployments';
import { useParamsStore } from '@/stores';

import { EditEnvVariablesModal } from './EditEnvVariablesButton';

export const DeploymentsDropdown: React.FC = () => {
  const { message: bannerMessage, setMessage } = useContext(BannerContext);
  const { open, close } = useContext(ModalContext);

  const {
    params: { deployment },
    setParams,
  } = useParamsStore();
  const { data: allDeployments = [] } = useListAllDeployments();
  const deploymentOptions: DropdownOptionGroups = [
    {
      options: allDeployments.map(({ name }) => ({
        label: name,
        value: name,
      })),
    },
  ];

  return (
    <Dropdown
      buttonClassName="py-0.5"
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
      optionGroups={deploymentOptions}
    />
  );
};
