import { useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';

import { UpdateAgent } from '@/cohere-client';
import { DataSourcesStep } from '@/components/Agents/AgentSettings/DataSourcesStep';
import { DefineAssistantStep } from '@/components/Agents/AgentSettings/DefineStep';
import { CollapsibleSection } from '@/components/CollapsibleSection';
import {
  DEFAULT_AGENT_TOOLS,
  TOOL_GOOGLE_DRIVE_ID,
  TOOL_PYTHON_INTERPRETER_ID,
  TOOL_READ_DOCUMENT_ID,
  TOOL_SEARCH_FILE_ID,
  TOOL_WEB_SEARCH_ID,
} from '@/constants';
import { useListTools } from '@/hooks/tools';
import { DataSourceArtifact } from '@/types/tools';
import { getDefaultUploadArtifacts } from '@/utils/artifacts';

import { ToolsStep } from './ToolsStep';
import { VisibilityStep } from './VisibilityStep';

type AgentSettingsFields = Omit<UpdateAgent, 'version' | 'temperature'>;
type Props = {
  existingAgent?: AgentSettingsFields;
  defaultValues?: ASSISTANT_SETTINGS_FORM;
  isExistingAgent?: boolean;
  onSubmit: VoidFunction;
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
  isPublic: boolean;
};

export const AgentSettingsForm: React.FC<Props> = ({
  existingAgent,
  defaultValues,
  isExistingAgent = false,
  onSubmit,
}) => {
  const [currentStep, setCurrentStep] = useState<number | null>(0);

  const existingAgentValues: ASSISTANT_SETTINGS_FORM | undefined = useMemo(() => {
    if (!existingAgent || !existingAgent.name) return;
    const googleDriveArtifacts = existingAgent?.tools_metadata?.find(
      (metadata) => metadata.tool_name === TOOL_GOOGLE_DRIVE_ID
    )?.artifacts as DataSourceArtifact[];
    const defaultUploadArtifacts = getDefaultUploadArtifacts(
      existingAgent?.tools_metadata?.find(
        (metadata) => metadata.tool_name === TOOL_READ_DOCUMENT_ID
      )?.artifacts as DataSourceArtifact[],
      existingAgent?.tools_metadata?.find((metadata) => metadata.tool_name === TOOL_SEARCH_FILE_ID)
        ?.artifacts as DataSourceArtifact[]
    );

    return {
      name: existingAgent.name,
      description: existingAgent.description,
      instructions: existingAgent.preamble,
      tools: existingAgent.tools ?? [],
      dataSources: {
        googleDrive: googleDriveArtifacts,
        defaultUpload: defaultUploadArtifacts,
      },
      isPublic: true,
    };
  }, [existingAgent]);

  const {
    register,
    setValue,
    watch,
    handleSubmit,
    formState: { errors },
  } = useForm<ASSISTANT_SETTINGS_FORM>({
    defaultValues: existingAgentValues ??
      defaultValues ?? {
        name: '',
        dataSources: {},
        isPublic: true,
      },
  });
  const { data: listToolsData } = useListTools();
  const name = watch('name');
  const dataSources = watch('dataSources');
  const tools = watch('tools');
  const isPublic = watch('isPublic');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col space-y-6 p-8">
      {/* Step 1: Define your assistant - name, description, instruction */}
      <CollapsibleSection
        title="Define your assistant"
        number={1}
        description="What does your assistant do?"
        isExpanded={currentStep === 0}
        setIsExpanded={(expanded: boolean) => setCurrentStep(expanded ? 0 : null)}
      >
        <DefineAssistantStep register={register} handleNext={() => setCurrentStep(1)} />
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
          dataSources={dataSources}
          googleDriveEnabled={
            !!listToolsData?.find((t) => t.name === TOOL_GOOGLE_DRIVE_ID)?.is_available
          }
          isUpdatingAgent={isExistingAgent}
          setDataSources={(val: AgentDataSources) => setValue('dataSources', val)}
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
          pythonTool={listToolsData?.find((t) => t.name === TOOL_PYTHON_INTERPRETER_ID)}
          webSearchTool={listToolsData?.find((t) => t.name === TOOL_WEB_SEARCH_ID)}
          activeTools={tools}
          setActiveTools={(tools?: string[]) => setValue('tools', tools)}
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
          isPublic={isPublic}
          setIsPublic={(isPublic: boolean) => setValue('isPublic', isPublic)}
          handleNext={onSubmit}
          handleBack={() => setCurrentStep(3)}
          canSubmit={!!name && !!name.trim() && !errors.name}
        />
      </CollapsibleSection>
    </form>
  );
};
