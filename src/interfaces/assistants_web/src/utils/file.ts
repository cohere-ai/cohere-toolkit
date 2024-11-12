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
 * Decode base64 text into utf-8.
 * @param text
 * @returns decoded text
 */
export const decodeBase64 = (text: string) => {
  return Buffer.from(text, 'base64').toString('utf-8');
};

/**
 * Map file extension to mime type.
 * @param extension
 * @returns mime type
 */
export const mapExtensionToMimeType = (extension: string) => {
  return (
    {
      ['csv']: 'text/csv',
      ['tsv']: 'text/tab-separated-values',
      ['html']: 'text/html',
      ['md']: 'text/markdown',
      ['ics']: 'text/calendar',
      ['doc']: 'application/msword',
      ['docx']: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      ['xlsx']: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      ['pptx']: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      ['json']: 'application/json',
      ['pdf']: 'application/pdf',
      ['epub']: 'application/epub+zip',
      ['parquet']: 'application/vnd.apache.parquet',
      ['png']: 'image/png',
      ['txt']: 'text/plain',
      ['zip']: 'application/zip',
    }[extension] || 'text/plain'
  );
};

/**
 * Map mime type to file extension.
 * @param mimeType
 * @returns extension
 */
export const mapMimeTypeToExtension = (mimeType: string) => {
  return (
    {
      ['text/csv']: 'csv',
      ['text/tab-separated-values']: 'tsv',
      ['text/html']: 'html',
      ['text/markdown']: 'md',
      ['text/calendar']: 'ics',
      ['application/msword']: 'doc',
      ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']: 'docx',
      ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']: 'xlsx',
      ['application/vnd.openxmlformats-officedocument.presentationml.presentation']: 'pptx',
      ['application/json']: 'json',
      ['application/pdf']: 'pdf',
      ['application/epub+zip']: 'epub',
      ['application/vnd.apache.parquet']: 'parquet',
      ['image/png']: 'png',
      ['text/plain']: 'txt',
      ['application/zip']: 'zip',
    }[mimeType] || 'txt'
  );
};
