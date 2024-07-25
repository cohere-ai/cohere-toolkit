'use client';

import { Button, Text } from '@/components/Shared';
import { pluralize } from '@/utils';

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
        Once you delete {numConversations === 1 ? 'this chat' : 'these chats'} you will be unable to
        see or retrieve the messages. You cannot undo this action.
      </Text>
      <div className="flex flex-col-reverse items-center justify-between gap-y-4 md:flex-row">
        <Button
          kind="secondary"
          onClick={onClose}
          className="flex w-auto items-center justify-center md:mt-0"
        >
          <Text>Cancel</Text>
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
              ? 'Deleting...'
              : `Delete ${numConversations === 1 ? '' : numConversations} ${pluralize(
                  'conversation',
                  numConversations
                )}`}
          </Text>
        </Button>
      </div>
    </section>
  );
};
