'use client';

import { Transition } from '@headlessui/react';
import { useMemo, useState } from 'react';

import { IconButton } from '@/components/IconButton';
import { Banner, Button, Icon, Switch, Tabs, Text, Tooltip } from '@/components/Shared';
import { TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { useAgent } from '@/hooks/agents';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useFileActions, useListFiles } from '@/hooks/files';
import { useParamsStore } from '@/stores';
import { GoogleDriveToolArtifact } from '@/types/tools';
import { pluralize } from '@/utils';

type Props = {};

const AgentRightPanel: React.FC<Props> = () => {
  const [isDeletingFile, setIsDeletingFile] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  // TODO: (khalil) configure this to use Google drive files
  const [useAssistantKnowledge, setUseAssistantKnowledge] = useState(true);
  const { agentId, conversationId } = useChatRoutes();
  const { data: agent, isLoading: isAgentLoading } = useAgent({ agentId });

  const {
    params: { fileIds },
    setParams,
  } = useParamsStore();

  const { data: files, isLoading: isFilesLoading } = useListFiles(conversationId);
  const { deleteFile } = useFileActions();

  const agentGoogleDriveArtifcats = useMemo(() => {
    if (!agent)
      return {
        files: [],
        folders: [],
      };

    const artifacts =
      (agent.tools_metadata?.find(
        (tool_metadata) => tool_metadata.tool_name === TOOL_GOOGLE_DRIVE_ID
      )?.artifacts as GoogleDriveToolArtifact[]) ?? [];

    const files = artifacts.filter((artifact) => artifact.type === 'file');
    const folders = artifacts.filter((artifact) => artifact.type === 'folder');
    return {
      files,
      folders,
    };
  }, [agent]);

  const agentKnowledgeFiles = [
    ...agentGoogleDriveArtifcats.files,
    ...agentGoogleDriveArtifcats.folders,
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
    <Tabs
      selectedIndex={selectedIndex}
      onChange={setSelectedIndex}
      isLoading={isAgentLoading || isFilesLoading}
      tabs={[
        <span className="flex items-center gap-x-2" key="knowledge">
          <Icon name="folder" kind="outline" />
          Knowledge
        </span>,
        <span className="flex items-center gap-x-2" key="citations">
          <Icon name="link" kind="outline" />
          Citations
        </span>,
      ]}
      tabGroupClassName="h-full"
      kind="blue"
    >
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
                theme="blue"
                checked={useAssistantKnowledge}
                onChange={setUseAssistantKnowledge}
              />
            </div>
            <Transition
              show={useAssistantKnowledge}
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
                  <Button theme="blue" className="mt-4" label="Add Data Source" icon="add" />
                </Banner>
              ) : (
                <div className="flex flex-col gap-y-3">
                  <Text as="div" className="flex items-center gap-x-3">
                    <Icon name="folder" kind="outline" />
                    {/*  This renders the number of folders and files in the agent's Google Drive.
                    For example, if the agent has 2 folders and 3 files, it will render:
                    - "2 folders and 3 files" */}
                    {agentGoogleDriveArtifcats.folders.length > 0 &&
                      `${agentGoogleDriveArtifcats.folders.length} ${pluralize(
                        'folder',
                        agentGoogleDriveArtifcats.folders.length
                      )} ${agentGoogleDriveArtifcats.files.length > 0 ? 'and' : ''}`}
                    {agentGoogleDriveArtifcats.files.length > 0 &&
                      `${agentGoogleDriveArtifcats.files.length} ${pluralize(
                        'file',
                        agentGoogleDriveArtifcats.files.length
                      )}`}
                  </Text>
                  {agentKnowledgeFiles.map((file) => (
                    <Text as="div" key={file.id} className="ml-6 flex items-center gap-x-3">
                      <Icon name={file.type === 'folder' ? 'folder' : 'file'} kind="outline" />
                      {file.name}
                    </Text>
                  ))}
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
                      className="hidden group-hover:flex"
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
      <div>Citations</div>
    </Tabs>
  );
};

export default AgentRightPanel;
