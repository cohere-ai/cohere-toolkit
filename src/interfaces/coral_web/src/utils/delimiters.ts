/**
 * Simple helper to check if a string has common delimiters. For now this is only looking for commas.
 */
export const hasCommonDelimiters = (str: string): boolean => {
  return str.includes(',');
};
