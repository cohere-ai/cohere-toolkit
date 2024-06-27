import { useLocalStorageValue } from '@react-hookz/web';
import { useQuery } from '@tanstack/react-query';
import useDrivePicker from 'react-google-drive-picker';

import { ManagedTool, useCohereClient } from '@/cohere-client';
import { LOCAL_STORAGE_KEYS, TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { env } from '@/env.mjs';

export const useListTools = (enabled: boolean = true) => {
  const client = useCohereClient();
  return useQuery<ManagedTool[], Error>({
    queryKey: ['tools'],
    queryFn: async () => {
      return await client.listTools({});
    },
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

export const useOpenGoogleDrivePicker = (callbackFunction: (data: any) => void) => {
  const [openPicker] = useDrivePicker();
  const { data: toolsData } = useListTools();

  const googleDriveTool = toolsData?.find((tool) => tool.name === TOOL_GOOGLE_DRIVE_ID);

  return () =>
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
      callbackFunction,
    });
};
