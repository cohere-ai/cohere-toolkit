import { AccessibleIcon } from '@/components/Shared/Icon/AccessibleIcon';
import {
  Add,
  ArrowClockwise,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowSubmit,
  ArrowUp,
  ArrowUpRight,
  BookOpenText,
  Calculator,
  ChatCircleDots,
  Checkmark,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CirclesFour,
  CirclesThree,
  Close,
  CloseDrawer,
  CodeSimple,
  Compass,
  Copy,
  Desktop,
  Download,
  Edit,
  File,
  FileSearch,
  Folder,
  GoogleDrive,
  Hide,
  Information,
  Kebab,
  Link,
  List,
  Menu,
  Moon,
  NewMessage,
  OneDrive,
  Paperclip,
  Profile,
  Search,
  Setttings,
  Share,
  Show,
  SignOut,
  Sparkle,
  Subtract,
  Sun,
  ThumbsDown,
  ThumbsUp,
  Trash,
  Upload,
  UsersThree,
  Warning,
  Web,
} from '@/components/Shared/Icon/Icons';
import { cn } from '@/utils';

export const IconList = [
  'add',
  'arrow-clockwise',
  'arrow-down',
  'arrow-left',
  'arrow-right',
  'arrow-submit',
  'arrow-up-right',
  'arrow-up',
  'book-open-text',
  'calculator',
  'chat-circle-dots',
  'checkmark',
  'chevron-down',
  'chevron-left',
  'chevron-right',
  'chevron-up',
  'circles-four',
  'circles-three',
  'close-drawer',
  'close',
  'code-simple',
  'compass',
  'copy',
  'desktop',
  'download',
  'edit',
  'file-search',
  'file',
  'folder',
  'google-drive',
  'hide',
  'information',
  'kebab',
  'link',
  'list',
  'menu',
  'moon',
  'new-message',
  'one-drive',
  'paperclip',
  'profile',
  'search',
  'settings',
  'share',
  'show',
  'sign-out',
  'sparkle',
  'subtract',
  'sun',
  'thumbs-down',
  'thumbs-up',
  'trash',
  'upload',
  'users-three',
  'warning',
  'web',
] as const;

export type IconName = (typeof IconList)[number];
export type IconKind = 'default' | 'outline';

type Props = {
  name: IconName;
  kind?: IconKind;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'inherit';
  className?: string;
};

export const Icon: React.FC<Props> = ({ name, kind = 'default', size = 'md', className }) => {
  const sizeClass = cn({
    'h-inherit w-inherit': size == 'inherit',
    'h-icon-xs w-icon-xs': size === 'xs',
    'h-icon-sm w-icon-sm': size === 'sm',
    'h-icon-md w-icon-md': size === 'md',
    'h-icon-lg w-icon-lg': size === 'lg',
    'h-icon-xl w-icon-xl': size === 'xl',
  });

  return (
    <div className={cn(sizeClass, 'fill-volcanic-100 dark:fill-marble-950', className)}>
      {getIcon(name, kind)}
    </div>
  );
};

