'use client';

import { Transition } from '@headlessui/react';
import { Fragment, PropsWithChildren } from 'react';

import { StreamSearchResults, StreamToolCallsGeneration, ToolCall } from '@/cohere-client';
import { Markdown } from '@/components/Markdown';
import { Icon, IconButton, IconName, Text, Tooltip } from '@/components/UI';
import {
  TOOL_CALCULATOR_ID,
  TOOL_GOOGLE_DRIVE_ID,
  TOOL_PYTHON_INTERPRETER_ID,
  TOOL_WEB_SEARCH_ID,
} from '@/constants';
import { cn, getToolIcon, getValidURL } from '@/utils';

type Props = {
  show: boolean;
  isStreaming: boolean;
  isLast: boolean;
  events: StreamToolCallsGeneration[] | undefined;
};

const hasToolErrorsDocuments = (search_results: StreamSearchResults | null) => {
  return search_results?.documents?.some((document) => document.fields?.success === 'false');
};

const getErrorDocumentsFromEvent = (search_results: StreamSearchResults | null) =>
  search_results?.documents?.filter((document) => document.fields?.success === 'false') || [];

/**
 * @description Renders a list of events depending on the model's plan and tool inputs.
 */
export const ToolEvents: React.FC<Props> = ({ show, isStreaming, isLast, events }) => {
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
          {toolEvent.stream_search_results && toolEvent.stream_search_results.search_results && (
            <ToolEvent stream_search_results={toolEvent.stream_search_results} />
          )}
          {toolEvent.text && <ToolEvent plan={toolEvent.text} />}
          {toolEvent.tool_calls?.map((toolCall, j) => (
            <ToolEvent key={`event-${j}`} event={toolCall} />
          ))}
        </Fragment>
      ))}
      {isStreaming && isLast && (
        <Text className={cn('flex min-w-0 text-volcanic-400')} as="span">
          Working on it
          <span className="w-max">
            <div className="animate-typing-ellipsis overflow-hidden whitespace-nowrap pr-1">
              ...
            </div>
          </span>
        </Text>
      )}
    </Transition>
  );
};

type ToolEventProps = {
  plan?: string;
  event?: ToolCall;
  stream_search_results?: StreamSearchResults | null;
};

/**
 * @description Renders a step event depending on the tool's input or output.
 */
const ToolEvent: React.FC<ToolEventProps> = ({ plan, event, stream_search_results }) => {
  if (plan) {
    return <ToolEventWrapper>{plan}</ToolEventWrapper>;
  }
  const toolName = event?.name || '';

  if (stream_search_results) {
    const artifacts =
      stream_search_results.documents
        ?.map((doc) => {
          return { title: truncateString(doc.title || doc.url || ''), url: getValidURL(doc.url) };
        })
        .filter((entry) => !!entry.title)
        .filter((value, index, self) => index === self.findIndex((t) => t.title === value.title)) ||
      [];

    const hasErrorsDocuments = hasToolErrorsDocuments(stream_search_results);
    const errorDocuments = getErrorDocumentsFromEvent(stream_search_results);

    return hasErrorsDocuments ? (
      <ToolErrorWrapper
        tooltip={errorDocuments[errorDocuments.length - 1].fields?.details as string}
      >
        {errorDocuments[errorDocuments.length - 1].text}
      </ToolErrorWrapper>
    ) : toolName && toolName != TOOL_PYTHON_INTERPRETER_ID ? (
      <ToolEventWrapper icon="book-open-text">
        {artifacts.length > 0 ? (
          <>
            Referenced the following resources:
            <article className="grid grid-cols-2 gap-x-2">
              {artifacts.map((artifact) => (
                <b key={artifact.title} className="truncate font-medium">
                  {artifact.url ? (
                    <a href={artifact.url} target="_blank" className="underline">
                      {artifact.title}
                    </a>
                  ) : (
                    <p>{artifact.title}</p>
                  )}
                </b>
              ))}
            </article>
          </>
        ) : (
          <>No resources found.</>
        )}
      </ToolEventWrapper>
    ) : null;
  }

  const icon = getToolIcon(toolName);

  switch (toolName) {
    case TOOL_PYTHON_INTERPRETER_ID: {
      if (event?.parameters?.code) {
        let codeString = '```python\n';
        codeString += event?.parameters?.code;
        codeString += '\n```';

        return (
          <>
            <ToolEventWrapper icon={icon}>
              Using <b className="font-medium">{toolName}.</b>
            </ToolEventWrapper>
            <Markdown text={codeString} className="w-full" />
          </>
        );
      } else {
        return (
          <ToolEventWrapper icon={icon}>
            Using <b className="font-medium">{toolName}.</b>
          </ToolEventWrapper>
        );
      }
    }

    case TOOL_CALCULATOR_ID: {
      return (
        <ToolEventWrapper icon={icon}>
          Calculating <b className="font-medium">{event?.parameters?.code as any}.</b>
        </ToolEventWrapper>
      );
    }

    case TOOL_WEB_SEARCH_ID: {
      return (
        <ToolEventWrapper icon={icon}>
          Searching <b className="font-medium">{event?.parameters?.query as any}.</b>
        </ToolEventWrapper>
      );
    }

    case TOOL_GOOGLE_DRIVE_ID: {
      return (
        <ToolEventWrapper icon={icon}>
          Searching <b className="font-medium">{event?.parameters?.query as any}</b> in {toolName}.
        </ToolEventWrapper>
      );
    }

    default: {
      return (
        <ToolEventWrapper icon={icon}>
          Using <b className="font-medium">{toolName}.</b>
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
    <div className="flex w-full items-start gap-x-2 overflow-hidden rounded bg-mushroom-950 px-3 py-2 transition-colors ease-in-out group-hover:bg-mushroom-900 dark:bg-volcanic-200 dark:group-hover:bg-volcanic-200">
      <Icon
        name={icon}
        kind="outline"
        className="mt-0.5 flex h-[21px] flex-shrink-0 items-center fill-mushroom-500 dark:fill-marble-950"
      />
      <Text className="pt-px text-mushroom-300 dark:text-marble-850" styleAs="p-sm" as="span">
        {children}
      </Text>
    </div>
  );
};

const ToolErrorWrapper: React.FC<PropsWithChildren<{ tooltip: string }>> = ({
  tooltip = 'Some error occurred',
  children,
}) => {
  return (
    <div className="flex w-full items-start gap-x-2 overflow-hidden rounded bg-mushroom-950 px-3 py-2 transition-colors ease-in-out group-hover:bg-mushroom-900 dark:bg-volcanic-200 dark:group-hover:bg-volcanic-200">
      <Tooltip
        label={tooltip}
        size={'sm'}
        hover
        iconClassName="mt-0.5 flex h-[21px] flex-shrink-0 items-center fill-danger-350 dark:fill-danger-500"
      />
      <Text className="pt-px text-danger-350 dark:text-danger-500" styleAs="p-sm" as="span">
        {children}
      </Text>
    </div>
  );
};

const truncateString = (str: string, max_length: number = 50) => {
  return str.length < max_length ? str : str.substring(0, max_length) + '...';
};
