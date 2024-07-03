import React, { useEffect, useState } from 'react';

import {
  AgentForm,
  AgentFormFieldKeys,
  UpdateAgentFormFields,
} from '@/components/Agents/AgentForm';
import { IconButton } from '@/components/IconButton';
import { Banner, Button, Spinner, Text } from '@/components/Shared';
import { useAgent, useIsAgentNameUnique, useUpdateAgent } from '@/hooks/agents';
import { useSession } from '@/hooks/session';
import { useNotify } from '@/hooks/toast';
import { useAgentsStore } from '@/stores';
import { cn } from '@/utils';

type Props = {
  agentId?: string;
};

export const UpdateAgentPanel: React.FC<Props> = ({ agentId }) => {
  const { error, success } = useNotify();

  const { setEditAgentPanelOpen } = useAgentsStore();
  const { data: agent, isLoading } = useAgent({ agentId });
  const { mutateAsync: updateAgent } = useUpdateAgent();
  const isAgentNameUnique = useIsAgentNameUnique();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fields, setFields] = useState<UpdateAgentFormFields>({
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
    ...(isAgentNameUnique(fields.name ?? '', agentId)
      ? {}
      : { name: 'Assistant name must be unique' }),
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
    setEditAgentPanelOpen(false);
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
      const newAgent = await updateAgent({ request: fields, agentId });
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
    <>
      <header
        className={cn(
          'flex h-header flex-shrink-0 items-center justify-between border-b border-marble-400',
          'pl-4 pr-3 lg:pl-10 lg:pr-8'
        )}
      >
        <Text>{isAgentCreator ? `Update ${agent.name}` : `About ${agent.name}`}</Text>
        <IconButton iconName="close" onClick={handleClose} />
      </header>
      <div className={cn('flex flex-col gap-y-5 overflow-y-auto', 'p-4 lg:p-10')}>
        {isAgentCreator && <InfoBanner agentName={agent.name} className="flex md:hidden" />}
        <AgentForm
          fields={fields}
          errors={fieldErrors}
          onChange={handleChange}
          onToolToggle={handleToolToggle}
          disabled={!isAgentCreator}
        />
      </div>
      {isAgentCreator && (
        <div className="flex flex-col gap-y-12 px-4 py-4 lg:px-10 lg:pb-8 lg:pt-0">
          <InfoBanner agentName={agent.name} className="hidden md:flex" />
          <Button
            className="self-end"
            splitIcon="check-mark"
            label={isSubmitting ? 'Updating' : 'Update'}
            onClick={handleSubmit}
            disabled={!canSubmit}
          />
        </div>
      )}
    </>
  );
};

const InfoBanner: React.FC<{ agentName: string; className?: string }> = ({
  agentName,
  className,
}) => (
  <Banner theme="secondary" size="sm" className={cn('w-full', className)}>
    Updating {agentName} will affect everyone using the assistant
  </Banner>
);
