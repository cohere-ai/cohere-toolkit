import { cn } from '@/utils/cn';

const BG_COLOR_LIST = [
  'bg-green-500 dark:bg-green-500',
  'bg-coral-600 dark:bg-coral-600',
  'bg-evolved-quartz-500 dark:bg-evolved-quartz-500',
  'bg-evolved-mushroom-500 dark:bg-evolved-mushroom-500',
  'bg-evolved-green-500 dark:bg-evolved-green-500',
  'bg-mushroom-700 dark:bg-mushroom-700',
];

const TEXT_COLOR_LIST = [
  'text-green-500 dark:text-green-500 fill-green-500 dark:fill-green-500',
  'text-coral-600 dark:text-coral-600 fill-coral-600 dark:fill-coral-600',
  'text-evolved-quartz-500 dark:text-evolved-quartz-500 fill-evolved-quartz-500 dark:fill-evolved-quartz-500',
  'text-evolved-mushroom-500 dark:text-evolved-mushroom-500 fill-evolved-mushroom-500 dark:fill-evolved-mushroom-500',
  'text-evolved-green-500 dark:text-evolved-green-500 fill-evolved-green-500 dark:fill-evolved-green-500',
  'text-mushroom-700 dark:text-mushroom-700 fill-mushroom-700 dark:fill-mushroom-700',
];

const FILL_COLOR_LIST = [
  'fill-green-500 dark:fill-green-500',
  'fill-coral-600 dark:fill-coral-600',
  'fill-evolved-quartz-500 dark:fill-evolved-quartz-500',
  'fill-evolved-mushroom-500 dark:fill-evolved-mushroom-500',
  'fill-evolved-green-500 dark:fill-evolved-green-500',
  'fill-mushroom-700 dark:fill-mushroom-700',
];

const CONTRAST_TEXT_COLOR_LIST = [
  'text-marble-950 dark:text-marble-950 fill-marble-950 dark:fill-marble-950', // green 500
  'text-volcanic-100 dark:text-volcanic-100 fill-volcanic-100 dark:fill-volcanic-100', // coral 600
  'text-marble-950 dark:text-marble-950 fill-marble-950 dark:fill-marble-950', // evolved quartz 500
  'text-volcanic-100 dark:text-volcanic-100 fill-volcanic-100 dark:fill-volcanic-100', // evolved mushroom 500
  'text-volcanic-100 dark:text-volcanic-100 fill-volcanic-100 dark:fill-volcanic-100', // evolved green 500
  'text-mushroom-300 dark:text-mushroom-300 fill-mushroom-300 dark:fill-mushroom-300', // mushroom 700
];

const BORDER_COLOR_LIST = [
  'border-green-500 dark:border-green-500',
  'border-coral-600 dark:border-coral-600',
  'border-evolved-quartz-500 dark:border-evolved-quartz-500',
  'border-evolved-mushroom-500 dark:border-evolved-mushroom-500',
  'border-evolved-green-500 dark:border-evolved-green-500',
  'border-mushroom-700 dark:border-mushroom-700',
];

const DEFAULT_BG_COLOR = 'bg-evolved-blue-500';
const DEFAULT_TEXT_COLOR = 'text-evolved-blue-500 dark:text-blue-700';
const DEFAULT_FILL_COLOR = 'fill-evolved-blue-500 dark:fill-blue-700';
const DEFAULT_CONTRAST_TEXT_COLOR = 'text-blue-800 dark:text-blue-800';
const DEFAULT_BORDER_COLOR = 'border-evolved-blue-500';

/**
 * @description Get a color from the Cohere color palette, when no index is provided, a random color is returned
 * @param id - id for generating a constant color in the palette
 * @param options - options for the color, text, border, or background
 * @param options.text - if true, returns a text color
 * @param options.fill - if true, returns a fill color
 * @param options.border - if true, returns a border color
 * @param options.background - if true, returns a background color
 * @param options.contrastText - if true, returns a contrast text color
 * @returns color from the Cohere color palette
 */
export const getCohereColor = (
  id: string | undefined,
  options: {
    text?: boolean;
    fill?: boolean;
    border?: boolean;
    background?: boolean;
    contrastText?: boolean;
  }
): string => {
  if (id === undefined) {
    const colors = [];
    if (options.text) {
      colors.push(DEFAULT_TEXT_COLOR);
    }
    if (options.fill) {
      colors.push(DEFAULT_FILL_COLOR);
    }
    if (options.border) {
      colors.push(DEFAULT_BORDER_COLOR);
    }
    if (options.background) {
      colors.push(DEFAULT_BG_COLOR);
    }
    if (options.contrastText) {
      colors.push(DEFAULT_CONTRAST_TEXT_COLOR);
    }
    return cn(colors);
  }

  const colors = [];
  if (options.text) {
    colors.push(TEXT_COLOR_LIST);
  }
  if (options.fill) {
    colors.push(FILL_COLOR_LIST);
  }
  if (options.border) {
    colors.push(BORDER_COLOR_LIST);
  }
  if (options.background) {
    colors.push(BG_COLOR_LIST);
  }
  if (options.contrastText) {
    colors.push(CONTRAST_TEXT_COLOR_LIST);
  }

  const idNumber = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const index = idNumber % TEXT_COLOR_LIST.length;
  return cn(colors.map((color) => color[index]));
};
