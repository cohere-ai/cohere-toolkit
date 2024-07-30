import { useState } from 'react';
import { useForm } from 'react-hook-form';

import { CreateAgent, ManagedTool } from '@/cohere-client';
import { DataSourcesStep } from '@/components/Agents/AgentSettings/DataSourcesStep';
import { DefineAssistantStep } from '@/components/Agents/AgentSettings/DefineStep';
import { CollapsibleSection } from '@/components/CollapsibleSection';
import { TOOL_GOOGLE_DRIVE_ID, TOOL_PYTHON_INTERPRETER_ID, TOOL_WEB_SEARCH_ID } from '@/constants';
import { useListTools, useOpenGoogleDrivePicker } from '@/hooks/tools';
import { DataSourceArtifact } from '@/types/tools';

import { ToolsStep } from './ToolsStep';

type AgentSettingsFields = Omit<CreateAgent, 'version' | 'temperature'>;
type Props = {
  fields?: AgentSettingsFields;
  setFields: (fields: AgentSettingsFields) => void;
  handleOpenFilePicker: VoidFunction;
};

export type AgentDataSources = {
  googleDrive?: DataSourceArtifact[];
  defaultUpload?: DataSourceArtifact[];
};
export type ASSISTANT_SETTINGS_FORM = {
  name: string;
  description?: string | null;
  instruction?: string | null;
  tools?: string[];
  dataSources: AgentDataSources;
};

export const AgentSettingsForm: React.FC<Props> = ({ fields, setFields, handleOpenFilePicker }) => {
  const [currentStep, setCurrentStep] = useState<number | null>(0);
  const { register, setValue, getValues, watch } = useForm<ASSISTANT_SETTINGS_FORM>({
    defaultValues: {
      name: fields?.name ?? '',
      description: fields?.description,
      instruction: fields?.preamble,
    },
  });
  const { data: listToolsData } = useListTools();
  const dataSources = watch('dataSources');
  const tools = watch('tools');

  return (
    <div className="flex flex-col space-y-6 p-8">
      {/* Step 1: Define your assistant - name, description, instruction */}
      <CollapsibleSection
        title="Define your assistant"
        number={1}
        description="What does your assistant do?"
        expanded={currentStep === 0}
        // setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 0 : null)}
      >
        <DefineAssistantStep register={register} handleNext={() => setCurrentStep(1)} />
      </CollapsibleSection>
      {/* Step 2: Data sources - google drive and file upload */}
      <CollapsibleSection
        title="Add data sources"
        number={2}
        description="Build a robust knowledge base for the assistant by adding files, folders, and documents."
        expanded={currentStep === 1}
      >
        <DataSourcesStep
          dataSources={dataSources}
          googleDriveEnabled={
            !!listToolsData?.find((t) => t.name === TOOL_GOOGLE_DRIVE_ID)?.is_available
          }
          setDataSources={(val: AgentDataSources) => setValue('dataSources', val)}
        />
      </CollapsibleSection>
      {/* Step 3: Tools */}
      <CollapsibleSection
        title="Set default tools"
        number={3}
        description="Select which external tools will be on by default in order to enhance the assistant’s capabilities and expand its foundational knowledge."
        expanded={currentStep === 2}
      >
        <ToolsStep
          pythonTool={listToolsData?.find((t) => t.name === TOOL_PYTHON_INTERPRETER_ID)}
          webSearchTool={listToolsData?.find((t) => t.name === TOOL_WEB_SEARCH_ID)}
          activeTools={tools}
          setActiveTools={(tools?: string[]) => setValue('tools', tools)}
        />
      </CollapsibleSection>
    </div>
  );
};
