import { FILE_TOOL_CATEGORY, ManagedTool } from '@/cohere-client';

/**
 * Gets the file extension from its name.
 * @param filename
 * @returns file extension e.g. .pdf or .txt
 */
export const getFileExtension = (filename: string): string | undefined => {
  const ext = filename.split('.').pop();
  return ext ? `.${ext}` : undefined;
};

/**
 * Generate a random number between min and max.
 * @param min
 * @param max
 * @returns random number between min and max
 */
export const getRandomNumberInBetween = (min: number, max: number) => {
  return Math.floor(Math.random() * (max - min) + min);
};

/**
 * Estimate the upload time in ms based on the file size.
 * This equation estimates upload speed using a least squares regression of some existing data points with various file sizes.
 * 18MB, 60 seconds,
 * 12MB, 45 seconds,
 * 8.7MB, 32 seconds,
 * 6MB, 23 seconds,
 * 4.3MB, 12 seconds,
 * 1.9MB, 4.8 seconds,
 * 1.1MB, 3 seconds,
 * 350KB, 1.51 seconds
 * @param fileSizeInBytes
 * @returns random number between min and max
 */
export const getFileUploadTimeEstimateInMs = (fileSizeInBytes: number) => {
  // This equation estimates upload speed based on some existing data points with various file sizes.
  return ((3.51 * fileSizeInBytes) / 1000000 - 0.3) * 1000;
};

/**
 * @description Determines if a tool is the default file loader tool.
 */
export const isDefaultFileLoaderTool = (t: ManagedTool) =>
  t.category === FILE_TOOL_CATEGORY && t.is_visible;
