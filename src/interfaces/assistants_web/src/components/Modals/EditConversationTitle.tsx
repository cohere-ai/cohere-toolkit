'use client';

import { useState } from 'react';

import { Button, Input, Text } from '@/components/Shared';
import { useEditConversation } from '@/hooks/conversation';
import { useConversationStore } from '@/stores';

type Props = {
  conversationId: string;
  initialConversationTitle: string;
  onClose: VoidFunction;
};

export const EditConversationTitle: React.FC<Props> = ({
  conversationId = '',
  initialConversationTitle,
  onClose,
}) => {
  const [title, setTitle] = useState(initialConversationTitle);
  const [errorMessage, setErrorMessage] = useState('');

  const { mutateAsync: editConversation, isPending } = useEditConversation();
  const { setConversation } = useConversationStore();

  const onConfirm = async () => {
    try {
      setErrorMessage('');
      await editConversation({ request: { title }, conversationId });

      if (window?.location.pathname.includes(conversationId)) {
        setConversation({ name: title });
      }
      onClose();
    } catch {
      setErrorMessage('Failed to update conversation title. Please try again.');
    }
  };

  return (
    <div>
      <Input
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        disabled={isPending}
      />

      <Text className="mt-2 text-danger-350 first-letter:uppercase">{errorMessage}</Text>

      <div className="mt-6 flex items-center justify-between">
        <Button label="Cancel" kind="secondary" onClick={onClose} />
        <Button
          kind="cell"
          onClick={onConfirm}
          disabled={isPending}
          isLoading={isPending}
          label="Save"
        />
      </div>
    </div>
  );
};
