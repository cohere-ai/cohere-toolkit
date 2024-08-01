'use client';

import { AgentsList } from '@/components/Agents/AgentsList';
import ConversationListPanel from '@/components/ConversationList/ConversationListPanel';
import { AgentsLayout, Layout } from '@/components/Layout';
import { useExperimentalFeatures } from '@/hooks/experimentalFeatures';

export const MainLayout: React.FC<React.PropsWithChildren> = ({ children }) => {
  const { data: experimentalFeatures } = useExperimentalFeatures();
  const isAgentsModeOn = !!experimentalFeatures?.USE_AGENTS_VIEW;

  if (isAgentsModeOn) {
    return <AgentsLayout showSettingsDrawer leftElement={<AgentsList />} mainElement={children} />;
  }

  return <Layout leftDrawerElement={<ConversationListPanel />} mainElement={children} />;
};
