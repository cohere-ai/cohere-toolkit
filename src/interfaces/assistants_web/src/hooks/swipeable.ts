import { useEffect } from 'react';
import { useSwipeable as useSwipe } from 'react-swipeable';

import { useSettingsStore } from '@/stores';

export const useSwipeable = () => {
  const { setLeftPanelOpen, setRightPanelOpen } = useSettingsStore();
  const { ref } = useSwipe({
    onSwipedLeft: ({}) => {
      setLeftPanelOpen(false);
      setRightPanelOpen(true);
    },
    onSwipedRight: ({}) => {
      setLeftPanelOpen(true);
      setRightPanelOpen(false);
    },
  });

  useEffect(() => {
    ref(window.document as unknown as HTMLElement);
    return () => ref(null);
  }, [ref]);
};
