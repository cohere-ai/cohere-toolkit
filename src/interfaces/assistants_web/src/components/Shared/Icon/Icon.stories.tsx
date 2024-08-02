import type { Meta, StoryFn, StoryObj } from '@storybook/react';

import { Icon, IconList, Text } from '@/components/Shared';

const meta: Meta<typeof Icon> = {
  title: 'Components/Icon',
  component: Icon,
};

export default meta;
type Story = StoryObj<typeof Icon>;

export const AllIcons: StoryFn<typeof Icon> = () => (
  <div className="grid grid-cols-4">
    {IconList.map((icon) => (
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

export const Selection: Story = {
  args: {
    name: 'add',
    kind: 'outline',
    size: 'md',
  },
  argTypes: {
    name: {
      options: IconList,
      control: { type: 'select' },
    },
    kind: {
      options: ['outline', 'fill'],
      control: { type: 'radio' },
    },
    size: {
      options: ['xs', 'sm', 'md', 'lg', 'xl'],
      control: { type: 'radio' },
    },
  },
};
