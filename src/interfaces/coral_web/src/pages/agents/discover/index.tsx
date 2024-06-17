import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';

import { CohereClient } from '@/cohere-client';
import { DiscoverAgentCard } from '@/components/Agents/DiscoverAgentCard';
import { Layout, LeftSection, MainSection } from '@/components/Agents/Layout';
import { LeftPanel } from '@/components/Agents/LeftPanel';
import { Input, Text } from '@/components/Shared';
import { appSSR } from '@/pages/_app';
import { cn } from '@/utils';

type Props = {};

const AgentsNewPage: NextPage<Props> = () => {
  const agents = [
    {
      id: '1',
      name: 'Agent 1',
      description: 'This is the first agent',
    },
    {
      id: '2',
      name: 'Agent 2',
      description: 'This is the second agent',
    },
    {
      id: '3',
      name: 'Agent 3',
      description: 'This is the third agent',
    },
    {
      id: '4',
      name: 'Agent 4',
      description: 'This is the fourth agent',
    },
    {
      id: '5',
      name: 'Agent 5',
      description: 'This is the fifth agent',
    },
    {
      id: '6',
      name: 'Agent 6',
      description: 'This is the sixth agent',
    },
    {
      id: '7',
      name: 'Agent 7',
      description: 'This is the seventh agent',
    },
    {
      id: '8',
      name: 'Agent 8',
      description: 'This is the eighth agent',
    },
    {
      id: '9',
      name: 'Agent 9',
      description: 'This is the ninth agent',
    },
    {
      id: '10',
      name: 'Agent 10',
      description: 'This is the tenth agent',
    },
    {
      id: '11',
      name: 'Agent 11',
      description: 'This is the eleventh agent',
    },
    {
      id: '12',
      name: 'Agent 12',
      description: 'This is the twelfth agent',
    },
  ];

  return (
    <Layout>
      <LeftSection>
        <LeftPanel />
      </LeftSection>
      <MainSection>
        <div className="flex h-full w-full flex-grow flex-col overflow-y-auto rounded-lg border border-marble-400 bg-marble-100 md:ml-0">
          <div
            className={cn(
              'border-b border-marble-400 bg-cover',
              'flex flex-shrink-0 flex-col gap-y-2',
              'bg-[url(/images/cellBackground.svg)]',
              'px-4 py-6 md:px-9 md:py-10 lg:px-10'
            )}
          >
            <Text styleAs="h4" className="text-volcanic-700">
              Discover Assistants
            </Text>
            <Text>
              Assistants created by your peers to help you solve tasks and increase efficiency
            </Text>
          </div>
          <div className="max-w-screen-xl flex-grow overflow-y-auto px-4 py-10 md:px-9 lg:px-10">
            <div className="grid grid-cols-1 gap-x-4 gap-y-5 md:grid-cols-3">
              {agents.length >= 10 && (
                <>
                  <Input size="sm" kind="default" actionType="search" placeholder="Search" />
                  <div className="col-span-2 hidden md:flex" />
                </>
              )}
              <DiscoverAgentCard
                isBaseAgent
                name="Command R+"
                description="Review, understand and ask questions about  internal financial documents."
              />
              {agents.map((agent) => (
                <DiscoverAgentCard key={agent.name} {...agent} />
              ))}
            </div>
          </div>
        </div>
      </MainSection>
    </Layout>
  );
};

export const getServerSideProps: GetServerSideProps = async () => {
  const deps = appSSR.initialize() as {
    queryClient: QueryClient;
    cohereClient: CohereClient;
  };

  return {
    props: {
      appProps: {
        reactQueryState: dehydrate(deps.queryClient),
      },
    },
  };
};

export default AgentsNewPage;
