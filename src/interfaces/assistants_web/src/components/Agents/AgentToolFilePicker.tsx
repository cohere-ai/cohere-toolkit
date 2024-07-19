'use client';

import { IconButton } from '@/components/IconButton';
import { Button, Icon, Text } from '@/components/Shared';
import { GoogleDriveToolArtifact } from '@/types/tools';

type Props = {
  googleDriveFiles?: GoogleDriveToolArtifact[];
  disabled?: boolean;
  handleRemoveGoogleDriveFiles: (id: string) => void;
  handleOpenFilePicker: VoidFunction;
};

/**
 * @description Component to display the selected files/folders from Google Drive
 * @param {GoogleDriveToolArtifact[]} googleDriveFiles - List of selected files/folders from Google Drive
 * @param {boolean} disabled - Flag to disable the file picker
 * @param {Function} handleRemoveGoogleDriveFiles - Function to remove a file/folder from the selected list
 * @param {Function} handleOpenFilePicker - Function to open the file picker
 */
export const AgentToolFilePicker: React.FC<Props> = ({
  googleDriveFiles,
  disabled,
  handleRemoveGoogleDriveFiles,
  handleOpenFilePicker,
}) => {
  return (
    <div className="flex max-w-[300px] flex-col gap-y-2">
      {!disabled && (
        <Button
          kind="secondary"
          startIcon={<Icon name="add" kind="outline" className="text-green-250" />}
          label="Select files/folders"
          onClick={handleOpenFilePicker}
        />
      )}

      {googleDriveFiles && googleDriveFiles.length > 0 && (
        <div className="flex max-h-[262px] flex-col gap-y-1 overflow-y-auto rounded border border-marble-950 px-3 py-1">
          {googleDriveFiles.map(({ type, id, name }) => (
            <div key={id} className="flex flex-shrink-0 items-center gap-x-2 truncate">
              <Icon
                name={type === 'folder' ? 'folder' : 'file'}
                className="text-mushroom-500"
                size="sm"
              />
              <Text styleAs="caption" className="truncate">
                {name}
              </Text>
              {!disabled && (
                <IconButton
                  onClick={() => handleRemoveGoogleDriveFiles(id)}
                  iconName="close"
                  size="sm"
                  className="ml-auto"
                />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
