'use client';

import { useState } from 'react';

import { AgentSettingsFields } from '@/components/AgentSettingsForm';
import { Dropdown } from '@/components/UI';
import { DEFAULT_AGENT_MODEL } from '@/constants';
import { useListAllDeployments } from '@/hooks';

type Props = {
  fields: AgentSettingsFields;
  isNewAssistant: boolean;
  nameError?: string;
  setFields: (fields: AgentSettingsFields) => void;
};

export const ConfigStep: React.FC<Props> = ({ fields, setFields }) => {
  const [selectedValue, setSelectedValue] = useState<string | undefined>(fields.model);

  const { data: deployments } = useListAllDeployments();

  const selectedDeploymentModels = deployments?.find(
    ({ name }) => name === fields.deployment
  )?.models;
  const modelOptions = selectedDeploymentModels?.map((model) => ({ value: model, label: model }));

  return (
    <div className="flex flex-col space-y-4">
      <Dropdown
        label="Model"
        options={modelOptions ?? []}
        value={selectedValue}
        onChange={(model) => {
          setFields({ ...fields, model: model });
          setSelectedValue(model);
        }}
      />
    </div>
  );
};
