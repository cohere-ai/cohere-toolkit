import { useSessionStorageValue } from '@react-hookz/web';
import React, { useEffect, useState } from 'react';

import { AgentForm, AgentFormFieldKeys, AgentFormFields } from '@/components/Agents/AgentForm';
import { IconButton } from '@/components/IconButton';
import { Banner, Button, Spinner, Text } from '@/components/Shared';
import { TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { useAgent, useIsAgentNameUnique, useUpdateAgent } from '@/hooks/agents';
import { useSession } from '@/hooks/session';
import { useNotify } from '@/hooks/toast';
import { useListTools, useOpenGoogleDrivePicker } from '@/hooks/tools';
import { useAgentsStore } from '@/stores';
import { cn } from '@/utils';

type Props = {
  agentId?: string;
};

export const UpdateAgentPanel: React.FC<Props> = ({ agentId }) => {
  const { error, success } = useNotify();
  const { setEditAgentPanelOpen } = useAgentsStore();
  const { data: agent, isLoading } = useAgent({ agentId });
  const { data: toolsData } = useListTools();
  const { mutateAsync: updateAgent } = useUpdateAgent();
  const isAgentNameUnique = useIsAgentNameUnique();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fields, setFields] = useState<AgentFormFields>({
    name: '',
    description: '',
    deployment: '',
    model: '',
    tools: [],
    tools_metadata: [],
  });
  const [googleDriveFiles, setGoogleDriveFiles] = useState<Record<string, any>[]>();

  const { set: setPendingAssistant } = useSessionStorageValue<AgentFormFields>(
    'pending_assistant',
    {
      defaultValue: fields,
      initializeWithValue: false,
    }
  );

  const openFilePicker = useOpenGoogleDrivePicker((data) => {
    if (data.docs) {
      setGoogleDriveFiles(
        data.docs.map((doc) => ({ id: doc.id, name: doc.name, type: doc.type, url: doc.url }))
      );
    }
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
        tools_metadata: agent.tools_metadata,
      });
      const driveArtifacts: Record<string, any>[] = [];
      agent.tools_metadata
        ?.filter((metadata) => metadata.tool_name === TOOL_GOOGLE_DRIVE_ID)
        .forEach((metadata) => {
          driveArtifacts.push(...metadata.artifacts);
        });

      setGoogleDriveFiles(driveArtifacts);
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

  const handleToolToggle = (toolName: string, checked: boolean, authUrl?: string) => {
    const enabledTools = fields.tools ?? [];
    if (toolName === TOOL_GOOGLE_DRIVE_ID) {
      handleGoogleDriveToggle(checked, authUrl);
    }

    setFields({
      ...fields,
      tools: checked ? [...enabledTools, toolName] : enabledTools.filter((t) => t !== toolName),
    });
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
      setGoogleDriveFiles(undefined);
    }
  };

  const handleSubmit = async () => {
    if (!canSubmit || !agentId) return;

    try {
      setIsSubmitting(true);
      const newAgent = await updateAgent({
        ...fields,
        // tools_metadata: [{ tool_name: TOOL_GOOGLE_DRIVE_ID, artifacts: googleDriveFiles ?? [] }],
        agentId,
      });
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
      <div className="flex flex-col gap-y-5 overflow-y-auto px-8 py-8 md:px-14">
        {isAgentCreator && <InfoBanner agentName={agent.name} className="flex md:hidden" />}
        <AgentForm
          fields={fields}
          errors={fieldErrors}
          onChange={handleChange}
          onToolToggle={handleToolToggle}
          disabled={!isAgentCreator}
          handleOpenFilePicker={openFilePicker}
          googleDriveFiles={googleDriveFiles}
          setGoogleDriveFiles={setGoogleDriveFiles}
        />
      </div>
      {isAgentCreator && (
        <div className="flex flex-col gap-y-12 px-8 py-4 md:px-14 md:pb-8 md:pt-0">
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
    </div>
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
