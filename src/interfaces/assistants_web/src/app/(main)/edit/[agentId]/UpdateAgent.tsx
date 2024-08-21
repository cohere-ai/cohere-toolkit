'use client';

import { useLocalStorageValue } from '@react-hookz/web';
import Link from 'next/link';
import React, { useState } from 'react';

import { AgentPublic } from '@/cohere-client';
import { AgentSettingsFields, AgentSettingsForm } from '@/components/AgentSettingsForm';
import { MobileHeader } from '@/components/Global';
import { DeleteAgent } from '@/components/Modals/DeleteAgent';
import { Button, Icon, Spinner, Text } from '@/components/UI';
import { DEFAULT_AGENT_MODEL } from '@/constants/conversation';
import { DEPLOYMENT_COHERE_PLATFORM } from '@/constants/setup';
import { useContextStore } from '@/context';
import { useIsAgentNameUnique, useUpdateAgent } from '@/hooks/agents';
import { useNotify } from '@/hooks/toast';

type Props = {
  agent: AgentPublic;
};

export const UpdateAgent: React.FC<Props> = ({ agent }) => {
  const { error, success } = useNotify();
  const { open, close } = useContextStore();

  const { mutateAsync: updateAgent } = useUpdateAgent();
  const isAgentNameUnique = useIsAgentNameUnique();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fields, setFields] = useState<AgentSettingsFields>({
    name: agent.name,
    description: agent.description,
    deployment: agent.deployment ?? DEPLOYMENT_COHERE_PLATFORM,
    model: agent.model ?? DEFAULT_AGENT_MODEL,
    tools: agent.tools,
    preamble: agent.preamble,
    tools_metadata: agent.tools_metadata,
    is_private: agent.is_private,
  });

  const { set: setPendingAssistant } = useLocalStorageValue<AgentSettingsFields>(
    'pending_assistant',
    {
      defaultValue: fields,
      initializeWithValue: false,
    }
  );

  const handleOpenDeleteModal = () => {
    open({
      title: `Delete ${agent.name}`,
      content: <DeleteAgent name={agent.name} agentId={agent.id} onClose={close} />,
    });
  };

  const handleSubmit = async () => {
    const tools_metadata = (fields.tools_metadata ?? []).map((tool) => ({
      ...tool,
      id: agent.tools_metadata?.find((t) => t.tool_name === tool.tool_name)?.id,
    }));
    try {
      setIsSubmitting(true);
      const newAgent = await updateAgent({
        request: { ...fields, tools_metadata },
        agentId: agent.id,
      });
      setIsSubmitting(false);
      success(`Updated ${newAgent?.name}`);
    } catch (e) {
      setIsSubmitting(false);
      error(`Failed to update ${agent?.name}`);
      console.error(e);
    }
  };

  return (
    <div className="flex h-full w-full flex-col overflow-y-auto">
      <header className="flex flex-col gap-y-3 border-b px-4 py-6 dark:border-volcanic-150 lg:px-10 lg:py-10">
        <MobileHeader />
        <div className="flex items-center space-x-2">
          <Link href="/discover">
            <Text className="dark:text-volcanic-600">Explore assistants</Text>
          </Link>
          <Icon name="chevron-right" className="dark:text-volcanic-600" />
          <Text className="dark:text-volcanic-600">Edit assistant</Text>
        </div>
        <Text styleAs="h4">Edit {agent.name}</Text>
      </header>
      <div className="flex flex-grow flex-col gap-y-8 overflow-y-hidden px-8 pt-8">
        <div className="flex-grow overflow-y-auto">
          <AgentSettingsForm
            source="update"
            fields={fields}
            setFields={setFields}
            onSubmit={handleSubmit}
            savePendingAssistant={() => setPendingAssistant(fields)}
            agentId={agent.id}
          />
        </div>
        <div className="space-y-5 pb-8">
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
