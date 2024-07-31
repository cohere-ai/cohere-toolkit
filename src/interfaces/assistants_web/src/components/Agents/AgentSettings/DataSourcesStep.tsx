import { Dispatch, SetStateAction, useRef } from 'react';

import { IconButton } from '@/components/IconButton';
import { Button, Icon, IconName, Text } from '@/components/Shared';
import { ACCEPTED_FILE_TYPES, TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { useBatchUploadFile } from '@/hooks/files';
import { DataSourceArtifact } from '@/types/tools';

type Props = {
  googleDriveEnabled: boolean;
  googleFiles?: DataSourceArtifact[];
  defaultUploadFiles?: DataSourceArtifact[];
  openGoogleFilePicker: VoidFunction;
  setGoogleFiles: Dispatch<SetStateAction<DataSourceArtifact[]>>;
  setDefaultUploadFiles: Dispatch<SetStateAction<DataSourceArtifact[]>>;
};

export const DataSourcesStep: React.FC<Props> = ({
  googleDriveEnabled,
  googleFiles,
  defaultUploadFiles,
  openGoogleFilePicker,
  setGoogleFiles,
  setDefaultUploadFiles,
}) => {
  const { mutateAsync: batchUploadFiles } = useBatchUploadFile();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleRemoveGoogleDriveFile = (id: string) => {
    setGoogleFiles((prev) => {
      return prev?.filter((artifact) => artifact.id !== id);
    });
  };

  const handleRemoveUploadFile = (id: string) => {
    setDefaultUploadFiles((prev) => {
      return prev?.filter((artifact) => artifact.id !== id);
    });
  };

  const handleRemoveAllFiles = (dataSource: 'google-drive' | 'default-upload') => {
    if (dataSource === 'google-drive') {
      setGoogleFiles([]);
    } else {
      setDefaultUploadFiles([]);
    }
  };

  const handleOpenFileExplorer = (callback: VoidFunction) => {
    if (!fileInputRef.current) return;
    fileInputRef.current.click();
    callback();
  };

  const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFileIds = await batchUploadFiles({ files: [...(e.target.files ?? [])] });
    if (!newFileIds) return;
    setDefaultUploadFiles(
      newFileIds.map(({ id, file_name }) => ({
        id,
        name: file_name,
        type: 'file',
      }))
    );
  };

  const hasActiveDataSources =
    (googleFiles && !!googleFiles.length) || (defaultUploadFiles && !!defaultUploadFiles.length);

  return (
    <div className="flex flex-col gap-4">
      {hasActiveDataSources && <Text styleAs="label">Active Data Sources</Text>}
      {googleDriveEnabled && googleFiles && !!googleFiles.length && (
        <DataSourceFileList
          name="Google Drive"
          icon="google-drive"
          artifacts={googleFiles}
          handleRemoveTool={() => handleRemoveAllFiles('google-drive')}
          handleRemoveFile={(removedId: string) => handleRemoveGoogleDriveFile(removedId)}
        />
      )}
      {defaultUploadFiles && !!defaultUploadFiles.length && (
        <DataSourceFileList
          name="Files"
          icon="desktop"
          artifacts={defaultUploadFiles}
          handleRemoveTool={() => handleRemoveAllFiles('default-upload')}
          handleRemoveFile={(removedId: string) => handleRemoveUploadFile(removedId)}
        />
      )}
      <Text styleAs="label">Add {hasActiveDataSources ? 'More' : ''} Data Sources</Text>
      <div className="flex gap-4">
        {googleDriveEnabled && !(googleFiles && googleFiles.length) && (
          <Button
            kind="outline"
            theme="mushroom"
            icon="google-drive"
            label="Google Drive"
            onClick={openGoogleFilePicker}
          />
        )}
        {!(defaultUploadFiles && defaultUploadFiles.length) && (
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
