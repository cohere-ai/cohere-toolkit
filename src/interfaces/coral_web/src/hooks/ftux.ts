import { useLocalStorageValue } from '@react-hookz/web';
import { usePathname } from 'next/navigation';

import { LOCAL_STORAGE_KEYS } from '@/constants';

export enum WelcomeGuideStep {
  ONE = '1',
  TWO = '2',
  THREE = '3',
  DONE = 'done',
}

/**
 * @description returns the current welcome guide state and methods to update it.
 * We store the state in local storage so that it persists across page refreshes.
 */
export const useWelcomeGuideState = () => {
  const { value: welcomeGuideState, set: setWelcomeGuideState } = useLocalStorageValue(
    LOCAL_STORAGE_KEYS.welcomeGuideState,
    {
      defaultValue: WelcomeGuideStep.ONE,
      initializeWithValue: false,
    }
  );

  return {
    welcomeGuideState,
    setWelcomeGuideState,
    progressWelcomeGuideStep: () => {
      if (welcomeGuideState === WelcomeGuideStep.ONE) {
        setWelcomeGuideState(WelcomeGuideStep.TWO);
      } else if (welcomeGuideState === WelcomeGuideStep.TWO) {
        setWelcomeGuideState(WelcomeGuideStep.THREE);
      } else if (welcomeGuideState === WelcomeGuideStep.THREE) {
        setWelcomeGuideState(WelcomeGuideStep.DONE);
      }
    },
    finishWelcomeGuide: () => {
      setWelcomeGuideState(WelcomeGuideStep.DONE);
    },
  };
};

/**
 * @description determines whether to show the welcome guide flow. The flow
 * should not show on pages outside of the new chat page.
 */
export const useShowWelcomeGuide = () => {
  const pathname = usePathname();
  const { welcomeGuideState } = useWelcomeGuideState();

  return pathname === '/' && welcomeGuideState !== WelcomeGuideStep.DONE;
};

/**
 * @description determines whether to show the Tools info box. The info box
 * should not show unless the welcome tooltip guides are completed.
 */
export const useShowToolsInfoBox = () => {
  const { welcomeGuideState } = useWelcomeGuideState();
  const { value: hasDismissed, set } = useLocalStorageValue(
    LOCAL_STORAGE_KEYS.welcomeGuideInfoBox,
    {
      defaultValue: false,
      initializeWithValue: true,
    }
  );

  return {
    show: welcomeGuideState === WelcomeGuideStep.DONE && !hasDismissed,
    onDismissed: () => set(true),
  };
};
