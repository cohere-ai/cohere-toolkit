import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';
import useDrivePicker from 'react-google-drive-picker';
import type { PickerCallback } from 'react-google-drive-picker/dist/typeDefs';

import { Agent, ManagedTool, useCohereClient } from '@/cohere-client';
import { DEFAULT_AGENT_TOOLS, TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { env } from '@/env.mjs';
import { useNotify } from '@/hooks/toast';
import { useParamsStore } from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';

export const useListTools = (enabled: boolean = true) => {
  const client = useCohereClient();
  return useQuery<ManagedTool[], Error>({
    queryKey: ['tools'],
    queryFn: async () => {
      const tools = await client.listTools({});
      return tools.filter((tool) => !DEFAULT_AGENT_TOOLS.includes(tool.name ?? ''));
    },
    refetchOnWindowFocus: false,
    enabled,
  });
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

export const useAvailableTools = ({
  agent,
  managedTools,
}: {
  agent?: Agent;
  managedTools?: ManagedTool[];
}) => {
  const requiredTools = agent?.tools;

  const { data: tools } = useListTools();
  const { params, setParams } = useParamsStore();
  const { tools: paramTools } = params;
  const enabledTools = paramTools ?? [];
  const unauthedTools =
    tools?.filter(
      (tool) => tool.is_auth_required && tool.name && requiredTools?.includes(tool.name)
    ) ?? [];

  const availableTools = useMemo(() => {
    return (managedTools ?? []).filter(
      (t) =>
        t.is_visible &&
        t.is_available &&
        (!requiredTools || requiredTools.some((rt) => rt === t.name))
    );
  }, [managedTools, requiredTools]);

  const handleToggle = (name: string, checked: boolean) => {
    const newParams: Partial<ConfigurableParams> = {
      tools: checked
        ? [...enabledTools, { name }]
        : enabledTools.filter((enabledTool) => enabledTool.name !== name),
    };

    setParams(newParams);
  };

  return {
    availableTools,
    unauthedTools,
    handleToggle,
  };
};
