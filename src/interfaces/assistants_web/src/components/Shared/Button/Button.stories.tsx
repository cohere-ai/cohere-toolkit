// Replace your-framework with the name of your framework
import type { Meta, StoryObj } from '@storybook/react';

import { Button } from '@/components/Shared';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  decorators: [
    (Story) => (
      <div className="flex gap-2">
        <div className="dark">
          <Story />
        </div>
        <div className="light">
          <Story />
        </div>
      </div>
    ),
  ],
};

export default meta;

type Story = StoryObj<typeof Button>;

export const Secondary: Story = {
  args: {
    kind: 'secondary',
    icon: 'arrow-right',
    animate: true,
    theme: 'evolved-green',
    label: 'Button',
  },
};
