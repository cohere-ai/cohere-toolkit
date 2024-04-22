import type { CellKind, CellTheme } from '../../Cell/cellTheming';

export interface CellButtonTheme {
  cellKind: CellKind;
  theme: CellTheme;
  hoverTheme: CellTheme;
  focusTheme: CellTheme;
  disabledTheme: CellTheme;
  /* Include the trapezoid edge on the left side - option to 'flip' edge upside down */
  leftCell: boolean | 'flip';
  /* Include the trapezoid edge on the right side - option to 'flip' edge upside down */
  rightCell: boolean | 'flip';
  textClasses?: string;
  /* Optionally choose to change the focus outline Cell kind - default 'outline' */
  focusCellKind?: CellKind;
  /* Optionally choose to change the focus outline Cell theme - default 'coral' */
  focusCellTheme?: CellTheme;
}

export const DEFAULT_THEME: CellButtonTheme = {
  cellKind: 'default',
  theme: 'volcanic',
  hoverTheme: 'volcanic',
  focusTheme: 'primaryDark',
  disabledTheme: 'grayDark',
  leftCell: false,
  rightCell: true,
};

interface SizeAttributes {
  [size: string]: {
    widthClass: string;
    focusOutlineWidth: number;
  };
}

export const SIZE_ATTRIBUTES: SizeAttributes = {
  sm: {
    widthClass: 'sm:w-btn-sm',
    focusOutlineWidth: 5,
  },
  md: {
    widthClass: 'sm:w-btn-md',
    focusOutlineWidth: 6,
  },
  lg: {
    widthClass: 'sm:w-btn-lg',
    focusOutlineWidth: 8,
  },
  xl: {
    widthClass: 'sm:w-btn-xl',
    focusOutlineWidth: 10,
  },
};
