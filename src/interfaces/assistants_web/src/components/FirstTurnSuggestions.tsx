'use client';

import { Transition } from '@headlessui/react';
import React, { useMemo } from 'react';

import ButtonGroup from '@/components/ButtonGroup';
import { TOOL_CALCULATOR_ID, TOOL_PYTHON_INTERPRETER_ID, TOOL_WEB_SEARCH_ID } from '@/constants';
import { useListTools } from '@/hooks/tools';
import { useParamsStore } from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';
import { cn } from '@/utils';

type Prompt = {
  label: string;
  params: Partial<ConfigurableParams>;
  message: string;
};

const SUGGESTED_PROMPTS: Prompt[] = [
  {
    label: 'Plot real estate data',
    params: {
      fileIds: [],
      tools: [
        { name: TOOL_PYTHON_INTERPRETER_ID },
        { name: TOOL_CALCULATOR_ID },
        { name: TOOL_WEB_SEARCH_ID },
      ],
    },
    message:
      'Plot the average 1 bedroom rental price in Jan 2024 for the 5 most expensive cities in North America',
  },
  {
    label: 'Clean up data in Python',
    params: { fileIds: [], tools: [] },
    message: `I want to figure out how to remove nan values from my array. For example, my array looks something like this:
    
    x = [1400, 1500, 1600, nan, nan, nan, 1700] #Not in this exact configuration
        
    How can I remove the nan values from x to get something like:
        
    x = [1400, 1500, 1600, 1700]`,
  },
  {
    label: 'Write a business plan in French',
    params: { fileIds: [], tools: [] },
    message:
      'Write a business plan outline for an marketing agency in French. Highlight all the section titles, and make it less than 300 words.',
  },
];

type Props = {
  isFirstTurn: boolean;
  onSuggestionClick: (message: string, overrides?: Partial<ConfigurableParams>) => void;
};

/**
 * @description Shows clickable suggestions for the user's first turn in the conversation.
 */
export const FirstTurnSuggestions: React.FC<Props> = ({ isFirstTurn, onSuggestionClick }) => {
  const { data } = useListTools();
  const { setParams } = useParamsStore();

  const suggestedPromptButtons = useMemo(
    () =>
      SUGGESTED_PROMPTS.filter((prompt) =>
        prompt.params?.tools?.every((tool) => data?.find((t) => t.name === tool.name)?.is_available)
      ).map((prompt) => ({
        label: prompt.label,
        onClick: () => handleSuggestionClick(prompt.message, prompt.params),
      })),
    [data]
  );

  const handleSuggestionClick = (message: string, params: Partial<ConfigurableParams>) => {
    onSuggestionClick(message, params);
    if (params) {
      setParams(params);
    }
  };

  return (
    <Transition
      show={isFirstTurn}
      className={cn('flex overflow-x-auto py-2', { hidden: !isFirstTurn })}
      enterFrom="opacity-0"
      enterTo="opacity-100"
      enter="transition-opacity duration-300"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
      leave="transition-opacity duration-300"
      as="div"
    >
      <ButtonGroup buttons={suggestedPromptButtons} />
    </Transition>
  );
};
