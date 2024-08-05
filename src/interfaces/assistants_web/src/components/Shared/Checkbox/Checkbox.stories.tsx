import { Meta, StoryFn, StoryObj } from '@storybook/react';
import { useState } from 'react';

import { Checkbox, Text } from '@/components/Shared';

export default {
  title: 'Components/Checkbox',
  component: Checkbox,
} as Meta<typeof Checkbox>;

export const Template: StoryFn<typeof Checkbox> = () => {
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
