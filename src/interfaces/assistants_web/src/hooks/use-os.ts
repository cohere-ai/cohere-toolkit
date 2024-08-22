// A hook that returns the current OS
// macOS, Windows, Linux, iOS, Android, Chrome OS, etc.
import { useMemo } from 'react';

type OS = 'macOS' | 'Windows' | 'Linux' | 'iOS' | 'Android' | 'Chrome OS' | 'Unknown';

export const useOS = () => {
  return useMemo<OS>(() => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    if (userAgent.indexOf('mac os') !== -1) {
      return 'macOS';
    } else if (userAgent.indexOf('win') !== -1) {
      return 'Windows';
    } else if (userAgent.indexOf('linux') !== -1) {
      return 'Linux';
    } else if (userAgent.indexOf('iphone') !== -1) {
      return 'iOS';
    } else if (userAgent.indexOf('android') !== -1) {
      return 'Android';
    } else if (userAgent.indexOf('cros') !== -1) {
      return 'Chrome OS';
    } else {
      return 'Unknown';
    }
  }, []);
};
