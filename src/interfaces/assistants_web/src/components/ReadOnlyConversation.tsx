'use client';

import MessageRow from '@/components/MessageRow';
import { Button, Text } from '@/components/Shared';
import { ChatMessage } from '@/types/message';
import { cn } from '@/utils';

type Props = {
  title: string;
  messages: ChatMessage[];
};

/**
 * @description Read only view of a shared conversation
 */
export const ReadOnlyConversation: React.FC<Props> = ({ title, messages }) => {
  return (
    <>
      <div className="flex w-full max-w-share-content flex-col gap-2 pb-28 pt-12 md:px-5 dark:bg-volcanic-100">
        <Text styleAs="h3" className="text-center text-volcanic-300">
          {title}
        </Text>

        <div className={cn('my-6 w-full border-b border-marble-800')} />

        <div className="flex flex-col gap-y-4 py-6 md:gap-y-6">
          {messages.map((m, i) => (
            <div key={i} className="flex items-start justify-between gap-x-3">
              <MessageRow
                message={m}
                isLast={i === messages.length - 1}
                isStreamingToolEvents={false}
                className="w-full max-w-full md:max-w-full"
              />
            </div>
          ))}
        </div>
      </div>
      <div className="fixed bottom-0 left-0 z-read-only-conversation-footer flex w-full items-center justify-center bg-white py-4 shadow-top dark:bg-volcanic-150">
        <Button
          label="Start a new conversation"
          href="/"
          icon="arrow-right"
          kind="primary"
          theme="evolved-green"
        />
      </div>
    </>
  );
};
