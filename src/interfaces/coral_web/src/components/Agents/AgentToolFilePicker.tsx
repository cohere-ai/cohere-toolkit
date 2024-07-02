import { IconButton } from '@/components/IconButton';
import { Button, Icon, Text } from '@/components/Shared';
import { GoogleDriveToolArtifact } from '@/types/tools';

type Props = {
  googleDriveFiles?: GoogleDriveToolArtifact[];
  handleRemoveGoogleDriveFiles: (id: string) => void;
  handleOpenFilePicker: VoidFunction;
};
export const AgentToolFilePicker: React.FC<Props> = ({
  googleDriveFiles,
  handleRemoveGoogleDriveFiles,
  handleOpenFilePicker,
}) => {
  return (
    <div className="flex max-w-[300px] flex-col gap-y-2">
      <Button
        kind="secondary"
        startIcon={<Icon name="add" kind="outline" className="text-green-700" />}
        label="Select files/folders"
        onClick={handleOpenFilePicker}
      />

      {googleDriveFiles && googleDriveFiles.length > 0 && (
        <div className="flex max-h-[262px] flex-col gap-y-1 overflow-y-auto rounded border border-marble-300 px-3 py-1">
          {googleDriveFiles.map(({ type, id, name }) => (
            <div key={id} className="flex flex-shrink-0 items-center gap-x-2 truncate">
              <Icon
                name={type === 'folder' ? 'folder' : 'file'}
                className="text-secondary-600"
                size="sm"
              />
              <Text styleAs="caption" className="truncate">
                {name}
              </Text>
              <IconButton
                onClick={() => handleRemoveGoogleDriveFiles(id)}
                iconName="close"
                size="sm"
                className="ml-auto"
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
