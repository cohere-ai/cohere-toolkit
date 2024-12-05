'use client';

import React, { useMemo } from 'react';

import { CreateAgentRequest, UpdateAgentRequest } from '@/cohere-client';
import { AgentToolFilePicker } from '@/components/Agents/AgentToolFilePicker';
import { Checkbox, Input, InputLabel, STYLE_LEVEL_TO_CLASSES, Text } from '@/components/Shared';
import { BACKGROUND_TOOLS, TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { DYNAMIC_STRINGS, STRINGS } from '@/constants/strings';
import { useListTools } from '@/hooks/tools';
import { GoogleDriveToolArtifact } from '@/types/tools';
import { cn } from '@/utils';

export type CreateAgentFormFields = Omit<
  CreateAgentRequest,
  'version' | 'temperature' | 'organization_id'
>;
export type UpdateAgentFormFields = Omit<
  UpdateAgentRequest,
  'version' | 'temperature' | 'organization_id'
>;
export type AgentFormFieldKeys = keyof CreateAgentFormFields | keyof UpdateAgentFormFields;

type Props<K extends UpdateAgentFormFields | CreateAgentFormFields> = {
  fields: K;
  setFields: React.Dispatch<React.SetStateAction<K>>;
  onToolToggle: (toolName: string, checked: boolean, authUrl?: string) => void;
  handleOpenFilePicker: VoidFunction;
  isAgentCreator: boolean;
  errors?: Partial<Record<AgentFormFieldKeys, string>>;
  className?: string;
};
/**
 * @description Base form for creating/updating an agent.
 */
export function AgentForm<K extends CreateAgentFormFields | UpdateAgentFormFields>({
  fields,
  setFields,
  onToolToggle,
  handleOpenFilePicker,
  errors,
  isAgentCreator,
  className,
}: Props<K>) {
  const { data: toolsData } = useListTools();
  const tools =
    toolsData?.filter((t) => t.is_available && !BACKGROUND_TOOLS.includes(t.name ?? '')) ?? [];

  const googleDrivefiles: GoogleDriveToolArtifact[] = useMemo(() => {
    const toolsMetadata = fields.tools_metadata ?? [];
    return (toolsMetadata.find((t) => t.tool_name === TOOL_GOOGLE_DRIVE_ID)?.artifacts ??
      []) as GoogleDriveToolArtifact[];
  }, [fields]);

  const handleRemoveGoogleDriveFiles = (id: string) => {
    setFields((prev) => {
      const toolsMetadata = prev.tools_metadata ?? [];
      return {
        ...prev,
        tools_metadata: [
          ...toolsMetadata.filter((tool) => tool.tool_name !== TOOL_GOOGLE_DRIVE_ID),
          {
            ...toolsMetadata.find((tool) => tool.tool_name === TOOL_GOOGLE_DRIVE_ID),
            artifacts: googleDrivefiles.filter((file) => file.id !== id),
          },
        ],
      };
    });
  };

  return (
    <div className={cn('flex flex-col gap-y-4', className)}>
      <RequiredInputLabel label="name" className="pb-2">
        <Input
          kind="default"
          value={fields.name ?? ''}
          placeholder={STRINGS.assistantNameDescription}
          onChange={(e) => setFields((prev) => ({ ...prev, name: e.target.value }))}
          hasError={!!errors?.name}
          errorText={errors?.name}
          disabled={!isAgentCreator}
        />
      </RequiredInputLabel>
      <InputLabel label="description" className="pb-2">
        <Input
          kind="default"
          value={fields.description ?? ''}
          placeholder={STRINGS.assistantDescriptionDescription}
          onChange={(e) => setFields((prev) => ({ ...prev, description: e.target.value }))}
          disabled={!isAgentCreator}
        />
      </InputLabel>
      <InputLabel
        label={STRINGS.instructions}
        tooltipLabel={<Text>{DYNAMIC_STRINGS.assistantInstructionsDescription}</Text>}
      >
        <textarea
          value={fields.preamble ?? ''}
          placeholder={STRINGS.assistantPreambleDescription}
          className={cn(
            'mt-2 w-full flex-1 resize-none p-3',
            'transition ease-in-out',
            'rounded-lg border',
            'bg-marble-1000',
            'border-marble-800 placeholder:text-volcanic-600 focus:border-mushroom-400',
            'focus-visible:outline focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-900',
            'disabled:text-volcanic-700',
            {
              'border-marble-800 bg-marble-950': !isAgentCreator,
            },
            STYLE_LEVEL_TO_CLASSES.p
          )}
          rows={5}
          onChange={(e) => setFields((prev) => ({ ...prev, preamble: e.target.value }))}
          data-testid="input-preamble"
          disabled={!isAgentCreator}
        />
      </InputLabel>
      <div className="flex flex-col space-y-2">
        <Text className="text-volcanic-100" as="span" styleAs="label">
          {STRINGS.tools}
        </Text>
        <div className="flex flex-col gap-y-4 px-3">
          {tools.map((tool, i) => {
            const enabledTools = [...(fields.tools ? fields.tools : [])];
            const enabledTool = enabledTools.find((t) => t === tool.name);
            const checked = !!enabledTool;
            const isGoogleDrive = tool.name === TOOL_GOOGLE_DRIVE_ID;

            return (
              <div key={i}>
                <Checkbox
                  label={tool.display_name ?? tool.name ?? ''}
                  tooltipLabel={tool.description}
                  name={tool.name ?? '' + i}
                  checked={checked}
                  onChange={(e) =>
                    onToolToggle(tool.name ?? '', e.target.checked, tool.auth_url ?? '')
                  }
                  disabled={!isAgentCreator}
                />
                {isGoogleDrive && checked && (
                  <div className="mt-2 pl-10">
                    <AgentToolFilePicker
                      googleDriveFiles={googleDrivefiles}
                      handleRemoveGoogleDriveFiles={handleRemoveGoogleDriveFiles}
                      handleOpenFilePicker={handleOpenFilePicker}
                      disabled={!isAgentCreator}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

const RequiredInputLabel: React.FC<{
  label: string;
  children: React.ReactNode;
  className?: string;
}> = ({ label, children, className }) => (
  <InputLabel
    label={
      <div className="flex items-center gap-x-2">
        <Text as="span" styleAs="label" className="text-volcanic-100">
          {label}
        </Text>
        <Text as="span" styleAs="label" className="text-danger-350">
          *{STRINGS.required}
        </Text>
      </div>
    }
    className={className}
  >
    {children}
  </InputLabel>
);
