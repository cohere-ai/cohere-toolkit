'use client';

import { useLocalStorageValue } from '@react-hookz/web';
import { uniqBy } from 'lodash';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import React, { useContext, useEffect, useState } from 'react';

import { AgentForm, CreateAgentFormFields } from '@/components/Agents/AgentForm';
import { Button, Text } from '@/components/Shared';
import {
  DEFAULT_AGENT_MODEL,
  DEFAULT_AGENT_TOOLS,
  DEFAULT_PREAMBLE,
  DEPLOYMENT_COHERE_PLATFORM,
  TOOL_GOOGLE_DRIVE_ID,
} from '@/constants';
import { ModalContext } from '@/context/ModalContext';
import { useCreateAgent, useIsAgentNameUnique, useRecentAgents } from '@/hooks/agents';
import { useNotify } from '@/hooks/toast';
import { useListTools, useOpenGoogleDrivePicker } from '@/hooks/tools';
import { GoogleDriveToolArtifact } from '@/types/tools';

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
  const { open, close } = useContext(ModalContext);

  const {
    value: pendingAssistant,
    set: setPendingAssistant,
    remove: removePendingAssistant,
  } = useLocalStorageValue<CreateAgentFormFields>('pending_assistant', {
    initializeWithValue: false,
    defaultValue: undefined,
  });

  const { data: toolsData } = useListTools();
  const { error } = useNotify();
  const { mutateAsync: createAgent } = useCreateAgent();
  const { addRecentAgentId } = useRecentAgents();
  const isAgentNameUnique = useIsAgentNameUnique();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fields, setFields] = useState<CreateAgentFormFields>(DEFAULT_FIELD_VALUES);

  const openFilePicker = useOpenGoogleDrivePicker((data) => {
    if (data.docs) {
      setFields((prev) => {
        const updatedArtifacts = [
          ...(prev.tools_metadata?.find((tool) => tool.tool_name === TOOL_GOOGLE_DRIVE_ID)
            ?.artifacts ?? []),
          ...data.docs.map(
            (doc) =>
              ({
                id: doc.id,
                name: doc.name,
                type: doc.type,
                url: doc.url,
              } as GoogleDriveToolArtifact)
          ),
        ];

        return {
          ...prev,
          tools_metadata: [
            ...(prev.tools_metadata?.filter((tool) => tool.tool_name !== TOOL_GOOGLE_DRIVE_ID) ??
              []),
            ...[
              {
                tool_name: TOOL_GOOGLE_DRIVE_ID,
                artifacts: uniqBy(updatedArtifacts, 'id'),
              },
            ],
          ],
        };
      });
    }
  });

  const fieldErrors = {
    ...(isAgentNameUnique(fields.name) ? {} : { name: 'Assistant name must be unique' }),
  };

  const canSubmit = (() => {
    const { name, deployment, model } = fields;
    const requredFields = { name, deployment, model };
    return Object.values(requredFields).every(Boolean) && !Object.keys(fieldErrors).length;
  })();

  const handleToolToggle = (toolName: string, checked: boolean, authUrl?: string) => {
    const enabledTools = [...(fields.tools ? fields.tools : [])];

    if (toolName === TOOL_GOOGLE_DRIVE_ID) {
      handleGoogleDriveToggle(checked, authUrl);
    }

    setFields((prev) => ({
      ...prev,
      tools: checked ? [...enabledTools, toolName] : enabledTools.filter((t) => t !== toolName),
    }));
  };

  const handleGoogleDriveToggle = (checked: boolean, authUrl?: string) => {
    const driveTool = toolsData?.find((tool) => tool.name === TOOL_GOOGLE_DRIVE_ID);
    if (checked) {
      if (driveTool?.is_auth_required && authUrl) {
        setPendingAssistant({
          ...fields,
          tools: [...(fields.tools ?? []), TOOL_GOOGLE_DRIVE_ID],
        });
        authUrl && window.open(authUrl, '_self');
      } else {
        openFilePicker();
      }
    } else {
      setFields((prev) => ({
        ...prev,
        tools: (fields.tools ?? []).filter((t) => t !== TOOL_GOOGLE_DRIVE_ID),
        tools_metadata: fields.tools_metadata?.filter((t) => t.tool_name !== TOOL_GOOGLE_DRIVE_ID),
      }));
    }
  };

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
    if (!canSubmit) return;

    try {
      setIsSubmitting(true);

      const agent = await createAgent(fields);
      addRecentAgentId(agent.id);
      setFields(DEFAULT_FIELD_VALUES);
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
      <div className="flex-grow overflow-y-scroll">
        <div className="flex max-w-[650px] flex-col gap-y-2 p-10">
          <Text styleAs="h4">Create an Assistant</Text>
          <Text className="text-volcanic-400">
            Create an unique assistant and share with your org
          </Text>
          <AgentForm<CreateAgentFormFields>
            fields={fields}
            setFields={setFields}
            onToolToggle={handleToolToggle}
            handleOpenFilePicker={openFilePicker}
            errors={fieldErrors}
            className="mt-6"
            isAgentCreator
          />
        </div>
      </div>
      <div className="flex w-full flex-shrink-0 justify-end border-t border-marble-950 bg-white px-4 py-4 md:py-8">
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
