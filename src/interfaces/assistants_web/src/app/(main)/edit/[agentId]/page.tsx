import { NextPage } from 'next';

import { UpdateAgent } from '@/components/Agents/UpdateAgent';

type Props = {
  params: {
    agentId: string;
  };
  searchParams: Record<string, string>;
};

const Page: NextPage<Props> = ({ params }) => {
  return (
    <div className="h-full w-full rounded-lg border border-marble-950 bg-marble-980 dark:border-volcanic-150 dark:bg-volcanic-100">
      <UpdateAgent agentId={params.agentId} />
    </div>
  );
};

export default Page;
