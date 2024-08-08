'use client';

import { useLocalStorageValue } from '@react-hookz/web';
import Link from 'next/link';
import React, { useEffect, useState } from 'react';

import {
  AgentSettingsFields,
  AgentSettingsForm,
} from '@/components/Agents/AgentSettings/AgentSettingsForm';
import { DeleteAgent } from '@/components/Agents/DeleteAgent';
import { Button, Icon, Spinner, Text } from '@/components/Shared';
import { DEFAULT_AGENT_MODEL, DEPLOYMENT_COHERE_PLATFORM } from '@/constants';
import { useContextStore } from '@/context';
import { useAgent, useIsAgentNameUnique, useUpdateAgent } from '@/hooks/agents';
import { useNotify } from '@/hooks/toast';

type Props = {
  agentId: string;
};

export const UpdateAgent: React.FC<Props> = ({ agentId }) => {
  const { error, success } = useNotify();
  const { data: agent, isLoading } = useAgent({ agentId });
  const { open, close } = useContextStore();

  const { mutateAsync: updateAgent } = useUpdateAgent();
  const isAgentNameUnique = useIsAgentNameUnique();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fields, setFields] = useState<AgentSettingsFields>();

  const { set: setPendingAssistant } = useLocalStorageValue<AgentSettingsFields>(
    'pending_assistant',
    {
      defaultValue: fields,
      initializeWithValue: false,
    }
  );

  useEffect(() => {
    if (agent) {
      setFields({
        name: agent.name,
        description: agent.description,
        deployment: agent.deployment ?? DEPLOYMENT_COHERE_PLATFORM,
        model: agent.model ?? DEFAULT_AGENT_MODEL,
        tools: agent.tools,
        preamble: agent.preamble,
        tools_metadata: agent.tools_metadata,
      });
    }
  }, [agent]);

  const handleOpenDeleteModal = () => {
    if (!agent || !agent.name || !agentId) return;
    open({
      title: `Delete ${agent.name}`,
      content: <DeleteAgent name={agent.name} agentId={agentId} onClose={close} />,
    });
  };

  if (isLoading && !fields) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (!agent || !fields) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Text className="text-danger-350">Unable to load assistant information</Text>
      </div>
    );
  }

  const handleSubmit = async () => {
    if (!agentId) return;
    const tools_metadata = (fields.tools_metadata ?? []).map((tool) => ({
      ...tool,
      id: agent.tools_metadata?.find((t) => t.tool_name === tool.tool_name)?.id,
    }));
    try {
      setIsSubmitting(true);
      const newAgent = await updateAgent({ request: { ...fields, tools_metadata }, agentId });
      setIsSubmitting(false);
      success(`Updated ${newAgent?.name}`);
    } catch (e) {
      setIsSubmitting(false);
      error(`Failed to update ${agent?.name}`);
      console.error(e);
    }
  };

  return (
    <div className="relative flex h-full w-full flex-col overflow-y-auto">
      <header className="flex flex-col space-y-5 border-b px-12 py-10 dark:border-volcanic-150">
        <div className="flex items-center space-x-2">
          <Link href="/discover">
            <Text className="dark:text-volcanic-600">Explore assistants</Text>
          </Link>
          <Icon name="chevron-right" className="dark:text-volcanic-600" />
          <Text className="dark:text-volcanic-600">Edit assistant</Text>
        </div>
        <Text styleAs="h4">Edit {agent.name}</Text>
      </header>
      <div className="flex flex-col overflow-y-auto">
        <AgentSettingsForm
          source="update"
          fields={fields}
          setFields={setFields}
          onSubmit={handleSubmit}
          savePendingAssistant={() => setPendingAssistant(fields)}
          agentId={agentId}
        />
        <div className="space-y-5 p-8">
          <div className="flex w-full max-w-screen-md items-center justify-between ">
            <Button label="Cancel" kind="secondary" href="/discover" />
            <Button
              label="Update"
              theme="default"
              kind="cell"
              icon={'checkmark'}
              iconOptions={{ customIcon: isSubmitting ? <Spinner /> : undefined }}
              disabled={
                isSubmitting ||
                !fields.name.trim() ||
                isAgentNameUnique(fields.name.trim(), agent.id)
              }
              onClick={handleSubmit}
            />
          </div>
          <Button
            label="Delete assistant"
            icon="trash"
            theme="danger"
            kind="secondary"
            onClick={handleOpenDeleteModal}
          />
        </div>
      </div>
    </div>
  );
};
