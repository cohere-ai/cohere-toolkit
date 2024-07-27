'use client';

import React, { useMemo, useState } from 'react';

import { CreateAgent, ManagedTool, UpdateAgent } from '@/cohere-client';
import { Button, Icon, Input, InputLabel, Switch, Text, Textarea } from '@/components/Shared';
import {
  DEFAULT_AGENT_TOOLS,
  TOOL_FALLBACK_ICON,
  TOOL_GOOGLE_DRIVE_ID,
  TOOL_ID_TO_DISPLAY_INFO,
} from '@/constants';
import { useListTools } from '@/hooks/tools';
import { GoogleDriveToolArtifact } from '@/types/tools';

import { CollapsibleSection } from '../../CollapsibleSection';
import { IconButton } from '../../IconButton';
import { DataSourcesStep } from './DataSourcesStep';
import { DefineAssistantStep } from './DefineAssistantStep';

export type CreateAgentFormFields = Omit<CreateAgent, 'version' | 'temperature'>;
export type UpdateAgentFormFields = Omit<UpdateAgent, 'version' | 'temperature'>;
export type AgentFormFieldKeys = keyof CreateAgentFormFields | keyof UpdateAgentFormFields;

type Props<K extends UpdateAgentFormFields | CreateAgentFormFields> = {
  fields: K;
  setFields: React.Dispatch<React.SetStateAction<K>>;
  onToolToggle: (toolName: string, checked: boolean, authUrl?: string) => void;
  handleOpenFilePicker: VoidFunction;
  handleSubmit: VoidFunction;
  isAgentCreator: boolean;
  canSubmit: boolean;
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
  handleSubmit,
  errors,
  isAgentCreator,
  canSubmit,
  className,
}: Props<K>) {
  const [currentStep, setCurrentStep] = useState<number | undefined>(0);
  const { data: toolsData } = useListTools();
  const tools = toolsData?.filter((t) => t.is_available) ?? [];

  const [documents, setDocuments] = useState<Document[]>([]);
  const googleDriveFiles: GoogleDriveToolArtifact[] = useMemo(() => {
    const toolsMetadata = fields.tools_metadata ?? [];
    return (toolsMetadata.find((t) => t.tool_name === TOOL_GOOGLE_DRIVE_ID)?.artifacts ?? [
      { type: 'folder', id: 'test', name: 'test', url: 'test' },
      { type: 'file', id: 'test', name: 'test', url: 'test' },
      { type: 'folder', id: 'test', name: 'test', url: 'test' },
    ]) as GoogleDriveToolArtifact[];
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
            artifacts: googleDriveFiles.filter((file) => file.id !== id),
          },
        ],
      };
    });
  };

  const googleDriveTool = tools.find((t) => t.name === TOOL_GOOGLE_DRIVE_ID);
  const requireGoogleAuth = googleDriveTool?.is_auth_required;

  return (
    <div className="flex flex-col space-y-6 p-8">
      {/* Step 1 - Define your assistant */}
      <CollapsibleSection
        title="Define your assistant"
        number={1}
        description="What does your assistant do?"
        isExpanded={currentStep === 0}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 0 : undefined)}
      >
        <DefineAssistantStep
          fields={fields}
          setFields={setFields}
          errors={errors}
          isAgentCreator={isAgentCreator}
          setCurrentStep={setCurrentStep}
        />
      </CollapsibleSection>

      {/* Step 2 -  Data sources */}
      <CollapsibleSection
        title="Add data sources"
        number={2}
        description="Build a robust knowledge base for the assistant by adding files, folders, and documents."
        isExpanded={currentStep === 1}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 1 : undefined)}
      >
        <DataSourcesStep
          fields={fields}
          tools={tools}
          googleDriveFiles={googleDriveFiles}
          isAgentCreator={isAgentCreator}
          onToolToggle={onToolToggle}
          handleRemoveGoogleDriveFile={handleRemoveGoogleDriveFiles}
          setFields={setFields}
        />
        {/* use new button styles -> kind='outline' theme='mushroom-marble' icon  */}
        <div className="flex items-center justify-between pt-3">
          {/* use new button styles -> kind='primary' theme='evolved-green' icon='arrow-right' iconPosition='end' */}
          <Button kind="secondary" label="Back" onClick={() => setCurrentStep(1)} />
          <Button className="w-fit" label="Next" onClick={() => setCurrentStep(2)} />
        </div>
      </CollapsibleSection>

      {/* Step 3 -  Tools */}
      <CollapsibleSection
        title="Set default tools"
        number={3}
        description="Select which external tools will be on by default in order to enhance the assistant’s capabilities and expand its foundational knowledge."
        isExpanded={currentStep === 2}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 2 : undefined)}
      >
        <div className="flex flex-col space-y-2">
          {tools.map((tool, i) => {
            const toolName = tool?.name || '';
            if (toolName === TOOL_GOOGLE_DRIVE_ID) return;
            const enabledTools = [...(fields.tools ? fields.tools : [])];
            const currentToolEnabled = enabledTools.find((t) => t === toolName);
            const isEnabled = !!currentToolEnabled;

            return (
              <ToolSwitch
                key={i}
                tool={tool}
                checked={isEnabled}
                handleSwitch={(enabled) =>
                  toolName === TOOL_GOOGLE_DRIVE_ID
                    ? enabled
                      ? handleOpenFilePicker
                      : handleRemoveGoogleDriveFiles
                    : onToolToggle(tool.name ?? '', enabled, tool.auth_url ?? '')
                }
              />
            );
          })}
          <div className="flex items-center justify-between pt-2">
            {/* use new button styles -> kind='primary' theme='evolved-green' icon='arrow-right' iconPosition='end' */}
            <Button kind="secondary" label="Back" onClick={() => setCurrentStep(2)} />
            <div className="flex items-center space-x-2">
              <Button kind="secondary" label="Skip" onClick={() => setCurrentStep(3)} />
              <Button className="w-fit" label="Next" onClick={() => setCurrentStep(3)} />
            </div>
          </div>
        </div>
      </CollapsibleSection>

      {/* Step 4 -  Visibility */}
      <CollapsibleSection
        title="Set visibility"
        number={4}
        description="Control who can access this assistant and its knowledge base"
        isExpanded={currentStep === 3}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 3 : undefined)}
      >
        <div className="flex flex-col">
          <div className="flex items-center justify-between">
            {/* use new button styles -> kind='primary' theme='evolved-green' icon='check' iconPosition='end' */}
            <Button kind="secondary" label="Back" onClick={() => setCurrentStep(3)} />
            <Button className="w-fit" label="Create" onClick={handleSubmit} disabled={!canSubmit} />
          </div>
        </div>
      </CollapsibleSection>
    </div>
  );
}

const ToolSwitch: React.FC<{
  tool: ManagedTool;
  checked: boolean;
  handleSwitch: (checked: boolean) => void;
}> = ({ tool, checked, handleSwitch }) => {
  const toolName = tool?.name || '';
  const icon = TOOL_ID_TO_DISPLAY_INFO[toolName]?.icon ?? TOOL_FALLBACK_ICON;
  return (
    <div className="flex w-full items-start justify-between rounded-md border p-4 dark:border-volcanic-300 dark:bg-volcanic-100">
      <div className="flex flex-grow flex-col space-y-1">
        <div className="flex items-center space-x-2">
          <Icon
            name={icon}
            kind="outline"
            className="flex h-5 w-5 items-center justify-center rounded-sm dark:bg-volcanic-200 dark:text-marble-950"
          />
          <Text styleAs="label">{tool.name}</Text>
        </div>
        <Text className="dark:text-marble-800">{tool.description}</Text>
      </div>
      <Switch theme="evolved-green" checked={checked} onChange={handleSwitch} />
    </div>
  );
};
