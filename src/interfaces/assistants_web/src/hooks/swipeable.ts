import { useEffect } from 'react';
import { useSwipeable as useSwipe } from 'react-swipeable';

import { useSettingsStore } from '@/stores';

export const useSwipeable = () => {
  const { setAgentsLeftSidePanelOpen, setAgentsRightSidePanelOpen } = useSettingsStore();
  const { ref } = useSwipe({
    onSwipedLeft: ({}) => {
      setAgentsLeftSidePanelOpen(false);
      setAgentsRightSidePanelOpen(true);
    },
    onSwipedRight: ({}) => {
      setAgentsRightSidePanelOpen(false);
      setAgentsLeftSidePanelOpen(true);
    },
  });

  useEffect(() => {
    ref(window.document as unknown as HTMLElement);
    return () => ref(null);
  }, [ref]);
};
