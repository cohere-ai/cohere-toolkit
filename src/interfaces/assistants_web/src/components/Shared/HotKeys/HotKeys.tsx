'use client';

import { HotKeysProvider } from '@/components/Shared/HotKeys/HotKeysProvider';
import { useConversationHotKeys, useLayoutHotKeys } from '@/hooks/actions';

export const HotKeys: React.FC = () => {
  const conversationHotKeys = useConversationHotKeys();
  const layoutHotKeys = useLayoutHotKeys();
  const hotKeys = [...conversationHotKeys, ...layoutHotKeys];
  return <HotKeysProvider hotKeys={hotKeys} />;
};
