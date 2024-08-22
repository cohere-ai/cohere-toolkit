import { Metadata } from 'next';

import { DiscoverAgents } from './DiscoverAgents';

export const metadata: Metadata = {
  title: 'Discover Assistants',
};

const DiscoverAssistantPage: React.FC = () => {
  return <DiscoverAgents />;
};

export default DiscoverAssistantPage;
