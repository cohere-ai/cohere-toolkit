import { IconButton } from '@/components/IconButton';
import { Button, Icon, Text } from '@/components/Shared';

type Props = {
  googleDriveFiles?: Record<string, any>[];
  setGoogleDriveFiles: (files: Record<string, any>[]) => void;
  handleOpenFilePicker: VoidFunction;
};
export const AgentToolFielPicker: React.FC<Props> = ({
  googleDriveFiles,
  setGoogleDriveFiles,
  handleOpenFilePicker,
}) => {
  const handleRemoveFile = (id: string) => {
    setGoogleDriveFiles(googleDriveFiles?.filter((file) => file.id !== id) ?? []);
  };
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
                kind="outline"
                className="text-secondary-600"
              />
              <Text styleAs="caption" className="truncate">
                {name}
              </Text>
              <IconButton
                onClick={() => handleRemoveFile(id)}
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
