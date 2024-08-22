import { NextPage } from 'next';

import { UpdateAgent } from './UpdateAgent';
import { getCohereServerClient } from '@/server/cohereServerClient';

type Props = {
  params: {
    agentId: string;
  };
  searchParams: Record<string, string>;
};

const Page: NextPage<Props> = async ({ params }) => {
  const cohereServerClient = getCohereServerClient();
  const agent = await cohereServerClient.getAgent(params.agentId);

  return <UpdateAgent agent={agent} />;
};

export default Page;
