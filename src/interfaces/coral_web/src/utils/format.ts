import { DYNAMIC_STRINGS } from '@/constants/strings';
import { pluralize } from '@/utils';

const WEEK_IN_MILLIS = 7 * 24 * 60 * 60 * 1000;

/**
 * Returns the number of weeks ago and a string representation of the number of weeks ago.
 */
export const getWeeksAgo = (date: string | Date): { weeksAgo: number; weeksAgoStr: string } => {
  const now = new Date();
  const diffInMillis = now.getTime() - new Date(date).getTime();
  const weeksAgo = Math.floor(diffInMillis / WEEK_IN_MILLIS);
  const weeksAgoStr = DYNAMIC_STRINGS.weeksAgo(weeksAgo);

  return {
    weeksAgo,
    weeksAgoStr,
  };
};

/**
 * Converts a file size in megabytes to bytes
 */
export const fileSizeToBytes = (size: number): number => {
  return size * 1024 * 1024;
};

/**
 * Converts a file size in bytes to megabytes
 * */
export const fileSizeToMB = (size: number): number => {
  return size / 1024 / 1024;
};

/**
 * Returns file size with units e.g. 10 bytes, 10 KB, 10 MB
 * Only works for bytes, KB, and MB
 * Add additional units as needed
 */
export const formatFileSize = (bytes: number): string => {
  const kb = 1024;
  const mb = kb * 1024;

  if (bytes < kb) {
    return DYNAMIC_STRINGS.numBytes(bytes);
  } else if (bytes < mb) {
    return DYNAMIC_STRINGS.numKB((bytes / kb).toFixed(1));
  } else {
    return DYNAMIC_STRINGS.numMB((bytes / mb).toFixed(1));
  }
};
