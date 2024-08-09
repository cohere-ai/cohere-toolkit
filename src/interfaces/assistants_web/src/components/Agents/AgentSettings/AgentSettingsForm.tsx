'use client';

import { uniqBy } from 'lodash';
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

import { CreateAgentRequest, UpdateAgentRequest } from '@/cohere-client';
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
  | Omit<UpdateAgentRequest, 'version' | 'temperature'>
  | Omit<CreateAgentRequest, 'version' | 'temperature'>,
  'name' | 'model' | 'deployment'
>;

type Props = {
  source?: 'update' | 'create';
  fields: AgentSettingsFields;
  savePendingAssistant: VoidFunction;
  setFields: (fields: AgentSettingsFields) => void;
  onSubmit: VoidFunction;
  agentId?: string;
};

export const AgentSettingsForm: React.FC<Props> = ({
  source = 'create',
  fields,
  savePendingAssistant,
  setFields,
  onSubmit,
  agentId,
}) => {
  const { data: listToolsData, status: listToolsStatus } = useListTools();
  const isAgentNameUnique = useIsAgentNameUnique();
  const params = useSearchParams();
  const defaultStep = params.has('datasources');

  const [currentStep, setCurrentStep] = useState<
    'define' | 'dataSources' | 'tools' | 'visibility' | undefined
  >(() => (defaultStep ? 'dataSources' : 'define'));

  const [googleFiles, setGoogleFiles] = useState<DataSourceArtifact[]>(
    fields.tools_metadata?.find((metadata) => metadata.tool_name === TOOL_GOOGLE_DRIVE_ID)
      ?.artifacts as DataSourceArtifact[]
  );
  // read_document and search_files have identical metadata -> using read_document as base
  const [defaultUploadFiles, setDefaultUploadFiles] = useState<DataSourceArtifact[]>(
    fields.tools_metadata?.find((metadata) => metadata.tool_name === TOOL_READ_DOCUMENT_ID)
      ?.artifacts as DataSourceArtifact[]
  );

  const nameError = isAgentNameUnique(fields.name.trim(), agentId)
    ? 'Assistant name must be unique'
    : undefined;

  const canCreate = !nameError;

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

  useEffect(() => {
    if (googleFiles || defaultUploadFiles) {
      setToolsMetadata();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [googleFiles, defaultUploadFiles]);

  const openGoogleFilePicker = useOpenGoogleDrivePicker((data) => {
    if (data.docs) {
      setGoogleFiles((prev) => {
        const updatedArtifacts = [
          ...data.docs.map(
            (doc) =>
              ({
                id: doc.id,
                name: doc.name,
                type: doc.type,
                url: doc.url,
              } as DataSourceArtifact)
          ),
        ];

        return uniqBy([...(prev ?? []), ...updatedArtifacts], 'id');
      });
    }
  });

  const handleGoogleFilePicker = () => {
    savePendingAssistant();
    openGoogleFilePicker();
  };

  return (
    <div className="flex flex-col space-y-6 p-8">
      {/* Step 1: Define your assistant - name, description, instruction */}
      <CollapsibleSection
        title="Define your assistant"
        number={1}
        description="What does your assistant do?"
        isExpanded={currentStep === 'define'}
        setIsExpanded={(expanded) => setCurrentStep(expanded ? 'define' : undefined)}
      >
        <DefineAssistantStep fields={fields} setFields={setFields} nameError={nameError} />
        <StepButtons
          handleNext={() => setCurrentStep('dataSources')}
          hide={source !== 'create'}
          disabled={!!nameError}
        />
      </CollapsibleSection>
      {/* Step 2: Data sources - google drive and file upload */}
      <CollapsibleSection
        title="Add data sources"
        number={2}
        description="Build a robust knowledge base for the assistant by adding files, folders, and documents."
        isExpanded={currentStep === 'dataSources'}
        setIsExpanded={(expanded) => setCurrentStep(expanded ? 'dataSources' : undefined)}
      >
        <DataSourcesStep
          googleDriveEnabled={
            !!listToolsData?.find((t) => t.name === TOOL_GOOGLE_DRIVE_ID)?.is_available
          }
          googleFiles={googleFiles}
          defaultUploadFiles={defaultUploadFiles}
          isLoading={listToolsStatus === 'pending'}
          openGoogleFilePicker={handleGoogleFilePicker}
          setGoogleFiles={setGoogleFiles}
          setDefaultUploadFiles={setDefaultUploadFiles}
        />
        <StepButtons
          handleNext={() => setCurrentStep('tools')}
          handleBack={() => setCurrentStep('define')}
          hide={source !== 'create'}
        />
      </CollapsibleSection>
      {/* Step 3: Tools */}
      <CollapsibleSection
        title="Set default tools"
        number={3}
        description="Select which external tools will be on by default in order to enhance the assistant’s capabilities and expand its foundational knowledge."
        isExpanded={currentStep === 'tools'}
        setIsExpanded={(expanded) => setCurrentStep(expanded ? 'tools' : undefined)}
      >
        <ToolsStep
          tools={listToolsData}
          activeTools={fields.tools ?? []}
          setActiveTools={(tools: string[]) => setFields({ ...fields, tools })}
        />
        <StepButtons
          handleNext={() => setCurrentStep('visibility')}
          handleBack={() => setCurrentStep('dataSources')}
          hide={source !== 'create'}
        />
      </CollapsibleSection>
      {/* Step 4: Visibility */}
      <CollapsibleSection
        title="Set visibility"
        number={4}
        description="Control who can access this assistant and its knowledge base."
        isExpanded={currentStep === 'visibility'}
        setIsExpanded={(expanded) => setCurrentStep(expanded ? 'visibility' : undefined)}
      >
        <VisibilityStep
          isPublic={true}
          // TODO: add visibility when available
          setIsPublic={(_: boolean) => alert('to be developed!')}
        />
        <StepButtons
          handleNext={onSubmit}
          handleBack={() => setCurrentStep('tools')}
          nextLabel="Create"
          disabled={!canCreate}
          isSubmit
          hide={source !== 'create'}
        />
      </CollapsibleSection>
    </div>
  );
};

const StepButtons: React.FC<{
  handleNext: VoidFunction;
  handleBack?: VoidFunction;
  nextLabel?: string;
  isSubmit?: boolean;
  disabled?: boolean;
  hide?: boolean;
}> = ({
  handleNext,
  handleBack,
  nextLabel = 'Next',
  isSubmit = false,
  disabled = false,
  hide = false,
}) => {
  return (
    <div
      className={cn('flex w-full items-center justify-between pt-5', {
        'justify-end': !handleBack,
        hidden: hide,
      })}
    >
      <Button
        label="Back"
        kind="secondary"
        onClick={handleBack}
        className={cn({ hidden: !handleBack })}
      />
      <div className="flex items-center gap-4">
        <Button
          label={nextLabel}
          theme="default"
          kind="cell"
          icon={isSubmit ? 'checkmark' : 'arrow-right'}
          disabled={disabled}
          onClick={handleNext}
        />
      </div>
    </div>
  );
};
