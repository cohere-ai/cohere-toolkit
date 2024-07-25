import { cn } from '@/utils/cn';

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

const CONTRAST_TEXT_COLOR_LIST = [
  'text-marble-950 dark:text-marble-950', // green 500
  'text-volcanic-100 dark:text-volcanic-100', // coral 600
  'text-marble-950 dark:text-marble-950', // evolved quartz 500
  'text-volcanic-100 dark:text-volcanic-100', // evolved mushroom 500
  'text-volcanic-100 dark:text-volcanic-100', // evolved green 500
  'text-marble-950 dark:text-marble-950', // evolved blue 500
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
const DEFAULT_TEXT_COLOR = 'text-mushroom-500 dark:text-mushroom-700';
const DEFAULT_CONTRAST_TEXT_COLOR = 'text-mushroom-300 dark:text-mushroom-300';
const DEFAULT_BORDER_COLOR = 'border-mushroom-700';
/**
 * @description Get a color from the Cohere color palette, when no index is provided, a random color is returned
 * @param id - id for generating a constant color in the palette
 * @param background - if true, returns a background color, otherwise returns a text color
 * @returns color from the Cohere color palette
 */
export const getCohereColor = (
  id?: string,
  options: { background?: boolean } = { background: true }
) => {
  const COLOR_LIST = options?.background ? BG_COLOR_LIST : TEXT_COLOR_LIST;
  if (id === undefined) {
    const randomIndex = Math.floor(Math.random() * COLOR_LIST.length);

    return COLOR_LIST[randomIndex];
  }
  const idNumber = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const index = idNumber % COLOR_LIST.length;
  return COLOR_LIST[index];
};
