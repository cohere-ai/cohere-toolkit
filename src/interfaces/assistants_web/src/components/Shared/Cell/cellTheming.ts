export type CellKind = 'default' | 'outline';
export type CellTheme =
  | 'volcanic'
  | 'volcanicAlt'
  | 'green'
  | 'greenDark'
  | 'greenAlt'
  | 'primary'
  | 'primaryLight'
  | 'primaryDark'
  | 'gray'
  | 'grayDark'
  | 'marble'
  | 'marbleDark'
  | 'secondary'
  | 'secondaryDark'
  | 'danger'
  | 'dangerDark'
  | 'transparent'
  | 'volcanicLight'
  | 'blue'
  | 'blueDark'
  | 'quartz'
  | 'quartzAlt';
export type CellSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

/*
 * The theming process is unable to be set up more dynamically due to limitations with Tailwind's class detection
 * Details: https://tailwindcss.com/docs/content-configuration#class-detection-in-depth
 *
 * If you need a new cell color, please set it up in the THEME_CLASSES mapping, for both 'outline' and 'default' versions of the cell
 */

interface CellThemes {
  [themeName: string]: {
    default: {
      bg: string;
      fill: string;
      text: string;
    };
    outline: {
      text: string;
      stroke: string;
      outlineFill: string;
      fill: string;
      bg: string;
    };
  };
}

