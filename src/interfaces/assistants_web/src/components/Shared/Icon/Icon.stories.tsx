import type { Meta, StoryFn, StoryObj } from '@storybook/react';

import { Icon, Text } from '@/components/Shared';

const meta: Meta<typeof Icon> = {
  title: 'Components/Icon',
  component: Icon,
};

export default meta;
type Story = StoryObj<typeof Icon>;

const Icons = [
  'google-drive',
  'one-drive',
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
  'hide',
  'information',
  'kebab',
  'link',
  'list',
  'menu',
  'moon',
  'new-message',
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

export const AllIcons: StoryFn<typeof Icon> = () => (
  <div className="grid grid-cols-4">
    {Icons.map((icon) => (
      <div key={icon}>
        <Text>{icon}</Text>
        <div className="flex items-center gap-2">
          <Icon name={icon} size="xs" />
          <Icon name={icon} size="sm" />
          <Icon name={icon} size="md" />
          <Icon name={icon} size="lg" />
          <Icon name={icon} size="xl" />
        </div>
        <div className="flex items-center gap-2">
          <Icon name={icon} size="xs" kind="outline" />
          <Icon name={icon} size="sm" kind="outline" />
          <Icon name={icon} size="md" kind="outline" />
          <Icon name={icon} size="lg" kind="outline" />
          <Icon name={icon} size="xl" kind="outline" />
        </div>
      </div>
    ))}
  </div>
);
