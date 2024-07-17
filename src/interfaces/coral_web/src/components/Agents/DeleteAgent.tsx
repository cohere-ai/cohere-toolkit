'use client';

import { useRouter } from 'next/navigation';

import { Button, Text } from '@/components/Shared';
import { useDeleteAgent } from '@/hooks/agents';
import { useChatRoutes } from '@/hooks/chatRoutes';

type Props = {
  name: string;
  agentId: string;
  onClose: () => void;
};

/**
 * @description This component renders a confirmation dialog to delete an agent.
 */
export const DeleteAgent: React.FC<Props> = ({ name, agentId, onClose }) => {
  const { mutateAsync: deleteAgent, isPending } = useDeleteAgent();
  const { agentId: currentAgentId } = useChatRoutes();
  const router = useRouter();

  const handleDeleteAgent = async () => {
    await deleteAgent({ agentId });
    onClose();
    if (agentId === currentAgentId) {
      router.push('/', undefined);
    }
  };

  return (
    <div className="flex flex-col gap-y-20">
      <Text>
        Your assistant <strong>{name}</strong> will be deleted. This action cannot be undone.
      </Text>
      <div className="flex justify-between">
        <Button kind="secondary" onClick={onClose}>
          Cancel
        </Button>
        <Button
          kind="danger"
          onClick={handleDeleteAgent}
          splitIcon="arrow-right"
          disabled={isPending}
        >
          {isPending ? 'Deleting' : 'Delete'}
        </Button>
      </div>
    </div>
  );
};
