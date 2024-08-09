'use client';

import { Transition } from '@headlessui/react';
import { uniqBy } from 'lodash';
import { useMemo, useState } from 'react';

import { IconButton } from '@/components/IconButton';
import { Banner, Button, Icon, Switch, Text, Tooltip } from '@/components/Shared';
import { TOOL_GOOGLE_DRIVE_ID, TOOL_READ_DOCUMENT_ID, TOOL_SEARCH_FILE_ID } from '@/constants';
import { useAgent } from '@/hooks/agents';
import { useBrandedColors } from '@/hooks/brandedColors';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useFileActions, useListFiles } from '@/hooks/files';
import { useParamsStore, useSettingsStore } from '@/stores';
import { DataSourceArtifact } from '@/types/tools';
import { pluralize } from '@/utils';

type Props = {};

const AgentRightPanel: React.FC<Props> = () => {
  const [isDeletingFile, setIsDeletingFile] = useState(false);
  const { disabledAssistantKnowledge, setUseAssistantKnowledge, setAgentsRightSidePanelOpen } =
    useSettingsStore();
  const { agentId, conversationId } = useChatRoutes();
  const { data: agent } = useAgent({ agentId });
  const { theme } = useBrandedColors(agentId);

  const {
    params: { fileIds },
    setParams,
  } = useParamsStore();

  const { data: files } = useListFiles(conversationId);
  const { deleteFile } = useFileActions();

  const agentToolMetadataArtifacts = useMemo(() => {
    if (!agent) {
      return {
        files: [],
        folders: [],
      };
    }

    const fileArtifacts = uniqBy(
      (
        agent.tools_metadata?.filter((tool_metadata) =>
          [TOOL_GOOGLE_DRIVE_ID, TOOL_READ_DOCUMENT_ID, TOOL_SEARCH_FILE_ID].includes(
            tool_metadata.tool_name
          )
        ) ?? []
      )
        .map((tool_metadata) => tool_metadata.artifacts as DataSourceArtifact[])
        .flat(),
      'id'
    );

    const files = fileArtifacts.filter((artifact) => artifact.type === 'file');
    const folders = fileArtifacts.filter((artifact) => artifact.type === 'folder');
    return {
      files,
      folders,
    };
  }, [agent]);

  const agentKnowledgeFiles = [
    ...agentToolMetadataArtifacts.files,
    ...agentToolMetadataArtifacts.folders,
  ];

  const handleDeleteFile = async (fileId: string) => {
    if (isDeletingFile || !conversationId) return;

    setIsDeletingFile(true);
    try {
      await deleteFile({ conversationId, fileId });
      setParams({ fileIds: (fileIds ?? []).filter((id) => id !== fileId) });
    } finally {
      setIsDeletingFile(false);
    }
  };

  return (
    <aside className="space-y-5 py-4">
      <header className="flex items-center gap-2">
        <IconButton
          onClick={() => setAgentsRightSidePanelOpen(false)}
          iconName="arrow-right"
          className="flex h-auto flex-shrink-0 self-center lg:hidden"
        />
        <Text styleAs="p-sm" className="font-medium uppercase">
          Knowledge
        </Text>
      </header>
      <div className="flex flex-col gap-y-10">
        {agentId && (
          <div className="flex flex-col gap-y-4">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-x-2">
                <Text styleAs="label" className="font-medium">
                  Assistant Knowledge
                </Text>
                <Tooltip
                  hover
                  size="sm"
                  placement="top-start"
                  hoverDelay={250}
                  label="Enables assistant knowledge to provide more accurate responses."
                />
              </span>
              <Switch
                theme={theme}
                checked={!disabledAssistantKnowledge.includes(agentId)}
                onChange={(checked) => setUseAssistantKnowledge(checked, agentId)}
              />
            </div>
            <Transition
              show={!disabledAssistantKnowledge.includes(agentId) ?? false}
              enter="duration-300 ease-in-out transition-all"
              enterFrom="opacity-0 scale-90"
              enterTo="opacity-100 scale-100"
              leave="duration-200 ease-in-out transition-all"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-90"
              as="div"
            >
              {agentKnowledgeFiles.length === 0 ? (
                <Banner className="flex flex-col">
                  Add a data source to expand the assistant’s knowledge.
                  <Button
                    theme={theme}
                    className="mt-4 w-full"
                    label="Add Data Source"
                    stretch
                    icon="add"
                    href={`/edit/${agentId}?datasources=1`}
                  />
                </Banner>
              ) : (
                <div className="flex flex-col gap-y-3">
                  <Text as="div" className="flex items-center gap-x-3">
                    <Icon name="folder" kind="outline" className="flex-shrink-0" />
                    {/*  This renders the number of folders and files in the agent's Google Drive.
                    For example, if the agent has 2 folders and 3 files, it will render:
                    - "2 folders and 3 files" */}
                    {agentToolMetadataArtifacts.folders.length > 0 &&
                      `${agentToolMetadataArtifacts.folders.length} ${pluralize(
                        'folder',
                        agentToolMetadataArtifacts.folders.length
                      )} ${agentToolMetadataArtifacts.files.length > 0 ? 'and ' : ''}`}
                    {agentToolMetadataArtifacts.files.length > 0 &&
                      `${agentToolMetadataArtifacts.files.length} ${pluralize(
                        'file',
                        agentToolMetadataArtifacts.files.length
                      )}`}
                  </Text>
                  <ol className="space-y-2">
                    {agentKnowledgeFiles.map((file) => (
                      <li key={file.id} className="ml-6 flex items-center gap-x-3">
                        <Icon
                          name={file.type === 'folder' ? 'folder' : 'file'}
                          kind="outline"
                          className="flex-shrink-0"
                        />
                        <Text>{file.name}</Text>
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </Transition>
          </div>
        )}
        <section className="relative flex flex-col gap-y-6">
          <div className="flex gap-x-2">
            <Text styleAs="label" className="font-medium">
              My files
            </Text>
            <Tooltip
              hover
              size="sm"
              placement="top-start"
              label="To use uploaded files, at least 1 File Upload tool must be enabled"
            />
          </div>
          {files && files.length > 0 && (
            <div className="flex flex-col gap-y-4">
              {files.map(({ file_name: name, id }) => (
                <div
                  key={id}
                  className="group flex w-full flex-col gap-y-2 rounded-lg p-2 dark:hover:bg-volcanic-200"
                >
                  <div className="group flex w-full items-center justify-between gap-x-4">
                    <div className="flex items-center gap-x-2 overflow-hidden">
                      <Icon
                        name="file"
                        kind="outline"
                        className="fill-mushroom-300 dark:fill-marble-950"
                      />
                      <Text className="truncate">{name}</Text>
                    </div>
                    <IconButton
                      onClick={() => handleDeleteFile(id)}
                      disabled={isDeletingFile}
                      iconName="close"
                      className="invisible group-hover:visible"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
          <Text styleAs="caption" className="text-mushroom-300 dark:text-marble-800">
            These files will only be accessible to you and won’t impact others.
          </Text>
        </section>
      </div>
    </aside>
  );
};

export default AgentRightPanel;
