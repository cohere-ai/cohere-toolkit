'use client';

import { useLocalStorageValue } from '@react-hookz/web';
import { cloneDeep } from 'lodash';
import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';

import {
  AgentSettingsFields,
  AgentSettingsForm,
} from '@/components/Agents//AgentSettings/AgentSettingsForm';
import { Button, Icon, Text } from '@/components/Shared';
import {
  DEFAULT_AGENT_MODEL,
  DEFAULT_AGENT_TOOLS,
  DEFAULT_PREAMBLE,
  DEPLOYMENT_COHERE_PLATFORM,
} from '@/constants';
import { useContextStore } from '@/context';
import { useCreateAgent } from '@/hooks/agents';
import { useNotify } from '@/hooks/toast';

const DEFAULT_FIELD_VALUES = {
  name: '',
  description: '',
  preamble: DEFAULT_PREAMBLE,
  deployment: DEPLOYMENT_COHERE_PLATFORM,
  model: DEFAULT_AGENT_MODEL,
  tools: DEFAULT_AGENT_TOOLS,
};
/**
 * @description Form to create a new agent.
 */
export const CreateAgent: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { open, close } = useContextStore();

  const { error } = useNotify();
  const { mutateAsync: createAgent } = useCreateAgent();

  const [fields, setFields] = useState<AgentSettingsFields>(cloneDeep(DEFAULT_FIELD_VALUES));
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    value: pendingAssistant,
    set: setPendingAssistant,
    remove: removePendingAssistant,
  } = useLocalStorageValue<AgentSettingsFields>('pending_assistant', {
    initializeWithValue: false,
    defaultValue: undefined,
  });

  const queryString = searchParams.get('p');
  useEffect(() => {
    if (queryString) {
      if (pendingAssistant) {
        setFields(pendingAssistant);
        removePendingAssistant();
      }

      window.history.replaceState(null, '', pathname);
    }
  }, [queryString, pendingAssistant]);

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
    try {
      setIsSubmitting(true);
      const agent = await createAgent(fields);
      close();
      setIsSubmitting(false);
      router.push(`/a/${agent.id}`);
    } catch (e) {
      setIsSubmitting(false);
      close();
      error('Failed to create assistant');
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
          <Text className="dark:text-volcanic-600">Create assistant</Text>
        </div>
        <Text styleAs="h4">Create assistant</Text>
      </header>
      <div className="overflow-y-auto">
        <AgentSettingsForm
          fields={fields}
          setFields={setFields}
          onSubmit={handleOpenSubmitModal}
          savePendingAssistant={() => setPendingAssistant(fields)}
        />
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
