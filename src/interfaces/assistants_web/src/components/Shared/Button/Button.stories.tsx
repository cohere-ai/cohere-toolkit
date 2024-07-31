// Replace your-framework with the name of your framework
import type { Meta, StoryObj } from '@storybook/react';

import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
};

export default meta;

type Story = StoryObj<typeof Button>;

export const Secondary: Story = {
  // render: (...args) => (
  //   <div className="dark">
  //     <Button />
  //   </div>
  // ),
  args: {
    kind: 'secondary',
    label: 'Button',
  },
};
