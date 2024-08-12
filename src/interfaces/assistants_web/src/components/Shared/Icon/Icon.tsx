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

const getIcon = (name: IconName, kind: IconKind) => {
  switch (name) {
    case 'add':
      return (
        <AccessibleIcon label="add">
          <Add />
        </AccessibleIcon>
      );
    case 'close':
      return (
        <AccessibleIcon label="close">
          <Close />
        </AccessibleIcon>
      );
    case 'checkmark':
      return (
        <AccessibleIcon label="checkmark">
          <Checkmark />
        </AccessibleIcon>
      );
    case 'arrow-down':
      return (
        <AccessibleIcon label="arrow down">
          <ArrowDown />
        </AccessibleIcon>
      );
    case 'arrow-left':
      return (
        <AccessibleIcon label="arrow left">
          <ArrowLeft />
        </AccessibleIcon>
      );
    case 'arrow-right':
      return (
        <AccessibleIcon label="arrow right">
          <ArrowRight />
        </AccessibleIcon>
      );
    case 'arrow-up':
      return (
        <AccessibleIcon label="arrow up">
          <ArrowUp />
        </AccessibleIcon>
      );
    case 'arrow-up-right':
      return (
        <AccessibleIcon label="arrow up right">
          <ArrowUpRight />
        </AccessibleIcon>
      );
    case 'chevron-down':
      return (
        <AccessibleIcon label="chevron down">
          <ChevronDown />
        </AccessibleIcon>
      );
    case 'chevron-left':
      return (
        <AccessibleIcon label="chevron left">
          <ChevronLeft />
        </AccessibleIcon>
      );
    case 'chevron-right':
      return (
        <AccessibleIcon label="chevron right">
          <ChevronRight />
        </AccessibleIcon>
      );
    case 'chevron-up':
      return (
        <AccessibleIcon label="chevron up">
          <ChevronRight />
        </AccessibleIcon>
      );
    case 'menu':
      return (
        <AccessibleIcon label="menu">
          <Menu />
        </AccessibleIcon>
      );
    case 'search':
      return (
        <AccessibleIcon label="search">
          <Search kind={kind} />
        </AccessibleIcon>
      );
    case 'kebab':
      return (
        <AccessibleIcon label="kebab">
          <Kebab />
        </AccessibleIcon>
      );
    case 'copy':
      return (
        <AccessibleIcon label="copy">
          <Copy kind={kind} />
        </AccessibleIcon>
      );
    case 'link':
      return (
        <AccessibleIcon label="link">
          <Link />
        </AccessibleIcon>
      );
    case 'list':
      return (
        <AccessibleIcon label="list">
          <List />
        </AccessibleIcon>
      );
    case 'profile':
      return (
        <AccessibleIcon label="profile">
          <Profile />
        </AccessibleIcon>
      );
    case 'warning':
      return (
        <AccessibleIcon label="warning">
          <Warning kind={kind} />
        </AccessibleIcon>
      );
    case 'information':
      return (
        <AccessibleIcon label="information">
          <Information kind={kind} />
        </AccessibleIcon>
      );
    case 'upload':
      return (
        <AccessibleIcon label="upload">
          <Upload />
        </AccessibleIcon>
      );
    case 'close-drawer':
      return (
        <AccessibleIcon label="close drawer">
          <CloseDrawer />
        </AccessibleIcon>
      );
    case 'trash':
      return (
        <AccessibleIcon label="trash">
          <Trash />
        </AccessibleIcon>
      );
    case 'show':
      return (
        <AccessibleIcon label="show">
          <Show />
        </AccessibleIcon>
      );
    case 'hide':
      return (
        <AccessibleIcon label="hide">
          <Hide />
        </AccessibleIcon>
      );
    case 'edit':
      return (
        <AccessibleIcon label="edit">
          <Edit />
        </AccessibleIcon>
      );
    case 'file':
      return (
        <AccessibleIcon label="file">
          <File kind={kind} />
        </AccessibleIcon>
      );
    case 'folder':
      return (
        <AccessibleIcon label="folder">
          <Folder kind={kind} />
        </AccessibleIcon>
      );
    case 'thumbs-up':
      return (
        <AccessibleIcon label="thumbs up">
          <ThumbsUp kind={kind} />
        </AccessibleIcon>
      );
    case 'thumbs-down':
      return (
        <AccessibleIcon label="thumbs down">
          <ThumbsDown kind={kind} />
        </AccessibleIcon>
      );
    case 'new-message':
      return (
        <AccessibleIcon label="new message">
          <NewMessage />
        </AccessibleIcon>
      );
    case 'web':
      return (
        <AccessibleIcon label="web">
          <Web kind={kind} />
        </AccessibleIcon>
      );
    case 'download':
      return (
        <AccessibleIcon label="download">
          <Download />
        </AccessibleIcon>
      );
    case 'share':
      return (
        <AccessibleIcon label="share">
          <Share />
        </AccessibleIcon>
      );
    case 'calculator':
      return (
        <AccessibleIcon label="calculator">
          <Calculator />
        </AccessibleIcon>
      );
    case 'file-search':
      return (
        <AccessibleIcon label="calculator">
          <FileSearch />
        </AccessibleIcon>
      );
    case 'code-simple':
      return (
        <AccessibleIcon label="code simple">
          <CodeSimple />
        </AccessibleIcon>
      );
    case 'desktop':
      return (
        <AccessibleIcon label="desktop">
          <Desktop />
        </AccessibleIcon>
      );
    case 'paperclip':
      return (
        <AccessibleIcon label="paperclip">
          <Paperclip />
        </AccessibleIcon>
      );
    case 'circles-three':
      return (
        <AccessibleIcon label="circles three">
          <CirclesThree />
        </AccessibleIcon>
      );
    case 'circles-four':
      return (
        <AccessibleIcon label="circles four">
          <CirclesFour />
        </AccessibleIcon>
      );
    case 'users-three':
      return (
        <AccessibleIcon label="circles four">
          <UsersThree />
        </AccessibleIcon>
      );
    case 'arrow-clockwise':
      return (
        <AccessibleIcon label="arrow clockwise">
          <ArrowClockwise />
        </AccessibleIcon>
      );
    case 'arrow-submit':
      return (
        <AccessibleIcon label="arrow submit">
          <ArrowSubmit />
        </AccessibleIcon>
      );
    case 'chat-circle-dots':
      return (
        <AccessibleIcon label="arrow submit">
          <ChatCircleDots kind={kind} />
        </AccessibleIcon>
      );
    case 'settings':
      return (
        <AccessibleIcon label="settings">
          <Setttings kind={kind} />
        </AccessibleIcon>
      );
    case 'compass':
      return (
        <AccessibleIcon label="compass">
          <Compass />
        </AccessibleIcon>
      );
    case 'sparkle':
      return (
        <AccessibleIcon label="sparkle">
          <Sparkle />
        </AccessibleIcon>
      );
    case 'book-open-text':
      return (
        <AccessibleIcon label="book open text">
          <BookOpenText />
        </AccessibleIcon>
      );
    case 'sun':
      return (
        <AccessibleIcon label="sun">
          <Sun />
        </AccessibleIcon>
      );
    case 'moon':
      return (
        <AccessibleIcon label="moon">
          <Moon />
        </AccessibleIcon>
      );
    case 'sign-out':
      return (
        <AccessibleIcon label="moon">
          <SignOut />
        </AccessibleIcon>
      );
    case 'subtract':
      return (
        <AccessibleIcon label="subtract">
          <Subtract />
        </AccessibleIcon>
      );
    case 'google-drive':
      return (
        <AccessibleIcon label="Google Drive">
          <GoogleDrive />
        </AccessibleIcon>
      );
    case 'one-drive':
      return (
        <AccessibleIcon label="One Drive">
          <OneDrive />
        </AccessibleIcon>
      );
  }
};
