import React from 'react';

import { CreateAgent } from '@/cohere-client';
import {
  Checkbox,
  Dropdown,
  DropdownOptionGroups,
  Input,
  InputLabel,
  STYLE_LEVEL_TO_CLASSES,
} from '@/components/Shared';
import { useModels } from '@/hooks/deployments';
import { useListTools } from '@/hooks/tools';
import { cn } from '@/utils';

export type AgentFormFields = Omit<CreateAgent, 'version' | 'temperature'>;
export type AgentFormFieldKeys = keyof AgentFormFields;

type Props = {
  fields: AgentFormFields;
  onChange: (key: Omit<AgentFormFieldKeys, 'tools'>, value: string) => void;
  onToolToggle: (toolName: string, checked: boolean) => void;
  onEnvVariableChange: (envVar: string) => (e: React.ChangeEvent<HTMLInputElement>) => void;
  errors?: Partial<Record<AgentFormFieldKeys, string>>;
  className?: string;
};
/**
 * @description Base form for creating/updating an agent.
 */
export const AgentForm: React.FC<Props> = ({
  fields,
  onChange,
  onToolToggle,
  onEnvVariableChange,
  errors,
  className,
}) => {
  const { models } = useModels(fields.deployment);
  const modelOptions: DropdownOptionGroups = [
    {
      options: models.map((model) => ({
        label: model,
        value: model,
      })),
    },
  ];
  const { data: toolsData } = useListTools();
  const tools = toolsData?.filter((t) => t.is_available) ?? [];

  const handleDeploymentChange = (value: string) => {
    onChange('deployment', value);

    if (value === DEPLOYMENT_COHERE_PLATFORM) {
      onChange('model', MODEL_COMMMAND_R_PLUS);
    } else {
      onChange('model', '');
    }
  };

  return (
    <div className={cn('flex flex-col gap-y-4', className)}>
      <InputLabel label="name" className="pb-2">
        <Input
          kind="default"
          value={fields.name ?? ''}
          placeholder="Give your assistant a name"
          onChange={(e) => onChange('name', e.target.value)}
          hasError={!!errors?.name}
          errorText={errors?.name}
        />
      </InputLabel>
      <InputLabel label="description" className="pb-2">
        <Input
          kind="default"
          value={fields.description ?? ''}
          placeholder="What does your assistant do?"
          onChange={(e) => onChange('description', e.target.value)}
        />
      </InputLabel>
      <InputLabel label="Preamble">
        <textarea
          value={fields.preamble ?? ''}
          placeholder="Give instructions to your chatbot. What does it do? How does it behave?"
          className={cn(
            'mt-2 w-full flex-1 resize-none p-3',
            'transition ease-in-out',
            'rounded-lg border',
            'bg-marble-100',
            'border-marble-500 placeholder:text-volcanic-700 focus:border-secondary-700',
            'focus-visible:outline focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-900',
            STYLE_LEVEL_TO_CLASSES.p
          )}
          rows={5}
          onChange={(e) => onChange('preamble', e.target.value)}
          data-testid="input-preamble"
        />
      </InputLabel>
      <InputLabel label="Deployment" className="pb-2">
        <EnvVariablesForm
          deployment={fields.deployment}
          deploymentOptions={deploymentOptions}
          envVariables={envVariables}
          onDeploymentChange={handleDeploymentChange}
          onEnvVariableChange={onEnvVariableChange}
        />
      </InputLabel>
      <Dropdown
        className="w-full"
        label="Model"
        kind="default"
        value={fields.model}
        onChange={(model: string) => onChange('model', model)}
        optionGroups={modelOptions}
      />
      <InputLabel label="Tools" className="mb-2">
        <div className="flex flex-col gap-y-4 px-3">
          {tools.map((tool) => {
            const enabledTools = [...(fields.tools ? fields.tools : [])];
            const enabledTool = enabledTools.find((t) => t === tool.name);
            const checked = !!enabledTool;
            return (
              <Checkbox
                key={tool.name}
                label={tool.name}
                checked={checked}
                onChange={(e) => onToolToggle(tool.name, e.target.checked)}
              />
            );
          })}
        </div>
      </InputLabel>
    </div>
  );
};
