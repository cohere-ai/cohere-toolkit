import { Avatar } from '@/components/Avatar';
import { Button, Markdown, Text } from '@/components/Shared';
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
            <div key={i} className="flex w-full gap-x-2">
              <Avatar message={m} />
              <div className="flex w-full flex-col justify-center gap-y-1 whitespace-pre-wrap py-1 [overflow-wrap:anywhere] md:max-w-4xl">
                <Markdown text={m.text || ''} />
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="fixed bottom-0 left-0 flex w-full items-center justify-center bg-white py-4 shadow-top">
        <Button label="Start a new conversation" href="/" splitIcon="arrow-right" kind="primary" />
      </div>
    </>
  );
};
