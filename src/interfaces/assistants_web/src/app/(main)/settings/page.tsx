import { Metadata } from 'next';
import { Suspense } from 'react';

import { Settings } from '@/components/Agents/Settings';

export const metadata: Metadata = {
  title: 'Settings',
};

const SettingsPage: React.FC = () => {
  return (
    <Suspense>
      <Settings />
    </Suspense>
  );
};

export default SettingsPage;
