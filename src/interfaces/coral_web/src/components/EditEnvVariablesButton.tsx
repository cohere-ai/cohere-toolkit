'use client';

import React, { useContext, useMemo, useState } from 'react';

import { BasicButton, Button, Dropdown, DropdownOptionGroups, Input } from '@/components/Shared';
import { STRINGS } from '@/constants/strings';
import { ModalContext } from '@/context/ModalContext';
import { useListAllDeployments, useUpdateDeploymentConfig } from '@/hooks/deployments';
import { useParamsStore } from '@/stores';

/**
 * @description Button to trigger a modal to edit .env variables.
 */
export const EditEnvVariablesButton: React.FC<{ className?: string }> = () => {
  const { open, close } = useContext(ModalContext);

  const handleClick = () => {
    open({
      title: STRINGS.configureModelDeploymentTitle,
      content: <EditEnvVariablesModal onClose={close} defaultDeployment="" />,
    });
  };

  return (
    <BasicButton
      label={STRINGS.configure}
      size="sm"
      kind="minimal"
      className="py-0"
      onClick={handleClick}
    />
  );
};

/**
 * @description Renders a modal to edit a selected deployment's config
 */
export const EditEnvVariablesModal: React.FC<{
  defaultDeployment: string;
  onClose: () => void;
}> = ({ defaultDeployment, onClose }) => {
  const { data: deployments } = useListAllDeployments();
  const updateConfigMutation = useUpdateDeploymentConfig();

  const [deployment, setDeployment] = useState<string | undefined>(defaultDeployment);
  const [envVariables, setEnvVariables] = useState<Record<string, string>>(() => {
    const selectedDeployment = deployments?.find(({ name }) => name === defaultDeployment);
    return selectedDeployment?.config ?? {};
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { setParams } = useParamsStore();

  const deploymentOptions: DropdownOptionGroups = useMemo(
    () => [
      {
        options: (deployments ?? []).map(({ name }) => ({
          label: name,
          value: name,
        })),
      },
    ],
    [deployments]
  );

  const handleDeploymentChange = (newDeployment: string) => {
    setDeployment(newDeployment);
    const selectedDeployment = deployments?.find(({ name }) => name === newDeployment);
    setEnvVariables(selectedDeployment?.config ?? {});
  };

  const handleEnvVariableChange = (envVar: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setEnvVariables({ ...envVariables, [envVar]: e.target.value });
  };

  const handleSubmit = async () => {
    if (!deployment) return;
    const selectedDeployment = deployments?.find(({ name }) => name === deployment);
    if (!selectedDeployment) return;

    setIsSubmitting(true);

    // Only update the env variables that have changed. We need to do this for now because the backend
    // reports config values as "*****" and we don't want to overwrite the real values with these
    // obscured values.
    const originalEnvVariables = selectedDeployment.config ?? {};
    const updatedEnvVariables = Object.keys(envVariables).reduce((acc, key) => {
      if (envVariables[key] !== originalEnvVariables[key]) {
        acc[key] = envVariables[key];
      }
      return acc;
    }, {} as Record<string, string>);

    await updateConfigMutation.mutateAsync({
      deploymentId: selectedDeployment.id,
      config: updatedEnvVariables,
    });
    setIsSubmitting(false);
    onClose();
  };

  return (
    <div className="flex flex-col gap-y-4 p-4">
      <Dropdown
        value={deployment}
        optionGroups={deploymentOptions}
        onChange={handleDeploymentChange}
      />

      {Object.keys(envVariables).map((envVar) => (
        <Input
          key={envVar}
          placeholder={STRINGS.value}
          label={envVar}
          type="text"
          value={envVariables[envVar]}
          onChange={handleEnvVariableChange(envVar)}
        />
      ))}

      <span className="mt-10 flex items-center justify-between">
        <BasicButton kind="minimal" size="sm" label={STRINGS.cancel} onClick={onClose} />
        <Button
          label={isSubmitting ? STRINGS.saving : STRINGS.save}
          onClick={handleSubmit}
          splitIcon="arrow-right"
          disabled={isSubmitting}
        />
      </span>
    </div>
  );
};
