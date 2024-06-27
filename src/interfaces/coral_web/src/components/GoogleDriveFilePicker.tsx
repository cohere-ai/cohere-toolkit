import useDrivePicker from 'react-google-drive-picker';

import { IconButton } from '@/components/IconButton';
import { Button, Icon, Text } from '@/components/Shared';
import { env } from '@/env.mjs';
import { useListTools } from '@/hooks/tools';
import { useParamsStore } from '@/stores';
import { cn } from '@/utils';

const GOOGLE_DRIVE_TOOL_NAME = 'google_drive';

export const GoogleDriveFilePicker: React.FC = () => {
  const [openPicker] = useDrivePicker();
  const { data: toolsData } = useListTools();
  const {
    params: { googleDriveFiles },
    setGoogleDriveFiles,
    removeGoogleDriveFile,
  } = useParamsStore();

  const handleOpenPicker = () => {
    const googleDriveTool = toolsData?.find((tool) => tool.name === GOOGLE_DRIVE_TOOL_NAME);
    openPicker({
      clientId: env.NEXT_PUBLIC_GOOGLE_DRIVE_CLIENT_ID,
      developerKey: env.NEXT_PUBLIC_GOOGLE_DRIVE_DEVELOPER_KEY,
      token: googleDriveTool?.token || '',
      setIncludeFolders: true,
      setSelectFolderEnabled: true,
      showUploadView: false,
      showUploadFolders: false,
      supportDrives: true,
      multiselect: true,
      callbackFunction: (data) => {
        if (data.docs) {
          setGoogleDriveFiles(
            data.docs.map((doc) => ({
              id: doc.id,
              name: doc.name,
              type: doc.type,
            }))
          );
        }
      },
    });
  };

  return (
    <div className="flex flex-col gap-y-3">
      <Button onClick={handleOpenPicker} className="text-sm underline" kind="secondary" size="sm">
        Select files/folders
      </Button>

      {googleDriveFiles?.map(({ type, id, name }, idx, arr) => (
        <div
          key={id}
          className={cn('flex items-center gap-x-2 truncate border-b border-marble-400 pb-1', {
            'border-b-0': idx === arr.length - 1,
          })}
        >
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
  );
};
