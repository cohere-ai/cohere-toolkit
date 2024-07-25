import { Metadata } from 'next';
import { Suspense } from 'react';

import { CreateAgent } from '@/components/Agents/CreateAgent';
import { CollapsibleSection } from '@/components/CollapsibleSection';

export const metadata: Metadata = {
  title: 'New Assistant',
};

const NewAssistantPage: React.FC = () => {
  return (
    <Suspense>
      <CreateAgent />
    </Suspense>
  );
};

export default NewAssistantPage;
