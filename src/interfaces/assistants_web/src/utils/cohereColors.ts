import { COHERE_BRANDED_COLORS } from '@/constants';
import { cn } from '@/utils/cn';

/** !IMPORTANT: Order of colors must match the order of COHERE_BRANDED_COLORS
 * DEFAULT COLOR: evolved-blue
 * 1. green
 * 2. coral
 * 3. evolved-quartz
 * 4. evolved-mushroom
 * 5. evolved-green
 * 6. mushroom
 */

/**
 * THEMES
 */

const COHERE_THEMES_MAP: { default: COHERE_BRANDED_COLORS; branded: COHERE_BRANDED_COLORS[] } = {
  default: 'evolved-blue',
  branded: ['green', 'coral', 'evolved-quartz', 'evolved-mushroom', 'evolved-green', 'mushroom'],
};

/**
 * HOVER CLASSES
 */

const HOVER_BG_COLOR_LIST = [
  'hover:bg-green-500 hover:dark:bg-green-500',
  'hover:bg-coral-600 hover:dark:bg-coral-600',
  'hover:bg-evolved-quartz-500 hover:dark:bg-evolved-quartz-500',
  'hover:bg-evolved-mushroom-500 hover:dark:bg-evolved-mushroom-500',
  'hover:bg-evolved-green-500 hover:dark:bg-evolved-green-500',
  'hover:bg-mushroom-700 hover:dark:bg-mushroom-700',
];

const HOVER_TEXT_COLOR_LIST = [
  'hover:text-green-500 hover:dark:text-green-500 hover:fill-green-500 hover:dark:fill-green-500',
  'hover:text-coral-600 hover:dark:text-coral-600 hover:fill-coral-600 hover:dark:fill-coral-600',
  'hover:text-evolved-quartz-500 hover:dark:text-evolved-quartz-500 hover:fill-evolved-quartz-500 hover:dark:fill-evolved-quartz-500',
  'hover:text-evolved-mushroom-500 hover:dark:text-evolved-mushroom-500 hover:fill-evolved-mushroom-500 hover:dark:fill-evolved-mushroom-500',
  'hover:text-evolved-green-500 hover:dark:text-evolved-green-500 hover:fill-evolved-green-500 hover:dark:fill-evolved-green-500',
  'hover:text-mushroom-700 hover:dark:text-mushroom-700 hover:fill-mushroom-700 hover:dark:fill-mushroom-700',
];

const HOVER_FILL_COLOR_LIST = [
  'hover:fill-green-500 hover:dark:fill-green-500',
  'hover:fill-coral-600 hover:dark:fill-coral-600',
  'hover:fill-evolved-quartz-500 hover:dark:fill-evolved-quartz-500',
  'hover:fill-evolved-mushroom-500 hover:dark:fill-evolved-mushroom-500',
  'hover:fill-evolved-green-500 hover:dark:fill-evolved-green-500',
  'hover:fill-mushroom-700 hover:dark:fill-mushroom-700',
];

const HOVER_CONTRAST_TEXT_COLOR_LIST = [
  'hover:text-marble-950 dark:hover:text-marble-950 hover:fill-marble-950 dark:hover:fill-marble-950', // green 500
  'hover:text-volcanic-100 dark:hover:text-volcanic-100 hover:fill-volcanic-100 dark:hover:fill-volcanic-100', // coral 600
  'hover:text-marble-950 dark:hover:text-marble-950 hover:fill-marble-950 dark:hover:fill-marble-950', // evolved quartz 500
  'hover:text-volcanic-100 dark:hover:text-volcanic-100 hover:fill-volcanic-100 dark:hover:fill-volcanic-100', // evolved mushroom 500
  'hover:text-volcanic-100 dark:hover:text-volcanic-100 hover:fill-volcanic-100 dark:hover:fill-volcanic-100', // evolved green 500
  'hover:text-mushroom-300 dark:hover:text-mushroom-300 hover:fill-mushroom-300 dark:hover:fill-mushroom-300', // mushroom 700
];

const HOVER_BORDER_COLOR_LIST = [
  'hover:border-green-500 dark:hover:border-green-500',
  'hover:border-coral-600 dark:hover:border-coral-600',
  'hover:border-evolved-quartz-500 dark:hover:border-evolved-quartz-500',
  'hover:border-evolved-mushroom-500 dark:hover:border-evolved-mushroom-500',
  'hover:border-evolved-green-500 dark:hover:border-evolved-green-500',
  'hover:border-mushroom-700 dark:hover:border-mushroom-700',
];

/**
 * END OF DECORATOR CLASSES
 */

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

// DEFAULT COLORS
const DEFAULT_BG_COLOR = 'bg-evolved-blue-500 dark:bg-evolved-blue-500';
const DEFAULT_TEXT_COLOR = 'text-evolved-blue-500 dark:text-blue-700';
const DEFAULT_FILL_COLOR = 'fill-evolved-blue-500 dark:fill-blue-700';
const DEFAULT_CONTRAST_TEXT_COLOR = 'text-blue-800 dark:text-blue-800';
const DEFAULT_BORDER_COLOR = 'border-evolved-blue-500 dark:border-blue-500';
const HOVER_DEFAULT_BG_COLOR = 'hover:bg-evolved-blue-500 dark:hover:bg-evolved-blue-500';
const HOVER_DEFAULT_TEXT_COLOR = 'hover:text-evolved-blue-500 dark:hover:text-blue-700';
const HOVER_DEFAULT_FILL_COLOR = 'hover:fill-evolved-blue-500 dark:hover:fill-blue-700';
const HOVER_DEFAULT_CONTRAST_TEXT_COLOR = 'hover:text-blue-800 dark:hover:text-blue-800';
const HOVER_DEFAULT_BORDER_COLOR = 'hover:border-evolved-blue-500 dark:hover:border-blue-500';

