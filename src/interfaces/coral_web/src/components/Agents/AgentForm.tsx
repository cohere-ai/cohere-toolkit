import React from 'react';

import { CreateAgent, UpdateAgent } from '@/cohere-client';
import { Checkbox, Input, InputLabel, STYLE_LEVEL_TO_CLASSES, Text } from '@/components/Shared';
import { useListTools } from '@/hooks/tools';
import { cn } from '@/utils';

export type CreateAgentFormFields = Pick<
  CreateAgent,
  'name' | 'description' | 'preamble' | 'deployment' | 'model' | 'tools'
>;
export type UpdateAgentFormFields = UpdateAgent;
export type AgentFormFieldKeys = keyof CreateAgentFormFields | keyof UpdateAgentFormFields;

type Props = {
  fields: CreateAgentFormFields | UpdateAgentFormFields;
  onChange: (key: Omit<AgentFormFieldKeys, 'tools'>, value: string) => void;
  onToolToggle: (toolName: string, checked: boolean) => void;
  errors?: Partial<Record<AgentFormFieldKeys, string>>;
  disabled?: boolean;
  className?: string;
};
/**
 * @description Base form for creating/updating an agent.
 */
export const AgentForm: React.FC<Props> = ({
  fields,
  onChange,
  onToolToggle,
  errors,
  disabled,
  className,
}) => {
  const { data: toolsData } = useListTools();
  const tools = toolsData?.filter((t) => t.is_available) ?? [];

  return (
    <div className={cn('flex flex-col gap-y-4', className)}>
      <RequiredInputLabel label="name" className="pb-2">
        <Input
          kind="default"
          value={fields.name ?? ''}
          placeholder="Give your assistant a name"
          onChange={(e) => onChange('name', e.target.value)}
          hasError={!!errors?.name}
          errorText={errors?.name}
          disabled={disabled}
        />
      </RequiredInputLabel>
      <InputLabel label="description" className="pb-2">
        <Input
          kind="default"
          value={fields.description ?? ''}
          placeholder="What does your assistant do?"
          onChange={(e) => onChange('description', e.target.value)}
          disabled={disabled}
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
            'disabled:text-volcanic-700',
            {
              'border-marble-500 bg-marble-300': disabled,
            },
            STYLE_LEVEL_TO_CLASSES.p
          )}
          rows={5}
          onChange={(e) => onChange('preamble', e.target.value)}
          data-testid="input-preamble"
          disabled={disabled}
        />
      </InputLabel>
      <InputLabel label="Tools" className="mb-2">
        <div className="flex flex-col gap-y-4 px-3">
          {tools.map((tool, i) => {
            const enabledTools = [...(fields.tools ? fields.tools : [])];
            const enabledTool = enabledTools.find((t) => t === tool.name);
            const checked = !!enabledTool;
            return (
              <Checkbox
                key={tool.name}
                label={tool.name}
                name={tool.name + i}
                checked={checked}
                onChange={(e) => onToolToggle(tool.name, e.target.checked)}
                disabled={disabled}
              />
            );
          })}
        </div>
      </InputLabel>
    </div>
  );
};

const RequiredInputLabel: React.FC<{
  label: string;
  children: React.ReactNode;
  className?: string;
}> = ({ label, children, className }) => (
  <InputLabel
    label={
      <div className="flex items-center gap-x-2">
        <Text as="span" styleAs="label" className="text-volcanic-900">
          {label}
        </Text>
        <Text as="span" styleAs="label" className="text-danger-500">
          *required
        </Text>
      </div>
    }
    className={className}
  >
    {children}
  </InputLabel>
);
