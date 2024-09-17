'use client';

import { useState } from 'react';

import { Button, Input, Spinner, Text } from '@/components/Shared';
import { STRINGS } from '@/constants/strings';
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
      setErrorMessage(STRINGS.updateConversationTitleError);
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
        <Button kind="secondary" onClick={onClose}>
          {STRINGS.cancel}
        </Button>
        <Button onClick={onConfirm} splitIcon="arrow-right" disabled={isPending}>
          {isPending ? <Spinner /> : STRINGS.save}
        </Button>
      </div>
    </div>
  );
};
