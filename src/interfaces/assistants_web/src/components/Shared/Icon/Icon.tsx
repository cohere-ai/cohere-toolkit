'use client';

import cx from 'classnames';

export const Icons = [
  'add-in-frame',
  'add',
  'arrow-down',
  'arrow-left',
  'arrow-right',
  'arrow-up-right',
  'arrow-up',
  'at',
  'book-open-text',
  'book',
  'calculator',
  'calendar',
  'chat',
  'check-mark',
  'chevron-down',
  'chevron-left',
  'chevron-right',
  'chevron-up',
  'circles-four',
  'citations',
  'clip',
  'close-drawer',
  'close',
  'code-block',
  'code',
  'compass',
  'copy',
  'dashboard',
  'download',
  'edit',
  'enter',
  'error',
  'file',
  'flask',
  'folder',
  'fullscreen',
  'github',
  'globe-stand',
  'grid',
  'help',
  'hide',
  'hourglass',
  'information',
  'kebab',
  'key',
  'link',
  'list-magnifying-glass',
  'list',
  'magnifying-glass',
  'menu',
  'new-message',
  'newspaper',
  'notification',
  'payment',
  'pin',
  'plugs-connected',
  'profile',
  'range',
  'redo',
  'reorder',
  'search',
  'selection-slash',
  'settings',
  'share',
  'show',
  'side-panel',
  'sources',
  'sparkle',
  'start-now',
  'subtract',
  'success',
  'template',
  'thumbs-down',
  'thumbs-up',
  'trash',
  'upload',
  'warning',
  'web',
  'wrench',
] as const;

export type IconName = (typeof Icons)[number];

export type StandardIconSize = 'sm' | 'md' | 'lg' | 'xl';

export interface IconProps
  extends React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> {
  name: IconName;
  kind?: 'default' | 'outline';
  size?: StandardIconSize | 'inherit';
}

const SIZE_CLASSES = {
  sm: 'text-icon-sm',
  md: 'text-icon-md',
  lg: 'text-icon-lg',
  xl: 'text-icon-xl',
};

/**
 * Use IcoMoon (https://icomoon.io/app/#/select) to update the icon font.
 */
export const Icon = ({
  kind = 'default',
  size = 'inherit',
  name,
  className,
  ...rest
}: IconProps) => {
  const sizeClass = size === 'inherit' ? '' : SIZE_CLASSES[size] || '';
  return <i className={cx(`icon-${kind}`, `icon-${name}`, sizeClass, className)} {...rest} />;
};
