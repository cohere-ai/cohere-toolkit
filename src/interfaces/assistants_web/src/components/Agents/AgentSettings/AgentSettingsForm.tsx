import { useState } from 'react';
import { useForm } from 'react-hook-form';

import { CreateAgent } from '@/cohere-client';
import { DataSourcesStep } from '@/components/Agents/AgentSettings/DataSourcesStep';
import { DefineAssistantStep } from '@/components/Agents/AgentSettings/DefineStep';
import { CollapsibleSection } from '@/components/CollapsibleSection';
import { useListTools, useOpenGoogleDrivePicker } from '@/hooks/tools';
import { DataSourceArtifact } from '@/types/tools';

type AgentSettingsFields = Omit<CreateAgent, 'version' | 'temperature'>;
type Props = {
  fields?: AgentSettingsFields;
  setFields: (fields: AgentSettingsFields) => void;
  handleOpenFilePicker: VoidFunction;
};

export type ASSISTANT_SETTINGS_FORM = {
  name: string;
  description?: string | null;
  instruction?: string | null;
  tools: string[];
  dataSourceArtifacts?: {
    googleDrive?: DataSourceArtifact[];
    fileUpload?: DataSourceArtifact[];
  };
};

export const AgentSettingsForm: React.FC<Props> = ({ fields, setFields, handleOpenFilePicker }) => {
  const [currentStep, setCurrentStep] = useState<number | null>(0);
  const { register, setValue, getValues } = useForm<ASSISTANT_SETTINGS_FORM>({
    defaultValues: {
      name: fields?.name ?? '',
      description: fields?.description,
      instruction: fields?.preamble,
      tools: [],
    },
  });
  const { data: listToolsData } = useListTools();

  const openFilePicker = useOpenGoogleDrivePicker((data) => {
    if (data.docs) {
      setValue(
        'dataSourceArtifacts.googleDrive',
        data.docs.map(
          (doc) =>
            ({
              id: doc.id,
              name: doc.name,
              type: doc.type,
              url: doc.url,
            } as DataSourceArtifact)
        )
      );
    }
  });

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
          fields={getValues()}
          setValue={setValue}
          tools={listToolsData}
          openFilePicker={openFilePicker}
        />
      </CollapsibleSection>
    </div>
  );
};
