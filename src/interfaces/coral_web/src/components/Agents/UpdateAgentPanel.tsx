import React, { useEffect, useState } from 'react';

import { AgentForm, AgentFormFieldKeys, AgentFormFields } from '@/components/Agents/AgentForm';
import { IconButton } from '@/components/IconButton';
import { Banner, Button, Spinner, Text } from '@/components/Shared';
import { useAgent, useIsAgentNameUnique, useUpdateAgent } from '@/hooks/agents';
import { useSession } from '@/hooks/session';
import { useNotify } from '@/hooks/toast';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';

type Props = {
  agentId?: string;
};

export const UpdateAgentPanel: React.FC<Props> = ({ agentId }) => {
  const { error, success } = useNotify();
  const { setSettings } = useSettingsStore();
  const { data: agent, isLoading } = useAgent({ agentId });
  const { mutateAsync: updateAgent } = useUpdateAgent();
  const isAgentNameUnique = useIsAgentNameUnique();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fields, setFields] = useState<AgentFormFields>({
    name: '',
    description: '',
    deployment: '',
    model: '',
    tools: [],
  });

  const { userId } = useSession();
  const isAgentCreator = agent && agent.user_id === userId;

  const isDirty = () => {
    if (!agent) return false;
    return Object.entries(fields).some(
      ([key, value]) => agent[key as AgentFormFieldKeys] !== value
    );
  };

  const fieldErrors = {
    ...(isAgentNameUnique(fields.name, agentId) ? {} : { name: 'Assistant name must be unique' }),
  };

  const canSubmit = (() => {
    const { name, deployment, model } = fields;
    const requredFields = { name, deployment, model };
    return (
      Object.values(requredFields).every(Boolean) && !Object.keys(fieldErrors).length && isDirty()
    );
  })();

  useEffect(() => {
    if (agent) {
      setFields({
        name: agent.name,
        description: agent.description,
        deployment: agent.deployment,
        model: agent.model,
        tools: agent.tools,
        preamble: agent.preamble,
      });
    }
  }, [agent]);

  const handleClose = () => {
    setSettings({ isEditAgentPanelOpen: false });
  };

  const handleChange = (key: Omit<AgentFormFieldKeys, 'tools'>, value: string) => {
    setFields({
      ...fields,
      [key as string]: value,
    });
  };

  const handleToolToggle = (toolName: string, checked: boolean) => {
    const enabledTools = fields.tools ?? [];
    setFields({
      ...fields,
      tools: checked ? [...enabledTools, toolName] : enabledTools.filter((t) => t !== toolName),
    });
  };

  const handleSubmit = async () => {
    if (!canSubmit || !agentId) return;

    try {
      setIsSubmitting(true);
      const newAgent = await updateAgent({ ...fields, agentId });
      setIsSubmitting(false);
      success(`Updated ${newAgent?.name}`);
    } catch (e) {
      setIsSubmitting(false);
      error(`Failed to update ${agent?.name}`);
      console.error(e);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Text className="text-danger-500">Unable to load assistant information</Text>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'flex h-full flex-col bg-marble-100',
        '2xl:agent-panel-2xl absolute left-0 top-0 w-full md:relative md:w-agent-panel lg:w-agent-panel-lg'
      )}
    >
      <header className="flex h-header flex-shrink-0 items-center justify-between border-b border-marble-400 pl-14 pr-6">
        <Text>{isAgentCreator ? `Update ${agent.name}` : `About ${agent.name}`}</Text>
        <IconButton iconName="close" onClick={handleClose} />
      </header>
      <div className="flex flex-col gap-y-5 overflow-y-auto px-14 py-8">
        <AgentForm
          fields={fields}
          errors={fieldErrors}
          onChange={handleChange}
          onToolToggle={handleToolToggle}
          disabled={!isAgentCreator}
        />
        {isAgentCreator && (
          <>
            <Banner className="w-full">
              Updating {agent.name} will affect everyone using the assistant
            </Banner>
            <Button
              className="mt-14 self-end"
              splitIcon="check-mark"
              label={isSubmitting ? 'Updating' : 'Update'}
              onClick={handleSubmit}
              disabled={!canSubmit}
            />
          </>
        )}
      </div>
    </div>
  );
};
