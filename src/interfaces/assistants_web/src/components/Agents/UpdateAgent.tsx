'use client';

import { useLocalStorageValue } from '@react-hookz/web';
import { uniqBy } from 'lodash';
import React, { useEffect, useState } from 'react';

import { AgentForm, UpdateAgentFormFields } from '@/components/Agents/AgentForm';
import { IconButton } from '@/components/IconButton';
import { Banner, Button, Spinner, Text } from '@/components/Shared';
import { TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { useAgent, useIsAgentNameUnique, useUpdateAgent } from '@/hooks/agents';
import { useSession } from '@/hooks/session';
import { useNotify } from '@/hooks/toast';
import { useListTools, useOpenGoogleDrivePicker } from '@/hooks/tools';
import { useAgentsStore } from '@/stores';
import { GoogleDriveToolArtifact } from '@/types/tools';
import { cn } from '@/utils';

type Props = {
  agentId?: string;
};

export const UpdateAgent: React.FC<Props> = ({ agentId }) => {
  const { error, success } = useNotify();
  const { setEditAgentPanelOpen } = useAgentsStore();
  const { data: agent, isLoading } = useAgent({ agentId });
  const { data: toolsData } = useListTools();
  const { mutateAsync: updateAgent } = useUpdateAgent();
  const isAgentNameUnique = useIsAgentNameUnique();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [fields, setFields] = useState<UpdateAgentFormFields>({
    name: '',
    description: '',
    deployment: '',
    model: '',
    tools: [],
    tools_metadata: [],
  });

  const { userId } = useSession();
  const isAgentCreator = !!agent && agent.user_id === userId;

  const { set: setPendingAssistant } = useLocalStorageValue<UpdateAgentFormFields>(
    'pending_assistant',
    {
      defaultValue: fields,
      initializeWithValue: false,
    }
  );

  const openFilePicker = useOpenGoogleDrivePicker((data) => {
    if (data.docs) {
      setFields((prev) => {
        const currentGoogleDriveTool = prev.tools_metadata?.find(
          (tool) => tool.tool_name === TOOL_GOOGLE_DRIVE_ID
        );
        // If the tool is not already enabled, add it to the list of tools
        if (!currentGoogleDriveTool) {
          return {
            ...prev,
            tools_metadata: [
              ...(prev.tools_metadata ?? []),
              {
                tool_name: TOOL_GOOGLE_DRIVE_ID,
                artifacts: data.docs.map(
                  (doc) =>
                    ({
                      id: doc.id,
                      name: doc.name,
                      type: doc.type,
                      url: doc.url,
                    } as GoogleDriveToolArtifact)
                ),
              },
            ],
          };
        }

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

        // If the tool is already enabled, update the artifacts
        const updateGoogleDriveTool = {
          ...currentGoogleDriveTool,
          artifacts: uniqBy(updatedArtifacts, 'id'),
        };

        return {
          ...prev,
          tools_metadata: [
            ...(prev.tools_metadata?.filter((tool) => tool.tool_name !== TOOL_GOOGLE_DRIVE_ID) ??
              []),
            updateGoogleDriveTool,
          ],
        };
      });
    }
  });

  const isDirty = () => {
    if (!agent) return false;
    return Object.entries(fields).some(
      ([key, value]) => agent[key as keyof UpdateAgentFormFields] !== value
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
        tools_metadata: agent.tools_metadata,
      });
    }
  }, [agent]);

  const handleClose = () => {
    setEditAgentPanelOpen(false);
  };

  const handleToolToggle = (toolName: string, checked: boolean, authUrl?: string) => {
    const enabledTools = fields.tools ?? [];
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
        tools: prev.tools?.filter((t) => t !== TOOL_GOOGLE_DRIVE_ID),
        tools_metadata: prev.tools_metadata?.filter((t) => t.tool_name !== TOOL_GOOGLE_DRIVE_ID),
      }));
    }
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
        <Text className="text-danger-350">Unable to load assistant information</Text>
      </div>
    );
  }

  return (
    <>
      <header
        className={cn(
          'flex h-header flex-shrink-0 items-center justify-between border-b border-marble-950',
          'pl-4 pr-3 lg:pl-10 lg:pr-8'
        )}
      >
        <Text>{isAgentCreator ? `Update ${agent.name}` : `About ${agent.name}`}</Text>
        <IconButton iconName="close" onClick={handleClose} />
      </header>
      <div className={cn('flex flex-col gap-y-5 overflow-y-auto', 'p-4 lg:p-10')}>
        {isAgentCreator && <InfoBanner agentName={agent.name} className="flex md:hidden" />}
        <AgentForm<UpdateAgentFormFields>
          fields={fields}
          errors={fieldErrors}
          setFields={setFields}
          onToolToggle={handleToolToggle}
          isAgentCreator={isAgentCreator}
          handleOpenFilePicker={openFilePicker}
        />
      </div>
      {isAgentCreator && (
        <div className="flex flex-col gap-y-6 px-4 py-4 lg:px-10 lg:pb-8 lg:pt-0">
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
