'use client';

import { Transition } from '@headlessui/react';
import React, { useMemo } from 'react';

import ButtonGroup from '@/components/ButtonGroup';
import { TOOL_CALCULATOR_ID, TOOL_PYTHON_INTERPRETER_ID, TOOL_WEB_SEARCH_ID } from '@/constants';
import { STRINGS } from '@/constants/strings';
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
    label: STRINGS.plotRealEstateData,
    params: {
      fileIds: [],
      tools: [
        { name: TOOL_PYTHON_INTERPRETER_ID },
        { name: TOOL_CALCULATOR_ID },
        { name: TOOL_WEB_SEARCH_ID },
      ],
    },
    message: STRINGS.plotRealEstateDataPrompt,
  },
  {
    label: STRINGS.cleanUpDataInPython,
    params: { fileIds: [], tools: [] },
    message: STRINGS.cleanUpDataInPythonPrompt,
  },
  {
    label: STRINGS.writeABusinessPlanInFrench,
    params: { fileIds: [], tools: [] },
    message: STRINGS.writeABusinessPlanInFrenchPrompt,
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
