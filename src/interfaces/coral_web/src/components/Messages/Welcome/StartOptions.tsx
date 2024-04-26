import { RadioGroup } from '@headlessui/react';
import React from 'react';

import { DEFAULT_CHAT_TOOL } from '@/cohere-client';
import { OptionCard } from '@/components/Messages/Welcome/OptionCard';
import { Text } from '@/components/Shared';
import { useFocusComposer } from '@/hooks/actions';
import { useParamsStore } from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';

export enum StartOptionKey {
  UNGROUNDED = 'ungrounded',
  WEB_SEARCH = 'web-search',
  DOCUMENTS = 'documents',
}

type StartOption = {
  title: string;
  description: string;
  features: string[];
  params: Partial<ConfigurableParams>;
  onChange?: VoidFunction;
};

/**
 * @description Renders the getting started options for new conversations
 */
export const StartOptions: React.FC<{
  selectedOption: StartOptionKey;
  onOptionSelect: (option: StartOptionKey) => void;
}> = ({ selectedOption, onOptionSelect }) => {
  const { setParams } = useParamsStore();
  const { focusComposer } = useFocusComposer();

  const START_OPTIONS: Record<StartOptionKey, StartOption> = {
    [StartOptionKey.UNGROUNDED]: {
      title: 'Chat only',
      description: 'The model will respond without any sources and citations.',
      features: [
        'Code generation: "Help me debug this code..."',
        'Brainstorming: "10 startup name ideas"',
        'Creative writing: "Email to my boss about time off"',
      ],
      params: {
        tools: [],
        fileIds: [],
      },
    },
    [StartOptionKey.WEB_SEARCH]: {
      title: 'Chat with Wikipedia',
      description:
        'If required for response model will search wikipedia first to find a response. Uses default tool Langchain WikiRetriever.',
      features: ['Topic learning: "How does photosynthesis work"'],
      params: {
        tools: [{ name: DEFAULT_CHAT_TOOL }],
      },
    },
    [StartOptionKey.DOCUMENTS]: {
      title: 'Chat with documents',
      description: 'Upload a PDF or TXT file for the model to search and cite in its response.',
      features: ['Long document analysis and summarization'],
      params: {},
      onChange: () => {
        setTimeout(() => focusComposer(), 100);
      },
    },
  };

  const handleSelectOption = (key: StartOptionKey) => {
    const { params } = START_OPTIONS[key];
    onOptionSelect(key);
    setParams(params);
  };

  return (
    <div className="flex flex-col items-center gap-y-6">
      <Text styleAs="h4">Choose an option to get started</Text>
      <RadioGroup
        value={selectedOption}
        onChange={(key: StartOptionKey) => {
          const { onChange } = START_OPTIONS[key];
          handleSelectOption(key);
          onChange?.();
        }}
        className="flex w-full flex-col justify-center gap-x-6 gap-y-4 pb-10 md:flex-row"
      >
        {(Object.keys(START_OPTIONS) as StartOptionKey[]).map((key) => {
          const option = START_OPTIONS[key];
          return <OptionCard key={key} value={key as StartOptionKey} {...option} />;
        })}
      </RadioGroup>
    </div>
  );
};
