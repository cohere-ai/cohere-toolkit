import { IconButton } from '@/components/IconButton';
import { Button, Icon, Text } from '@/components/Shared';

type Props = {
  googleDriveFiles?: { id: string; name: string; type: string; url: string }[];
  setGoogleDriveFiles: (files: { id: string; name: string; type: string; url: string }[]) => void;
  handleOpenFilePicker: VoidFunction;
};
export const CreateAgentFilePicker: React.FC<Props> = ({
  googleDriveFiles,
  setGoogleDriveFiles,
  handleOpenFilePicker,
}) => {
  const handleRemoveFile = (id: string) => {
    setGoogleDriveFiles(googleDriveFiles?.filter((file) => file.id !== id) ?? []);
  };
  return (
    <div className="flex max-w-[300px] flex-col gap-y-3">
      <Button
        kind="secondary"
        startIcon={<Icon name="add" kind="outline" className="text-green-700" />}
        label="Select files/folders"
        onClick={handleOpenFilePicker}
      />

      {googleDriveFiles && googleDriveFiles.length > 0 && (
        <div className="rounded border border-marble-300 p-2">
          {googleDriveFiles.map(({ type, id, name }) => (
            <div key={id} className="flex items-center gap-x-2 truncate pb-1">
              <Icon
                name={type === 'folder' ? 'folder' : 'file'}
                kind="outline"
                className="text-secondary-600"
              />
              <Text className="truncate">{name}</Text>
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
