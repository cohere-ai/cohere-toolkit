import MessageRow from '@/components/MessageRow';
import { Button, Text } from '@/components/Shared';
import { PageHead } from '@/components/Shared/PageHead';
import { ChatMessage } from '@/types/message';

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
      <PageHead title={title} />
      <div className="flex w-full max-w-share-content flex-col gap-2 pb-20 pt-12">
        <Text styleAs="h3" className="text-volcanic-800">
          {title}
        </Text>

        <div className="my-6 w-full border-b border-marble-500" />

        <div className="flex flex-col  gap-y-4 px-4 py-6 md:gap-y-6">
          {messages.map((m, i) => (
            <MessageRow
              key={i}
              message={m}
              isLast={messages.length - 1 === i}
              isStreamingToolEvents={false}
            />
          ))}
        </div>
      </div>
      <div className="fixed bottom-0 left-0 flex w-full items-center justify-center bg-white py-4 shadow-top">
        <Button label="Start a new conversation" href="/" splitIcon="arrow-right" kind="primary" />
      </div>
    </>
  );
};
