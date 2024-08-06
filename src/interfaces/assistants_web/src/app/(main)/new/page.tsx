import { Metadata } from 'next';
import { Suspense } from 'react';

import { CreateAgent } from '@/components/Agents/CreateAgent';

export const metadata: Metadata = {
  title: 'New Assistant',
};

const NewAssistantPage: React.FC = () => {
  return (
    <Suspense>
      <div className="h-full w-full rounded-lg border border-marble-950 bg-marble-980 dark:border-volcanic-150 dark:bg-volcanic-100">
        <CreateAgent />
      </div>
    </Suspense>
  );
};

export default NewAssistantPage;
