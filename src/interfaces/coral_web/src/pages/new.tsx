import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';

import { CohereClient } from '@/cohere-client';
import { AgentsList } from '@/components/Agents/AgentsList';
import { CreateAgent } from '@/components/Agents/CreateAgent';
import { AgentsLayout, LeftSection, MainSection } from '@/components/Layout';
import { ProtectedPage } from '@/components/ProtectedPage';
import { appSSR } from '@/pages/_app';

type Props = {};

const AgentsNewPage: NextPage<Props> = () => {
  return (
    <ProtectedPage>
      <AgentsLayout>
        <LeftSection>
          <AgentsList />
        </LeftSection>
        <MainSection>
          <CreateAgent />
        </MainSection>
      </AgentsLayout>
    </ProtectedPage>
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
