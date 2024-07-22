'use client';

import React, { useMemo } from 'react';

import { ManagedTool } from '@/cohere-client';
import { ToolsInfoBox } from '@/components/Settings/ToolsInfoBox';
import { Button, Icon, Text } from '@/components/Shared';
import { ToggleCard } from '@/components/ToggleCard';
import { WelcomeGuideTooltip } from '@/components/WelcomeGuideTooltip';
import { TOOL_FALLBACK_ICON, TOOL_ID_TO_DISPLAY_INFO } from '@/constants';
import { useAgent } from '@/hooks/agents';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useDefaultFileLoaderTool } from '@/hooks/files';
import { useListTools, useUnauthedTools } from '@/hooks/tools';
import { useFilesStore, useParamsStore } from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';
import { cn } from '@/utils';

/**
 * @description Tools tab content that shows a list of available tools and files
 */
export const AgentsToolsTab: React.FC<{
  requiredTools: string[] | undefined;
  className?: string;
}> = ({ requiredTools, className = '' }) => {
  const { agentId } = useChatRoutes();
  const { data: agent } = useAgent({ agentId });
  const { params, setParams } = useParamsStore();
  const { data } = useListTools();
  const { tools: paramTools } = params;
  const enabledTools = paramTools ?? [];
  const { defaultFileLoaderTool } = useDefaultFileLoaderTool();
  const { clearComposerFiles } = useFilesStore();

  const { unauthedTools } = useUnauthedTools();
  const availableTools = useMemo(() => {
    return (data ?? []).filter(
      (t) =>
        t.is_visible &&
        t.is_available &&
        (!requiredTools || requiredTools.some((rt) => rt === t.name))
    );
  }, [data, requiredTools]);

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
    <section className={cn('relative flex flex-col gap-y-5 px-5 pb-10', className)}>
      <ToolsInfoBox />
      <article className={cn('flex flex-col gap-y-5 pb-10')}>
        <Text styleAs="p-sm" className="text-mushroom-300">
          {availableTools.length === 0
            ? `${agent?.name} does not use any tools.`
            : 'Tools are data sources the assistant can search such as databases or the internet.'}
        </Text>

        {unauthedTools.length > 0 && (
          <>
            <div className="flex items-center justify-between">
              <Text as="span" styleAs="label" className="font-medium">
                Action Required
              </Text>
              <Icon name="warning" kind="outline" />
            </div>
            <ConnectDataBox tools={unauthedTools} />
          </>
        )}

        {unauthedTools.length > 0 && availableTools.length > 0 && (
          <hr className="border-t border-marble-950" />
        )}

        {availableTools.length > 0 && (
          <>
            <Text as="span" styleAs="label" className="font-medium">
              Ready to Use
            </Text>

            <div className="flex flex-col gap-y-5">
              {availableTools.map(({ name, display_name, description, error_message }) => {
                const enabledTool = enabledTools.find((enabledTool) => enabledTool.name === name);
                const checked = !!enabledTool;
                const disabled = !!requiredTools;

                return (
                  <ToggleCard
                    key={name}
                    disabled={disabled}
                    errorMessage={error_message}
                    checked={checked}
                    label={display_name ?? name ?? ''}
                    icon={TOOL_ID_TO_DISPLAY_INFO[name ?? '']?.icon ?? TOOL_FALLBACK_ICON}
                    description={description ?? ''}
                    onToggle={(checked) => handleToggle(name ?? '', checked)}
                  />
                );
              })}
            </div>
          </>
        )}
      </article>
      <WelcomeGuideTooltip step={2} className="fixed right-0 mr-3 mt-12 md:right-full md:mt-0" />
    </section>
  );
};

/**
 * @description Info box that prompts the user to connect their data to enable tools
 */
const ConnectDataBox: React.FC<{
  tools: ManagedTool[];
}> = ({ tools }) => {
  return (
    <div className="flex flex-col gap-y-4 rounded border border-dashed border-coral-800 bg-coral-800 p-4">
      <div className="flex flex-col gap-y-3">
        <Text styleAs="h5">Connect your data</Text>
        <Text>
          In order to get the most accurate answers grounded on your data, connect the following:
        </Text>
      </div>
      <div className="flex flex-col gap-y-1">
        {tools.map((tool) => (
          <Button
            key={tool.name}
            kind="secondary"
            href={tool.auth_url ?? ''}
            endIcon={<Icon name="arrow-up-right" className="ml-1" />}
          >
            {tool.display_name}
          </Button>
        ))}
      </div>
    </div>
  );
};
