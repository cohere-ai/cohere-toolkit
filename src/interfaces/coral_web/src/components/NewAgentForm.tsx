import Link from 'next/link';
import React, { useState } from 'react';

import { AgentModel, CreateAgent, ToolName } from '@/cohere-client';
import IconButton from '@/components/IconButton';
import { Button, Checkbox, Dropdown, Input, InputLabel, Text } from '@/components/Shared';
import { useCreateAgent } from '@/hooks/agents';
import { cn } from '@/utils';

type AgentForm = Omit<CreateAgent, 'version' | 'temperature' | 'deployment'>;

/**
 * @description Form to create a new agent.
 */
export const NewAgentForm: React.FC = () => {
  const { mutateAsync: createAgent } = useCreateAgent();
  const tools = Object.values(ToolName);
  const modelOptions = [
    {
      options: Object.values(AgentModel).map((model) => ({
        label: model,
        value: model,
      })),
    },
  ];

  const [fields, setFields] = useState<AgentForm>({
    name: '',
    description: '',
    preamble: '',
    model: AgentModel.COMMAND_R_PLUS,
    tools: [],
  });
  const canSubmit = (() => {
    const { tools: enabledTools, ...textFields } = fields;
    return enabledTools && enabledTools.length > 0 && Object.values(textFields).every(Boolean);
  })();

  const handleTextFieldChange = (key: Omit<keyof AgentForm, 'tools'>, value: string) => {
    setFields({
      ...fields,
      [key as string]: value,
    });
  };

  const handleToolToggle = (toolName: ToolName, checked: boolean) => {
    const enabledTools = [...(fields.tools ? fields.tools : [])];
    setFields({
      ...fields,
      tools: checked ? [...enabledTools, toolName] : enabledTools.filter((t) => t !== toolName),
    });
  };

  const handleSubmit = () => {
    if (!canSubmit) return;

    createAgent(fields);
  };

  return (
    <div className="flex max-w-[650px] flex-col p-10">
      <Link className="mb-4 flex items-center gap-x-2 text-green-700" href="/agents">
        <IconButton iconName="chevron-left" />
        <Text>Back to Assistant</Text>
      </Link>
      <Text styleAs="h3">New Assistant</Text>
      <div className="my-10 flex flex-col gap-y-4">
        <Input
          value={fields.name ?? ''}
          label="name"
          placeholder="Give your assistant a name"
          onChange={(e) => handleTextFieldChange('name', e.target.value)}
        />
        <Input
          value={fields.description ?? ''}
          label="description"
          placeholder="What does your assistant do?"
          onChange={(e) => handleTextFieldChange('description', e.target.value)}
        />
        <div
          className={cn(
            'mt-2 w-full flex-1 resize-none p-3',
            'rounded-lg border',
            'border-marble-500 placeholder:text-volcanic-700 focus:border-secondary-700',
            'focus-visible:outline focus-visible:outline-1 focus-visible:outline-offset-4 focus-visible:outline-volcanic-900'
          )}
        >
          <InputLabel label="Preamble">
            <textarea
              value={fields.preamble ?? ''}
              placeholder="Give instructions to your chatbot. What does it do? How does it behave?"
              className="mt-1 w-full resize-none bg-marble-100 text-sm"
              rows={5}
              onChange={(e) => handleTextFieldChange('preamble', e.target.value)}
              data-testid="input-preamble"
            />
          </InputLabel>
        </div>
        <Dropdown
          className="w-full"
          label="Model"
          kind="default"
          value={fields.model}
          onChange={(model: string) => handleTextFieldChange('model', model)}
          optionGroups={modelOptions}
        />
        <div
          className={cn(
            'w-full flex-1 p-3',
            'transition ease-in-out',
            'rounded-lg border',
            'border-marble-500 placeholder:text-volcanic-700 focus:border-secondary-700'
          )}
        >
          <InputLabel label="Tools" className="mb-2" />
          <div className="flex flex-col gap-y-4">
            {tools.map((toolName) => {
              const enabledTools = [...(fields.tools ? fields.tools : [])];
              const enabledTool = enabledTools.find((tool) => tool === toolName);
              const checked = !!enabledTool;
              return (
                <Checkbox
                  key={toolName}
                  label={toolName}
                  checked={checked}
                  onChange={(e) => handleToolToggle(toolName, e.target.checked)}
                />
              );
            })}
          </div>
        </div>
      </div>
      <Button
        splitIcon="check-mark"
        onClick={handleSubmit}
        disabled={!canSubmit}
        className="self-end"
      >
        Create
      </Button>
    </div>
  );
};
