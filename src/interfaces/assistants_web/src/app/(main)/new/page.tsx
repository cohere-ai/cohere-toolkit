import { Metadata } from 'next';

import { CreateAgent } from './CreateAgent';

export const metadata: Metadata = {
  title: 'New Assistant',
};

const NewAssistantPage: React.FC = () => {
  return <CreateAgent />;
};

export default NewAssistantPage;
