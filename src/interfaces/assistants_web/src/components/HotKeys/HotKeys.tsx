'use client';

import { HotKeysProvider } from '@/components/HotKeys';
import { useAssistantHotKeys } from '@/components/HotKeys/hotkeys/assistants';
import { useConversationHotKeys } from '@/components/HotKeys/hotkeys/conversation';
import { useSearchHotKeys } from '@/components/HotKeys/hotkeys/search';
import { useSettingsHotKeys } from '@/components/HotKeys/hotkeys/settings';
import { useViewHotKeys } from '@/components/HotKeys/hotkeys/view';

export const HotKeys: React.FC = () => {
  const searchHotKeys = useSearchHotKeys();
  const conversationHotKeys = useConversationHotKeys();
  const viewHotKeys = useViewHotKeys();
  const settingsHotKeys = useSettingsHotKeys();
  const assistantHotKeys = useAssistantHotKeys({ displayRecentAgentsInDialog: false });
  const hotKeys = [
    ...searchHotKeys,
    ...conversationHotKeys,
    ...viewHotKeys,
    ...assistantHotKeys,
    ...settingsHotKeys,
  ];

  return <HotKeysProvider hotKeys={hotKeys} />;
};
