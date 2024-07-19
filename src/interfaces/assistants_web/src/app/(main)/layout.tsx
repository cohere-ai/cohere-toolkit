'use client';

import { NextPage } from 'next';

import { AgentsList } from '@/components/Agents/AgentsList';
import { Layout, LeftSection, MainSection } from '@/components/Layout';
import { ProtectedPage } from '@/components/ProtectedPage';

const MainLayout: NextPage<React.PropsWithChildren> = ({ children }) => {
  return (
    <ProtectedPage>
      <Layout showSettingsDrawer>
        <LeftSection>
          <AgentsList />
        </LeftSection>
        <MainSection>{children}</MainSection>
      </Layout>
    </ProtectedPage>
  );
};

export default MainLayout;
