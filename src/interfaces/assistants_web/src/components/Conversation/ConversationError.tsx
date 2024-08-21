'use client';

import Link from 'next/link';

import { isNotFoundError } from '@/cohere-client';
import { Icon, Text } from '@/components/UI';
import { useChatRoutes } from '@/hooks';
import { cn } from '@/utils';

import { Header } from './Header';

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
            <>
              This conversation does not exist, <br /> why not create a{' '}
              <Link href={url} className="underline">
                new one
              </Link>
              ?
            </>
          ) : (
            <>
              Something went wrong. <br /> Please try again later.
            </>
          )}
        </Text>
      </section>
    </>
  );
};
