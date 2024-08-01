'use client';

import { useState } from 'react';

import { CreateAgent, UpdateAgent } from '@/cohere-client';
import { DataSourcesStep } from '@/components/Agents/AgentSettings/DataSourcesStep';
import { DefineAssistantStep } from '@/components/Agents/AgentSettings/DefineStep';
import { ToolsStep } from '@/components/Agents/AgentSettings/ToolsStep';
import { VisibilityStep } from '@/components/Agents/AgentSettings/VisibilityStep';
import { CollapsibleSection } from '@/components/CollapsibleSection';
import { Button } from '@/components/Shared';
import { TOOL_GOOGLE_DRIVE_ID, TOOL_READ_DOCUMENT_ID, TOOL_SEARCH_FILE_ID } from '@/constants';
import { useIsAgentNameUnique } from '@/hooks/agents';
import { useListTools, useOpenGoogleDrivePicker } from '@/hooks/tools';
import { DataSourceArtifact } from '@/types/tools';
import { cn } from '@/utils';

type RequiredAndNotNull<T> = {
  [P in keyof T]-?: Exclude<T[P], null | undefined>;
};

type RequireAndNotNullSome<T, K extends keyof T> = RequiredAndNotNull<Pick<T, K>> & Omit<T, K>;

export type AgentSettingsFields = RequireAndNotNullSome<
  Omit<UpdateAgent, 'version' | 'temperature'> | Omit<CreateAgent, 'version' | 'temperature'>,
  'name' | 'model' | 'deployment'
>;

type Props = {
  source?: 'update' | 'create';
  fields: AgentSettingsFields;
  savePendingAssistant: VoidFunction;
  setFields: (fields: AgentSettingsFields) => void;
  onSubmit: VoidFunction;
};

