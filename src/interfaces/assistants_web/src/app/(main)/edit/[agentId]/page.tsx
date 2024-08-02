import { NextPage } from 'next';

import { UpdateAgent } from '@/components/Agents/UpdateAgent';

type Props = {
  params: {
    agentId: string;
  };
  searchParams: Record<string, string>;
};

const Page: NextPage<Props> = ({ params }) => {
  return <UpdateAgent agentId={params.agentId} />;
};

export default Page;
