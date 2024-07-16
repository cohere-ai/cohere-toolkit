import { useLocalStorageValue } from '@react-hookz/web';
import { useQuery } from '@tanstack/react-query';
import useDrivePicker from 'react-google-drive-picker';
import type { PickerCallback } from 'react-google-drive-picker/dist/typeDefs';

import { ManagedTool, useCohereClient } from '@/cohere-client';
import { LOCAL_STORAGE_KEYS, TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { env } from '@/env.mjs';
import { useNotify } from '@/hooks/toast';

export const useListTools = (enabled: boolean = true) => {
  const client = useCohereClient();
  return useQuery<ManagedTool[], Error>({
    queryKey: ['tools'],
    queryFn: () => client.listTools({}),
    refetchOnWindowFocus: false,
    enabled,
  });
};

/**
 * @description A hook that returns a list of tools that require authentication
 */
export const useUnauthedTools = (enabled: boolean = true) => {
  const { data: tools } = useListTools(enabled);
  const unauthedTools = tools?.filter((tool) => tool.is_auth_required) ?? [];
  const isToolAuthRequired = unauthedTools.length > 0;
  return { unauthedTools, isToolAuthRequired };
};

export const useShowUnauthedToolsModal = () => {
  const { isToolAuthRequired } = useUnauthedTools();
  const { value: hasDismissed, set } = useLocalStorageValue(
    LOCAL_STORAGE_KEYS.unauthedToolsModalDismissed,
    {
      defaultValue: false,
      initializeWithValue: true,
    }
  );
  return {
    show: !hasDismissed && isToolAuthRequired,
    onDismissed: () => set(true),
  };
};

export const useOpenGoogleDrivePicker = (callbackFunction: (data: PickerCallback) => void) => {
  const [openPicker] = useDrivePicker();
  const { data: toolsData } = useListTools();
  const { info } = useNotify();

  const googleDriveTool = toolsData?.find((tool) => tool.name === TOOL_GOOGLE_DRIVE_ID);

  const handleCallback = (data: PickerCallback) => {
    if (!data.docs) return;

    const folders = data.docs.filter((doc) => doc.type === 'folder');
    const files = data.docs.filter((doc) => doc.type !== 'folder');

    if (folders.length > 0 && files.length > 0) {
      info('Please select either files or folders.');
      return;
    }
    if (files.length > 5) {
      info('You can only select a maximum of 5 files.');
      return;
    }

    callbackFunction(data);
  };

  const googleDriveClientId = env.NEXT_PUBLIC_GOOGLE_DRIVE_CLIENT_ID;
  const googleDriveDeveloperKey = env.NEXT_PUBLIC_GOOGLE_DRIVE_DEVELOPER_KEY;
  if (!googleDriveClientId || !googleDriveDeveloperKey) {
    return () => {
      info('Google Drive is not available at the moment.');
    };
  }

  return () =>
    openPicker({
      clientId: googleDriveClientId,
      developerKey: googleDriveDeveloperKey,
      token: googleDriveTool?.token || '',
      setIncludeFolders: true,
      setSelectFolderEnabled: true,
      showUploadView: false,
      showUploadFolders: false,
      supportDrives: true,
      multiselect: true,
      callbackFunction: handleCallback,
    });
};
