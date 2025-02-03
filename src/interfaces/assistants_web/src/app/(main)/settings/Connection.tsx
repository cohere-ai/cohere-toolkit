'use client';

import { useEffect, useState } from 'react';

import { StatusConnection } from '@/components/AgentSettingsForm/StatusConnection';
import { Button, Icon, IconName, Text } from '@/components/UI';
import { useDeleteAuthTool, useListTools, useNotify } from '@/hooks';
import { getToolAuthUrl } from '@/utils';

type Props = {
  toolId: string;
  toolName: string;
  iconName: IconName;
  description: string;
  showSyncButton: boolean;
};

export const Connection: React.FC<Props> = ({
  toolId,
  toolName,
  iconName,
  description,
  showSyncButton,
}) => {
  const [init, setInit] = useState(false);
  const { data } = useListTools();
  const { mutateAsync: deleteAuthTool } = useDeleteAuthTool();
  const notify = useNotify();
  const tool = data?.find((tool) => tool.name === toolId);

  // This is used to resolve hydration error where the server side rendered content and
  // the client side content don't align because the client side content depends on information
  // from the API that is only available at run time.
  useEffect(() => setInit(true), []);

  if (!tool) return null;

  const handleDeleteAuthTool = async () => {
    try {
      await deleteAuthTool(tool.name!);
    } catch {
      notify.error(`Failed to delete ${toolName} connection`);
    }
  };

  const isConnected = !(tool.is_auth_required ?? false);
  const isAvailable = tool.is_available ?? false;
  const error = tool.error_message ?? '';
  const authUrl = getToolAuthUrl(tool.auth_url);

  return (
    <article className="rounded-md border border-marble-800 p-4 dark:border-volcanic-500">
      <header className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon name={iconName} size="xl" />
          <Text className="text-volcanic-400 dark:text-mushroom-950">{toolName}</Text>
        </div>
        <StatusConnection connected={isConnected} />
      </header>
      <Text className="mb-6 text-volcanic-400 dark:text-mushroom-800">{description}</Text>
      {init && (
        <section>
          {!isAvailable ? (
            <div className="justify-items-start space-y-6">
              <div className="flex items-center justify-between">
                <p className="font-body text-p-sm uppercase text-danger-500">
                  {error || `${toolName} connection is not available.`}
                </p>
              </div>
            </div>
          ) : isConnected ? (
            <div className="space-y-6">
              {showSyncButton && (
                <Button label="Sync now" kind="secondary" icon="arrow-clockwise" href={authUrl} />
              )}
              <Button
                label="Delete connection"
                kind="secondary"
                icon="trash"
                theme="danger"
                onClick={handleDeleteAuthTool}
              />
            </div>
          ) : (
            <Button
              label="Authenticate"
              href={authUrl}
              kind="secondary"
              theme="default"
              icon="arrow-up-right"
            />
          )}
        </section>
      )}
    </article>
  );
};
