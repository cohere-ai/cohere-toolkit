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
      bg: 'bg-volcanic-900',
      fill: 'fill-volcanic-900',
      text: 'text-white',
    },
    outline: {
      text: 'text-volcanic-900',
      stroke: 'stroke-volcanic-900',
      outlineFill: 'fill-volcanic-900',
      fill: 'fill-marble-100',
      bg: 'bg-marble-100',
    },
  },
  volcanicAlt: {
    default: {
      bg: 'bg-marble-100',
      fill: 'fill-marble-100',
      text: 'text-volcanic-900',
    },
    outline: {
      text: 'bg-volcanic-900',
      stroke: 'stroke-marble-100',
      outlineFill: 'fill-marble-100',
      fill: 'fill-volcanic-900',
      bg: 'text-white',
    },
  },
  primary: {
    default: {
      bg: 'bg-primary-500',
      fill: 'fill-primary-500',
      text: 'text-white',
    },
    outline: {
      text: 'text-volcanic-900',
      stroke: 'stroke-primary-300',
      outlineFill: 'fill-primary-300',
      fill: 'fill-primary-100',
      bg: 'bg-primary-100',
    },
  },
  primarylLight: {
    default: {
      bg: 'bg-primary-400',
      fill: 'fill-primary-400',
      text: 'text-white',
    },
    outline: {
      text: 'text-volcanic-900',
      stroke: 'stroke-primary-300',
      outlineFill: 'fill-primary-300',
      fill: 'fill-primary-100',
      bg: 'bg-primary-100',
    },
  },
  primaryDark: {
    default: {
      bg: 'bg-primary-500',
      fill: 'fill-primary-500',
      text: 'text-white',
    },
    outline: {
      text: 'text-primary-500',
      stroke: 'stroke-primary-500',
      outlineFill: 'fill-primary-500',
      fill: 'fill-primary-300',
      bg: 'bg-primary-300',
    },
  },
  green: {
    default: {
      bg: 'bg-green-700',
      fill: 'fill-green-700',
      text: 'text-white',
    },
    outline: {
      text: 'text-green-900',
      stroke: 'stroke-green-500',
      outlineFill: 'fill-green-500',
      fill: 'fill-green-50',
      bg: 'bg-green-50',
    },
  },
  greenDark: {
    default: {
      bg: 'bg-green-900',
      fill: 'fill-green-900',
      text: 'text-white',
    },
    outline: {
      text: 'text-green-900',
      stroke: 'stroke-green-900',
      outlineFill: 'fill-green-700',
      fill: 'fill-green-100',
      bg: 'bg-green-100',
    },
  },
  greenAlt: {
    default: {
      bg: 'bg-green-700',
      fill: 'fill-green-700',
      text: 'text-white',
    },
    outline: {
      text: 'text-green-700',
      stroke: 'stroke-green-700',
      outlineFill: 'fill-green-700',
      fill: 'fill-marble-100',
      bg: 'bg-marble-100',
    },
  },
  gray: {
    default: {
      bg: 'bg-marble-300',
      fill: 'fill-marble-300',
      text: 'text-volcanic-700',
    },
    outline: {
      text: 'text-volcanic-600',
      stroke: 'stroke-volcanic-600',
      outlineFill: 'fill-volcanic-600',
      fill: 'fill-marble-300',
      bg: 'bg-marble-300',
    },
  },
  grayDark: {
    default: {
      bg: 'bg-volcanic-600',
      fill: 'fill-volcanic-600',
      text: 'text-volcanic-900',
    },
    outline: {
      text: 'text-volcanic-600',
      stroke: 'stroke-volcanic-600',
      outlineFill: 'fill-volcanic-600',
      fill: 'fill-marble-300',
      bg: 'bg-marble-300',
    },
  },
  marble: {
    default: {
      bg: 'bg-marble-300',
      fill: 'fill-marble-300',
      text: 'text-volcanic-900',
    },
    outline: {
      text: 'text-volcanic-900',
      stroke: 'stroke-marble-400',
      outlineFill: 'fill-marble-400',
      fill: 'fill-marble-100',
      bg: 'bg-marble-100',
    },
  },
  marbleDark: {
    default: {
      bg: 'bg-marble-400',
      fill: 'fill-marble-400',
      text: 'text-volcanic-900',
    },
    outline: {
      text: 'text-volcanic-900',
      stroke: 'stroke-marble-400',
      outlineFill: 'fill-marble-400',
      fill: 'fill-marble-200',
      bg: 'bg-marble-200',
    },
  },
  secondary: {
    default: {
      bg: 'bg-secondary-50',
      fill: 'fill-secondary-50',
      text: 'text-volcanic-800',
    },
    outline: {
      text: 'text-volcanic-900',
      stroke: 'stroke-secondary-500',
      outlineFill: 'fill-secondary-500',
      fill: 'fill-secondary-50',
      bg: 'bg-secondary-50',
    },
  },
  secondaryDark: {
    default: {
      bg: 'bg-secondary-100',
      fill: 'fill-secondary-100',
      text: 'text-volcanic-800',
    },
    outline: {
      text: 'text-volcanic-800',
      stroke: 'stroke-secondary-300',
      outlineFill: 'fill-secondary-300',
      fill: 'fill-secondary-100',
      bg: 'bg-secondary-100',
    },
  },
  danger: {
    default: {
      bg: 'bg-danger-500',
      fill: 'fill-danger-500',
      text: 'text-marble-100',
    },
    outline: {
      text: 'text-danger-500',
      stroke: 'stroke-danger-500',
      outlineFill: 'fill-danger-500',
      fill: 'fill-danger-50',
      bg: 'bg-danger-50',
    },
  },
  dangerDark: {
    default: {
      bg: 'bg-danger-900',
      fill: 'fill-danger-900',
      text: 'text-marble-100',
    },
    outline: {
      text: 'text-danger-900',
      stroke: 'stroke-danger-900',
      outlineFill: 'fill-danger-900',
      fill: 'fill-danger-50',
      bg: 'bg-danger-50',
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
      bg: 'bg-volcanic-800/50',
      fill: 'fill-volcanic-800/50',
      text: 'text-white',
    },
    outline: {
      text: 'text-volcanic-800',
      stroke: 'stroke-volcanic-800',
      outlineFill: 'fill-volcanic-800',
      fill: 'fill-marble-100',
      bg: 'bg-marble-100',
    },
  },
  blue: {
    default: {
      bg: 'bg-blue-500',
      fill: 'fill-blue-500',
      text: 'text-white',
    },
    outline: {
      text: 'text-blue-800',
      stroke: 'stroke-blue-500',
      outlineFill: 'fill-blue-500',
      fill: 'fill-blue-50',
      bg: 'bg-blue-50',
    },
  },
  blueDark: {
    default: {
      bg: 'bg-blue-800',
      fill: 'fill-blue-800',
      text: 'text-white',
    },
    outline: {
      text: 'text-blue-800',
      stroke: 'stroke-blue-800',
      outlineFill: 'fill-blue-800',
      fill: 'fill-blue-50',
      bg: 'bg-blue-50',
    },
  },
  quartz: {
    default: {
      bg: 'bg-quartz-700',
      fill: 'fill-quartz-700',
      text: 'text-white',
    },
    outline: {
      text: 'text-volcanic-900',
      stroke: 'stroke-quartz-700',
      outlineFill: 'fill-quartz-700',
      fill: 'fill-quartz-50',
      bg: 'bg-quartz-50',
    },
  },
  quartzAlt: {
    default: {
      bg: 'bg-quartz-500',
      fill: 'fill-quartz-500',
      text: 'text-white',
    },
    outline: {
      text: 'text-quartz-500',
      stroke: 'stroke-quartz-500',
      outlineFill: 'fill-quartz-500',
      fill: 'fill-marble-100',
      bg: 'bg-marble-100',
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
