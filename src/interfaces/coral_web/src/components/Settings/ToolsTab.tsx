import React, { useMemo } from 'react';

import { ManagedTool } from '@/cohere-client';
import { FilesSection } from '@/components/Settings/Files';
import { ToolsInfoBox } from '@/components/Settings/ToolsInfoBox';
import { Text } from '@/components/Shared';
import { ToggleCard } from '@/components/ToggleCard';
import { WelcomeGuideTooltip } from '@/components/WelcomeGuideTooltip';
import { TOOL_FALLBACK_ICON, TOOL_ID_TO_DISPLAY_INFO } from '@/constants';
import { useDefaultFileLoaderTool, useFilesInConversation } from '@/hooks/files';
import { useListTools } from '@/hooks/tools';
import { useConversationStore, useFilesStore, useParamsStore } from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';
import { cn } from '@/utils';

/**
 * @description Tools tab content that shows a list of available tools and files
 */
export const ToolsTab: React.FC<{ className?: string }> = ({ className = '' }) => {
  const {
    conversation: { id: conversationId },
  } = useConversationStore();
  const { files } = useFilesInConversation();
  return (
    <article className={cn('flex flex-col pb-10', className)}>
      <ToolSection />

      {/* File upload is not supported for conversarions without an id */}
      {conversationId && files.length > 0 && (
        <>
          <hr className="my-6 border-t border-marble-400" />
          <FilesSection />
        </>
      )}
    </article>
  );
};

/**
 * @description List of available tools.
 */
const ToolSection = () => {
  const { params, setParams } = useParamsStore();
  const { data } = useListTools();
  const { tools: paramTools } = params;
  const enabledTools = paramTools ?? [];
  const { defaultFileLoaderTool } = useDefaultFileLoaderTool();
  const { clearComposerFiles } = useFilesStore();

  const { availableTools, unavailableTools } = useMemo(() => {
    return (data ?? [])
      .filter((t) => t.is_visible)
      .reduce<{ availableTools: ManagedTool[]; unavailableTools: ManagedTool[] }>(
        (acc, tool) => {
          if (tool.is_available) {
            acc.availableTools.push(tool);
          } else {
            acc.unavailableTools.push(tool);
          }
          return acc;
        },
        { availableTools: [], unavailableTools: [] }
      );
  }, [data]);

  const handleToggle = (name: string, checked: boolean) => {
    const newParams: Partial<ConfigurableParams> = {
      tools: checked
        ? [...enabledTools, { name }]
        : enabledTools.filter((enabledTool) => enabledTool.name !== name),
    };

    if (name === defaultFileLoaderTool?.name) {
      newParams.fileIds = [];
      clearComposerFiles();
    }

    setParams(newParams);
  };

  return (
    <section className="relative flex flex-col gap-y-5 px-5">
      <ToolsInfoBox />
      <article className={cn('flex flex-col gap-y-5 pb-10')}>
        <Text styleAs="p-sm" className="text-secondary-800">
          Tools are data sources the assistant can search such as databases or the internet.
        </Text>

        {unavailableTools.length > 0 && (
          <>
            <Text as="span" styleAs="label" className="font-medium">
              Action Required
            </Text>

            <div className="flex flex-col gap-y-5">
              {unavailableTools.map(({ name, display_name, description, error_message }) => {
                return (
                  <ToggleCard
                    key={name}
                    disabled
                    errorMessage={error_message}
                    checked={false}
                    label={display_name ?? name}
                    icon={TOOL_ID_TO_DISPLAY_INFO[name]?.icon ?? TOOL_FALLBACK_ICON}
                    description={description ?? ''}
                    onToggle={(checked) => handleToggle(name, checked)}
                  />
                );
              })}
            </div>
          </>
        )}

        {unavailableTools.length > 0 && availableTools.length > 0 && (
          <hr className="border-t border-marble-400" />
        )}

        {availableTools.length > 0 && (
          <>
            <Text as="span" styleAs="label" className="font-medium">
              Ready to Use
            </Text>

            <div className="flex flex-col gap-y-5">
              {availableTools.map(
                ({ name, display_name, is_available, description, error_message }) => {
                  const enabledTool = enabledTools.find(
                    (enabledTool) =>
                      enabledTool.name.toLocaleLowerCase() === name.toLocaleLowerCase()
                  );
                  const checked = !!enabledTool;
                  const disabled = !is_available;

                  return (
                    <ToggleCard
                      key={name}
                      disabled={disabled}
                      errorMessage={error_message}
                      checked={checked}
                      label={display_name ?? name}
                      icon={TOOL_ID_TO_DISPLAY_INFO[name]?.icon ?? TOOL_FALLBACK_ICON}
                      description={description ?? ''}
                      onToggle={(checked) => handleToggle(name, checked)}
                    />
                  );
                }
              )}
            </div>
          </>
        )}
      </article>
      <WelcomeGuideTooltip step={2} className="fixed right-0 mr-3 mt-12 md:right-full md:mt-0" />
    </section>
  );
};
