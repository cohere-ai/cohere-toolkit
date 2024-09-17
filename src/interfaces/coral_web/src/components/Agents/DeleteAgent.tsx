'use client';

import { useRouter } from 'next/navigation';

import { Button, Text } from '@/components/Shared';
import { DYNAMIC_STRINGS, STRINGS } from '@/constants/strings';
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
      <Text>{DYNAMIC_STRINGS.deleteAssistantConfirmationDescription(name)}</Text>
      <div className="flex justify-between">
        <Button kind="secondary" onClick={onClose}>
          {STRINGS.cancel}
        </Button>
        <Button
          kind="danger"
          onClick={handleDeleteAgent}
          splitIcon="arrow-right"
          disabled={isPending}
        >
          {isPending ? STRINGS.deleting : STRINGS.delete}
        </Button>
      </div>
    </div>
  );
};
