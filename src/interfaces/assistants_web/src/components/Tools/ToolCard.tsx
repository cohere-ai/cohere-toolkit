import { ManagedTool } from '@/cohere-client';
import { Button, Icon, Text } from '@/components/UI';
import { useDeleteAuthTool, useNotify } from '@/hooks';
import { cn, getToolAuthUrl } from '@/utils';

type Props = {
  tool: ManagedTool;
};

const ToolCard: React.FC<Props> = ({ tool }) => {
  const { mutateAsync: deleteAuthTool } = useDeleteAuthTool();
  const notify = useNotify();

  const handleDeleteAuthTool = async () => {
    try {
      await deleteAuthTool(tool.name!);
    } catch (e) {
      notify.error(`Failed to delete ${tool.display_name} connection`);
    }
  };

  const isToolConnected = !tool.is_auth_required ?? false;
  const authUrl = getToolAuthUrl(tool.auth_url);

  return (
    <article className="rounded-md border border-marble-800 p-4 dark:border-volcanic-500">
      <header className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Icon name="google-drive" size="xl" />
          <Text className="text-volcanic-400 dark:text-mushroom-950">{tool.display_name}</Text>
        </div>
        <Text styleAs="p-sm" className="flex items-center gap-2 uppercase dark:text-mushroom-950">
          <span
            className={cn('size-[10px] rounded-full', {
              'bg-evolved-green-700': isToolConnected,
              'bg-danger-500': !isToolConnected,
            })}
          />
          {isToolConnected ? 'Connected' : 'Disconnected'}
        </Text>
      </header>
      <Text className="mb-6 text-volcanic-400 dark:text-mushroom-800">
        Connect to Google Drive and add files to the assistant
      </Text>
      <section>
        {isToolConnected ? (
          <div className="space-y-6">
            <div className="space-y-2">
              <Text styleAs="p-sm" className="uppercase text-volcanic-400 dark:text-mushroom-950">
                Last Sync
              </Text>
              <Text styleAs="p-sm" className="uppercase text-volcanic-400 dark:text-mushroom-950">
                Aug 15, 2024 11:20 AM
              </Text>
            </div>
            <div className="flex items-center justify-between">
              <Button
                label="Sync now"
                kind="secondary"
                icon="arrow-clockwise"
                href={authUrl ?? ''}
              />
              <Button
                label="Delete connection"
                kind="secondary"
                icon="trash"
                theme="danger"
                onClick={handleDeleteAuthTool}
              />
            </div>
          </div>
        ) : (
          <Button
            label="Authenticate"
            href={getToolAuthUrl(tool.auth_url)}
            kind="secondary"
            theme="default"
            icon="arrow-up-right"
          />
        )}
      </section>
    </article>
  );
};

export default ToolCard;
