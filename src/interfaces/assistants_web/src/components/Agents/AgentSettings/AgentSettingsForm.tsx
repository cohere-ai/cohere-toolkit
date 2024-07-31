import { useMemo, useState } from 'react';

import { CreateAgent, UpdateAgent } from '@/cohere-client';
import { DataSourcesStep } from '@/components/Agents/AgentSettings/DataSourcesStep';
import { DefineAssistantStep } from '@/components/Agents/AgentSettings/DefineStep';
import { ToolsStep } from '@/components/Agents/AgentSettings/ToolsStep';
import { VisibilityStep } from '@/components/Agents/AgentSettings/VisibilityStep';
import { CollapsibleSection } from '@/components/CollapsibleSection';
import { Button } from '@/components/Shared';
import { TOOL_GOOGLE_DRIVE_ID, TOOL_READ_DOCUMENT_ID, TOOL_SEARCH_FILE_ID } from '@/constants';
import { useIsAgentNameUnique } from '@/hooks/agents';
import { useListTools } from '@/hooks/tools';
import { DataSourceArtifact } from '@/types/tools';

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
  setFields: (fields: AgentSettingsFields) => void;
  onSubmit: VoidFunction;
};

export const AgentSettingsForm: React.FC<Props> = ({
  source = 'create',
  fields,
  setFields,
  onSubmit,
}) => {
  const { data: listToolsData } = useListTools();
  const isAgentNameUnique = useIsAgentNameUnique();

  const [currentStep, setCurrentStep] = useState<number | null>(0);

  const [googleFiles, setGoogleFiles] = useState<DataSourceArtifact[]>(
    fields.tools_metadata?.find((metadata) => metadata.tool_name === TOOL_GOOGLE_DRIVE_ID)
      ?.artifacts as DataSourceArtifact[]
  );
  // read_document and search_files have identical metadata -> using read_document as base
  const [defaultUploadFiles, setDefaultUploadFiles] = useState<DataSourceArtifact[]>(
    fields.tools_metadata?.find((metadata) => metadata.tool_name === TOOL_READ_DOCUMENT_ID)
      ?.artifacts as DataSourceArtifact[]
  );

  const nameError = useMemo(() => {
    return !fields.name.trim()
      ? 'Assistant name is required'
      : isAgentNameUnique(fields.name.trim())
      ? 'Assistant name must be unique'
      : undefined;
  }, [fields.name]);

  const handleSubmit = () => {
    const tools_metadata = [
      ...(!!googleFiles.length
        ? [
            {
              tool_name: TOOL_GOOGLE_DRIVE_ID,
              artifacts: googleFiles,
            },
          ]
        : []),
      ...(!!defaultUploadFiles.length
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

    onSubmit();
  };

  return (
    <div className="flex flex-col space-y-6 p-8">
      {/* Step 1: Define your assistant - name, description, instruction */}
      <CollapsibleSection
        title="Define your assistant"
        number={1}
        description="What does your assistant do?"
        isExpanded={currentStep === 0}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 0 : null)}
      >
        <DefineAssistantStep
          fields={fields}
          setFields={setFields}
          handleNext={() => setCurrentStep(1)}
        />
      </CollapsibleSection>
      {/* Step 2: Data sources - google drive and file upload */}
      <CollapsibleSection
        title="Add data sources"
        number={2}
        description="Build a robust knowledge base for the assistant by adding files, folders, and documents."
        isExpanded={currentStep === 1}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 1 : null)}
      >
        <DataSourcesStep
          googleDriveEnabled={
            !!listToolsData?.find((t) => t.name === TOOL_GOOGLE_DRIVE_ID)?.is_available
          }
          googleFiles={googleFiles}
          defaultUploadFiles={defaultUploadFiles}
          setGoogleFiles={setGoogleFiles}
          setDefaultUploadFiles={setDefaultUploadFiles}
          handleNext={() => setCurrentStep(2)}
          handleBack={() => setCurrentStep(1)}
        />
      </CollapsibleSection>
      {/* Step 3: Tools */}
      <CollapsibleSection
        title="Set default tools"
        number={3}
        description="Select which external tools will be on by default in order to enhance the assistant’s capabilities and expand its foundational knowledge."
        isExpanded={currentStep === 2}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 2 : null)}
      >
        <ToolsStep
          tools={listToolsData}
          activeTools={fields.tools ?? []}
          setActiveTools={(tools: string[]) => setFields({ ...fields, tools })}
          handleNext={() => setCurrentStep(3)}
          handleBack={() => setCurrentStep(2)}
        />
      </CollapsibleSection>
      {/* Step 4: Visibility */}
      <CollapsibleSection
        title="Set visibility"
        number={4}
        description="Control who can access this assistant and its knowledge base."
        isExpanded={currentStep === 3}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 3 : null)}
      >
        <VisibilityStep
          isPublic={true}
          setIsPublic={(isPublic: boolean) => alert('to be developed!')}
        />
        <div className="flex w-full items-center justify-between">
          <Button label="Back" kind="secondary" onClick={() => setCurrentStep(2)} />
          <Button
            label={source === 'create' ? 'Create' : 'Update'}
            theme="evolved-green"
            kind="cell"
            icon="checkmark"
            disabled={!nameError}
            onClick={handleSubmit}
          />
        </div>
      </CollapsibleSection>
    </div>
  );
};
