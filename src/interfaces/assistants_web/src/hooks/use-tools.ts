import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useMemo } from 'react';
import useDrivePicker from 'react-google-drive-picker';
import type { PickerCallback } from 'react-google-drive-picker/dist/typeDefs';

import { AgentPublic, ApiError, ToolDefinition, useCohereClient } from '@/cohere-client';
import { TOOL_GOOGLE_DRIVE_ID } from '@/constants';
import { env } from '@/env.mjs';
import { useNotify } from '@/hooks';
import { useParamsStore } from '@/stores';
import { ConfigurableParams } from '@/stores/slices/paramsSlice';
import { checkIsDefaultAgent } from '@/utils';

export const useListTools = (enabled: boolean = true) => {
  const client = useCohereClient();
  return useQuery<ToolDefinition[], Error>({
    queryKey: ['tools'],
    queryFn: async () => {
      const tools = await client.listTools({});
      return tools.filter((tool) => tool.is_enabled);
    },
    refetchOnWindowFocus: false,
    enabled,
  });
};

export const useListDefaultTool = (enabled: boolean = true) => {
  const client = useCohereClient();
  return useQuery<ToolDefinition[], Error>({
    queryKey: ['defaultTools'],
    queryFn: async () => {
      const tools = await client.listTools({});
      return tools.filter((tool) => tool.is_enabled && tool.is_default_tool);
    },
    refetchOnWindowFocus: false,
    enabled,
  });
};

export const useOpenGoogleDrivePicker = (callbackFunction: (data: PickerCallback) => void) => {
  const [openPicker] = useDrivePicker();
  const { data: toolsData } = useListTools();
  const { info } = useNotify();

  const googlePicker = window.google?.picker;

  if (googlePicker === undefined) {
    return;
  }

  const googleDriveTool = toolsData?.find((tool) => tool.name === TOOL_GOOGLE_DRIVE_ID);

  const handleCallback = (data: PickerCallback) => {
    if (!data.docs) return;

    callbackFunction(data);
  };

  const googleDriveClientId = env.NEXT_PUBLIC_GOOGLE_DRIVE_CLIENT_ID;
  const googleDriveDeveloperKey = env.NEXT_PUBLIC_GOOGLE_DRIVE_DEVELOPER_KEY;
  if (!googleDriveClientId || !googleDriveDeveloperKey) {
    return () => {
      info('Google Drive is not available at the moment.');
    };
  }

  const defaultView = new googlePicker.DocsView(googlePicker.ViewId.DOCS)
    .setIncludeFolders(true)
    .setSelectFolderEnabled(true)
    .setMode(googlePicker.DocsViewMode.LIST);

  const myFilesView = new googlePicker.DocsView(googlePicker.ViewId.DOCS)
    .setOwnedByMe(true)
    .setSelectFolderEnabled(true)
    .setIncludeFolders(true)
    .setMode(googlePicker.DocsViewMode.LIST);

  const sharedView = new googlePicker.DocsView(googlePicker.ViewId.DOCS)
    .setEnableDrives(true)
    .setIncludeFolders(true)
    .setSelectFolderEnabled(true)
    .setMode(google.picker.DocsViewMode.LIST);

  const customViewsArray = [defaultView, myFilesView, sharedView];

  return () =>
    openPicker({
      clientId: googleDriveClientId,
      developerKey: googleDriveDeveloperKey,
      token: googleDriveTool?.token || '',
      disableDefaultView: true,
      callbackFunction: handleCallback,
      multiselect: true,
      customViews: customViewsArray,
    });
};

export const useAvailableTools = ({
  agent,
  allTools,
}: {
  agent?: AgentPublic;
  allTools?: ToolDefinition[];
}) => {
  const requiredTools = agent?.tools;
  const { data: tools } = useListTools();
  const { params, setParams } = useParamsStore();
  const { tools: paramTools } = params;
  const enabledTools = paramTools ?? [];
  const isDefaultAgent = checkIsDefaultAgent(agent);

  let unauthedTools =
    tools?.filter(
      (tool) => tool.is_auth_required && tool.name && requiredTools?.includes(tool.name)
    ) ?? [];

  let availableTools = useMemo(() => {
    return (allTools ?? []).filter(
      (t) => t.is_available && (!requiredTools || requiredTools.some((rt) => rt === t.name))
    );
  }, [allTools, requiredTools]);

  // Only keep default tools if using default Agent
  if (isDefaultAgent) {
    unauthedTools = unauthedTools.filter((t) => {
      t.is_default_tool;
    });

    availableTools = availableTools.filter((t) => {
      t.is_default_tool;
    });
  }

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

export const useDeleteAuthTool = () => {
  const client = useCohereClient();
  const queryClient = useQueryClient();
  return useMutation<void, ApiError, string>({
    mutationFn: async (toolId) => {
      await client.deleteAuthTool({ toolId });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tools'] });
    },
  });
};
