'use client';

import cx from 'classnames';

import type { CellSize, CellTheme } from './cellTheming';
import { SIZE_CLASSES, THEME_CLASSES } from './cellTheming';

interface SideCellProps {
  size: CellSize;
  theme: CellTheme;
  flip?: boolean;
}

/*
 * The trapezoidal edge SVGs for the default cell
 */

export const DefaultRightCell = ({ theme = 'volcanic', size = 'md', flip }: SideCellProps) => {
  return (
    <svg
      viewBox="0 0 18 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cx(SIZE_CLASSES[size], {
        '-scale-y-100': flip,
        '-ml-[1px]': theme !== 'volcanicLight',
      })}
    >
      <path
        d="M10.899 0H0V40H2C4.40603 40 6.55968 38.5075 7.4045 36.2547L17.4533 9.45786C19.1694 4.88161 15.7864 0 10.899 0Z"
        className={THEME_CLASSES[theme].default.fill}
      />
    </svg>
  );
};
export const DefaultLeftCell = ({ theme = 'volcanic', size = 'md', flip }: SideCellProps) => {
  return (
    <svg
      viewBox="0 0 18 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cx(SIZE_CLASSES[size], {
        '-scale-y-100': flip,
        '-mr-[1px]': theme !== 'volcanicLight',
      })}
    >
      <path
        d="M7.101 40H18V0H16C13.594 0 11.4403 1.49249 10.5955 3.74532L0.546698 30.5421C-1.1694 35.1184 2.21356 40 7.101 40Z"
        className={THEME_CLASSES[theme].default.fill}
      />
    </svg>
  );
};

/*
 * The standard rounded edge SVGs for the default cell
 */
export const DefaultRightSide = ({ theme = 'volcanic', size = 'md' }: SideCellProps) => {
  return (
    <svg
      viewBox="0 0 10 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cx(SIZE_CLASSES[size], { '-ml-[1px]': theme !== 'volcanicLight' })}
    >
      <path
        d="M0 40V0H4C7.31371 0 10 2.68629 10 6V34C10 37.3137 7.31371 40 4 40H0Z"
        className={THEME_CLASSES[theme].default.fill}
      />
    </svg>
  );
};
export const DefaultLeftSide = ({ theme = 'volcanic', size = 'md' }: SideCellProps) => {
  return (
    <svg
      viewBox="0 0 10 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cx(SIZE_CLASSES[size], { '-mr-[1px]': theme !== 'volcanicLight' })}
    >
      <path
        d="M10 40V0H6C2.68629 0 0 2.68629 0 6V34C0 37.3137 2.68629 40 6 40H10Z"
        className={THEME_CLASSES[theme].default.fill}
      />
    </svg>
  );
};

/*
 * The trapezoidal edge SVGs for the outline cell
 */
export const OutlineRightCell = ({ theme = 'volcanic', size = 'md', flip }: SideCellProps) => {
  return (
    <svg
      viewBox="0 0 19 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cx(SIZE_CLASSES[size], {
        '-scale-y-100': flip,
        '-ml-[1px]': theme !== 'volcanicLight',
      })}
    >
      <path
        d="M0 0.5H10.9293C15.8084 0.5 19.1908 5.36619 17.4905 9.93942L7.95337 35.5909C7.07963 37.941 4.83674 39.5 2.32949 39.5H2H0"
        className={cx(THEME_CLASSES[theme].outline.stroke, THEME_CLASSES[theme].outline.fill)}
      />
    </svg>
  );
};
export const OutlineLeftCell = ({ theme = 'volcanic', size = 'md', flip }: SideCellProps) => {
  return (
    <svg
      viewBox="0 0 19 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cx(SIZE_CLASSES[size], {
        '-scale-y-100': flip,
        '-mr-[1px]': theme !== 'volcanicLight',
      })}
    >
      <path
        d="M19 39.5H8.07072C3.19164 39.5 -0.190776 34.6338 1.50953 30.0606L11.0466 4.40907C11.9204 2.059 14.1633 0.5 16.6705 0.5H17H19"
        className={cx(THEME_CLASSES[theme].outline.stroke, THEME_CLASSES[theme].outline.fill)}
      />
    </svg>
  );
};

/*
 * The standard rounded edge SVGs for the outline cell
 */
export const OutlineRightSide = ({ theme = 'volcanic', size = 'md' }: SideCellProps) => {
  return (
    <svg
      viewBox="0 0 11 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cx(SIZE_CLASSES[size], { '-ml-[1px]': theme !== 'volcanicLight' })}
    >
      <path
        d="M9.05991e-05 39.5H3.99992C7.31363 39.5 9.99992 36.8137 9.99992 33.5L9.99999 6.50002C9.99999 3.1863 7.3137 0.5 3.99999 0.5H9.05991e-05"
        className={cx(THEME_CLASSES[theme].outline.stroke, THEME_CLASSES[theme].outline.fill)}
      />
    </svg>
  );
};
export const OutlineLeftSide = ({ theme = 'volcanic', size = 'md' }: SideCellProps) => {
  return (
    <svg
      viewBox="0 0 11 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cx(SIZE_CLASSES[size], { '-mr-[1px]': theme !== 'volcanicLight' })}
    >
      <path
        d="M10.9999 39.5H7.00008C3.68637 39.5 1.00008 36.8137 1.00008 33.5L1.00001 6.50002C1.00001 3.1863 3.6863 0.5 7.00001 0.5H10.9999"
        className={cx(THEME_CLASSES[theme].outline.stroke, THEME_CLASSES[theme].outline.fill)}
      />
    </svg>
  );
};

/*
 * The middle section of the outline cell
 */
export const OutlineCellBody = ({ theme = 'volcanic', size = 'md' }: SideCellProps) => {
  return (
    <svg
      viewBox="0 0 29 40"
      fill="none"
      preserveAspectRatio="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cx(SIZE_CLASSES[size], 'absolute w-full')}
    >
      <path
        d="M0 1H29V-1H0V1ZM29 39H0V41H29V39Z"
        mask="url(#path-1-inside-1_511_249246)"
        className={THEME_CLASSES[theme].outline.outlineFill}
      />
    </svg>
  );
};
