import { NextPage } from 'next';

import Chat from '@/app/(main)/(chat)/Chat';

type Props = {
  params: {
    agentId: string;
    conversationId: string;
  };
  searchParams: Record<string, string>;
};

const Page: NextPage<Props> = ({ params }) => {
  return <Chat conversationId={params.conversationId} agentId={params.agentId} />;
};

export default Page;
