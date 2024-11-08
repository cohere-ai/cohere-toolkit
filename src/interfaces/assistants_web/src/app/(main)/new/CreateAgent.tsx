'use client';

import { cloneDeep } from 'lodash';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';

import { AgentSettingsFields, AgentSettingsForm } from '@/components/AgentSettingsForm';
import { MobileHeader } from '@/components/Global';
import { Button, Icon, Text } from '@/components/UI';
import {
  DEFAULT_AGENT_MODEL,
  DEFAULT_PREAMBLE,
  DEPLOYMENT_COHERE_PLATFORM,
} from '@/constants';
import { useContextStore } from '@/context';
import { useCreateAgent, useListDefaultTool, useNotify } from '@/hooks';

interface FieldValues {
  name: string;
  description: string;
  preamble: string;
  deployment: string;
  model: string;
  tools: string[]; // Specify the type here (e.g., string[])
  is_private: boolean;
};

const DEFAULT_FIELD_VALUES: FieldValues = {
  name: '',
  description: '',
  preamble: DEFAULT_PREAMBLE,
  deployment: DEPLOYMENT_COHERE_PLATFORM,
  model: DEFAULT_AGENT_MODEL,
  tools: [],
  is_private: false,
};

/**
 * @description Form to create a new agent.
 */
export const CreateAgent: React.FC = () => {
  const router = useRouter();
  const { open, close } = useContextStore();

  const { error } = useNotify();
  const { mutateAsync: createAgent } = useCreateAgent();
  const { data: defaultTools = []} = useListDefaultTool();
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Set default fields
  const defaultToolIds = defaultTools
  .map((t) => t.name)
  .filter((name): name is string => name !== null && name !== undefined);
  const defaultFieldValues = cloneDeep(DEFAULT_FIELD_VALUES)
  defaultFieldValues.tools.push(...defaultToolIds);
  const [fields, setFields] = useState<AgentSettingsFields>(defaultFieldValues);

  const handleOpenSubmitModal = () => {
    if (fields.is_private) {
      handleSubmit();
      return;
    }

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
    try {
      setIsSubmitting(true);
      const agent = await createAgent(fields);
      close();
      router.push(`/a/${agent.id}`);
    } catch (e) {
      setIsSubmitting(false);
      close();
      error('Failed to create assistant');
      console.error(e);
    }
  };

  return (
    <div className="flex h-full w-full flex-col overflow-y-auto rounded-lg border border-marble-950 bg-marble-980 pb-6 dark:border-volcanic-100 dark:bg-volcanic-100">
      <header className="flex flex-col gap-y-3 border-b px-4 py-6 dark:border-volcanic-150 lg:px-10 lg:py-10">
        <MobileHeader />
        <div className="flex items-center space-x-2">
          <Link href="/discover">
            <Text className="dark:text-volcanic-600">Explore assistants</Text>
          </Link>
          <Icon name="chevron-right" className="dark:text-volcanic-600" />
          <Text className="dark:text-volcanic-600">Create assistant</Text>
        </div>
        <Text styleAs="h4">Create assistant</Text>
      </header>
      <div className="flex flex-grow flex-col gap-y-8 overflow-y-hidden px-8 pt-8">
        <div className="flex-grow overflow-y-auto">
          <AgentSettingsForm
            source="create"
            fields={fields}
            setFields={setFields}
            onSubmit={handleOpenSubmitModal}
          />
        </div>
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
      <Button label="Cancel" kind="secondary" onClick={onClose} />
      <Button
        label={isSubmitting ? 'Creating assistant' : 'Yes, make it public'}
        onClick={onSubmit}
        icon="arrow-right"
        iconPosition="end"
        disabled={isSubmitting}
      />
    </div>
  </div>
);
