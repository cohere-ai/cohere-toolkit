import { useRef } from 'react';

import { ManagedTool } from '@/cohere-client';
import { AgentDataSources } from '@/components/Agents/AgentSettings/AgentSettingsForm';
import { IconButton } from '@/components/IconButton';
import { Button, Icon, IconName, Text } from '@/components/Shared';
import { ACCEPTED_FILE_TYPES, TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { useBatchUploadFile } from '@/hooks/files';
import { useOpenGoogleDrivePicker } from '@/hooks/tools';
import { DataSourceArtifact } from '@/types/tools';

type Props = {
  dataSources: AgentDataSources;
  googleDriveEnabled: boolean;
  setDataSources: (sources: AgentDataSources) => void;
};

const isToolAvailable = (name: string | string[], tools?: ManagedTool[]) => {
  if (!tools) return false;
  const checkedTools = Array.isArray(name)
    ? tools.filter((t) => t.name && name.includes(t.name))
    : [tools.find((t) => t.name === name)];
  return checkedTools.every((t) => !!t?.is_available);
};

export const DataSourcesStep: React.FC<Props> = ({
  dataSources,
  googleDriveEnabled,
  setDataSources,
}) => {
  const { mutateAsync: batchUploadFiles } = useBatchUploadFile();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpdateDataSources = ({
    source,
    artifacts,
    removedId,
  }: {
    source: 'googleDrive' | 'defaultUpload';
    artifacts?: DataSourceArtifact[];
    removedId?: string;
  }) => {
    const updatedGoogleDrive =
      source === 'googleDrive'
        ? artifacts
        : removedId
        ? dataSources.googleDrive?.filter((f) => f.id !== removedId)
        : dataSources.googleDrive;
    const updatedDefaultUpload =
      source === 'defaultUpload'
        ? artifacts
        : removedId
        ? dataSources.defaultUpload?.filter((f) => f.id !== removedId)
        : dataSources.defaultUpload;

    setDataSources({
      ...(updatedGoogleDrive && !!updatedGoogleDrive.length
        ? { googleDrive: updatedGoogleDrive }
        : {}),
      ...(updatedDefaultUpload && !!updatedDefaultUpload.length
        ? { defaultUpload: updatedDefaultUpload }
        : {}),
    });
  };

  const handleGoogleDriveFilePicker = useOpenGoogleDrivePicker((data) => {
    if (data.docs) {
      handleUpdateDataSources({
        source: 'googleDrive',
        artifacts: data.docs.map(
          (doc) =>
            ({
              id: doc.id,
              name: doc.name,
              type: doc.type,
              url: doc.url,
            } as DataSourceArtifact)
        ),
      });
    }
  });

  const handleOpenFileExplorer = (callback: VoidFunction) => {
    if (!fileInputRef.current) return;
    fileInputRef.current.click();
    callback();
  };

  const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFileIds = await batchUploadFiles({ files: [...(e.target.files ?? [])] });
    if (!newFileIds) return;
    handleUpdateDataSources({
      source: 'defaultUpload',
      artifacts: newFileIds.map(({ id, file_name }) => ({
        id,
        name: file_name,
        type: 'file',
      })),
    });
  };

  const hasActiveDataSources = dataSources.googleDrive?.length || dataSources.defaultUpload?.length;
  return (
    <div className="flex flex-col space-y-3">
      {hasActiveDataSources && <Text styleAs="label">Active Data Sources</Text>}
      {googleDriveEnabled && dataSources.googleDrive?.length && (
        <DataSourceFileList
          name="Google Drive"
          icon="google-drive"
          artifacts={dataSources.googleDrive}
          handleRemoveTool={() => handleUpdateDataSources({ source: 'googleDrive', artifacts: [] })}
          handleRemoveFile={(removedId: string) =>
            handleUpdateDataSources({ source: 'googleDrive', removedId })
          }
        />
      )}
      {dataSources.defaultUpload?.length && (
        <DataSourceFileList
          name="Files"
          icon="desktop"
          artifacts={dataSources.defaultUpload}
          handleRemoveTool={() =>
            handleUpdateDataSources({ source: 'defaultUpload', artifacts: [] })
          }
          handleRemoveFile={(removedId: string) =>
            handleUpdateDataSources({ source: 'defaultUpload', removedId })
          }
        />
      )}
      <Text styleAs="label">Add {hasActiveDataSources ? 'More' : ''} Data Sources</Text>
      <div className="flex space-x-4">
        {googleDriveEnabled && !dataSources.googleDrive?.length && (
          <Button
            kind="outline"
            theme="mushroom"
            icon="google-drive"
            label="Google Drive"
            onClick={handleGoogleDriveFilePicker}
          />
        )}
        {!dataSources.defaultUpload?.length && (
          <>
            <input
              type="file"
              accept={ACCEPTED_FILE_TYPES.join(',')}
              className="hidden"
              multiple
              ref={fileInputRef}
              onChange={handleFileInputChange}
            />
            <Button
              kind="outline"
              theme="mushroom"
              icon="desktop"
              label="Upload Files"
              onClick={() => handleOpenFileExplorer(close)}
            />
          </>
        )}
      </div>
    </div>
  );
};

const DataSourceFileList: React.FC<{
  name: string;
  icon: IconName;
  artifacts?: DataSourceArtifact[];
  handleRemoveFile: (id: string) => void;
  handleRemoveTool: VoidFunction;
}> = ({ name, icon, artifacts = [], handleRemoveFile, handleRemoveTool }) => {
  return (
    <div className="flex flex-col space-y-6 rounded-md border border-volcanic-500 p-4">
      <div className="flex flex-col space-y-2">
        <div className="flex justify-between">
          <div className="flex space-x-2">
            <Icon name={icon} />
            <Text>{name}</Text>
          </div>
          <Button icon="trash" kind="secondary" theme="danger" onClick={handleRemoveTool} />
        </div>
        <Text className="text-marble-800">
          {name === TOOL_GOOGLE_DRIVE_ID ? 'Connect to Google Drive and add ' : 'Add '} files to the
          assistant.
        </Text>
      </div>
      <div className="flex flex-col">
        {artifacts.map(({ id, type, name }) => (
          <div
            key={id}
            className="flex w-full items-center gap-x-2 border-b border-mushroom-500 py-2 dark:border-volcanic-300"
          >
            <Icon
              kind="outline"
              name={type === 'folder' ? 'folder' : 'file'}
              className="text-mushroom-500 dark:text-marble-950"
              size="sm"
            />
            <Text styleAs="overline" className="dark:test-marble-950 mr-auto truncate">
              {name}
            </Text>
            <Button icon="close" />
            <IconButton
              size="sm"
              iconName="close"
              className="text-mushroom-500 dark:text-marble-950"
              onClick={() => handleRemoveFile(id)}
            />
          </div>
        ))}
      </div>
    </div>
  );
};
