'use client';

import { HotKeysProvider } from '@/components/Shared/HotKeys/HotKeysProvider';
import { useChatHotKeys } from '@/hooks/actions';

export const HotKeys: React.FC = () => {
  const chatHotKeys = useChatHotKeys();
  return <HotKeysProvider customHotKeys={chatHotKeys} />;
};
