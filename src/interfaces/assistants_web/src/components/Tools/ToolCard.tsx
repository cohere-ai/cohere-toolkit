import { uniqBy } from 'lodash';
import { useMemo } from 'react';

import { AgentPublic, ManagedTool } from '@/cohere-client';
import { Button, Icon, Text } from '@/components/UI';
import { TOOL_FALLBACK_ICON, TOOL_ID_TO_DISPLAY_INFO } from '@/constants';
import { DataSourceArtifact } from '@/types/tools';
import { cn, getToolAuthUrl } from '@/utils';

type Props = {
  tool: ManagedTool;
  agent?: AgentPublic;
};

const ToolCard: React.FC<Props> = ({ tool, agent }) => {
  const isToolConnected = !tool.is_auth_required ?? false;
  const authUrl = getToolAuthUrl(tool.auth_url);

  const agentToolMetadataArtifacts = useMemo(() => {
    if (!agent) {
      return {
        files: [],
        folders: [],
      };
    }

    const fileArtifacts = uniqBy(
      (agent.tools_metadata?.filter((tool_metadata) => tool.name === tool_metadata.tool_name) ?? [])
        .map((tool_metadata) => tool_metadata.artifacts as DataSourceArtifact[])
        .flat(),
      'id'
    );

    const files = fileArtifacts.filter((artifact) => artifact.type !== 'folder'); // can be file, document, pdf, etc.
    const folders = fileArtifacts.filter((artifact) => artifact.type === 'folder');
    return {
      files,
      folders,
    };
  }, [agent, tool]);

  return (
    <article className="flex w-full flex-col gap-y-2 rounded-md border border-marble-800 p-4 dark:border-volcanic-500">
      <header className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon
            name={TOOL_ID_TO_DISPLAY_INFO[tool.name ?? ''].icon ?? TOOL_FALLBACK_ICON}
            size="lg"
          />
          <Text className="text-volcanic-400 dark:text-mushroom-950">{tool.display_name}</Text>
        </div>
        {isToolConnected ? (
          <Text styleAs="p-sm" className="flex items-center gap-2 uppercase dark:text-mushroom-950">
            <span
              className={cn('size-[10px] rounded-full', {
                'bg-success-300': isToolConnected,
                'bg-danger-500': !isToolConnected,
              })}
            />
            Connected
          </Text>
        ) : (
          <Button
            href={authUrl}
            kind="secondary"
            theme="coral"
            label={<Text className="!text-coral-600 dark:!text-coral-600">Connect</Text>}
            icon="arrow-up-right"
            iconOptions={{
              className: '!fill-coral-600',
            }}
            iconPosition="end"
          />
        )}
      </header>
      {isToolConnected && (
        <div className="flex flex-col gap-y-1">
          <div className="flex items-center justify-between gap-x-3">
            <Text styleAs="label">Last sync:</Text>
            <Text className="text-marble-850">Aug 16, 2024 11:20AM</Text>
          </div>
          {agentToolMetadataArtifacts.folders.length > 0 && (
            <div className="flex items-center justify-between gap-x-3">
              <Text styleAs="label">Shared folders:</Text>
              <Text className="text-marble-850">{agentToolMetadataArtifacts.folders.length}</Text>
            </div>
          )}
          {agentToolMetadataArtifacts.files.length > 0 && (
            <div className="flex items-center justify-between gap-x-3">
              <Text styleAs="label">Shared files:</Text>
              <Text className="text-marble-850">{agentToolMetadataArtifacts.files.length}</Text>
            </div>
          )}
        </div>
      )}
    </article>
  );
};

export default ToolCard;
