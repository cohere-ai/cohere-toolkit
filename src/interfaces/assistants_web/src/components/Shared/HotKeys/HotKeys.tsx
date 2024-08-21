'use client';

import { HotKeysProvider } from '@/components/Shared/HotKeys/HotKeysProvider';
import {
  useAssistantHotKeys,
  useConversationHotKeys,
  useSettingsHotKeys,
  useViewHotKeys,
} from '@/hooks/actions';

export const HotKeys: React.FC = () => {
  const conversationHotKeys = useConversationHotKeys();
  const viewHotKeys = useViewHotKeys();
  const settingsHotKeys = useSettingsHotKeys();
  const assistantHotKeys = useAssistantHotKeys({ displayRecentAgentsInDialog: false });
  const hotKeys = [...conversationHotKeys, ...viewHotKeys, ...assistantHotKeys, ...settingsHotKeys];

  return <HotKeysProvider hotKeys={hotKeys} />;
};
