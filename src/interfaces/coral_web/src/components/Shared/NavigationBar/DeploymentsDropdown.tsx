import { useContext } from 'react';

import { Dropdown, DropdownOptionGroups, Text } from '@/components/Shared';
import { BannerContext } from '@/context/BannerContext';
import { useListAllDeployments, useListDeployments } from '@/hooks/deployments';
import { useParamsStore } from '@/stores';

export const DeploymentsDropdown: React.FC = () => {
  const { message: bannerMessage, setMessage } = useContext(BannerContext);
  const {
    params: { deployment },
    setParams,
  } = useParamsStore();
  const { data: availableDeployments } = useListDeployments();
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
        if (availableDeployments?.every((ad) => ad.name !== deploymentName)) {
          setMessage(
            <Text as="span">
              If you wish to use <b className="font-medium">{deploymentName}</b>, please configure
              your .env file with these variables:{' '}
              <b className="font-medium">{deployment?.env_vars.join(', ')}</b>.
            </Text>
          );
        } else if (bannerMessage) {
          setMessage('');
        }
        setParams({ deployment: deploymentName });
      }}
      optionGroups={deploymentOptions}
    />
  );
};
