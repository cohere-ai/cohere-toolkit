'use client';

import { isNotFoundError } from '@/cohere-client';
import { Header } from '@/components/Conversation/Header';
import { Icon } from '@/components/Shared/Icon';
import { Text } from '@/components/Shared/Text';
import { DYNAMIC_STRINGS, STRINGS } from '@/constants/strings';
import { useChatRoutes } from '@/hooks/chatRoutes';
import { cn } from '@/utils';

type Props = {
  error: Error;
};

export const ConversationError: React.FC<Props> = ({ error }) => {
  const { agentId } = useChatRoutes();

  const url = agentId ? `/a/${agentId}` : '/';

  return (
    <>
      <Header />
      <section className={cn('grid h-full w-full place-content-center gap-2 px-8 md:px-0')}>
        <Icon name="warning" size="lg" className="mx-auto" />

        <Text className="max-w-sm text-center">
          {isNotFoundError(error) ? (
            DYNAMIC_STRINGS.conversationNotFoundDescription(url)
          ) : (
            <>
              {STRINGS.somethingWentWrong} <br /> {STRINGS.pleaseTryAgainLater}
            </>
          )}
        </Text>
      </section>
    </>
  );
};
