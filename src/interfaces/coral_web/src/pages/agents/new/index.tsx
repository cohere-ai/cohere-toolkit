import { QueryClient, dehydrate } from '@tanstack/react-query';
import { GetServerSideProps, NextPage } from 'next';

import { CohereClient } from '@/cohere-client';
import { Layout, LeftSection, MainSection } from '@/components/Agents/Layout';
import { LeftPanel } from '@/components/Agents/LeftPanel';
import { appSSR } from '@/pages/_app';

type Props = {};

const AgentsNewPage: NextPage<Props> = () => {
  return (
    <Layout>
      <LeftSection>
        <LeftPanel />
      </LeftSection>
      <MainSection>Create a new agent</MainSection>
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
