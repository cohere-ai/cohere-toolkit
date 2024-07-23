'use client';

import React from 'react';

import { Icon, IconName, Text } from '@/components/Shared';
import { TOOL_FALLBACK_ICON, TOOL_ID_TO_DISPLAY_INFO } from '@/constants';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { useDefaultFileLoaderTool, useListFiles } from '@/hooks/files';
import { useConversationStore, useFilesStore, useParamsStore } from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';

type Props = {
  isStreaming: boolean;
};

/**
 * @description Renders the enabled data sources in the composer toolbar.
 */
export const EnabledDataSources: React.FC<Props> = ({ isStreaming }) => {
  const { agentId } = useChatRoutes();
  const {
    conversation: { id },
  } = useConversationStore();
  const {
    params: { fileIds, tools: enabledTools },
    setParams,
  } = useParamsStore();
  const {
    files: { composerFiles },
    deleteComposerFile,
    clearComposerFiles,
  } = useFilesStore();
  const { defaultFileLoaderTool } = useDefaultFileLoaderTool();

  const { data: listFiles } = useListFiles(id);
  const enabledDocuments = fileIds?.map(
    (id) => listFiles?.find((doc) => doc.id === id) ?? composerFiles.find((file) => file.id === id)
  );

  const handleDeleteFile = (fileId: string) => () => {
    setParams({ fileIds: fileIds?.filter((id) => id !== fileId) });

    if (composerFiles.some((file) => file.id === fileId)) {
      deleteComposerFile(fileId);
    }
  };

  const handleDeleteTool = (toolName: string) => () => {
    const newParams: Partial<ConfigurableParams> = {
      tools: enabledTools?.filter((et) => et.name !== toolName),
    };
    if (toolName === defaultFileLoaderTool?.name) {
      newParams.fileIds = [];
      clearComposerFiles();
    }
    setParams(newParams);
  };

  return (
    <div className="flex gap-2 overflow-scroll">
      {enabledDocuments?.map((d, i) => (
        <DataSourceChip
          key={`doc-${i}`}
          iconName="clip"
          label={d?.file_name ?? ''}
          onDelete={handleDeleteFile(d?.id ?? '')}
          disabled={isStreaming}
        />
      ))}
      {enabledTools?.map((t, i) => (
        <DataSourceChip
          key={`tool-${i}`}
          iconName={TOOL_ID_TO_DISPLAY_INFO[t.name ?? '']?.icon ?? TOOL_FALLBACK_ICON}
          label={t.display_name ?? t.name ?? ''}
          onDelete={agentId ? undefined : handleDeleteTool(t.name ?? '')} // Disable removing tools for assistants
        />
      ))}
    </div>
  );
};

const DataSourceChip: React.FC<{
  iconName: IconName;
  label: string;
  onDelete?: React.MouseEventHandler;
  disabled?: boolean;
  hasEditableConfiguration?: boolean;
  onEditConfiguration?: VoidFunction;
}> = ({ iconName, label, onDelete, disabled, hasEditableConfiguration, onEditConfiguration }) => {
  return (
    <div className="flex items-center justify-between gap-x-2 rounded border border-dashed border-mushroom-800 bg-mushroom-950 px-2 py-0.5">
      <div className="flex items-center gap-x-1">
        <Icon name={iconName} kind="outline" />
        <Text className="max-w-[100px] truncate md:max-w-[200px]">{label}</Text>
      </div>
      {hasEditableConfiguration && (
        <button className="flex" onClick={onEditConfiguration} disabled={disabled}>
          <Icon name="kebab" size="sm" />
        </button>
      )}
      {onDelete && (
        <button className="flex" onClick={onDelete} disabled={disabled}>
          <Icon name="close" size="sm" />
        </button>
      )}
    </div>
  );
};
