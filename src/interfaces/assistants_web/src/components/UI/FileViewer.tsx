import { Markdown } from '@/components/Markdown';
import { Icon } from '@/components/UI/Icon';
import { Spinner } from '@/components/UI/Spinner';
import { Text } from '@/components/UI/Text';
import { useFile } from '@/hooks';

type Props = {
  fileId: string;
  agentId?: string;
  conversationId?: string;
};

export const FileViewer: React.FC<Props> = ({ fileId, agentId, conversationId }) => {
  const { data: file, isLoading } = useFile({ fileId, agentId, conversationId });

  if (isLoading) {
    return <Spinner />;
  }

  return (
    <div className="space-y-2.5">
      <header className="flex items-center gap-2">
        <div className="rounded bg-mushroom-800 p-2.5 dark:bg-volcanic-150">
          <Icon name={file ? 'file' : 'warning'} />
        </div>
        <Text styleAs="p-lg" className="truncate">
          {file?.file_name ?? 'Failed to load file content'}
        </Text>
      </header>
      {file && (
        <article className="max-h-96 overflow-y-auto">
          <Markdown className="font-variable" text={file.file_content} />
        </article>
      )}
    </div>
  );
};
