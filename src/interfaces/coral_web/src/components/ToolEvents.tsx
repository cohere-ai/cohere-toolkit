import { Transition } from '@headlessui/react';
import { Fragment, PropsWithChildren } from 'react';

import { StreamToolInput, ToolInputType } from '@/cohere-client';
import { Icon, IconName, Markdown, Text } from '@/components/Shared';
import {
  TOOL_FALLBACK_ICON,
  TOOL_ID_TO_DISPLAY_INFO,
  TOOL_INTERNET_SEARCH_ID,
  TOOL_PYTHON_INTERPRETER_ID,
} from '@/constants';
import { cn } from '@/utils';

type Props = {
  show: boolean;
  events: StreamToolInput[] | undefined;
};

/**
 * @description Renders a list of events depending on the model's plan and tool inputs.
 */
export const ToolEvents: React.FC<Props> = ({ show, events }) => {
  return (
    <Transition
      show={show}
      enterFrom="opacity-0"
      enterTo="opacity-100"
      enter="duration-500"
      leaveFrom="opacity-100"
      leaveTo="opacity-0"
      as="div"
      className={cn('flex w-full flex-col gap-y-2 pb-2', 'transition-opacity ease-in-out')}
    >
      {events?.map((toolEvent, i) => (
        <Fragment key={i}>
          {toolEvent.text && <ToolEvent plan={toolEvent.text} />}
          <ToolEvent event={toolEvent} />
        </Fragment>
      ))}
    </Transition>
  );
};

type ToolEventProps = {
  plan?: string;
  event?: StreamToolInput;
};

/**
 * @description Renders a step event depending on the tool's input or output.
 */
const ToolEvent: React.FC<ToolEventProps> = ({ plan, event }) => {
  if (!event) {
    return <ToolEventWrapper>{plan}</ToolEventWrapper>;
  }

  const toolName = event.tool_name;
  const input = event.input;
  const icon = toolName ? TOOL_ID_TO_DISPLAY_INFO[toolName]?.icon : TOOL_FALLBACK_ICON;

  switch (toolName) {
    case TOOL_PYTHON_INTERPRETER_ID: {
      if (event.input_type === ToolInputType.CODE) {
        let codeString = '```python\n';
        codeString += input;
        codeString += '\n```';

        return (
          <>
            <ToolEventWrapper icon={icon}>
              Using <b className="font-medium">{toolName}</b>
            </ToolEventWrapper>
            <Markdown text={codeString} className="w-full" />
          </>
        );
      } else {
        return (
          <ToolEventWrapper icon={icon}>
            Using <b className="font-medium">{toolName}</b>
          </ToolEventWrapper>
        );
      }
    }

    case TOOL_INTERNET_SEARCH_ID: {
      return (
        <ToolEventWrapper icon={icon}>
          Searching <b className="font-medium">{input}</b>
        </ToolEventWrapper>
      );
    }

    default: {
      return (
        <ToolEventWrapper icon={icon}>
          Using <b className="font-medium">{toolName}</b>
        </ToolEventWrapper>
      );
    }
  }
};

/**
 * @description Renders the wrapper for the tool event.
 */
const ToolEventWrapper: React.FC<PropsWithChildren<{ icon?: IconName }>> = ({
  icon = 'list',
  children,
}) => {
  return (
    <div className="flex w-full gap-x-2 rounded bg-secondary-50 px-3 py-2 transition-colors ease-in-out group-hover:bg-secondary-100">
      <Icon name={icon} kind="outline" className="flex h-[21px] items-center text-secondary-600" />
      <Text className="text-secondary-800">{children}</Text>
    </div>
  );
};
