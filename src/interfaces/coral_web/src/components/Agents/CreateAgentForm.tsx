import { useRouter } from 'next/router';
import React, { useContext, useState } from 'react';

import {
  AgentForm,
  AgentFormFieldKeys,
  CreateAgentFormFields,
} from '@/components/Agents/AgentForm';
import { Button, Text } from '@/components/Shared';
import { DEFAULT_AGENT_MODEL, DEPLOYMENT_COHERE_PLATFORM } from '@/constants';
import { ModalContext } from '@/context/ModalContext';
import { useCreateAgent, useIsAgentNameUnique, useRecentAgents } from '@/hooks/agents';
import { useNotify } from '@/hooks/toast';

/**
 * @description Form to create a new agent.
 */
export const CreateAgentForm: React.FC = () => {
  const router = useRouter();
  const { open, close } = useContext(ModalContext);
  const { error } = useNotify();
  const { mutateAsync: createAgent } = useCreateAgent();
  const { addRecentAgentId } = useRecentAgents();
  const isAgentNameUnique = useIsAgentNameUnique();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fields, setFields] = useState<CreateAgentFormFields>({
    name: '',
    description: '',
    preamble: '',
    deployment: DEPLOYMENT_COHERE_PLATFORM,
    model: DEFAULT_AGENT_MODEL,
    tools: [],
  });

  const fieldErrors = {
    ...(isAgentNameUnique(fields.name) ? {} : { name: 'Assistant name must be unique' }),
  };

  const canSubmit = (() => {
    const { name, deployment, model } = fields;
    const requredFields = { name, deployment, model };
    return Object.values(requredFields).every(Boolean) && !Object.keys(fieldErrors).length;
  })();

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

  const handleOpenSubmitModal = () => {
    open({
      title: `Create ${fields.name}?`,
      content: (
        <SubmitModalContent
          agentName={fields.name}
          onSubmit={handleSubmit}
          isSubmitting={isSubmitting}
          onClose={close}
        />
      ),
    });
  };
  const handleSubmit = async () => {
    if (!canSubmit) return;

    try {
      setIsSubmitting(true);
      const agent = await createAgent(fields);
      addRecentAgentId(agent.id);
      setFields({
        name: '',
        description: '',
        preamble: '',
        deployment: '',
        model: '',
        tools: [],
      });
      close();
      setIsSubmitting(false);
      router.push(`/agents/${agent.id}`, undefined, { shallow: true });
    } catch (e) {
      setIsSubmitting(false);
      close();
      error('Failed to create assistant');
      console.error(e);
    }
  };

  return (
    <div className="relative flex h-full w-full flex-col">
      <div className="flex-grow overflow-y-scroll">
        <div className="flex max-w-[650px] flex-col gap-y-2 p-10">
          <Text styleAs="h4">Create an Assistant</Text>
          <Text className="text-volcanic-700">
            Create an unique assistant and share with your org
          </Text>
          <AgentForm
            fields={fields}
            onChange={handleChange}
            onToolToggle={handleToolToggle}
            errors={fieldErrors}
            className="mt-6"
          />
        </div>
      </div>
      <div className="flex w-full flex-shrink-0 justify-end border-t border-marble-400 bg-white px-4 py-8">
        <Button kind="green" splitIcon="add" onClick={handleOpenSubmitModal} disabled={!canSubmit}>
          Create
        </Button>
      </div>
    </div>
  );
};

const SubmitModalContent: React.FC<{
  agentName: string;
  isSubmitting: boolean;
  onSubmit: () => void;
  onClose: () => void;
}> = ({ agentName, isSubmitting, onSubmit, onClose }) => (
  <div className="flex flex-col gap-y-20">
    <Text>
      Your assistant {agentName} is about be visible publicly. Everyone in your organization will be
      able to see and use it.
    </Text>
    <div className="flex justify-between">
      <Button kind="secondary" onClick={onClose}>
        Cancel
      </Button>
      <Button kind="green" onClick={onSubmit} splitIcon="arrow-right" disabled={isSubmitting}>
        {isSubmitting ? 'Creating assistant' : 'Yes, make it public'}
      </Button>
    </div>
  </div>
);
