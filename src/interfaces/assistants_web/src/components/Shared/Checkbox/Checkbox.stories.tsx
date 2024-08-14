import { Meta, StoryFn, StoryObj } from '@storybook/react';
import { useState } from 'react';

import { Checkbox, Text } from '@/components/Shared';

const meta: Meta<typeof Checkbox> = {
  title: 'Components/Checkbox',
  component: Checkbox,
};

export default meta;
type Story = StoryObj<typeof Checkbox>;

export const Default: StoryFn<typeof Checkbox> = () => {
  const [isChecked1, setIsChecked1] = useState(false);
  const [isChecked2, setIsChecked2] = useState(false);
  const [isChecked3, setIsChecked3] = useState(false);

  return (
    <div className="flex flex-col gap-3 p-3">
      <div className="flex gap-2">
        <Text>Coral</Text>
        <Checkbox theme="coral" checked={isChecked1} onChange={setIsChecked1} />
      </div>
      <div className="flex gap-2">
        <Text>Evolved Green</Text>
        <Checkbox theme="evolved-green" checked={isChecked2} onChange={setIsChecked2} />
      </div>
      <div className="flex gap-2">
        <Text>Disabled</Text>
        <Checkbox theme="evolved-green" checked={isChecked3} onChange={setIsChecked3} disabled />
      </div>
    </div>
  );
};

export const Selection: Story = {
  args: {
    checked: false,
    indeterminate: false,
    disabled: false,
    label: 'Label',
    theme: 'coral',
  },
  argTypes: {
    checked: {
      control: { type: 'boolean' },
    },
    indeterminate: {
      control: { type: 'boolean' },
    },
    disabled: {
      control: { type: 'boolean' },
    },
    label: {
      control: { type: 'text' },
    },
    theme: {
      options: ['coral', 'evolved-green'],
      control: { type: 'radio' },
    },
  },
};
