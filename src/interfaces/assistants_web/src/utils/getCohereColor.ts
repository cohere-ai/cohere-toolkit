const BG_COLOR_LIST = [
  'bg-green-500 dark:bg-green-500',
  'bg-coral-600 dark:bg-coral-600',
  'bg-evolved-quartz-500 dark:bg-evolved-quartz-500',
  'bg-evolved-mushroom-500 dark:bg-evolved-mushroom-500',
  'bg-evolved-green-500 dark:bg-evolved-green-500',
  'bg-evolved-blue-500 dark:bg-evolved-blue-500',
];

const TEXT_COLOR_LIST = [
  'text-green-500 dark:text-green-500',
  'text-coral-600 dark:text-coral-600',
  'text-evolved-quartz-500 dark:text-evolved-quartz-500',
  'text-evolved-mushroom-500 dark:text-evolved-mushroom-500',
  'text-evolved-green-500 dark:text-evolved-green-500',
  'text-evolved-blue-500 dark:text-evolved-blue-500',
];

const BORDER_COLOR_LIST = [
  'border-green-500 dark:border-green-500',
  'border-coral-600 dark:border-coral-600',
  'border-evolved-quartz-500 dark:border-evolved-quartz-500',
  'border-evolved-mushroom-500 dark:border-evolved-mushroom-500',
  'border-evolved-green-500 dark:border-evolved-green-500',
  'border-evolved-blue-500 dark:border-evolved-blue-500',
];

const DEFAULT_BG_COLOR = 'bg-mushroom-700';
const DEFAULT_TEXT_COLOR = 'text-mushroom-700';
const DEFAULT_BORDER_COLOR = 'border-mushroom-700';

/**
 * @description Get a color from the Cohere color palette, when no index is provided, a random color is returned
 * @param id - id for generating a constant color in the palette
 * @param options - options for the color, text, border, or background
 * @param options.text - if true, returns a text color
 * @param options.border - if true, returns a border color
 * @param options.background - if true, returns a background color
 * @returns color from the Cohere color palette
 */
export const getCohereColor = (
  id: string | undefined,
  options: { text?: boolean; border?: boolean; background?: boolean }
): string => {
  if (id === undefined) {
    const colors = [];
    if (options.text) {
      colors.push(DEFAULT_TEXT_COLOR);
    }
    if (options.border) {
      colors.push(DEFAULT_BORDER_COLOR);
    }
    if (options.background) {
      colors.push(DEFAULT_BG_COLOR);
    }
    return colors.join(' ');
  }

  const colors = [];
  if (options.text) {
    colors.push(TEXT_COLOR_LIST);
  }
  if (options.border) {
    colors.push(BORDER_COLOR_LIST);
  }
  if (options.background) {
    colors.push(BG_COLOR_LIST);
  }

  const idNumber = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const index = idNumber % TEXT_COLOR_LIST.length;
  return colors.map((color) => color[index]).join(' ');
};
