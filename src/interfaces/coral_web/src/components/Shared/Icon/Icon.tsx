import cx from 'classnames';

export const Icons = [
  'add-in-frame',
  'add',
  'arrow-down',
  'arrow-left',
  'arrow-right',
  'arrow-up',
  'arrow-up-right',
  'chat',
  'check-mark',
  'chevron-down',
  'chevron-left',
  'chevron-right',
  'chevron-up',
  'close',
  'close-drawer',
  'copy',
  'dashboard',
  'download',
  'edit',
  'error',
  'file',
  'folder',
  'fullscreen',
  'grid',
  'help',
  'hide',
  'hourglass',
  'information',
  'kebab',
  'key',
  'link',
  'list',
  'menu',
  'notification',
  'payment',
  'profile',
  'range',
  'reorder',
  'search',
  'show',
  'start-now',
  'subtract',
  'success',
  'template',
  'trash',
  'upload',
  'warning',
  'thumbs-up',
  'thumbs-down',
  'enter',
  'redo',
  'new-message',
  'sources',
  'citations',
  'side-panel',
  'sparkle',
  'web',
  'clip',
  'pin',
  'calendar',
  'code',
  'globe-stand',
  'book',
  'book-open-text',
  'flask',
  'list-magnifying-glass',
  'newspaper',
  'circles-four',
  'calculator',
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
