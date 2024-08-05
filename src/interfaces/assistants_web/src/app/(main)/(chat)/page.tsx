import { NextPage } from 'next';

import Chat from '@/app/(main)/(chat)/Chat';
import { DEFAULT_ASSISTANT_ID } from '@/constants';

const Page: NextPage = () => {
  return <Chat agentId={DEFAULT_ASSISTANT_ID} />;
};

export default Page;
