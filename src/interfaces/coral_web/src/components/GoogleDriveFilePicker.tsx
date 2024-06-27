import { IconButton } from '@/components/IconButton';
import { Button, Icon, Text } from '@/components/Shared';

type Props = {
  googleDriveFiles: { id: string; name: string; type: string }[];
  filePickerCallback: (files: { id: string; name: string; type: string }[] | undefined) => void;
  handleOpenPicker: VoidFunction;
};
export const GoogleDriveFilePicker: React.FC<Props> = ({
  googleDriveFiles,
  filePickerCallback,
  handleOpenPicker,
}) => {
  const removeGoogleDriveFile = (id: string) => {
    const newFiles = googleDriveFiles.filter((file) => file.id !== id);
    filePickerCallback(newFiles);
  };

  return (
    <div className="flex max-w-[300px] flex-col gap-y-3">
      <Button
        kind="secondary"
        startIcon={<Icon name="add" kind="outline" className="text-green-700" />}
        label="Select files/folders"
        onClick={handleOpenPicker}
      />
      {googleDriveFiles.length > 0 && (
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
                onClick={() => removeGoogleDriveFile(id)}
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
