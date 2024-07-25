'use client';

import { useLocalStorageValue } from '@react-hookz/web';
import { uniqBy } from 'lodash';
import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import React, { useContext, useEffect, useState } from 'react';

import { AgentForm, CreateAgentFormFields } from '@/components/Agents/AgentForm';
import { Button, Icon, Text } from '@/components/Shared';
import {
  DEFAULT_AGENT_MODEL,
  DEFAULT_AGENT_TOOLS,
  DEPLOYMENT_COHERE_PLATFORM,
  TOOL_GOOGLE_DRIVE_ID,
} from '@/constants';
import { ModalContext } from '@/context/ModalContext';
import { useCreateAgent, useIsAgentNameUnique, useRecentAgents } from '@/hooks/agents';
import { useNotify } from '@/hooks/toast';
import { useListTools, useOpenGoogleDrivePicker } from '@/hooks/tools';
import { GoogleDriveToolArtifact } from '@/types/tools';

import { CollapsibleSection } from '../CollapsibleSection';

const DEFAULT_FIELD_VALUES = {
  name: '',
  description: '',
  preamble: '',
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
  const [currentStep, setCurrentStep] = useState<number | undefined>(0);

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
      <div className="flex flex-col space-y-5 border-b px-12 py-10 dark:border-volcanic-150">
        <div className="flex items-center space-x-2">
          <Link href="/discover">
            <Text className="dark:text-volcanic-600">All assistants</Text>
          </Link>
          <Icon name="chevron-right" className="dark:text-volcanic-600" />
          <Text className="dark:text-volcanic-600">Create assistant</Text>
        </div>
        <Text styleAs="h4">Create assistant</Text>
      </div>
      <div className="flex flex-col space-y-6 p-8">
        <CollapsibleSection
          title="Define your assistant"
          number={1}
          description="What does your assistant do?"
          isExpanded={currentStep === 0}
          setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 0 : undefined)}
        >
          <div className="flex flex-col">
            {/* use new button styles -> kind='primary' theme='evolved-green' icon='arrow-right' iconPosition='end' */}
            <Button className="ml-auto w-fit" label="Next" onClick={() => setCurrentStep(1)} />
          </div>
        </CollapsibleSection>
        <CollapsibleSection
          title="Add data sources"
          number={2}
          description="Build a robust knowledge base for the assistant by adding files, folders, and documents."
          isExpanded={currentStep === 1}
          setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 1 : undefined)}
        >
          <div className="flex flex-col">
            {/* use new button styles -> kind='primary' theme='evolved-green' icon='arrow-right' iconPosition='end' */}
            <Button className="ml-auto w-fit" label="Next" onClick={() => setCurrentStep(2)} />
          </div>
        </CollapsibleSection>
        <CollapsibleSection
          title="Set default tools"
          number={3}
          description="Select which external tools will be on by default in order to enhance the assistant’s capabilities and expand its foundational knowledge."
          isExpanded={currentStep === 2}
          setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 2 : undefined)}
        >
          <div className="flex flex-col">
            {/* use new button styles -> kind='primary' theme='evolved-green' icon='arrow-right' iconPosition='end' */}
            <Button className="ml-auto w-fit" label="Next" onClick={() => setCurrentStep(3)} />
          </div>
        </CollapsibleSection>
        <CollapsibleSection
          title="Set visibility"
          number={4}
          description="Control who can access this assistant and its knowledge base"
          isExpanded={currentStep === 3}
          setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 3 : undefined)}
        >
          <div className="flex flex-col">
            {/* use new button styles -> kind='primary' theme='evolved-green' icon='arrow-right' iconPosition='end' */}
            <Button className="ml-auto w-fit" label="Next" onClick={handleOpenSubmitModal} />
          </div>
        </CollapsibleSection>
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