const COLORS_MAP = {
  text: {
    default: DEFAULT_TEXT_COLOR,
    defaultHover: HOVER_DEFAULT_TEXT_COLOR,
    brandedHover: HOVER_TEXT_COLOR_LIST,
    branded: TEXT_COLOR_LIST,
  },
  fill: {
    default: DEFAULT_FILL_COLOR,
    defaultHover: HOVER_DEFAULT_FILL_COLOR,
    brandedHover: HOVER_FILL_COLOR_LIST,
    branded: FILL_COLOR_LIST,
  },
  border: {
    default: DEFAULT_BORDER_COLOR,
    defaultHover: HOVER_DEFAULT_BORDER_COLOR,
    brandedHover: HOVER_BORDER_COLOR_LIST,
    branded: BORDER_COLOR_LIST,
  },
  background: {
    default: DEFAULT_BG_COLOR,
    defaultHover: HOVER_DEFAULT_BG_COLOR,
    brandedHover: HOVER_BG_COLOR_LIST,
    branded: BG_COLOR_LIST,
  },
  contrastText: {
    default: DEFAULT_CONTRAST_TEXT_COLOR,
    defaultHover: HOVER_DEFAULT_CONTRAST_TEXT_COLOR,
    brandedHover: HOVER_CONTRAST_TEXT_COLOR_LIST,
    branded: CONTRAST_TEXT_COLOR_LIST,
  },
};

/**
 * @description Get a color from the Cohere color palette, when no index is provided, a random color is returned
 * @param id - id for generating a constant color in the palette
 * @param options - options for the color, text, border, or background
 * @param options.text - if true, returns a text color
 * @param options.fill - if true, returns a fill color
 * @param options.border - if true, returns a border color
 * @param options.background - if true, returns a background color
 * @param options.contrastText - if true, returns a contrast text color
 * @param variant.hover - if true, returns a hover color
 * @param variant.theme - if true, returns the theme name
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
  },
  variant?: { hover?: boolean }
): string => {
  if (id === undefined) {
    const colors = [];

    if (options.text) {
      if (variant?.hover) {
        colors.push(COLORS_MAP.text.defaultHover);
      } else {
        colors.push(COLORS_MAP.text.default);
      }
    }
    if (options.fill) {
      if (variant?.hover) {
        colors.push(COLORS_MAP.fill.defaultHover);
      } else {
        colors.push(COLORS_MAP.fill.default);
      }
    }
    if (options.border) {
      if (variant?.hover) {
        colors.push(COLORS_MAP.border.defaultHover);
      } else {
        colors.push(COLORS_MAP.border.default);
      }
    }
    if (options.background) {
      if (variant?.hover) {
        colors.push(COLORS_MAP.background.defaultHover);
      } else {
        colors.push(COLORS_MAP.background.default);
      }
    }
    if (options.contrastText) {
      if (variant?.hover) {
        colors.push(COLORS_MAP.contrastText.defaultHover);
      } else {
        colors.push(COLORS_MAP.contrastText.default);
      }
    }
    return cn(colors);
  }

  const colors = [];
  if (options.text) {
    if (variant?.hover) {
      colors.push(COLORS_MAP.text.brandedHover);
    } else {
      colors.push(COLORS_MAP.text.branded);
    }
  }
  if (options.fill) {
    if (variant?.hover) {
      colors.push(COLORS_MAP.fill.brandedHover);
    } else {
      colors.push(COLORS_MAP.fill.branded);
    }
  }
  if (options.border) {
    if (variant?.hover) {
      colors.push(COLORS_MAP.border.brandedHover);
    } else {
      colors.push(COLORS_MAP.border.branded);
    }
  }
  if (options.background) {
    if (variant?.hover) {
      colors.push(COLORS_MAP.background.brandedHover);
    } else {
      colors.push(COLORS_MAP.background.branded);
    }
  }
  if (options.contrastText) {
    if (variant?.hover) {
      colors.push(COLORS_MAP.contrastText.brandedHover);
    } else {
      colors.push(COLORS_MAP.contrastText.branded);
    }
  }

  const idNumber = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const index = idNumber % TEXT_COLOR_LIST.length;
  return cn(colors.map((color) => color[index]));
};

/**
 * @description Get a theme color from the Cohere color palette, when no index is provided, a random color is returned
 * @param id - id for generating a constant color in the palette
 * @returns color from the Cohere color palette
 */
export const getCohereTheme = (id: string | undefined): COHERE_BRANDED_COLORS => {
  if (id === undefined) {
    return COHERE_THEMES_MAP.default;
  } else {
    const idNumber = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const index = idNumber % COHERE_THEMES_MAP.branded.length;
    return COHERE_THEMES_MAP.branded[index];
  }
};
