import React, { useContext, useMemo, useState } from 'react';

import {
  BasicButton,
  Button,
  Dropdown,
  DropdownOptionGroups,
  Input,
  Text,
} from '@/components/Shared';
import { ModalContext } from '@/context/ModalContext';
import { useListAllDeployments } from '@/hooks/deployments';
import { useUpdateDeploymentEnvVariables } from '@/hooks/envVariables';
import { cn } from '@/utils';

export const EditEnvVariablesButton: React.FC<{ className?: string }> = ({ className }) => {
  const { open, close } = useContext(ModalContext);

  const handleClick = () => {
    open({
      title: 'Edit .env variables',
      content: <EditEnvVariablesModal onClose={close} />,
    });
  };

  return (
    <BasicButton
      label="Edit .env variables"
      size="sm"
      kind="minimal"
      className={cn('py-0', className)}
      onClick={handleClick}
    />
  );
};

const EditEnvVariablesModal: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const { data: deployments } = useListAllDeployments();
  const { mutateAsync: updateDeploymentEnvVariables } = useUpdateDeploymentEnvVariables();

  const [deployment, setDeployment] = useState<string | undefined>();
  const [envVariables, setEnvVariables] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasError, setHasError] = useState(false);

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
    if (hasError) {
      setHasError(false);
    }

    setDeployment(newDeployment);
    const selectedDeployment = deployments?.find(({ name }) => name === newDeployment);
    const emptyEnvVariables =
      selectedDeployment?.env_vars.reduce<Record<string, string>>((acc, envVar) => {
        acc[envVar] = '';
        return acc;
      }, {}) ?? {};
    setEnvVariables(emptyEnvVariables);
  };

  const handleEnvVariableChange = (envVar: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    if (hasError) {
      setHasError(false);
    }

    setEnvVariables({ ...envVariables, [envVar]: e.target.value });
  };

  const handleSubmit = async () => {
    if (!deployment) return;

    if (hasError) {
      setHasError(false);
    }

    try {
      setIsSubmitting(true);
      await updateDeploymentEnvVariables({ name: deployment, env_vars: envVariables });
      setIsSubmitting(false);
      onClose();
    } catch (e) {
      console.error(e);
      setHasError(true);
      setIsSubmitting(false);
    }
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
          placeholder="value"
          label={envVar}
          value={envVariables[envVar]}
          onChange={handleEnvVariableChange(envVar)}
        />
      ))}

      {hasError && (
        <Text styleAs="p-sm" className="text-danger-500">
          An error occurred. Please try again.
        </Text>
      )}

      <span className="mt-10 flex items-center justify-between">
        <BasicButton kind="minimal" size="sm" label="Cancel" onClick={onClose} />
        <Button
          label={isSubmitting ? 'Submitting...' : 'Submit'}
          onClick={handleSubmit}
          splitIcon="arrow-right"
          disabled={isSubmitting}
        />
      </span>
    </div>
  );
};
