import { Spinner } from '@/components/UI/Spinner';
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

  return <div>{file!.file_name}</div>;
};
