import { useDebouncedState } from '@react-hookz/web';
import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';
import { useEffect, useState } from 'react';

import { CohereClient } from '@/cohere-client';
import { AgentsList } from '@/components/Agents/AgentsList';
import { DiscoverAgentCard } from '@/components/Agents/DiscoverAgentCard';
import { Layout, LeftSection, MainSection } from '@/components/Agents/Layout';
import { Input, Text } from '@/components/Shared';
import { useListAgents } from '@/hooks/agents';
import { appSSR } from '@/pages/_app';
import { cn } from '@/utils';

const MAX_DEBOUNCE_TIME = 300;

type Props = {};

const AgentsNewPage: NextPage<Props> = () => {
  const { data: agents = [] } = useListAgents();

  const [filterText, setFilterText] = useState('');
  const [filteredAgents, setFilteredAgents] = useDebouncedState(
    agents,
    MAX_DEBOUNCE_TIME,
    MAX_DEBOUNCE_TIME
  );

  useEffect(() => {
    if (!filterText) {
      setFilteredAgents(agents);
      return;
    }

    setFilteredAgents(
      agents.filter((agent) => agent.name.toLowerCase().includes(filterText.toLowerCase()))
    );
  }, [filterText]);

  return (
    <Layout>
      <LeftSection>
        <AgentsList />
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
            <div className="grid grid-cols-1 gap-x-4 gap-y-5 md:grid-cols-2 xl:grid-cols-3">
              {agents.length >= 1 && (
                <>
                  <Input
                    size="sm"
                    kind="default"
                    actionType="search"
                    placeholder="Search"
                    value={filterText}
                    onChange={(e) => setFilterText(e.target.value)}
                  />
                  <div className="col-span-2 hidden md:flex" />
                </>
              )}
              {'command r+'.includes(filterText.toLowerCase()) && (
                <DiscoverAgentCard
                  isBaseAgent
                  name="Command R+"
                  description="Review, understand and ask questions about  internal financial documents."
                />
              )}
              {filteredAgents?.map((agent) => (
                <DiscoverAgentCard
                  key={agent.name}
                  description={agent.description ?? undefined}
                  name={agent.name}
                  id={agent.id}
                />
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
