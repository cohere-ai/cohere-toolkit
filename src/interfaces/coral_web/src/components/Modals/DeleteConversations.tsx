'use client';

import { Button, Text } from '@/components/Shared';
import { DYNAMIC_STRINGS, STRINGS } from '@/constants/strings';

type Props = {
  conversationIds: string[];
  onClose: VoidFunction;
  onConfirm: VoidFunction;
  isPending: boolean;
};

export const DeleteConversations: React.FC<Props> = ({
  conversationIds,
  onClose,
  onConfirm,
  isPending,
}) => {
  const numConversations = conversationIds.length;

  return (
    <section>
      <Text className="mb-5">
        {DYNAMIC_STRINGS.deleteConversationDescription(numConversations)}
      </Text>
      <div className="flex flex-col-reverse items-center justify-between gap-y-4 md:flex-row">
        <Button
          kind="secondary"
          onClick={onClose}
          className="flex w-auto items-center justify-center md:mt-0"
        >
          <Text>{STRINGS.cancel}</Text>
        </Button>
        <Button
          kind="danger"
          onClick={onConfirm}
          splitIcon="trash"
          disabled={isPending}
          className="w-full md:w-fit"
        >
          <Text>
            {isPending
              ? STRINGS.deleting
              : DYNAMIC_STRINGS.deleteNumConversations(numConversations)}
          </Text>
        </Button>
      </div>
    </section>
  );
};
