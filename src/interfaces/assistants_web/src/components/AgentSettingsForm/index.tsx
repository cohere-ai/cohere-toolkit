'use client';

import { CarbonConnect } from 'carbon-connect';
import { uniqBy } from 'lodash';
import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

import { CreateAgentRequest, UpdateAgentRequest } from '@/cohere-client';
import { DataSourcesStep } from '@/components/AgentSettingsForm/DataSourcesStep';
import { DefineAssistantStep } from '@/components/AgentSettingsForm/DefineStep';
import { ToolsStep } from '@/components/AgentSettingsForm/ToolsStep';
import { VisibilityStep } from '@/components/AgentSettingsForm/VisibilityStep';
import { Button, CollapsibleSection } from '@/components/UI';
import { TOOL_GOOGLE_DRIVE_ID, TOOL_READ_DOCUMENT_ID, TOOL_SEARCH_FILE_ID } from '@/constants';
import { useIsAgentNameUnique, useListTools, useOpenGoogleDrivePicker } from '@/hooks';
import { DataSourceArtifact } from '@/types/tools';
import { cn, getToolAuthUrl } from '@/utils';

type RequiredAndNotNull<T> = {
  [P in keyof T]-?: Exclude<T[P], null | undefined>;
};

type RequireAndNotNullSome<T, K extends keyof T> = RequiredAndNotNull<Pick<T, K>> & Omit<T, K>;

type CreateAgentSettingsFields = RequireAndNotNullSome<
  Omit<CreateAgentRequest, 'version' | 'temperature'>,
  'name' | 'model' | 'deployment'
>;

type UpdateAgentSettingsFields = RequireAndNotNullSome<
  Omit<UpdateAgentRequest, 'version' | 'temperature'>,
  'name' | 'model' | 'deployment'
> & { is_private?: boolean };

export type AgentSettingsFields = CreateAgentSettingsFields | UpdateAgentSettingsFields;

type BaseProps = {
  fields: AgentSettingsFields;
  setFields: (fields: AgentSettingsFields) => void;
  onSubmit: VoidFunction;
};

type CreateProps = BaseProps & {
  source: 'create';
  carbonId?: string;
};

type UpdateProps = BaseProps & {
  source: 'update';
  agentId: string;
};

export type Props = CreateProps | UpdateProps;

export const AgentSettingsForm: React.FC<Props> = (props) => {
  const { source = 'create', fields, setFields, onSubmit } = props;
  const agentId = 'agentId' in props ? props.agentId : undefined;
  const carbonId = 'carbonId' in props ? props.carbonId : undefined;

  const { data: listToolsData, status: listToolsStatus } = useListTools();
  const isAgentNameUnique = useIsAgentNameUnique();
  const params = useSearchParams();
  const defaultStep = params.has('datasources');
  const defaultState = params.has('state');

  useEffect(() => {
    if (defaultState) {
      const state = params.get('state');
      if (state) {
        try {
          const fields = JSON.parse(atob(state));
          setFields(fields);
        } catch {
          console.error('Error parsing state');
        }
      }
    }
  }, [defaultState, params, setFields]);

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
      ...(googleFiles && googleFiles.length > 0
        ? [
            {
              tool_name: TOOL_GOOGLE_DRIVE_ID,
              artifacts: googleFiles,
            },
          ]
        : []),
      ...(defaultUploadFiles && defaultUploadFiles.length > 0
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
    let tools = fields.tools ?? [];
    if (tools_metadata.some((metadata) => metadata.tool_name === TOOL_GOOGLE_DRIVE_ID)) {
      tools = tools.concat(TOOL_GOOGLE_DRIVE_ID);
    } else {
      tools = tools.filter((tool) => tool !== TOOL_GOOGLE_DRIVE_ID);
    }

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

  const tokenFetcher = async () => {
    if (!carbonId) {
      throw new Error('Carbon ID not found');
    }
    const response = await fetch(
      `http://localhost:8000/v1/fetch_carbon_tokens?customer_id=${carbonId}`
    );
    const data = await response.json();

    return data;
  };

  const handleGoogleFilePicker = () => {
    const googleDriveTool = listToolsData?.find((t) => t.name === TOOL_GOOGLE_DRIVE_ID);
    if (!googleDriveTool?.is_available) {
      return;
    }

    // If auth is required and token is not present, redirect to auth url
    if (googleDriveTool?.is_auth_required && googleDriveTool.auth_url) {
      const state = JSON.stringify(fields);

      window.open(
        getToolAuthUrl(
          googleDriveTool.auth_url,
          `${window.location.href}?datasources=1&state=${btoa(state)}`
        ),
        '_self'
      );
    } else {
      openGoogleFilePicker?.();
    }
  };

  return (
    <div className="flex flex-col space-y-6">
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
      {carbonId && (
        <CollapsibleSection
          title="Set up carbon"
          number={4}
          description="configure carbon"
          isExpanded={true}
        >
          {/* TODO configure this!!! */}
          <CarbonConnect
            orgName="Cohere"
            tokenFetcher={tokenFetcher}
            tags={{
              tag1: 'tag1_value',
              tag2: 'tag2_value',
              tag3: 'tag3_value',
            }}
            maxFileSize={10000000}
            enabledIntegrations={[
              {
                id: 'GMAIL',
                chunkSize: 1000,
                overlapSize: 20,
                fileSyncConfig: {
                  detect_audio_language: true,
                  split_rows: true,
                },
              },
            ]}
            onSuccess={(data) => console.log('Data on Success: ', data)}
            onError={(error) => console.log('Data on Error: ', error)}
            primaryBackgroundColor="#F2F2F2"
            primaryTextColor="#555555"
            secondaryBackgroundColor="#f2f2f2"
            secondaryTextColor="#000000"
            allowMultipleFiles={true}
            open={false}
            chunkSize={1500}
            overlapSize={20}
          ></CarbonConnect>
        </CollapsibleSection>
      )}
      {/* Step 4: Visibility */}
      <CollapsibleSection
        title="Set visibility"
        number={5}
        description="Control who can access this assistant and its knowledge base."
        isExpanded={currentStep === 'visibility'}
        setIsExpanded={(expanded) => setCurrentStep(expanded ? 'visibility' : undefined)}
      >
        <VisibilityStep
          isPrivate={Boolean(fields.is_private)}
          setIsPrivate={(isPrivate) => setFields({ ...fields, is_private: isPrivate })}
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
