import type { Meta, StoryFn, StoryObj } from '@storybook/react';

import { Button } from '@/components/Shared';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
};

export default meta;
type Story = StoryObj<typeof Button>;

export const AllStyles: StoryFn<typeof Button> = () => (
  <div className="grid grid-cols-4 gap-4">
    <Button kind="primary" icon="add" label="Primary" />
    <Button kind="secondary" icon="add" label="Secondary" />
    <Button kind="cell" icon="add" label="Cell" />
    <Button kind="outline" icon="add" label="Outline" />
    <Button kind="primary" icon="add" disabled label="Primary - Disabled" />
    <Button kind="secondary" icon="add" disabled label="Secondary - Disabled" />
    <Button kind="cell" icon="add" disabled label="Cell - Disabled" />
    <Button kind="outline" icon="add" disabled label="Outline - Disabled" />
  </div>
);

export const Selection: Story = {
  args: {
    kind: 'primary',
    icon: 'arrow-right',
    animate: true,
    theme: 'evolved-green',
    label: 'Button',
  },
};
