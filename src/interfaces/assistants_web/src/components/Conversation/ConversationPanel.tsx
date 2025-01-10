'use client';

import { Transition } from '@headlessui/react';
import { uniqBy } from 'lodash';
import { useMemo, useState } from 'react';

import { Banner, Button, Icon, IconButton, Text, Tooltip } from '@/components/UI';
import { FileViewer } from '@/components/UI/FileViewer';
import { TOOL_GOOGLE_DRIVE_ID, TOOL_READ_DOCUMENT_ID, TOOL_SEARCH_FILE_ID } from '@/constants';
import { useContextStore } from '@/context';
import {
  useAgent,
  useBrandedColors,
  useChatRoutes,
  useConversationFileActions,
  useListConversationFiles,
  useSession,
} from '@/hooks';
import { useParamsStore, useSettingsStore } from '@/stores';
import { DataSourceArtifact } from '@/types/tools';
import { pluralize } from '@/utils';

type Props = {};

export const ConversationPanel: React.FC<Props> = () => {
  const [isDeletingFile, setIsDeletingFile] = useState(false);
  const { disabledAssistantKnowledge, setRightPanelOpen } = useSettingsStore();
  const { agentId, conversationId } = useChatRoutes();
  const { data: agent } = useAgent({ agentId });
  const { theme } = useBrandedColors(agentId);
  const { open } = useContextStore();

  const {
    params: { fileIds },
    setParams,
  } = useParamsStore();
  const session = useSession();
  const { data: files } = useListConversationFiles(conversationId);
  const { deleteFile } = useConversationFileActions();

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

    const files = fileArtifacts.filter((artifact) => artifact.type !== 'folder'); // can be file, document, pdf, etc.
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

  const handleOpenFile = ({
    fileId,
    agentId,
    conversationId,
    url,
  }: {
    fileId: string;
    agentId?: string;
    conversationId?: string;
    url?: string;
  }) => {
    if (url) {
      window.open(url, '_blank');
    } else {
      open({
        content: <FileViewer fileId={fileId} agentId={agentId} conversationId={conversationId} />,
        dialogPaddingClassName: 'p-5',
      });
    }
  };

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
          onClick={() => setRightPanelOpen(false)}
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
              {/* @DEV_NOTE: This is disabled while we add the ability in BE to enable/disable assistant knowledge */}
              {/* <Switch
                theme={theme}
                checked={!disabledAssistantKnowledge.includes(agentId)}
                onChange={(checked) => setUseAssistantKnowledge(checked, agentId)}
              /> */}
            </div>
            <Transition
              show={!disabledAssistantKnowledge.includes(agentId)}
              enter="duration-300 ease-in-out transition-all"
              enterFrom="opacity-0 scale-90"
              enterTo="opacity-100 scale-100"
              leave="duration-200 ease-in-out transition-all"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-90"
              as="div"
            >
              {agentKnowledgeFiles.length === 0 && session.userId === agent?.user_id ? (
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
                      <li
                        key={file.id}
                        className="group ml-6 flex items-center justify-between gap-x-4"
                      >
                        <span className="flex items-center gap-x-2 overflow-hidden">
                          <Icon
                            name={file.type === 'folder' ? 'folder' : 'file'}
                            kind="outline"
                            className="flex-shrink-0"
                          />
                          <Text className="truncate">{file.name}</Text>
                        </span>
                        <IconButton
                          iconName={file.url ? 'arrow-up-right' : 'show'}
                          tooltip={{ label: file.url ? 'Open url' : 'Show content' }}
                          className="invisible h-auto w-auto flex-shrink-0 self-center group-hover:visible"
                          onClick={() =>
                            handleOpenFile({ fileId: file.id, agentId: agent!.id, url: file.url })
                          }
                        />
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
              {files.map(({ id, conversation_id, file_name: name }) => (
                <div key={id} className="flex w-full flex-col gap-y-2 rounded-lg">
                  <div className="group flex w-full items-center justify-between gap-x-4">
                    <div className="flex items-center gap-x-2 overflow-hidden">
                      <Icon
                        name="file"
                        kind="outline"
                        className="fill-mushroom-300 dark:fill-marble-950"
                      />
                      <Text className="truncate">{name}</Text>
                    </div>
                    <div className="invisible flex items-center gap-x-3 group-hover:visible">
                      <IconButton
                        iconName="show"
                        tooltip={{ label: 'Show content' }}
                        className="h-auto w-auto flex-shrink-0 self-center"
                        disabled={isDeletingFile}
                        onClick={() =>
                          handleOpenFile({ fileId: id, conversationId: conversation_id })
                        }
                      />
                      <IconButton
                        iconName="close"
                        tooltip={{ label: 'Delete' }}
                        className="h-auto w-auto flex-shrink-0 self-center"
                        disabled={isDeletingFile}
                        onClick={() => handleDeleteFile(id)}
                      />
                    </div>
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
