'use client';

import { NextPage } from 'next';

import { useAgentTasks } from '@/hooks/agents';

type Props = {
  params: {
    agentId: string;
  };
  searchParams: Record<string, string>;
};

const Page: NextPage<Props> = ({ params }) => {
  const agentId = params.agentId;
  const { data: agentTasks } = useAgentTasks({ agentId });

  return (
    <div>
      <h1>Tasks will be here for {params.agentId}</h1>;<code>{JSON.stringify(agentTasks)}</code>
    </div>
  );
};

export default Page;
