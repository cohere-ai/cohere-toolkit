'use client';

import { NextPage } from 'next';

import { AgentsList } from '@/components/Agents/AgentsList';
import ConversationListPanel from '@/components/ConversationList/ConversationListPanel';
import { AgentsLayout, Layout, LeftSection, MainSection } from '@/components/Layout';
import { ProtectedPage } from '@/components/ProtectedPage';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';

const MainLayout: NextPage<React.PropsWithChildren> = ({ children }) => {
  const { data: experimentalFeatures } = useExperimentalFeatures();
  const isAgentsModeOn = !!experimentalFeatures?.USE_AGENTS_VIEW;

  if (isAgentsModeOn) {
    return (
      <ProtectedPage>
        <AgentsLayout showSettingsDrawer>
          <LeftSection>
            <AgentsList />
          </LeftSection>
          <MainSection>{children}</MainSection>
        </AgentsLayout>
      </ProtectedPage>
    );
  }

  return (
    <ProtectedPage>
      <Layout>
        <LeftSection>
          <ConversationListPanel />
        </LeftSection>
        <MainSection>{children}</MainSection>
      </Layout>
    </ProtectedPage>
  );
};

export default MainLayout;
