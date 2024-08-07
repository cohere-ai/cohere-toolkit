import type { Meta, StoryFn, StoryObj } from '@storybook/react';

import { Button, Text } from '@/components/Shared';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
};

export default meta;
type Story = StoryObj<typeof Button>;

export const AllStyles: StoryFn<typeof Button> = () => (
  <div className="flex flex-col gap-4">
    <div className="flex flex-col gap-2">
      <Text>Primary</Text>
      <div className="grid grid-cols-4 gap-4 xl:grid-cols-5">
        <Button kind="primary" icon="add" label="Primary" theme="default" />
        <Button kind="primary" icon="add" label="Primary" theme="evolved-green" />
        <Button kind="primary" icon="add" label="Primary" theme="blue" />
        <Button kind="primary" icon="add" label="Primary" theme="coral" />
        <Button kind="primary" icon="add" label="Primary" theme="quartz" />
        <Button kind="primary" icon="add" label="Primary" theme="mushroom" />
        <Button kind="primary" icon="add" label="Primary" theme="danger" />
        <Button kind="primary" icon="add" label="Primary" theme="evolved-blue" />
        <Button kind="primary" icon="add" label="Primary" theme="evolved-mushroom" />
        <Button kind="primary" icon="add" label="Primary" theme="evolved-quartz" />
        <Button kind="primary" icon="add" label="Primary" theme="green" />
        <Button kind="primary" icon="add" label="Primary" theme="evolved-green" disabled />
      </div>
    </div>
    <div className="flex flex-col gap-2">
      <Text>Primary as Link</Text>
      <div className="grid grid-cols-4 gap-4">
        <Button
          kind="primary"
          icon="add"
          label="Link Primary"
          theme="evolved-green"
          href="https://cohere.com"
        />
        <Button
          kind="primary"
          icon="add"
          label="Link disabled"
          theme="evolved-green"
          disabled
          href="https://cohere.com"
        />
      </div>
    </div>
    <div className="flex flex-col gap-2">
      <Text>Secondary</Text>
      <div className="grid grid-cols-4 gap-4 xl:grid-cols-5">
        <Button kind="secondary" icon="add" label="Secondary" theme="default" />
        <Button kind="secondary" icon="add" label="Secondary" theme="evolved-green" />
        <Button kind="secondary" icon="add" label="Secondary" theme="blue" />
        <Button kind="secondary" icon="add" label="Secondary" theme="coral" />
        <Button kind="secondary" icon="add" label="Secondary" theme="quartz" />
        <Button kind="secondary" icon="add" label="Secondary" theme="mushroom" />
        <Button kind="secondary" icon="add" label="Secondary" theme="danger" />
        <Button kind="secondary" icon="add" label="Secondary" theme="evolved-blue" />
        <Button kind="secondary" icon="add" label="Secondary" theme="evolved-mushroom" />
        <Button kind="secondary" icon="add" label="Secondary" theme="evolved-quartz" />
        <Button kind="secondary" icon="add" label="Secondary" theme="green" />
        <Button kind="secondary" icon="add" label="Secondary" theme="evolved-green" disabled />
      </div>
    </div>
    <div className="flex flex-col gap-2">
      <Text>Cell</Text>
      <div className="grid grid-cols-4 gap-4 xl:grid-cols-5">
        <Button kind="cell" icon="add" label="Cell" theme="default" />
        <Button kind="cell" icon="add" label="Cell" theme="evolved-green" />
        <Button kind="cell" icon="add" label="Cell" theme="blue" />
        <Button kind="cell" icon="add" label="Cell" theme="coral" />
        <Button kind="cell" icon="add" label="Cell" theme="quartz" />
        <Button kind="cell" icon="add" label="Cell" theme="mushroom" />
        <Button kind="cell" icon="add" label="Cell" theme="danger" />
        <Button kind="cell" icon="add" label="Cell" theme="evolved-blue" />
        <Button kind="cell" icon="add" label="Cell" theme="evolved-mushroom" />
        <Button kind="cell" icon="add" label="Cell" theme="evolved-quartz" />
        <Button kind="cell" icon="add" label="Cell" theme="green" />
        <Button kind="cell" icon="add" label="Cell" theme="evolved-green" disabled />
      </div>
    </div>
    <div className="flex flex-col gap-2">
      <Text>Outline</Text>
      <div className="grid grid-cols-4 gap-4 xl:grid-cols-5">
        <Button kind="outline" icon="add" label="Outline" theme="default" />
        <Button kind="outline" icon="add" label="Outline" theme="evolved-green" />
        <Button kind="outline" icon="add" label="Outline" theme="blue" />
        <Button kind="outline" icon="add" label="Outline" theme="coral" />
        <Button kind="outline" icon="add" label="Outline" theme="quartz" />
        <Button kind="outline" icon="add" label="Outline" theme="mushroom" />
        <Button kind="outline" icon="add" label="Outline" theme="danger" />
        <Button kind="outline" icon="add" label="Outline" theme="evolved-blue" />
        <Button kind="outline" icon="add" label="Outline" theme="evolved-mushroom" />
        <Button kind="outline" icon="add" label="Outline" theme="evolved-quartz" />
        <Button kind="outline" icon="add" label="Outline" theme="green" />
        <Button kind="outline" icon="add" label="Outline" theme="evolved-green" disabled />
      </div>
    </div>
  </div>
);

export const Selection: Story = {
  args: {
    kind: 'primary',
    icon: 'arrow-right',
    theme: 'evolved-green',
    label: 'Button',
    stretch: true,
  },
};
