import { NextPage } from 'next';

import { AgentsList } from '@/components/Agents/AgentsList';
import { Layout } from '@/components/Layout';

const MainLayout: NextPage<React.PropsWithChildren> = ({ children }) => {
  return <Layout showSettingsDrawer leftElement={<AgentsList />} mainElement={children} />;
};

export default MainLayout;
