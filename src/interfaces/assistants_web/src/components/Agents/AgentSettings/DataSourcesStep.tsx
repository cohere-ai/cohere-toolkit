import { uniqBy } from 'lodash';
import Link from 'next/link';
import { Dispatch, ReactNode, RefObject, SetStateAction, useRef } from 'react';

import { Button, Icon, IconName, Spinner, Text } from '@/components/Shared';
import { ACCEPTED_FILE_TYPES, TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { useBatchUploadFile } from '@/hooks/files';
import { DataSourceArtifact } from '@/types/tools';
import { pluralize } from '@/utils';

type Props = {
  googleDriveEnabled: boolean;
  googleFiles: DataSourceArtifact[];
  defaultUploadFiles: DataSourceArtifact[];
  isLoading?: boolean;
  openGoogleFilePicker: VoidFunction;
  setGoogleFiles: Dispatch<SetStateAction<DataSourceArtifact[]>>;
  setDefaultUploadFiles: Dispatch<SetStateAction<DataSourceArtifact[]>>;
};

export const DataSourcesStep: React.FC<Props> = ({
  googleDriveEnabled,
  googleFiles = [],
  defaultUploadFiles = [],
  isLoading,
  openGoogleFilePicker,
  setGoogleFiles,
  setDefaultUploadFiles,
}) => {
  const { mutateAsync: batchUploadFiles, status: batchUploadStatus } = useBatchUploadFile();
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
    setDefaultUploadFiles((prev) =>
      uniqBy(
        [
          ...(prev ?? []),
          ...newFileIds.map(({ id, file_name }) => ({
            id,
            name: file_name,
            type: 'file',
          })),
        ],
        'id'
      )
    );
  };

  const hasActiveDataSources =
    (googleFiles && !!googleFiles.length) || (defaultUploadFiles && !!defaultUploadFiles.length);

  if (isLoading) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Spinner />
      </div>
    );
  }
  return (
    <div className="flex flex-col gap-4">
      {hasActiveDataSources && <Text styleAs="label">Active Data Sources</Text>}
      {googleDriveEnabled && googleFiles && !!googleFiles.length && (
        <DataSourceFileList
          name="Google Drive"
          icon="google-drive"
          artifacts={googleFiles}
          addFileButton={googleDriveButton(openGoogleFilePicker, 'Add Files')}
          handleRemoveTool={() => handleRemoveAllFiles('google-drive')}
          handleRemoveFile={(removedId: string) => handleRemoveGoogleDriveFile(removedId)}
        />
      )}
      {defaultUploadFiles && !!defaultUploadFiles.length && (
        <DataSourceFileList
          name="Files"
          icon="desktop"
          artifacts={defaultUploadFiles}
          addFileButton={defaultUploadButton(
            'Add Files',
            fileInputRef,
            handleFileInputChange,
            batchUploadStatus,
            handleOpenFileExplorer
          )}
          handleRemoveTool={() => handleRemoveAllFiles('default-upload')}
          handleRemoveFile={(removedId: string) => handleRemoveUploadFile(removedId)}
        />
      )}
      <Text styleAs="label">Add {hasActiveDataSources ? 'More' : ''} Data Sources</Text>
      <div className="flex gap-4">
        {googleDriveEnabled &&
          !(googleFiles && googleFiles.length) &&
          googleDriveButton(openGoogleFilePicker, 'Google Drive')}
        {!(defaultUploadFiles && defaultUploadFiles.length) &&
          defaultUploadButton(
            'Add Files',
            fileInputRef,
            handleFileInputChange,
            batchUploadStatus,
            handleOpenFileExplorer
          )}
      </div>
      <Text styleAs="caption" className="dark:text-marble-800">
        Don&lsquo;t see the data source you need? {/* TODO: get tool request link from Elaine */}
        <Link className="underline" onClick={() => alert('Needs to be developed!')} href="">
          Make a request
        </Link>
      </Text>
    </div>
  );
};

const googleDriveButton = (handleAddFiles: VoidFunction, label: string | ReactNode) => {
  return (
    <Button
      kind="outline"
      theme="mushroom"
      icon={label === 'Add Files' ? 'add' : 'google-drive'}
      label={label}
      onClick={handleAddFiles}
    />
  );
};

const defaultUploadButton = (
  label: string | ReactNode,
  fileInputRef: RefObject<HTMLInputElement>,
  handleFileInputChange: (e: React.ChangeEvent<HTMLInputElement>) => Promise<void>,
  batchUploadStatus: 'error' | 'idle' | 'pending' | 'success',
  handleOpenFileExplorer: (callback: VoidFunction) => void
) => {
  return (
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
        icon={label === 'Add Files' ? 'add' : 'desktop'}
        label={label}
        isLoading={batchUploadStatus === 'pending'}
        onClick={() => handleOpenFileExplorer(close)}
      />
    </>
  );
};

const getCountString = (type: 'file' | 'folder', artifacts?: DataSourceArtifact[]) => {
  const count = artifacts ? artifacts.length : undefined;
  if (!count || count === 0) return;
  return `${count} ${pluralize(type, count)}`;
};

const DataSourceFileList: React.FC<{
  name: string;
  icon: IconName;
  artifacts?: DataSourceArtifact[];
  addFileButton: ReactNode;
  handleRemoveFile: (id: string) => void;
  handleRemoveTool: VoidFunction;
}> = ({ name, icon, artifacts = [], addFileButton, handleRemoveFile, handleRemoveTool }) => {
  const filesCount = getCountString(
    'file',
    artifacts.filter((artifact) => artifact.type === 'file')
  );
  const foldersCount = getCountString(
    'folder',
    artifacts.filter((artifact) => artifact.type === 'folder')
  );

  const countCopy = [filesCount, foldersCount].filter((text) => !!text).join(', ');

  return (
    <div className="flex flex-col space-y-6 rounded-md border border-volcanic-800 p-4">
      <div className="flex flex-col space-y-2">
        <div className="flex justify-between">
          <div className="flex items-center space-x-2">
            <Icon name={icon} size="lg" />
            <Text styleAs="p-lg">{name}</Text>
          </div>
          <Button icon="trash" kind="secondary" theme="danger" onClick={handleRemoveTool} />
        </div>
        <Text className="dark:text-marble-800">
          {name === TOOL_GOOGLE_DRIVE_ID
            ? 'Add relevant files to your assistant.'
            : 'Upload files and folders from your local drive.'}
        </Text>
      </div>
      <div className="flex flex-col">
        {artifacts.map(({ id, type, name }) => (
          <div
            key={id}
            className="flex w-full items-center gap-x-2 border-b border-mushroom-500 py-3 dark:border-volcanic-300"
          >
            <Icon kind="outline" name={type === 'folder' ? 'folder' : 'file'} size="sm" />
            <Text styleAs="label" className="dark:test-marble-950 mr-auto truncate">
              {name}
            </Text>
            <Button icon="close" kind="secondary" onClick={() => handleRemoveFile(id)} />
          </div>
        ))}

        <Text className="py-4 dark:text-marble-800">{countCopy}</Text>
        {addFileButton}
      </div>
    </div>
  );
};
