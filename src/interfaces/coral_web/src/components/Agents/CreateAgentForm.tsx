import { useRouter } from 'next/router';
import React, { useState } from 'react';

import { AgentForm, AgentFormFields, AgentFormTextFieldKeys } from '@/components/Agents/AgentForm';
import { Button, Text } from '@/components/Shared';
import { useCreateAgent, useIsAgentNameUnique } from '@/hooks/agents';
import { useListAllDeployments } from '@/hooks/deployments';
import { useParamsStore } from '@/stores';

/**
 * @description Form to create a new agent.
 */
export const CreateAgentForm: React.FC = () => {
  const router = useRouter();
  const { mutateAsync: createAgent } = useCreateAgent();
  const {
    params: { preamble },
  } = useParamsStore();
  const { data: deployments } = useListAllDeployments();
  const isAgentNameUnique = useIsAgentNameUnique();

  const [fields, setFields] = useState<AgentFormFields>({
    name: '',
    description: '',
    preamble,
    deployment: 'Azure',
    model: '',
    tools: [],
  });

  const [envVariables, setEnvVariables] = useState<Record<string, string>>(() => {
    const selectedDeployment = deployments?.find(({ name }) => name === fields.deployment);
    return (
      selectedDeployment?.env_vars.reduce<Record<string, string>>((acc, envVar) => {
        acc[envVar] = '';
        return acc;
      }, {}) ?? {}
    );
  });

  const fieldErrors = {
    ...(isAgentNameUnique(fields.name) ? {} : { name: 'Assistant name must be unique' }),
  };

  const canSubmit = (() => {
    const { tools, preamble, ...requredFields } = fields;
    return Object.values(requredFields).every(Boolean) && !Object.keys(fieldErrors).length;
  })();

  const handleChange = (key: AgentFormTextFieldKeys, value: string) => {
    console.debug(key, value);
    setFields({
      ...fields,
      [key as string]: value,
    });
  };

  const handleToolToggle = (toolName: string, checked: boolean) => {
    const enabledTools = [...(fields.tools ? fields.tools : [])];
    setFields({
      ...fields,
      tools: checked ? [...enabledTools, toolName] : enabledTools.filter((t) => t !== toolName),
    });
  };

  const handleEnvVariableChange = (envVar: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setEnvVariables({ ...envVariables, [envVar]: e.target.value });
  };

  const handleSubmit = async () => {
    if (!canSubmit) return;

    try {
      await createAgent(fields);
      router.push('/agents', undefined, { shallow: true });
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="relative h-full w-full">
      <div className="flex h-full max-w-[650px] flex-col gap-y-2 p-10">
        <Text styleAs="h4">Create an Assistant</Text>
        <Text className="text-volcanic-700">
          Create an unique assistant and share with your org
        </Text>
        <AgentForm
          fields={fields}
          envVariables={envVariables}
          onChange={handleChange}
          onToolToggle={handleToolToggle}
          onEnvVariableChange={handleEnvVariableChange}
          errors={fieldErrors}
          className="mt-6"
        />
      </div>
      <div className="absolute bottom-0 right-0 flex w-full justify-end border-t border-marble-400 bg-white px-4 py-8">
        <Button splitIcon="add" onClick={handleSubmit} disabled={!canSubmit}>
          Create
        </Button>
      </div>
    </div>
  );
};