export const THEME_CLASSES: CellThemes = {
  volcanic: {
    default: {
      bg: 'bg-volcanic-100',
      fill: 'fill-volcanic-100',
      text: 'text-white',
    },
    outline: {
      text: 'text-volcanic-100',
      stroke: 'stroke-volcanic-100',
      outlineFill: 'fill-volcanic-100',
      fill: 'fill-marble-1000',
      bg: 'bg-marble-1000',
    },
  },
  volcanicAlt: {
    default: {
      bg: 'bg-marble-1000',
      fill: 'fill-marble-1000',
      text: 'text-volcanic-100',
    },
    outline: {
      text: 'bg-volcanic-100',
      stroke: 'stroke-marble-1000',
      outlineFill: 'fill-marble-1000',
      fill: 'fill-volcanic-100',
      bg: 'text-white',
    },
  },
  primary: {
    default: {
      bg: 'bg-coral-700',
      fill: 'fill-coral-700',
      text: 'text-white',
    },
    outline: {
      text: 'text-volcanic-100',
      stroke: 'stroke-coral-800',
      outlineFill: 'fill-coral-800',
      fill: 'fill-coral-900',
      bg: 'bg-coral-900',
    },
  },
  primarylLight: {
    default: {
      bg: 'bg-coral-800',
      fill: 'fill-coral-800',
      text: 'text-white',
    },
    outline: {
      text: 'text-volcanic-100',
      stroke: 'stroke-coral-800',
      outlineFill: 'fill-coral-800',
      fill: 'fill-coral-900',
      bg: 'bg-coral-900',
    },
  },
  primaryDark: {
    default: {
      bg: 'bg-coral-700',
      fill: 'fill-coral-700',
      text: 'text-white',
    },
    outline: {
      text: 'text-coral-700',
      stroke: 'stroke-coral-700',
      outlineFill: 'fill-coral-700',
      fill: 'fill-coral-800',
      bg: 'bg-coral-800',
    },
  },
  green: {
    default: {
      bg: 'bg-green-250',
      fill: 'fill-green-250',
      text: 'text-white',
    },
    outline: {
      text: 'text-green-150',
      stroke: 'stroke-green-600',
      outlineFill: 'fill-green-600',
      fill: 'fill-green-950',
      bg: 'bg-green-950',
    },
  },
  greenDark: {
    default: {
      bg: 'bg-green-150',
      fill: 'fill-green-150',
      text: 'text-white',
    },
    outline: {
      text: 'text-green-150',
      stroke: 'stroke-green-150',
      outlineFill: 'fill-green-250',
      fill: 'fill-green-900',
      bg: 'bg-green-900',
    },
  },
  greenAlt: {
    default: {
      bg: 'bg-green-250',
      fill: 'fill-green-250',
      text: 'text-white',
    },
    outline: {
      text: 'text-green-250',
      stroke: 'stroke-green-250',
      outlineFill: 'fill-green-250',
      fill: 'fill-marble-1000',
      bg: 'bg-marble-1000',
    },
  },
  gray: {
    default: {
      bg: 'bg-marble-950',
      fill: 'fill-marble-950',
      text: 'text-volcanic-400',
    },
    outline: {
      text: 'text-volcanic-500',
      stroke: 'stroke-volcanic-500',
      outlineFill: 'fill-volcanic-500',
      fill: 'fill-marble-950',
      bg: 'bg-marble-950',
    },
  },
  grayDark: {
    default: {
      bg: 'bg-volcanic-500',
      fill: 'fill-volcanic-500',
      text: 'text-volcanic-100',
    },
    outline: {
      text: 'text-volcanic-500',
      stroke: 'stroke-volcanic-500',
      outlineFill: 'fill-volcanic-500',
      fill: 'fill-marble-950',
      bg: 'bg-marble-950',
    },
  },
  marble: {
    default: {
      bg: 'bg-marble-950',
      fill: 'fill-marble-950',
      text: 'text-volcanic-100',
    },
    outline: {
      text: 'text-volcanic-100',
      stroke: 'stroke-marble-950',
      outlineFill: 'fill-marble-950',
      fill: 'fill-marble-1000',
      bg: 'bg-marble-1000',
    },
  },
  marbleDark: {
    default: {
      bg: 'bg-marble-950',
      fill: 'fill-marble-950',
      text: 'text-volcanic-100',
    },
    outline: {
      text: 'text-volcanic-100',
      stroke: 'stroke-marble-950',
      outlineFill: 'fill-marble-950',
      fill: 'fill-marble-980',
      bg: 'bg-marble-980',
    },
  },
  secondary: {
    default: {
      bg: 'bg-mushroom-950',
      fill: 'fill-mushroom-950',
      text: 'text-volcanic-300',
    },
    outline: {
      text: 'text-volcanic-100',
      stroke: 'stroke-mushroom-600',
      outlineFill: 'fill-mushroom-600',
      fill: 'fill-mushroom-950',
      bg: 'bg-mushroom-950',
    },
  },
  secondaryDark: {
    default: {
      bg: 'bg-mushroom-900',
      fill: 'fill-mushroom-900',
      text: 'text-volcanic-300',
    },
    outline: {
      text: 'text-volcanic-300',
      stroke: 'stroke-mushroom-800',
      outlineFill: 'fill-mushroom-800',
      fill: 'fill-mushroom-900',
      bg: 'bg-mushroom-900',
    },
  },
  danger: {
    default: {
      bg: 'bg-danger-350',
      fill: 'fill-danger-350',
      text: 'text-marble-1000',
    },
    outline: {
      text: 'text-danger-350',
      stroke: 'stroke-danger-350',
      outlineFill: 'fill-danger-350',
      fill: 'fill-danger-950',
      bg: 'bg-danger-950',
    },
  },
  dangerDark: {
    default: {
      bg: 'bg-danger-350',
      fill: 'fill-danger-350',
      text: 'text-marble-1000',
    },
    outline: {
      text: 'text-danger-350',
      stroke: 'stroke-danger-350',
      outlineFill: 'fill-danger-350',
      fill: 'fill-danger-950',
      bg: 'bg-danger-950',
    },
  },
  transparent: {
    default: {
      bg: 'bg-transparent',
      fill: 'fill-transparent',
      text: 'text-inherit',
    },
    outline: {
      text: 'text-inherit',
      stroke: 'stroke-transparent',
      outlineFill: 'fill-transparent',
      fill: 'fill-transparent',
      bg: 'bg-transparent',
    },
  },
  volcanicLight: {
    default: {
      bg: 'bg-volcanic-300/50',
      fill: 'fill-volcanic-300/50',
      text: 'text-white',
    },
    outline: {
      text: 'text-volcanic-300',
      stroke: 'stroke-volcanic-300',
      outlineFill: 'fill-volcanic-300',
      fill: 'fill-marble-1000',
      bg: 'bg-marble-1000',
    },
  },
  blue: {
    default: {
      bg: 'bg-blue-600',
      fill: 'fill-blue-600',
      text: 'text-white',
    },
    outline: {
      text: 'text-blue-300',
      stroke: 'stroke-blue-600',
      outlineFill: 'fill-blue-600',
      fill: 'fill-blue-950',
      bg: 'bg-blue-950',
    },
  },
  blueDark: {
    default: {
      bg: 'bg-blue-300',
      fill: 'fill-blue-300',
      text: 'text-white',
    },
    outline: {
      text: 'text-blue-300',
      stroke: 'stroke-blue-300',
      outlineFill: 'fill-blue-300',
      fill: 'fill-blue-950',
      bg: 'bg-blue-950',
    },
  },
  quartz: {
    default: {
      bg: 'bg-quartz-700',
      fill: 'fill-quartz-700',
      text: 'text-white',
    },
    outline: {
      text: 'text-volcanic-100',
      stroke: 'stroke-quartz-700',
      outlineFill: 'fill-quartz-700',
      fill: 'fill-quartz-950',
      bg: 'bg-quartz-950',
    },
  },
  quartzAlt: {
    default: {
      bg: 'bg-quartz-700',
      fill: 'fill-quartz-700',
      text: 'text-white',
    },
    outline: {
      text: 'text-quartz-700',
      stroke: 'stroke-quartz-700',
      outlineFill: 'fill-quartz-700',
      fill: 'fill-marble-1000',
      bg: 'bg-marble-1000',
    },
  },
};

/*
 * The sizing process is unable to be set up more dynamically due to limitations with Tailwind's class detection
 * Details: https://tailwindcss.com/docs/content-configuration#class-detection-in-depth
 *
 * If you need a new size, please set it up in the SIZE_CLASSES mapping
 * May be worth including additional `-cell-` class names to theme.js
 */

interface SizeClasses {
  [sizeName: string]: string;
}

export const SIZE_CLASSES: SizeClasses = {
  xs: 'h-full min-h-cell-xs max-h-cell-xs',
  sm: 'h-full min-h-cell-sm max-h-cell-sm',
  md: 'h-full min-h-cell-md max-h-cell-md',
  lg: 'h-full min-h-cell-lg max-h-cell-lg',
  xl: 'h-full min-h-cell-xl max-h-cell-xl',
};
