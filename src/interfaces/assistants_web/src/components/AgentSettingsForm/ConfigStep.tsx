'use client';

import React, { useState } from 'react';

import { AgentSettingsFields } from '@/components/AgentSettingsForm';
import { Dropdown, Slider } from '@/components/UI';
import { useListAllDeployments } from '@/hooks';

type Props = {
  fields: AgentSettingsFields;
  nameError?: string;
  setFields: (fields: AgentSettingsFields) => void;
};

export const ConfigStep: React.FC<Props> = ({ fields, setFields }) => {
  const [selectedModelValue, setSelectedModelValue] = useState<string | undefined>(fields.model);
  const [selectedTemperatureValue, setSelectedTemperatureValue] = useState<number | undefined>(
    fields.temperature
  );

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
        value={selectedModelValue}
        onChange={(model) => {
          setFields({ ...fields, model: model });
          setSelectedModelValue(model);
        }}
      />
      <Slider
        label="Temperature"
        min={0}
        max={1.0}
        step={0.1}
        value={selectedTemperatureValue || 0}
        onChange={(temperature) => {
          setFields({ ...fields, temperature: temperature });
          setSelectedTemperatureValue(temperature);
        }}
      ></Slider>
    </div>
  );
};
