'use client';

import cx from 'classnames';
import Link from 'next/link';
import { MouseEventHandler, ReactElement, ReactNode, useState } from 'react';

import { Icon, type IconName, type StandardIconSize } from '@/components/Shared';
import {
  type CellButtonTheme,
  DEFAULT_THEME,
  SIZE_ATTRIBUTES,
} from '@/components/Shared/Button/CellButton/cellButtonTheming';
import { Cell, type CellSize } from '@/components/Shared/Cell';

type CellButtonType = 'button' | 'submit' | 'reset';

export type CellButtonProps = {
  id?: string;
  label?: ReactNode | string;
  children?: ReactNode;
  type?: CellButtonType;
  /* The config values like colours associated with the button */
  theme?: CellButtonTheme;
  /* Whether to style a fixed width from style guide. By default the button will shrink/grow based on content */
  fixedWidth?: boolean;
  size?: CellSize;
  disabled?: boolean;
  /* Icon right-aligned at the end of the button */
  endIcon?: ReactElement | IconName;
  /* Icon in an appended second cell */
  splitIcon?: ReactElement | IconName;
  className?: string;
  shouldCenterContent?: boolean;
  hoverFocusStyles?: boolean;
  hideFocusStyles?: boolean;
  onClick?: MouseEventHandler<HTMLButtonElement | HTMLAnchorElement>;
  href?: string;
  shallow?: boolean;
  rel?: string;
  target?: string;
  preventDefault?: boolean;
  stopPropagation?: boolean;
  form?: string;
  animate?: boolean;
};

interface CellContainerProps {
  children: ReactNode;
  theme: CellButtonTheme;
  hover: boolean;
  focus: boolean;
  disabled: boolean;
  shouldCenterContent: boolean;
  hideFocusStyles: boolean;
  size: CellSize;
  splitIcon?: ReactElement | IconName;
  animate?: boolean;
}

// The containers and styles to support the buttons that use the Cell component
const CellContainer = ({
  children,
  theme,
  hover,
  focus,
  disabled,
  shouldCenterContent,
  hideFocusStyles,
  splitIcon,
  size,
  animate,
}: CellContainerProps) => {
  const activeCellTheme = hover ? theme.hoverTheme : theme.theme;
  const cellTheme = disabled ? theme.disabledTheme : activeCellTheme;
  const cellKind = theme.cellKind;
  const leftCell = theme.leftCell;
  const rightCell = animate ? theme.rightCell || !!splitIcon || hover : theme.rightCell;

  const focusOutlineWidth = SIZE_ATTRIBUTES[size].focusOutlineWidth;

  const isSplitIconString = typeof splitIcon === 'string';

  return (
    <div className="relative flex grow">
      <div className="z-10 flex grow">
        <Cell
          theme={cellTheme}
          kind={cellKind}
          size={size}
          rightCell={rightCell}
          leftCell={leftCell}
        >
          <span
            className={cx(
              // If the content is at the very start of the container, we don't transition the main cell inwards for the animation
              // and keep the padding stable.
              { 'px-0': !shouldCenterContent || (splitIcon && hover) },
              { 'px-2': shouldCenterContent && splitIcon && !hover },
              {
                'justify-center': shouldCenterContent,
                'justify-between': !shouldCenterContent,
              },
              'duration-400 flex w-full items-center transition-[padding] ease-in-out'
            )}
          >
            {children}
          </span>
        </Cell>
        {splitIcon && (
          <Cell
            theme={cellTheme}
            kind={cellKind}
            size={size}
            leftCell={rightCell}
            className="-ml-1 grow-0"
          >
            <span
              className={cx(
                { 'px-2': hover },
                { 'px-0': !hover },
                'duration-400 flex items-center transition-all ease-in-out'
              )}
            >
              {isSplitIconString && <Icon name={splitIcon} size={size as StandardIconSize} />}
              {!isSplitIconString && splitIcon}
            </span>
          </Cell>
        )}
      </div>
      {!hideFocusStyles && focus && (
        <Cell
          theme={theme.focusTheme}
          kind="outline"
          size={size}
          leftCell={leftCell}
          rightCell={!splitIcon && rightCell}
          className="absolute scale-y-[130%]"
          style={{
            width: `calc(100% + ${focusOutlineWidth * 2}px)`,
            left: `-${focusOutlineWidth}px`,
          }}
        />
      )}
    </div>
  );
};

export const CellButton: React.FC<CellButtonProps> = (props) => {
  const {
    id,
    label,
    children,
    theme = DEFAULT_THEME,
    fixedWidth,
    type = 'button',
    size = 'md',
    hoverFocusStyles = false,
    hideFocusStyles = false,
    disabled = false,
    target,
    splitIcon,
    endIcon,
    className,
    onClick,
    href,
    shallow,
    rel,
    preventDefault = false,
    stopPropagation = false,
    form,
    shouldCenterContent,
    animate = true,
    ...rest
  } = props;

  // Due to the complexity of the button designs,
  // hover and focus styles for buttons with a cell background need to be applied with more than CSS alone.
  const [hover, setHover] = useState(false);
  const [focus, setFocus] = useState(false);

  const handleClick: React.MouseEventHandler<HTMLButtonElement | HTMLAnchorElement> = (e) => {
    if (preventDefault) e.preventDefault();
    if (stopPropagation) e.stopPropagation();
    if (onClick) onClick(e);
  };

  const isEndIconString = typeof endIcon === 'string';

  const inner = (
    <CellContainer
      theme={theme}
      hover={hover}
      focus={focus}
      disabled={disabled}
      hideFocusStyles={hideFocusStyles}
      splitIcon={splitIcon}
      size={size}
      shouldCenterContent={shouldCenterContent === true && !endIcon}
      animate={animate}
    >
      {label || children}
      {isEndIconString && <Icon name={endIcon} className="ml-1" />}
      {!isEndIconString && endIcon}
    </CellContainer>
  );

  const widthClasses = fixedWidth ? SIZE_ATTRIBUTES[size].widthClass : '';

  const buttonClassNames = cx(
    className,
    widthClasses,
    'focus:outline-none',
    'disabled:cursor-not-allowed inline-block'
  );

  // We cannot disable <a> elements natively so we show a disabled button instead
  return !disabled && href ? (
    <Link
      {...rest}
      id={id}
      href={href}
      rel={rel}
      shallow={shallow}
      className={buttonClassNames}
      target={target || '_self'}
      onClick={handleClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onFocus={() => (hoverFocusStyles ? setHover(true) : setFocus(true))}
      onBlur={() => (hoverFocusStyles ? setHover(false) : setFocus(false))}
    >
      {inner}
    </Link>
  ) : (
    <button
      {...rest}
      id={id}
      type={type}
      disabled={disabled}
      onClick={handleClick}
      form={form}
      className={buttonClassNames}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onFocus={() => (hoverFocusStyles ? setHover(true) : setFocus(true))}
      onBlur={() => (hoverFocusStyles ? setHover(false) : setFocus(false))}
    >
      {inner}
    </button>
  );
};