export const AgentSettingsForm: React.FC<Props> = ({
  source = 'create',
  fields,
  savePendingAssistant,
  setFields,
  onSubmit,
}) => {
  const { data: listToolsData } = useListTools();
  const isAgentNameUnique = useIsAgentNameUnique();

  const [currentStep, setCurrentStep] = useState<number>(0);

  const [googleFiles, setGoogleFiles] = useState<DataSourceArtifact[]>(
    fields.tools_metadata?.find((metadata) => metadata.tool_name === TOOL_GOOGLE_DRIVE_ID)
      ?.artifacts as DataSourceArtifact[]
  );
  // read_document and search_files have identical metadata -> using read_document as base
  const [defaultUploadFiles, setDefaultUploadFiles] = useState<DataSourceArtifact[]>(
    fields.tools_metadata?.find((metadata) => metadata.tool_name === TOOL_READ_DOCUMENT_ID)
      ?.artifacts as DataSourceArtifact[]
  );

  const nameError = !fields.name.trim()
    ? 'Assistant name is required'
    : !isAgentNameUnique(fields.name.trim())
    ? 'Assistant name must be unique'
    : undefined;

  const setToolsMetadata = () => {
    const tools_metadata = [
      ...(googleFiles && !!googleFiles.length
        ? [
            {
              tool_name: TOOL_GOOGLE_DRIVE_ID,
              artifacts: googleFiles,
            },
          ]
        : []),
      ...(defaultUploadFiles && !!defaultUploadFiles.length
        ? [
            {
              tool_name: TOOL_READ_DOCUMENT_ID,
              artifacts: defaultUploadFiles,
            },
            {
              tool_name: TOOL_SEARCH_FILE_ID,
              artifacts: defaultUploadFiles,
            },
          ]
        : []),
    ];
    const tools = fields.tools ?? [];
    tools_metadata.forEach((tool) => {
      if (!tools.includes(tool.tool_name)) {
        tools.push(tool.tool_name);
      }
    });

    setFields({ ...fields, tools, tools_metadata });
  };

  const openGoogleFilePicker = useOpenGoogleDrivePicker((data) => {
    if (data.docs) {
      setGoogleFiles(
        data.docs.map((doc) => ({
          id: doc.id,
          name: doc.name,
          type: doc.type,
          url: doc.url,
        }))
      );
    }
  });

  const handleGoogleFilePicker = () => {
    setToolsMetadata();
    savePendingAssistant();
    openGoogleFilePicker();
  };

  const handleStepChange = (action: 'next' | 'back' | 'submit') => {
    switch (action) {
      case 'back':
        setCurrentStep((prev) => prev - 1);
        return;
      case 'next':
        setCurrentStep((prev) => prev + 1);
        return;
      case 'submit':
        setToolsMetadata();
        onSubmit();
        return;
    }
  };

  return (
    <div className="flex flex-col space-y-6">
      {/* Step 1: Define your assistant - name, description, instruction */}
      <CollapsibleSection
        title="Define your assistant"
        number={1}
        description="What does your assistant do?"
        isExpanded={source === 'update' || currentStep === 0}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 0 : 1)}
      >
        <DefineAssistantStep fields={fields} setFields={setFields} />
        <StepButtons onClick={handleStepChange} hide={source !== 'create'} disabled={!!nameError} />
      </CollapsibleSection>
      {/* Step 2: Data sources - google drive and file upload */}
      <CollapsibleSection
        title="Add data sources"
        number={2}
        description="Build a robust knowledge base for the assistant by adding files, folders, and documents."
        isExpanded={source === 'update' || currentStep === 1}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 1 : 2)}
      >
        <DataSourcesStep
          googleDriveEnabled={
            !!listToolsData?.find((t) => t.name === TOOL_GOOGLE_DRIVE_ID)?.is_available
          }
          googleFiles={googleFiles}
          defaultUploadFiles={defaultUploadFiles}
          openGoogleFilePicker={handleGoogleFilePicker}
          setGoogleFiles={setGoogleFiles}
          setDefaultUploadFiles={setDefaultUploadFiles}
        />
        <StepButtons onClick={handleStepChange} allowBack hide={source !== 'create'} />
      </CollapsibleSection>
      {/* Step 3: Tools */}
      <CollapsibleSection
        title="Set default tools"
        number={3}
        description="Select which external tools will be on by default in order to enhance the assistant’s capabilities and expand its foundational knowledge."
        isExpanded={source === 'update' || currentStep === 2}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 2 : 3)}
      >
        <ToolsStep
          tools={listToolsData}
          activeTools={fields.tools ?? []}
          setActiveTools={(tools: string[]) => setFields({ ...fields, tools })}
        />
        <StepButtons onClick={handleStepChange} allowBack allowSkip hide={source !== 'create'} />
      </CollapsibleSection>
      {/* Step 4: Visibility */}
      <CollapsibleSection
        title="Set visibility"
        number={4}
        description="Control who can access this assistant and its knowledge base."
        isExpanded={source === 'update' || currentStep === 3}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 3 : 0)}
      >
        <VisibilityStep
          isPublic={true}
          // TODO: add visibility when available
          setIsPublic={(isPublic: boolean) => alert('to be developed!')}
        />
        <StepButtons
          onClick={handleStepChange}
          nextLabel="Create"
          disabled={!!nameError}
          allowBack
          isSubmit
          hide={source !== 'create'}
        />
      </CollapsibleSection>
    </div>
  );
};

const StepButtons: React.FC<{
  onClick: (action: 'next' | 'back' | 'submit') => void;
  nextLabel?: string;
  allowSkip?: boolean;
  allowBack?: boolean;
  isSubmit?: boolean;
  disabled?: boolean;
  hide?: boolean;
}> = ({
  onClick,
  nextLabel = 'Next',
  allowSkip = false,
  allowBack = false,
  isSubmit = false,
  disabled = false,
  hide = false,
}) => {
  return (
    <div
      className={cn('flex w-full items-center justify-between pt-5', {
        'justify-end': !allowBack,
        hidden: hide,
      })}
    >
      <Button
        label="Back"
        kind="secondary"
        onClick={() => onClick('back')}
        className={cn({ hidden: !allowBack })}
      />
      <div className="flex items-center gap-4">
        <Button
          label="Skip"
          kind="secondary"
          onClick={() => onClick('next')}
          className={cn({ hidden: !allowSkip })}
        />
        <Button
          label={nextLabel}
          theme="evolved-green"
          kind="cell"
          icon={isSubmit ? 'checkmark' : 'arrow-right'}
          disabled={disabled}
          onClick={() => onClick(isSubmit ? 'submit' : 'next')}
        />
      </div>
    </div>
  );
};
