import { useMemo } from 'react';
import { UseFormSetValue } from 'react-hook-form';

import { ManagedTool } from '@/cohere-client';
import { IconButton } from '@/components/IconButton';
import { Button, Icon, IconName, Text } from '@/components/Shared';
import { FILE_UPLOAD_TOOLS, TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { useOpenGoogleDrivePicker } from '@/hooks/tools';
import { DataSourceArtifact } from '@/types/tools';

type DataSourceState = {
  name: string;
  icon: IconName;
  id: string;
  artifacts: DataSourceArtifact[];
  diabledButton?: string;
};

type Props = {
  googleDriveArtifacts?: DataSourceArtifact[];
  fileUploadArtifacts?: DataSourceArtifact[];
  tools?: ManagedTool[];
  setGoogleDriveArtifacts: (artifacts?: DataSourceArtifact[]) => void;
  setFileUploadArtifacts: (artifacts?: DataSourceArtifact[]) => void;
};

const isToolAvailable = (name: string | string[], tools?: ManagedTool[]) => {
  if (!tools) return false;
  const checkedTools = Array.isArray(name)
    ? tools.filter((t) => t.name && name.includes(t.name))
    : [tools.find((t) => t.name === name)];
  return checkedTools.every(t => !!t?.is_available);
};

export const DataSourcesStep: React.FC<Props> = ({
  googleDriveArtifacts,
  fileUploadArtifacts,
  tools,
  setGoogleDriveArtifacts,
  setFileUploadArtifacts,
}) => {
  const isGoogleDriveAvailable = isToolAvailable(TOOL_GOOGLE_DRIVE_ID, tools);
  const isFileUploadAvailable = isToolAvailable(FILE_UPLOAD_TOOLS, tools);

  const isGoogleDriveActive = googleDriveArtifacts && !!googleDriveArtifacts.length;
  const isFileUploadActive = fileUploadArtifacts && !!fileUploadArtifacts.length;

  const dataSourcesActive = isGoogleDriveActive || isFileUploadActive;

  const handleGoogleDriveFilePicker = useOpenGoogleDrivePicker((data) => {
    if (data.docs) {
      setGoogleDriveArtifacts(
        data.docs.map(
          (doc) =>
            ({
              id: doc.id,
              name: doc.name,
              type: doc.type,
              url: doc.url,
            } as DataSourceArtifact)
        )
      );
    }
  });

  const handleRemoveGoogleDriveFile = (id: string) => {
    setGoogleDriveArtifacts(googleDriveArtifacts?.filter((f) => f.id !== id));
  };

  const handleFileUploadPicker = () => {};
  const handleRemoveFileUploadFile = (id: string) => {
    setFileUploadArtifacts(fileUploadArtifacts?.filter((f) => f.id !== id));
  };

  return (
    <div className="flex flex-col space-y-3">
      {dataSourcesActive && <Text styleAs="label">Active Data Sources</Text>}
      {isGoogleDriveAvailable && isGoogleDriveActive && (
        <DataSourceFileList
          name="Google Drive"
          icon="google-drive"
          artifacts={googleDriveArtifacts}
          handleRemoveTool={() => setGoogleDriveArtifacts(undefined)}
          handleRemoveFile={handleRemoveGoogleDriveFile}
        />
      )}
      {isFileUploadAvailable && isFileUploadActive && (
        <DataSourceFileList
          name="Files"
          icon="desktop"
          artifacts={fileUploadArtifacts}
          handleRemoveTool={() => setGoogleDriveArtifacts(undefined)}
          handleRemoveFile={handleRemoveFileUploadFile}
        />
      )}
      <Text styleAs="label">Add {dataSourcesActive ? 'More' : ''} Data Sources</Text>
      <div className="flex space-x-4">
        {isGoogleDriveAvailable && !isGoogleDriveActive && (
          <Button
            kind="outline"
            theme="mushroom"
            icon="google-drive"
            label="Google Drive"
            onClick={handleGoogleDriveFilePicker}
          />
        )}
        {isFileUploadAvailable && !isFileUploadActive && (
          <Button
            kind="outline"
            theme="mushroom"
            icon="desktop"
            label="Upload Files"
            onClick={handleFileUploadPicker}
          />
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
