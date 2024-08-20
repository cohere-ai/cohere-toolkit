'use client';

import { HotKeysProvider } from '@/components/Shared/HotKeys/HotKeysProvider';
import { useChatHotKeys, useLayoutHotKeys } from '@/hooks/actions';

export const HotKeys: React.FC = () => {
  const chatHotKeys = useChatHotKeys();
  const layoutHotKeys = useLayoutHotKeys();
  const hotKeys = [...chatHotKeys, ...layoutHotKeys];
  return <HotKeysProvider hotKeys={hotKeys} />;
};
