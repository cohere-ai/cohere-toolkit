'use client';

import cx from 'classnames';
import { CSSProperties, ReactNode } from 'react';

import {
  DefaultLeftCell,
  DefaultLeftSide,
  DefaultRightCell,
  DefaultRightSide,
  OutlineCellBody,
  OutlineLeftCell,
  OutlineLeftSide,
  OutlineRightCell,
  OutlineRightSide,
} from './CellParts';
import type { CellKind, CellSize, CellTheme } from './cellTheming';
import { SIZE_CLASSES, THEME_CLASSES } from './cellTheming';

/*
 * The 'Cell' is the trapezoid/polygon shape that can't quite be achieved with CSS alone
 * There are two 'kinds' of cell - default (filled), and outline
 * The implementation of the Cell is still fairly experimental and could be buggy. Message @laura if you run into issues.
 *
 * HOW TO USE
 * - Browse the existing colours and sizes available for use in `cellTheming.ts`
 *    - Preview all colours/sizes using Storybook
 * - Add a new size or colour theme if the one you need doesn't already exist
 *    - Push back if too many cell themes are getting added - can we use an existing one?
 * - Flexibility with props on which sides have the special cell/trapezoid edge
 * - Cell's default behaviour is growing to fit the width of their parent container
 */

type CellProps = {
  children?: ReactNode;
  kind?: CellKind;
  size?: CellSize;
  /* The colours associated with the cell */
  theme?: CellTheme;
  /* Include the trapezoid edge on the right side - option to 'flip' the edge upside down */
  rightCell?: boolean | 'flip';
  /* Include the trapezoid edge on the left side - option to 'flip' the edge upside down */
  leftCell?: boolean | 'flip';
  /* Additional classes as needed - applied to the outer container */
  className?: string;
  style?: CSSProperties;
  allowOverflow?: boolean;
};

const DefaultCell = ({
  className = '',
  theme = 'volcanic',
  size = 'md',
  rightCell,
  leftCell,
  children,
  style,
  allowOverflow = false,
}: CellProps) => {
  const containerClassNames = cx(SIZE_CLASSES[size], 'flex grow');

  const innerClassNames = cx(
    THEME_CLASSES[theme].default.bg,
    THEME_CLASSES[theme].default.text,
    SIZE_CLASSES[size],
    { truncate: !allowOverflow },
    'flex grow justify-between items-center'
  );

  return (
    <div className={cx(containerClassNames, className)} style={style}>
      {!leftCell && <DefaultLeftSide theme={theme} size={size} />}
      {leftCell && <DefaultLeftCell theme={theme} size={size} flip={leftCell === 'flip'} />}
      <div className={innerClassNames}>{children}</div>
      {!rightCell && <DefaultRightSide theme={theme} size={size} />}
      {rightCell && <DefaultRightCell theme={theme} size={size} flip={rightCell === 'flip'} />}
    </div>
  );
};

const OutlineCell = ({
  className = '',
  theme = 'volcanic',
  size = 'md',
  rightCell,
  leftCell,
  children,
  style,
  allowOverflow = false,
}: CellProps) => {
  const containerClassNames = cx(SIZE_CLASSES[size], 'flex grow');
  const innerClassNames = cx(
    THEME_CLASSES[theme].outline.text,
    THEME_CLASSES[theme].outline.bg,
    SIZE_CLASSES[size],
    { truncate: !allowOverflow },
    'flex grow relative'
  );

  return (
    <div className={cx(containerClassNames, className)} style={style}>
      {!leftCell && <OutlineLeftSide theme={theme} size={size} />}
      {leftCell && <OutlineLeftCell theme={theme} size={size} flip={leftCell === 'flip'} />}
      <div className={innerClassNames}>
        <div className="z-10 flex w-full items-center justify-between">{children}</div>
        <OutlineCellBody theme={theme} size={size} />
      </div>
      {!rightCell && <OutlineRightSide theme={theme} size={size} />}
      {rightCell && <OutlineRightCell theme={theme} size={size} flip={rightCell === 'flip'} />}
    </div>
  );
};

export const Cell = ({ kind = 'default', ...props }: CellProps) => {
  return kind === 'default' ? <DefaultCell {...props} /> : <OutlineCell {...props} />;
};
