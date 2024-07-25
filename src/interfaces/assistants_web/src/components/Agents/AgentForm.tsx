'use client';

import { Label } from '@headlessui/react';
import React, { useMemo, useState } from 'react';

import { CreateAgent, UpdateAgent } from '@/cohere-client';
import { AgentToolFilePicker } from '@/components/Agents/AgentToolFilePicker';
import { Button, Checkbox, Input, InputLabel, Switch, Text, Textarea } from '@/components/Shared';
import { DEFAULT_AGENT_TOOLS, TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { useListTools } from '@/hooks/tools';
import { GoogleDriveToolArtifact } from '@/types/tools';

import { CollapsibleSection } from '../CollapsibleSection';

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
  className,
}: Props<K>) {
  const [currentStep, setCurrentStep] = useState<number | undefined>(0);
  const { data: toolsData } = useListTools();
  const tools =
    toolsData?.filter((t) => t.is_available && !DEFAULT_AGENT_TOOLS.includes(t.name ?? '')) ?? [];

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
    <div className="flex flex-col space-y-6 p-8">
      {/* Step 1 - Define your assistant */}
      <CollapsibleSection
        title="Define your assistant"
        number={1}
        description="What does your assistant do?"
        isExpanded={currentStep === 0}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 0 : undefined)}
      >
        <div className="flex flex-col space-y-4">
          <Input
            label="Name"
            placeholder="e.g., HR Benefits Bot"
            value={fields.name ?? ''}
            onChange={(e) => setFields((prev) => ({ ...prev, name: e.target.value }))}
            errorText={errors?.name}
            disabled={!isAgentCreator}
          />
          <Textarea
            label="Description"
            placeholder="e.g., Answers questions about our company benefits."
            value={fields.description ?? ''}
            defaultRows={1}
            onChange={(e) => setFields((prev) => ({ ...prev, description: e.target.value }))}
            disabled={!isAgentCreator}
          />
          <Textarea
            label="Instruction (Optional)"
            placeholder="e.g., You are friendly and helpful. You answer questions based on files in Google Drive."
            value={fields.preamble ?? ''}
            defaultRows={1}
            onChange={(e) => setFields((prev) => ({ ...prev, preamble: e.target.value }))}
            disabled={!isAgentCreator}
          />
          {/* use new button styles -> kind='primary' theme='evolved-green' icon='arrow-right' iconPosition='end' */}
          <Button className="ml-auto w-fit" label="Next" onClick={() => setCurrentStep(1)} />
        </div>
      </CollapsibleSection>

      {/* Step 2 -  Data sources */}
      <CollapsibleSection
        title="Add data sources"
        number={2}
        description="Build a robust knowledge base for the assistant by adding files, folders, and documents."
        isExpanded={currentStep === 1}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 1 : undefined)}
      >
        <div className="flex flex-col">
          <Label>
            <Text styleAs="label">Active Data Sources</Text>
          </Label>
          <div className="flex items-center justify-between">
            {/* use new button styles -> kind='primary' theme='evolved-green' icon='arrow-right' iconPosition='end' */}
            <Button kind="secondary" label="Back" onClick={() => setCurrentStep(1)} />
            <Button className="w-fit" label="Next" onClick={() => setCurrentStep(2)} />
          </div>
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
        <div className="flex flex-col">
          {tools.map((tool, i) => {
            const enabledTools = [...(fields.tools ? fields.tools : [])];
            const currentToolEnabled = enabledTools.find((t) => t === tool.name);
            const isEnabled = !!currentToolEnabled;
            const isGoogleDrive = tool.name === TOOL_GOOGLE_DRIVE_ID;
            return (
              <div className="flex w-full rounded-md border p-4 dark:border-volcanic-300 dark:bg-volcanic-100">
                <div className="flex justify-between">
                  <Text styleAs="label">{tool.name}</Text>
                  <Switch
                    theme="evolved-green"
                    checked={isEnabled}
                    onChange={(enabled) =>
                      isGoogleDrive
                        ? enabled
                          ? handleOpenFilePicker
                          : handleRemoveGoogleDriveFiles
                        : onToolToggle(tool.name ?? '', enabled, tool.auth_url ?? '')
                    }
                  />
                </div>
                <Text>{tool.description}</Text>
              </div>
            );
          })}
          <div className="flex items-center justify-between">
            {/* use new button styles -> kind='primary' theme='evolved-green' icon='arrow-right' iconPosition='end' */}
            <Button kind="secondary" label="Back" onClick={() => setCurrentStep(2)} />
            <div className="flex items-center">
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
            <Button className="w-fit" label="Create" onClick={handleSubmit} />
          </div>
        </div>
      </CollapsibleSection>
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
          *required
        </Text>
      </div>
    }
    className={className}
  >
    {children}
  </InputLabel>
);