const getIcon = (name: IconName, kind: IconKind): React.ReactNode => {
  return {
    ['add']: (
      <AccessibleIcon label="Add">
        <Add />
      </AccessibleIcon>
    ),
    ['arrow-clockwise']: (
      <AccessibleIcon label="Arrow Clockwise">
        <ArrowClockwise />
      </AccessibleIcon>
    ),
    ['arrow-down']: (
      <AccessibleIcon label="Arrow Down">
        <ArrowDown />
      </AccessibleIcon>
    ),
    ['arrow-left']: (
      <AccessibleIcon label="Arrow Left">
        <ArrowLeft />
      </AccessibleIcon>
    ),
    ['arrow-right']: (
      <AccessibleIcon label="Arrow Right">
        <ArrowRight />
      </AccessibleIcon>
    ),
    ['arrow-submit']: (
      <AccessibleIcon label="Arrow Submit">
        <ArrowSubmit />
      </AccessibleIcon>
    ),
    ['arrow-up-right']: (
      <AccessibleIcon label="Arrow Up Right">
        <ArrowUpRight />
      </AccessibleIcon>
    ),
    ['arrow-up']: (
      <AccessibleIcon label="Arrow Up">
        <ArrowUp />
      </AccessibleIcon>
    ),
    ['book-open-text']: (
      <AccessibleIcon label="Book Open Text">
        <BookOpenText kind={kind} />
      </AccessibleIcon>
    ),
    ['calculator']: (
      <AccessibleIcon label="Calculator">
        <Calculator />
      </AccessibleIcon>
    ),
    ['chat-circle-dots']: (
      <AccessibleIcon label="Chat Circle Dots">
        <ChatCircleDots kind={kind} />
      </AccessibleIcon>
    ),
    ['checkmark']: (
      <AccessibleIcon label="Checkmark">
        <Checkmark />
      </AccessibleIcon>
    ),
    ['chevron-down']: (
      <AccessibleIcon label="Chevron Down">
        <ChevronDown />
      </AccessibleIcon>
    ),
    ['chevron-left']: (
      <AccessibleIcon label="Chevron Left">
        <ChevronLeft />
      </AccessibleIcon>
    ),
    ['chevron-right']: (
      <AccessibleIcon label="Chevron Right">
        <ChevronRight />
      </AccessibleIcon>
    ),
    ['chevron-up']: (
      <AccessibleIcon label="Chevron Up">
        <ChevronDown />
      </AccessibleIcon>
    ),
    ['circles-four']: (
      <AccessibleIcon label="Circles Four">
        <CirclesFour />
      </AccessibleIcon>
    ),
    ['circles-three']: (
      <AccessibleIcon label="Circles Three">
        <CirclesThree />
      </AccessibleIcon>
    ),
    ['close-drawer']: (
      <AccessibleIcon label="Close Drawer">
        <CloseDrawer />
      </AccessibleIcon>
    ),
    ['close']: (
      <AccessibleIcon label="Close">
        <Close />
      </AccessibleIcon>
    ),
    ['code-simple']: (
      <AccessibleIcon label="Code Simple">
        <CodeSimple />
      </AccessibleIcon>
    ),
    ['compass']: (
      <AccessibleIcon label="Compass">
        <Compass />
      </AccessibleIcon>
    ),
    ['copy']: (
      <AccessibleIcon label="Copy">
        <Copy kind={kind} />
      </AccessibleIcon>
    ),
    ['desktop']: (
      <AccessibleIcon label="Desktop">
        <Desktop />
      </AccessibleIcon>
    ),
    ['download']: (
      <AccessibleIcon label="Download">
        <Download />
      </AccessibleIcon>
    ),
    ['edit']: (
      <AccessibleIcon label="Edit">
        <Edit />
      </AccessibleIcon>
    ),
    ['file-search']: (
      <AccessibleIcon label="File Search">
        <FileSearch />
      </AccessibleIcon>
    ),
    ['file']: (
      <AccessibleIcon label="File">
        <File kind={kind} />
      </AccessibleIcon>
    ),
    ['folder']: (
      <AccessibleIcon label="Folder">
        <Folder kind={kind} />
      </AccessibleIcon>
    ),
    ['google-drive']: (
      <AccessibleIcon label="Google Drive">
        <GoogleDrive />
      </AccessibleIcon>
    ),
    ['hide']: (
      <AccessibleIcon label="Hide">
        <Hide />
      </AccessibleIcon>
    ),
    ['information']: (
      <AccessibleIcon label="Information">
        <Information kind={kind} />
      </AccessibleIcon>
    ),
    ['kebab']: (
      <AccessibleIcon label="Kebab">
        <Kebab />
      </AccessibleIcon>
    ),
    ['link']: (
      <AccessibleIcon label="Link">
        <Link />
      </AccessibleIcon>
    ),
    ['list']: (
      <AccessibleIcon label="List">
        <List />
      </AccessibleIcon>
    ),
    ['menu']: (
      <AccessibleIcon label="Menu">
        <Menu />
      </AccessibleIcon>
    ),
    ['moon']: (
      <AccessibleIcon label="Moon">
        <Moon kind={kind} />
      </AccessibleIcon>
    ),
    ['new-message']: (
      <AccessibleIcon label="New Message">
        <NewMessage />
      </AccessibleIcon>
    ),
    ['one-drive']: (
      <AccessibleIcon label="One Drive">
        <OneDrive />
      </AccessibleIcon>
    ),
    ['paperclip']: (
      <AccessibleIcon label="Paperclip">
        <Paperclip />
      </AccessibleIcon>
    ),
    ['profile']: (
      <AccessibleIcon label="Profile">
        <Profile />
      </AccessibleIcon>
    ),
    ['search']: (
      <AccessibleIcon label="Search">
        <Search kind={kind} />
      </AccessibleIcon>
    ),
    ['settings']: (
      <AccessibleIcon label="Settings">
        <Setttings kind={kind} />
      </AccessibleIcon>
    ),
    ['share']: (
      <AccessibleIcon label="Share">
        <Share />
      </AccessibleIcon>
    ),
    ['show']: (
      <AccessibleIcon label="Show">
        <Show />
      </AccessibleIcon>
    ),
    ['sign-out']: (
      <AccessibleIcon label="Sign Out">
        <SignOut />
      </AccessibleIcon>
    ),
    ['sparkle']: (
      <AccessibleIcon label="Sparkle">
        <Sparkle kind={kind} />
      </AccessibleIcon>
    ),
    ['subtract']: (
      <AccessibleIcon label="Subtract">
        <Subtract />
      </AccessibleIcon>
    ),
    ['sun']: (
      <AccessibleIcon label="Sun">
        <Sun kind={kind} />
      </AccessibleIcon>
    ),
    ['thumbs-down']: (
      <AccessibleIcon label="Thumbs Down">
        <ThumbsDown kind={kind} />
      </AccessibleIcon>
    ),
    ['thumbs-up']: (
      <AccessibleIcon label="Thumbs Up">
        <ThumbsUp kind={kind} />
      </AccessibleIcon>
    ),
    ['trash']: (
      <AccessibleIcon label="Trash">
        <Trash kind={kind} />
      </AccessibleIcon>
    ),
    ['upload']: (
      <AccessibleIcon label="Upload">
        <Upload />
      </AccessibleIcon>
    ),
    ['users-three']: (
      <AccessibleIcon label="Users Three">
        <UsersThree />
      </AccessibleIcon>
    ),
    ['warning']: (
      <AccessibleIcon label="Warning">
        <Warning kind={kind} />
      </AccessibleIcon>
    ),
    ['web']: (
      <AccessibleIcon label="Web">
        <Web kind={kind} />
      </AccessibleIcon>
    ),
  }[name];
};
