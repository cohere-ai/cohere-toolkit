import React, { useEffect, useState } from 'react';

import { AgentForm, AgentFormFieldKeys, AgentFormFields } from '@/components/Agents/AgentForm';
import { IconButton } from '@/components/IconButton';
import { Button, Spinner, Text } from '@/components/Shared';
import { useAgent, useIsAgentNameUnique, useUpdateAgent } from '@/hooks/agents';
import { useSession } from '@/hooks/session';
import { useNotify } from '@/hooks/toast';
import { useSettingsStore } from '@/stores';
import { cn } from '@/utils';

type Props = {
  agentId?: string;
};

export const UpdateAgentDrawer: React.FC<Props> = ({ agentId }) => {
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
    console.debug(
      Object.values(requredFields).every(Boolean),
      !Object.keys(fieldErrors).length,
      isDirty()
    );
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
      });
    }
  }, [agent, isLoading]);

  const handleClose = () => {
    setSettings({ isEditAgentDrawerOpen: false });
  };

  const handleChange = (key: Omit<AgentFormFieldKeys, 'tools'>, value: string) => {
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

  const handleSubmit = async () => {
    if (!canSubmit || !agentId) return;

    try {
      setIsSubmitting(true);
      await updateAgent({ ...fields, agentId });
      setIsSubmitting(false);
      success(`Updated ${agent?.name}`);
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
        '2xl:agent-drawer-2xl absolute left-0 top-0 z-configuration-drawer w-full md:relative md:w-agent-drawer lg:w-agent-drawer-lg'
      )}
    >
      <header className="flex h-header items-center justify-between border-b border-marble-400 pl-14 pr-6">
        <Text>{isAgentCreator ? `Update ${agent.name}` : `About ${agent.name}`}</Text>
        <IconButton iconName="close" onClick={handleClose} />
      </header>
      <div className="flex flex-col gap-y-5 px-14 py-8">
        <AgentForm
          fields={fields}
          errors={fieldErrors}
          onChange={handleChange}
          onToolToggle={handleToolToggle}
          disabled={!isAgentCreator}
        />
        {isAgentCreator && (
          <>
            <div className="w-full rounded border-2 border-dashed border-marble-500 bg-secondary-50 px-5 py-4">
              Updating {agent.name} will affect everyone using the assistant
            </div>
            <Button
              className="mt-14 self-end"
              splitIcon="check-mark"
              onClick={handleSubmit}
              disabled={!canSubmit}
            >
              {isSubmitting ? 'Updating' : 'Update'}
            </Button>
          </>
        )}
      </div>
    </div>
  );
};
